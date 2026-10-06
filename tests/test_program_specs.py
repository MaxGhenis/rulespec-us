"""Canonical jurisdiction program specs must be structurally valid and every
scope entry must resolve to a module in this repository.

Jurisdiction content lives beside each jurisdiction's programs/, so the audit
needs no external checkouts. Every declared scope entry must resolve; there is
no dangling-scope allowlist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tools.build_program_artifacts import discover_specs

ROOT = Path(__file__).resolve().parents[1]
JURISDICTION_RE = re.compile(r"^us(?:-[a-z0-9]+)*$")


def scope_prefix(program: str, scope_name: str) -> str:
    normalized = scope_name.strip()
    if normalized == "federal":
        return "us"
    if normalized == "state":
        return program.split("/", 1)[0]
    return normalized


def spec_paths() -> list[Path]:
    return sorted(
        path
        for jurisdiction in ROOT.iterdir()
        if jurisdiction.is_dir()
        and JURISDICTION_RE.fullmatch(jurisdiction.name) is not None
        for path in (jurisdiction / "programs").glob("**/*.yaml")
    )


def test_program_specs_exist() -> None:
    assert spec_paths(), "canonical <jurisdiction>/programs/ roots contain no specs"


def test_artifact_builder_discovers_every_program_yaml() -> None:
    expected = [path.relative_to(ROOT) for path in spec_paths()]
    discovered = [build.spec_path for build in discover_specs(ROOT)]
    assert discovered == expected


def test_artifact_builder_rejects_yaml_without_program(tmp_path: Path) -> None:
    spec = tmp_path / "us" / "programs" / "demo" / "fy-2026.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text("period: 2026-01\noutputs: [demo]\n")

    with pytest.raises(SystemExit, match="program must be a non-empty string"):
        discover_specs(tmp_path)


def test_artifact_builder_rejects_incomplete_program_spec(tmp_path: Path) -> None:
    spec = tmp_path / "us" / "programs" / "demo" / "fy-2026.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text("program: us/demo\nperiod: 2026-01\noutputs: []\n")

    with pytest.raises(SystemExit, match="outputs must be a non-empty list"):
        discover_specs(tmp_path)


def test_artifact_builder_rejects_atomic_or_unknown_program_spec_keys(
    tmp_path: Path,
) -> None:
    spec = tmp_path / "us" / "programs" / "demo" / "fy-2026.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(
        "program: us/demo\nperiod: 2026-01\noutputs: [demo]\nformat: rulespec/v1\n"
    )

    with pytest.raises(SystemExit, match="unsupported spec keys: format"):
        discover_specs(tmp_path)


@pytest.mark.parametrize("extension", (".yml", ".YAML"))
def test_artifact_builder_rejects_noncanonical_yaml_extensions(
    tmp_path: Path,
    extension: str,
) -> None:
    spec = tmp_path / "us" / "programs" / "demo" / f"fy-2026{extension}"
    spec.parent.mkdir(parents=True)
    spec.write_text("program: us/demo\nperiod: 2026-01\noutputs: [demo]\n")

    with pytest.raises(SystemExit, match="regular files using exact .yaml"):
        discover_specs(tmp_path)


def test_no_legacy_program_root_or_extension() -> None:
    assert not (ROOT / "programs").exists()
    legacy_extensions = [
        path.relative_to(ROOT).as_posix()
        for jurisdiction in ROOT.iterdir()
        if jurisdiction.is_dir()
        and JURISDICTION_RE.fullmatch(jurisdiction.name) is not None
        for path in (jurisdiction / "programs").glob("**/*.yml")
    ]
    assert legacy_extensions == []


def test_program_specs_are_structurally_valid() -> None:
    problems: list[str] = []
    for spec_path in spec_paths():
        rel = spec_path.relative_to(ROOT).as_posix()
        raw = yaml.safe_load(spec_path.read_text()) or {}
        if not isinstance(raw, dict):
            problems.append(f"{rel}: spec root must be a mapping")
            continue
        if not isinstance(raw.get("program"), str) or not raw.get("program"):
            problems.append(f"{rel}: missing or non-string `program`")
        else:
            segments = [segment for segment in raw["program"].split("/") if segment]
            relative = spec_path.relative_to(ROOT)
            if len(segments) < 2 or segments[0] != relative.parts[0]:
                problems.append(
                    f"{rel}: program id must begin with its jurisdiction directory"
                )
            elif Path(*segments[1:]) != spec_path.parent.relative_to(
                ROOT / relative.parts[0] / "programs"
            ):
                problems.append(
                    f"{rel}: canonical path must match the complete program id"
                )
        if "period" not in raw:
            problems.append(f"{rel}: missing `period`")
        outputs = raw.get("outputs")
        if (
            not isinstance(outputs, list)
            or not outputs
            or not all(isinstance(item, str) for item in outputs)
        ):
            problems.append(f"{rel}: `outputs` must be a non-empty list of strings")
        scope = raw.get("scope")
        if scope is not None and not isinstance(scope, dict):
            problems.append(f"{rel}: `scope` must be a mapping")
    assert problems == []


def test_every_scope_entry_resolves() -> None:
    problems: list[str] = []

    for spec_path in spec_paths():
        rel = spec_path.relative_to(ROOT).as_posix()
        raw = yaml.safe_load(spec_path.read_text()) or {}
        if not isinstance(raw, dict) or not isinstance(raw.get("program"), str):
            continue
        for scope_name, paths in (raw.get("scope") or {}).items():
            prefix = scope_prefix(raw["program"], scope_name)
            jurisdiction = ROOT / prefix
            if not jurisdiction.is_dir():
                problems.append(f"{rel}: no jurisdiction directory {prefix}/")
                continue
            for path in paths or []:
                if not (jurisdiction / f"{path}.yaml").exists():
                    problems.append(
                        f"{rel}: {scope_name}: {path} does not resolve in {prefix}/"
                    )
    assert problems == []
