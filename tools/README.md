# Program Artifact Pipeline

`<jurisdiction>/programs/` specs are source; compiled artifacts are build
outputs and are never committed. The `program-artifacts` workflow compiles
every spec through axiom-compose + axiom-rules-engine (pinned refs in the
workflow env):

- **On PRs** it is a gate: every canonical program spec must parse as a
  ProgramSpec, compose, and compile through the Rust engine. Any failure makes
  the check red, so spec/corpus drift (renamed module paths, coverage-gate
  violations) is caught at PR time.
- **On main** it repeats the same fail-closed build as a validation gate.
  Publishing or activating a release is a separate, explicitly approved
  operation.

Every artifact's `metadata.provenance` records the corpus SHA, spec path +
sha256, composer version, and engine version; the manifest carries the same
plus artifact sha256s. Given a corpus commit and the pinned toolchain, the
build is byte-reproducible.

Once a release is explicitly approved and published, consumers pin its tag and
per-file sha256s instead of vendoring artifacts.

Run locally:

```bash
AXIOM_RULES_ENGINE_BIN=~/axiom-rules/target/release/axiom-rules-engine \
  python tools/build_program_artifacts.py --root "$PWD"  # writes dist/
```
