# Step 3 — Abstract-level triage

Timestamp: 2026-08-31 Asia/Shanghai

`Overlap` is the 0–4 abstract-level axis count. `—` means unavailable metadata, not an inferred fact.

| Title | Date | Problem framing | Core mechanism | Key insight | Domain | Overlap | Source |
|---|---|---|---|---|---|---:|---|
| VLMPC | 2024 | future visual goals for manipulation | VLM/video predictive control | visual prediction can guide action | manipulation | 2 | doi:10.15607/rss.2024.xx.106 |
| GWM | 2025 | scalable 3D robot world modeling | Gaussian scene dynamics | explicit 3D aids scalable simulation | manipulation | 1 | openalex:W7077974710 |
| Towards High-Consistency Embodied World Model with Multi-View Trajectory Videos | 2025 | multi-view consistency | multi-view trajectory-video training | view consistency improves prediction | embodied AI | 1 | arXiv:2511.12882 |
| ConditionNET | 2024 | execution monitoring | learned preconditions/effects | task effects expose failure | manipulation | 2 | doi:10.1109/LRA.2024.3520916 |
| GR-2 | — | video-language-action generation | generative VLA | joint generation supports action | manipulation | 1 | doi:10.59350/m5s7m-3kd85 |
| Error correction of model analog forecasts… | — | ENSO forecasting | linear inverse correction | residual correction improves climate forecasts | climate | 0 | doi:10.5194/egusphere-egu26-16264 |
| Vision-Language-Action and Vision Language Models… | 2026 | VLA survey | survey | synthesis | robotics | 1 | doi:10.20944/preprints202606.0400.v1 |
| Online kinematic calibration of robot manipulator | 2024 | kinematic calibration | neural calibrator | online measurements correct kinematics | calibration | 0 | doi:10.1016/j.measurement.2024.115281 |
| Robot self-calibration using actuated 3D sensors | 2023 | sensor/robot calibration | actuated 3D sensing | self-observation calibrates geometry | calibration | 0 | doi:10.1002/rob.22259 |
| Distributed Simultaneous Localisation and Auto-Calibration… | 2024 | localization/calibration | Gaussian belief propagation | distributed beliefs support calibration | SLAM | 0 | doi:10.1109/LRA.2024.3352361 |
| Extrinsic Infrastructure Calibration… | 2023 | extrinsic calibration | hand-eye robot-world formulation | known geometry solves calibration | calibration | 0 | doi:10.1109/IV55152.2023.10186703 |
| Bayesian-Inference Approach to Calibrating Models for Simulation | 2023 | simulator parameter calibration | Bayesian inference | uncertainty-aware parameter fitting | simulation | 1 | doi:10.1115/1.4062199 |
| Position-Based Robot Calibration and Compensation… | 2023 | pose calibration | adjoint error model | structured residual compensates pose | calibration | 0 | doi:10.1007/s10846-023-01891-6 |
| Online Adaptation of Fourier Series Based Acoustic Transfer Function… | 2023 | acoustic localization | online Fourier adaptation | update transfer model online | audio robotics | 0 | doi:10.1109/RO-MAN57019.2023.10309550 |
| Robot Learning and Adaptation for Intelligent Behavior | 2023 | broad robot learning | — | — | robotics | 0 | doi:10.52783/tojqi.v11i4.10017 |
| Designing a Basic Robot Model & Creating Instructions | 2023 | educational robot design | tutorial | — | education | 0 | doi:10.1007/978-1-4842-9706-3_29 |
| Calibration and Proportional Line Follower | 2023 | line-follower calibration | tutorial | — | education | 0 | doi:10.1007/978-1-4842-9706-3_25 |
| Adapting World Models with Latent-State Dynamics Residuals | 2025-04 | adapt source WM to target dynamics | action-conditioned latent residual module | low-capacity residual adapts efficiently | visual MBRL/sim-to-real | 3 | arXiv:2504.02252 |
| New indoor propagation model proposed for future B5G/6G rollout | 2024 | wireless propagation | propagation model | — | communications | 0 | doi:10.1515/freq-2023-0234 |
| VDAWorld | 2025 | VLM-directed world abstraction | abstraction plus simulation | task abstraction structures simulation | embodied AI | 1 | arXiv:2512.11061 |
| Urban Macrocell Propagation Model… | 2023 | wireless propagation | propagation model | — | communications | 0 | doi:10.1109/IWCMC58020.2023.10182440 |
| WorldModelBench | 2025 | evaluate video generators as WMs | benchmark/judge | visual quality alone is insufficient | video world models | 1 | arXiv:2502.20694 |
| WorldWarp | 2025 | 3D-consistent video dynamics | asynchronous diffusion/geometry propagation | geometry improves consistency | video world models | 1 | arXiv:2512.19678 |
| ReVisionLLM | 2025 | hour-long temporal grounding | recursive VLM | recursive review handles long videos | video understanding | 0 | doi:10.1109/CVPR52734.2025.01771 |
| Rollout-Guided Switching to Failure-Trained Policies… | 2026 | switch policies before failure | rollout-guided residual RL | predicted failure selects controller | autonomous control | 1 | doi:10.1109/SAMI68106.2026.11420744 |
| ROCAP | 2026 | attack VLA | rollout/occlusion-calibrated patches | rollout awareness strengthens attacks | VLA security | 0 | doi:10.1109/ICCIR70228.2026.11633313 |
| Rollout of the Standardized Crediting Framework… | 2026 | finance/development | policy rollout report | — | finance | 0 | doi:10.1596/44940 |
| Feedback World Model Enables Precise Guidance of Diffusion Policy | 2026-05 | online WAM correction from real observations | latent observer feedback state plus action-aware guidance | deployment observations suppress WAM drift | manipulation | 4 | arXiv:2605.15705 |
| Say, Dream, and Act | 2026-02 | video-conditioned manipulation | distilled video WM plus real-observation-grounded action model | policy treats imagination as context, not command | manipulation | 3 | arXiv:2602.10717 |
| When to Trust Imagination | 2026-05 | future–reality WAM verification | FFDC verifier and adaptive chunk length | mismatch should trigger early replanning | manipulation | 3 | arXiv:2605.06222 |
| CheckVLA | 2026-07 | execution-time verification/repair | frozen action-conditioned WM, calibrated trigger, suffix rewrite | committed actions imply expected observations | long-horizon manipulation | 3 | arXiv:2607.26789 |
| DreamX-Phi 1.0 | 2026-08 | faithful action-conditioned video prediction | per-arm PRoPE, depth branch, object-focused teacher | realism does not imply action/physics fidelity | manipulation WAM | 2 | arXiv:2608.13489 |
| tau0-WM | 2026-06 | joint video/action prediction and test-time refinement | candidate simulation, reward scoring, future-conditioned re-query | prediction is useful when it changes actions | manipulation | 2 | arXiv:2606.01027 |
