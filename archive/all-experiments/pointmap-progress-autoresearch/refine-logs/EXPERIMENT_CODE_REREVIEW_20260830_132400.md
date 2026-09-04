# E0 post-fix code re-review

Verdict: **CHANGES_REQUIRED**

The reviewer verified that all seven blockers from the first review were fixed correctly:

- exact 5 x 12 x 6 grid and per-family class coverage;
- genuine target occlusion and exact NaN/RGB/seg provenance;
- separate rigid PointMap projection strata;
- authoritative instance association;
- exact audit/dataset/manifest/code/config result provenance;
- task-family-cluster statistics;
- finite operating thresholds and strict JSON.

No new label, metric, geometry, calibration, action-leakage, provenance, deterministic-runtime, or task-cluster arithmetic blocker was found.

One new blocking issue remained: Scene5 and Scene6 were both the same red-mug-on-plate semantic family, while the split treated their integer task indices as independent task families. A held-out mug/plate fold could therefore train on a near duplicate and inflate cross-family generalization.

Required correction:

1. Replace one near-duplicate task with a semantically distinct movable-reference `inside/on` task.
2. Store an explicit unique `task_family_id` per task.
3. Audit the family mapping and split/aggregate using `task_family_index`, not an implicit task-index assumption.
4. Rerun five-task sanity and obtain one final review before the registered collection.

The reviewer confirmed that the prior supplied implementation hashes matched and that AST parsing passed. No files were edited by the reviewer.
