# Archived experiment manifest

Snapshot date: 2026-09-04. The archive is a sanitized public snapshot of the
local research workspace.

## Included source roots

- `functional-geometry-vla-wam`
- `implementation-stage`
- `novelty7_autoresearch`
- `object-belief-autoresearch`
- `pi05-progress-autoresearch`
- `pointmap-progress-autoresearch`
- `ideaspark_run`
- `scoop_functional_geometry`
- `research-stage`
- `research-wiki`
- `refine-logs`
- `idea-stage`

In addition, `../skills/all-local-skills/` contains the source of every local
research skill that could be safely copied without its installed runtime.

The directory layout inside `archive/all-experiments/` preserves the original
relative paths so that old links in research notes remain meaningful.

## Included file types

Markdown, Python, shell/configuration files, JSON/JSONL, YAML, text logs,
research markers, manifests, and experiment metadata/results summaries.

## Deliberately omitted

- model/checkpoint binaries (`.pt`, `.pth`, `.ckpt`, `.safetensors`);
- array/data/video/image artifacts (`.npz`, `.npy`, `.mp4`, `.webm`, `.png`,
  `.jpg`, `.jpeg`, `.gif`);
- Python bytecode and cache directories;
- `.aris/vendor` and its third-party dependency tree;
- unselected private orchestration/runtime traces;
- raw paper/PDF collection and external datasets;
- SSH keys, credentials, server addresses, and private absolute paths.

One overlong literature filename was shortened to
`ideaspark_run/counterfactual-residual-transport/phase0/fulltext/user_ref_title_CheckVLA.md`;
its contents are unchanged apart from public-path redaction.

All path redactions use placeholders such as `<PERSONAL_RESEARCH_ROOT>` and
`<PRIVATE_SERVER>`. They are intentionally not executable paths.

`orchestration-redacted/` contains the research-related `.aris` state,
candidate, claim, compute, trace, tool and historical-backup subsets that were
safe to preserve after redaction. The local `.agents/runtime` dependency
installation is not included;
the reusable skill source is in `../skills/all-local-skills/` relative to
the repository root.

Some historical auto-research JSON files are raw orchestration/provenance
outputs and were already malformed in the source workspace (for example,
truncated strings in old configuration snapshots). They are preserved as
history; do not treat every archived JSON file as a runnable configuration.
Use the claim/audit Markdown files and the current portable scripts as the
authoritative handoff surface.
