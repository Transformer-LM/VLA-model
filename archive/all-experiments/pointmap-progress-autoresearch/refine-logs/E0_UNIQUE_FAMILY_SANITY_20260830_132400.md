# E0 explicit-family sanity

Status: **PASS for runtime/integrity sanity; not scientific evidence**.

The corrected task families are:

1. `packaged_food_in_basket` -- Living Room Scene 1;
2. `condiment_in_tray` -- Living Room Scene 3;
3. `mug_on_plate` -- Living Room Scene 5;
4. `bowl_on_bowl_stack` -- Kitchen Scene 2;
5. `bowl_on_plate` -- Kitchen Scene 5.

The five tasks come from five different scenes and no exact target/reference pair is repeated. The collector stores both `task_index` and explicit `task_family_index`/`task_family_id`; audit, training split, and aggregation use the explicit family field.

One reset seed generated all 30 requested cells. Label, relation, association, same-prestate, occlusion, non-finite, and PointMap-feature checks were zero-error. Median rigid-cloud projection errors were 1.1--4.8 mm on visible strata. The audit deliberately failed the registered-data gate because only one of twelve seeds was present; invalidated-target projection covered four of five families at this single seed, and the full twelve-seed audit still requires all five.

Remote sanity dataset SHA-256: `7481d3502c4f7eefa6a96f9b23bb6e9676fe3f40f8da114792f7706d35448846`.
