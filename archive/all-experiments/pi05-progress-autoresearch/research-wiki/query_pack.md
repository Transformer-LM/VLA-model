# Research Wiki Query Pack

_Auto-generated. Do not edit._

## Project Direction
# Research Brief — 长时序 VLA 的可靠进度、验证与恢复

**状态：** ready-for-discovery；已选定方向，自动 Idea 发现与实验规划  
**范围：** 研究与实验设计；论文写作关闭；本轮不启动 GPU 或真实机器人

## 现实问题

用户已经复现 π0.5，并在长时序、多阶段任务中观察到：策略会遗忘已完成步骤、误判动作成功、错误推进任务，以及在失败后无法恢复。需要判断这些失败来自历史缺失、任务进度误判、低层动作能力、固定 action chunk，还是恢复数据不足。

## 研究目标

自动寻找一个不以“再加一个通用 memory module”为创新、能够被严格查新、可由 π0.5 或另一可复现 VLA 验证的研究 Idea。WAM 仅在其能提供普通 VLM、状态机或几何 verifier 无法提供的机制增益时采用。

## 必须避免的重复

- 最近帧拼接、普通 RNN/Transformer history encoder；
- 通用 keyframe memory；
- 仅把执行历史总结成语言；
- 普通高层 VLM 分解任务、低层 VLA 执行；
- 无校准的 verifier + replan；
- 将 MemoryVLA、HAMLET、KEMO、LoHo-Manip、Goal2Skill 或 Explicit Lang
## Open Gaps
# Gap Map

## G1 — Unmeasured oracle-progress headroom

Status: unresolved. Existing papers show average gains from memory or progress modules, but the user's observed π0.5 failures have not been decomposed by giving the executor oracle current subtask, oracle completion, or oracle recovery. Without this test, a memory method may target the wrong bottleneck.

## G2 — Scalar progress is not semantic task state

Status: unresolved. ProgressVLA and task-progress probes use normalized scalar progress or normalized time. Branching, repeated, reversible, and partially completed tasks require a structured state whose components can advance independently or regress.

## G3 — Memory can preserve a wrong conclusion

Status: unresolved. Keyframe, recurrent-token, perceptual-cognitive, and language memories preserve history, but do not generally expose which evidence supports a completion claim or retract only the conclusions invalidated by contradictory evidence.

## G4 — Counterfactual history identifiability

Status: partially covered. MIKASA-Robo and recurrent-memory studies expose partial observability, but current comparisons rarely use paired episodes with matched current observations a
## Key Papers (22 total)
- [paper:bagaria2026_recursive_belief_vision] Recursive Belief Vision Language Action Models
- [paper:bhardwaj2026_decoding_task_progress] Decoding Task Progress from VLA Representations
- [paper:cherepanov2026_μvla_recurrent_memory] $μ$VLA: On Recurrent Memory for Partially Observable Manipulation in VLA Models
- [paper:intelligence2025_π05_visionlanguageaction_model] $π_{0.5}$: a Vision-Language-Action Model with Open-World Generalization
- [paper:kang2024_incorporating_task_progress] Incorporating Task Progress Knowledge for Subgoal Generation in Robotic Manipulation through Image Edits
- [paper:king2026_echomemory_controlled_study] Echo-Memory: A Controlled Study of Memory in Action World Models
- [paper:koo2025_hamlet_switch_your] HAMLET: Switch your Vision-Language-Action Model into a History-Aware Policy
- [paper:li2026_failureaware_reliable_offlinetoonline] Failure-Aware RL: Reliable Offline-to-Online Reinforcement Learning with Self-Recovery for Real-World Manipulation
- [paper:li2026_learning_actionable_manipulation] Learning Actionable Manipulation Recovery via Counterfactual Failure Synthesis
- [paper:lin2025_echovla_robotic_visionlanguageaction] EchoVLA: Robotic Vision-Language-Action Model with Synergistic Declarative Memory for Mobile Manipulation
- [paper:liu2025_trivla_triplesystembased_unified] TriVLA: A Triple-System-Based Unified Vision-Language-Action Model with Episodic World Modeling for General Robot Control
- [paper:liu2026_checkvla_executiontime_verification] CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation
## Recent Relationships (51 total)
  idea:causal-progress-harm-audit --addresses_gap--> gap:G6
  idea:wam-error-attribution-gate --addresses_gap--> gap:G3
  idea:wam-error-attribution-gate --addresses_gap--> gap:G5
  idea:wam-error-attribution-gate --addresses_gap--> gap:G6
  idea:pending-postcondition-memory --addresses_gap--> gap:G2
  idea:pending-postcondition-memory --addresses_gap--> gap:G3
  idea:pending-postcondition-memory --addresses_gap--> gap:G5
  idea:last-correctable-time-hazard --addresses_gap--> gap:G5
  idea:last-correctable-time-hazard --addresses_gap--> gap:G6
  idea:recoverability-signature --addresses_gap--> gap:G5
  idea:recoverability-signature --addresses_gap--> gap:G6
  idea:belief-update-firewall --addresses_gap--> gap:G2
  idea:belief-update-firewall --addresses_gap--> gap:G3
  idea:belief-update-firewall --addresses_gap--> gap:G4
  idea:memory-semantics-router --addresses_gap--> gap:G2
  idea:me
