# VLA/WAM research skill upgrade

Base: `research-sync-20260904`, commit `80e39e898943d11a0d3b075c9bbc1180ea6480d6`.

## Changes

- Preserve the existing eight-phase research workflow and WAM taxonomy.
- Enforce phase-specific artifacts, hash freshness, archived revisions and dedicated
  audit/review adjudication. Old states remain readable; unverified completions reopen.
- Add resource reservation and idempotent settlement, including failed jobs.
- Record immutable experiment nodes with hypothesis/parent IDs and protocol binding.
- Add deterministic execution diagnosis and visual-rollout diagnostic guidance.
- Resolve metrics by JSON key path, bind current audits, and distinguish pilot/main
  scope. Enforce configured training-seed minimums for main claims.
- Replace axis-count novelty scoring and empty-search novelty with explicit coverage
  and unresolved outcomes. Route idea generation through the selected provider and
  the actual project compute budget.
- Select WAM evidence per claim; preserve statistical uncertainty and negative results.
- Add scoped lessons and a skill-update proposal procedure. Existing skills remain the
  execution interface; no external autoresearch framework is installed.
- Synchronize both distributed copies of embodied-autoresearch. Historical archive
  files and completed research results are untouched.

## Validation

Run on Python 3.12 with no GPU, API key or model calls:

```text
python -X utf8 skills/embodied-autoresearch/tests/test_contracts.py
```

32 behavioral regression tests cover a complete negative-result dossier, bogus
artifacts, failed literature coverage, changed evaluator/raw results, stale revisions,
metric-key mismatch, insufficient main seeds, reservations, duplicate settlements,
overruns, nonfinite usage, reopening, legacy states and phase-local skill resolution.
Skill frontmatter is checked with skill-creator's quick_validate.py in UTF-8 mode.

### Follow-up audit (2026-09-27)

- Fixed omission of settled failed/cancelled jobs from experiment registration.
- Bound direct claim metrics to cited completed experiments. Separate aggregates
  now declare contributors and a versioned, hash-bound analysis script.
- Recompute budget status after configuration changes while retaining actual usage
  and active reservations; this does not grant permission to raise compute limits.
- Added four regression cases including rejection and recovery paths for these fixes.
- Confirmed origin is `Transformer-LM/VLA-model`, based on `research-sync-20260904`.
  GitHub connector identity is `qsgg686-coder`, with `push: false` at this audit;
  local commits must not be described as uploaded.

## Operational limits

- This is a skills/runtime-contract upgrade, not a completed VLA training experiment.
- The ledger records and validates reservations; the runner/scheduler must actually
  enforce process timeouts, editable file scope and execution permissions.
- Hashes and JSON linkage prove consistency, not scientific truth or that an external
  process honestly generated the data. Reviewers still inspect raw execution evidence.
- Model-family provenance is recorded metadata, not an attestation service.
- Aggregate lineage is declared metadata; the checker does not rerun statistics.
- Main-claim seed gating currently targets training studies; frozen-policy episode
  replication needs a separately reviewed acceptance design.
- Real-robot execution still requires a separate explicitly authorized adapter.
- Some ARIS dependencies are not bundled in this sanitized snapshot. Preflight reports
  their absence at the phase that needs them; it does not silently install archives.
- New experimental protocols use new runs, with baseline re-evaluation where needed.
- Scoped lesson promotion is a documented workflow, not automatic self-modification.

Source-level design references and exact artifact schemas are in
[`execution-contracts.md`](../skills/embodied-autoresearch/references/execution-contracts.md).

## 2026-09-27：官方更新与实际收益复核

### 结论与证据边界

这次改进提高了研究流程的可追踪性、失败记账和结论接入的一致性。
32 项测试证明这些具体检查能够接受有效样例、拒绝已覆盖的错误样例；
没有运行真实 GPU 训练或跨模型评审，也没有完成新旧版本的 VLA/WAM 对照实验。
因此不能据此声称研究成功率、创新性、实验效率或论文质量已经提高。

本次读取了 ARIS 的 Codex 镜像说明、审计/结论/实验桥接/方法规划/查新/评审技能，
以及 assurance、acceptance、evidence pre-check、reviewer independence、resume、
governance 和 compute contracts；同时对照下表所列项目的实际材料。
开源项目能力范围不同，未以 star 数或作者宣传排序“谁最好”。

### 与开源方案的对照

| 来源与本次查看材料 | 适合借鉴的机制 | 对本 skill 的判断 |
|---|---|---|
| [Karpathy program.md，228791f](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) | 固定评测、受限实验、逐次记录 | 已有固定协议和用量账本；通用 VLA 训练不适合照搬固定五分钟实验或无限循环。实际超时仍依赖 runner。 |
| [autoresearch-robotics program.md，ff30cc4](https://github.com/jellyheadandrew/autoresearch-robotics/blob/ff30cc481af9343b9c96f448b5ed72b75bfcd562/program.md) | 环境指标结合 rollout 视觉诊断、累积失败记录 | 已加入视觉诊断指引；还没有自动生成/分析 rollout 的完整适配器，不应称为已实现视觉闭环。 |
| [EvoScientist README，8a05cae](https://github.com/EvoScientist/EvoScientist/blob/8a05cae32ec8d23a077eeba07030cf7ded2951b4/README.md) | 持久记忆，重复观察提炼为待审核技能建议 | 已有带适用范围的 lesson/proposal 规范；没有安装 EvoMemory，也没有实现自动技能进化。其最新说明还涉及中文记忆检索和恢复修复，不能仅复制提示词获得这些运行时能力。 |
| [ARIS evidence-precheck，341f914](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/341f914024d270dc5c8fa51337d1ad38829273aa/skills/skills-codex/shared-references/evidence-precheck.md) | 先查证据存在，再做科学判断 | 本地使用精确 JSON key path 和实验 ID，避免“同一个文件里碰巧有这个数”通过；仍需语义审查。 |
| [ARIS HERO，4bcaa0f](https://github.com/wanshuiyin/HERO-Anti-OverDefense/blob/4bcaa0fe7f6dad34e90db3089567f416a66c122c/README.md) | 修复实际可达问题，避免审查流程无限膨胀 | 保留会触发状态失效的证据校验；新增检查必须对应实际失败。WAM 评审项目按结论适用，不能机械要求所有 endpoint。 |
| [Anti-Autoresearch README，f3ed757](https://github.com/wanshuiyin/Anti-Autoresearch/blob/f3ed7577beaff9c44280f8fcddcfce0e51a6292d/README.md) | 将不一致线索交给审查者，不自动判定造假或科学结论 | 适合外部材料核查；没有将其完整审稿工作流加入每个实验，也不以文风作为科研有效性的判据。 |

### ARIS 官方有哪些近期变化

官方仓库为 [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)。
本次锁定 main 提交 `341f914024d270dc5c8fa51337d1ad38829273aa`，提交时间为
2026-09-18 UTC。官方 release API 返回最新 ARIS-Code 为
[v0.4.27](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/releases/tag/v0.4.27)，
发布时间 2026-09-18 18:03 UTC（北京时间 9 月 19 日）。CLI 版本与 Markdown skill
快照分开记录；README 的新闻日期不能代替 release/commit 时间。

- [9 月 6 日 reviewer 更新，0472e53](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/commit/0472e530251cdbd3364c33b110063c58f819edd7)：更新默认 reviewer 模型及能力回退；保留执行者。没有据此修改用户的模型配置。
- [9 月 10 日 codex-exec bridge](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/341f914024d270dc5c8fa51337d1ad38829273aa/mcp-servers/codex-exec/README.md)：官方说明用于适配移除旧 MCP 入口后的 Codex CLI，保留线程和 reviewer 参数；仅影响使用该 MCP 路由的安装。
- 9 月 15 日新增 `research-implement-feature`，围绕声明假设组织实现；它是新能力，不代表现有 experiment-bridge 必须替换。
- 9 月 16 日新增插件打包、Codex native mirror 路由及 setup 接入。采用新安装方式前仍需保留用户自定义技能和审查配置。
- v0.4.27 主要修复空会话与恢复列表；这是 CLI 可用性改进，不是科研效果评测。

### 本次落地修正

1. **ARIS 审计交接**：保留原始 JSON，用 `aris_source` 关联本地报告；检查原始
   PASS、证据覆盖、hash 与 reviewer family，防止转换时升级判定或补造审查范围。
2. **独立性分开检查**：integrity audit 和 claim verdict 都必须记录不同模型家族，
   才能将 evidence-audit 阶段标为 independent。模型字段仍是声明，不是身份认证。
3. **依赖接入**：支持显式 `~/.codex/skills` 安装路径；非法 roots 输出结构化 blocker；
   idea-discovery 预检补上实际调用的 `novelty-check`。
4. **文档一致性**：可选 research-wiki/research-lit 缺失时不冒充已完成；明确训练种子
   门槛没有 episode-only 豁免，保留 scope 与未知项。
5. 新增 8 项行为测试，覆盖有效交接、六类非 PASS、遗漏证据、改写 reviewer 家族、
   混合审查独立性、全局安装路径、错误 roots 和缺失查新依赖。

### 仍需真实运行验证

- 仓库目前是定制技能分发快照，没有项目运行配置，也没有完整 ARIS 执行/审查依赖。
  不能把文件检查通过称为端到端无人值守研究可用。本次没有自动安装或升级全局 ARIS。
- 下一次真实 pilot 应固定同一研究问题、数据、基线和算力，比较旧版与新版的：
  可复现实验数/总用量、错误结论漏检数、误阻断数、人工干预次数及恢复成本。
- 对冻结 VLA 的 episode-only 评估，需要先定义统计独立单位和验收规则再实现支持；
  不应编造 training_seed 绕过现有检查。
- 大型 checkpoint 的 hash 成本、外部 scheduler 超时和远程失败恢复仍需在实际环境测量。
  本地回归测试不能替代这些运行验证。
