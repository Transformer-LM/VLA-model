# ISRAC preliminary results

Latest detailed result: `POLICY_SUPPORTED_MULTITASK_RESULTS_20260831.md`.

Current verdict: the frozen-StarVLA, LIBERO boundary-snapshot compiler has
produced machine-certified aliases on four successful tasks (the original
cream-cheese task plus three new tasks). On the three new tasks, six of eight
automatically screened boundaries passed and yielded 24 certified physical
pairs. The strongest new non-robot state separation is 0.1585 in the generic
pose-vector metric; the translational components are measured in metres while
quaternion components are dimensionless. Factual RGB, depth, proprio,
residual, and state are exact for the best pair at every passing boundary.

This is a partial LIBERO M1 result, not the full E0 gate. Matched-budget
baselines, a second simulator, multiple seeds, a frozen feedback WAM, and
correction-harm remain untested.
