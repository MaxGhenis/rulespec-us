from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reverse_index_workflow_has_no_retired_staleness_surface() -> None:
    assert not (ROOT / ".github/workflows/source-staleness.yml").exists()

    workflow = (ROOT / ".github/workflows/reverse-index.yml").read_text()
    assert "python tests/generate_reverse_index.py --check" in workflow
    assert "axiom_encode_ref" not in workflow
    assert "--corpus-root" not in workflow
    assert "check-source-staleness" not in workflow
    assert "programs/ specs belong exclusively" in workflow


def test_program_artifact_workflow_validates_without_publishing() -> None:
    workflow = (ROOT / ".github/workflows/program-artifacts.yml").read_text()
    builder = (ROOT / "tools/build_program_artifacts.py").read_text()

    assert "gh release create" not in workflow
    assert "attest-build-provenance" not in workflow
    assert "contents: write" not in workflow
    assert 'AXIOM_RULESPEC_REPO_ROOTS_EXCLUSIVE="1"' in builder
