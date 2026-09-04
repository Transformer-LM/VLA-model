# WAM Route Cards for Shortlisted Ideas

## C2｜Interaction Fingerprints（selected pilot）

- **WAM family**：R3/R4，object-structured task latent / structured state dynamics；不是 pixel-video WAM。
- **World state**：persistent address, object pose/state, visibility, identity posterior。
- **Action role**：实际已执行 action chunk 条件化 transition；首轮不做候选动作反事实规划。
- **Control role**：U6 observer/state estimator；仅在 pilot 通过后接 U3 recovery/next-decision gate。
- **Training target**：per-candidate action-effect likelihood 与 calibrated association posterior。
- **Inference consumption**：identity posterior；禁止只报告 pose prediction。
- **Strictness**：属于 embodied action-conditioned belief model，但首轮 oracle diagnostic 不宣称完整 WAM。
- **关键非等价**：不是 OA-WAM fixed address、不是纯 tracker、不是全局 EvoScene prior、不是 generic history concatenation。

## C10｜Non-target Negative Controls（supporting ablation）

- **WAM family**：R4 object-structured dynamics residual。
- **Action role**：模型预测哪些对象应保持零效应，形成 control set。
- **Control role**：U6 calibration/attribution，不单独生成动作。
- **Training target**：common-mode / target-only / pairwise-swap residual topology。
- **Status**：supporting mechanism；不作为第一主创新。

## C1｜Broad OAPCC（not selected）

- **WAM family**：R3/R4；U6 + U3。
- **Reason not selected**：OA-WAM、EvoScene、RB-VLA、CheckVLA、POT-VLA 的并集覆盖过强；只有在 C2/C10 得到明确机制正结果后才可作为系统整合。

