# ARIS integration

Read when resolving ARIS skills, updating them, or adapting their reviewer output.
Reviewed upstream: [ARIS at 341f914](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/341f914024d270dc5c8fa51337d1ad38829273aa),
checked 2026-09-27. This records the reviewed interface; it does not mean ARIS is
installed or automatically updated in this project.

## Installation and updates

ARIS is a skill collection. ARIS-Code is a separate packaged CLI; its v0.4.27
release number is not a version number for this custom embodied skill.

For Codex, use the upstream `skills/skills-codex` package, including its sibling
`shared-references` and helper tooling. Reviewer overlays are separate. Mainline
Claude skills, the Codex base mirror, and reviewer overlays are not interchangeable.
The Codex mirror README lists 83 skills at this revision. This repository's nine
custom skill directories do not include the complete ARIS dependency set.

Resolve project `.agents/skills` first, then this repository's custom roots.
For a deliberate global install, append `~/.codex/skills` to `skill_roots`.
For a different Codex home or a standalone upstream checkout, add its actual
absolute skills directory explicitly. `~` is supported; environment-variable
strings such as `$ARIS_REPO` are not expanded by the resolver.

For an existing ARIS installation, follow the upstream
[Codex installation/update instructions](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/341f914024d270dc5c8fa51337d1ad38829273aa/skills/skills-codex/README.md):
managed symlink installs use reconcile; copied installs use the smart updater's
preview before applying. Inspect changes to the selected skills, references and
tools. Preserve local customizations and the chosen reviewer configuration.
Record the upstream commit and rerun the relevant phase preflight after updating.
Do not install the whole package merely to satisfy an optional adapter.

`novelty-check` is a required dependency at idea discovery. Missing execution or
review skills block only their relevant phase. A resolved SKILL.md does not prove
that its model, MCP server, source connector, or scheduler is operational; check
those capabilities before invoking it and record an unavailable result honestly.

## Reviewer routing

The Codex base mirror uses a fresh same-family agent and remains provisional.
A configured cross-family overlay may support independent review; record the
actual models used for each verdict. An independently reviewed integrity report
does not confer independence on a same-family scientific claim verdict.

The official 2026-09-10 update adds an MCP bridge over `codex exec` for hosts that
previously invoked `codex mcp-server`. This matters to that MCP reviewer route;
it does not require a Codex-native executor to install a second orchestrator.
See the upstream [bridge documentation](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/341f914024d270dc5c8fa51337d1ad38829273aa/mcp-servers/codex-exec/README.md).
Keep the user's selected model and compute limits; a new upstream model default
does not authorize changing them.

## Audit handoff

ARIS `experiment-audit` emits `verdict`, `integrity_status`,
`audited_input_hashes`, `executor_family` and `reviewer_family`. The local runtime
expects `integrity`, `input_hashes`, run/revision fields and model-family fields.
Do not overwrite the only copy of an ARIS report to make it pass a local schema.

1. Give the auditor all registered manifests, their raw artifacts, and the exact
   claim scope. Preserve the prompt and raw response using ARIS review tracing.
2. Save the unmodified JSON, for example
   `refine-logs/aris/EXPERIMENT_AUDIT.original.json`. Preserve its trace files.
3. Write the native `refine-logs/EXPERIMENT_AUDIT.json` with current `run_id` and
   phase `revision`, and `aris_source` pointing to the original JSON. Bind that
   original file in `input_hashes` along with the experiment evidence.
4. Normalize `sha256:<hex>` to `<hex>` and project-contained paths to relative
   paths. Map `executor_family`/`reviewer_family` to the corresponding
   `executor_model_family`/`reviewer_model_family` without changing their values.
5. Only an original `verdict: PASS` and `integrity_status: pass` can enter the
   local pass gate. The runtime verifies its hashes and coverage of every
   registered manifest/artifact. Missing coverage needs a targeted auditor
   follow-up; the executor cannot claim the auditor reviewed additional inputs.

ARIS's general experiment-audit workflow allows advisory continuation on WARN or
FAIL. This embodied workflow can preserve those reports and do repairs, but its
final evidence gate requires a passing integrity audit. Report this difference
explicitly; do not silently loosen the local gate during an upstream update.

ARIS `result-to-claim` uses `yes | partial | no`. Construct local claim entries
with exact metric key paths and experiment IDs after scientific review:
`yes` may map to `supported`, `partial` to `partial`; `no` does not necessarily
mean `refuted`. Insufficient precision remains `inconclusive`. Deterministic
checks cannot choose between those interpretations. Bind preserved reviewer
artifacts in the native verdict's input hashes.

This handoff checks declared coverage and consistency. It does not authenticate
the reviewer, reproduce the experiment, or establish scientific truth.
