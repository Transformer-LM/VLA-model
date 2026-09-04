结论：**BLOCKING / 暂不应进入正式部署**。这是 same-family provisional fresh-agent review。核心连续语义和 geom subtraction 已基本实现，但当前产物尚不能支持“machine-verifiable certificate”与 matched-call yield 结论；尤其分析器与新 P025 schema 实质不兼容。

已确认的正确实现：

- factual 与 candidate 在一次 restore 后连续执行，candidate 确实从 factual endpoint 出发，并未二次 restore：[certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:118>)、[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:174>)。
- `G(C_candidate) \ G(C_factual)` 按 geom ID 做 subtraction，而不是 body-level subtraction：[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:67>)、[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:89>)。
- `max_selected_blocks` 是外部固定上限，当前选择器没有直接用 `|B*|` 决定预算；candidate-contact 只缺 factual subtraction。
- 三个 endpoint 只执行一次并复用于三组无序 pair 比较，这种复用本身正确；pair comparison 不应被重复计作 simulator execution。
- 编译器代码没有读入目标 WAM、score 或 residual 文件；主输出也采用临时文件加原子替换、`allow_nan=False`：[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:538>)。

## BLOCKING issues

1. **分析器与当前 P025 输出 schema 不兼容，真实结果会被解析成零。**

   [analyze_matched_compiler_pilot.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\analyze_matched_compiler_pilot.py:38>) 仍读取旧字段 `total_rollouts_including_selection`、`certified_pairs`、`compiled_pair_count` 和顶层 `best_pairs`；生成器当前输出的是 `actual_simulator_rollouts` / `charged_simulator_rollout_cap`、`certified_endpoint_pairs` / `unique_witness`、`raw_endpoint_pair_count` 和 `blocks[].endpoint_strength_curve`。因此新 artifact 的 unique witness、raw pair、certificate/equality/alignment/effect 都会被忽略或归零。

   具体补丁：

   - 对 `kind == israc_continuous_geom_contact_support_e0` 且 `protocol_version == P025-v1` 建立显式 schema parser。
   - unique witness 从 `sum(block["unique_witness"])` 读取；raw pair 从 `raw_endpoint_pair_count` 读取；证书从所有 `blocks[].endpoint_strength_curve` 展开。
   - 强制验证 `selected_block_count == len(blocks)`、`actual <= charged`、`unused == charged-actual`，以及汇总计数与 block 明细一致。
   - legacy schema 若仍需支持，必须通过显式 adapter/version 分支，禁止静默 fallback。

2. **当前 certificate 不是可独立机器验证的证书。**

   输出只保留 aggregate measurement 和一个摘要；没有保留每帧 factual/candidate state、proprio、RGB/depth、activation trace，甚至没有这些 evidence blob 的 hash。[certificate.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\israc\certificate.py:174>) 的 `certificate_sha256` 也只覆盖少量 metadata、measurements 和 failures，不覆盖：

   - 原始 trace 或 trace digest；
   - repeat envelope；
   - 参数 endpoint 值和 parameter address；
   - static configuration hash；
   - action 内容；
   - world/model/engine identity。

   因而证书摘要相同并不意味着证据相同，第三方无法从产物重新核验 equality、activation 和 first divergence。

   具体补丁：

   - 每个 endpoint 写只读 evidence artifact，例如 `.npz`，保存逐帧 state/proprio、观测度量、active geom、physical/task effect；主 JSON 写 evidence SHA-256。
   - canonical certificate payload 必须覆盖 evidence hashes、完整 envelope、参数地址与 endpoint、两个 static hashes、actions hash、snapshot hash、model/XML/BDDL hash、引擎版本、world IDs。
   - certificate hash 对 canonical 完整 payload 计算，而非仅对 aggregate measurements 计算。

3. **RGB/depth 的“SHA digest byte 向量距离”在有噪声时逻辑错误。**

   [certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:53>) 把图像 SHA-256 的 32 个字节当作数值向量；repeat envelope 再对这些随机化 digest bytes 求 max-abs。任何微小像素变化都可能让 digest 距离接近 255，于是 envelope 可膨胀到足以让完全不同的图像“相等”。这既不是 exact digest equality，也不是有效的图像误差度量。

   具体补丁：

   - 确定性协议：保存十六进制 SHA-256，RGB/depth equality 只允许字符串完全相同，任何不同即失败。
   - 容噪协议：保存原始数组或规范化数值统计，对 RGB 用明确的逐像素 L∞/L1，对 depth 用有限值 mask 下的数值误差；不要对密码学摘要做距离。
   - factual equality envelope 和 candidate divergence envelope 分开。当前代码把 factual repeat 与 candidate repeat 合成一个 envelope，再同时用于 factual equality 和 candidate divergence：[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:406>)。candidate 不稳定性不能放宽 factual equality。

4. **matched-call 计数单位不真实，固定预算分析因此不成立。**

   代码把一次连续 factual→candidate execution 记成两次“rollouts”，每个 block 的三个 endpoint 加一个 repeat 实际是四次 continuous executions，却记为八次 rollout segments：[certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:489>)。三个 endpoint 产生三个 pair 只是 post-hoc comparison，未增加 simulator calls。更重要的是 analyzer 的 yield 使用推导出的实际调用而不是统一的 charged cap，无法证明 fixed-cap advantage。

   具体补丁：

   - 只采用一个可审计单位：推荐实际 `env.step` 次数；其次是 restore 后的 continuous episode 次数。
   - 运行时增量计数，禁止由 `2 + 8*K` 公式推导。
   - matched fixed-budget 主指标分母使用相同 `charged_call_cap`；实际消耗和未用预算只作诊断字段。
   - 明确 endpoint reuse：三次 endpoint execution 产生三组 pair comparison，但 comparison 不计 simulator call。
   - 若某方法 pool 不足，剩余预算仍计入 fixed-cap 分母，或事先定义合法的预算再分配规则并对所有 selector 相同。

5. **replayed factual endpoint 与保存边界不一致时只记录误差，不拒绝样本。**

   `replay_endpoint_error` 被写入 JSON，但即使很大仍继续选择 contacts、修改 physics 并签发 certificate：[certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:381>)。这会使“同一 frozen successful trajectory boundary”失去锚点。

   具体补丁：

   - 在任何 candidate-contact 分析前进行 fail-closed endpoint check。
   - 阈值应来自独立 factual replay envelope，不能来自 candidate repeat。
   - 不匹配时产出结构化 `invalid_boundary` 结果，不得进入 witness 分母。
   - 增加显式测试，确认 candidate 首帧状态等于实际 factual rollout endpoint，且 factual 与 candidate 之间没有 restore。
   - 若 controller 有 simulator state 之外的 cache，`restore_canonical` 必须重置/克隆该 cache；否则应声明并保存其状态。仅写 `controller_state_mode` 字符串不是证明。

6. **所谓 static contact configuration hash 只覆盖两个数组，不足以证明静态物理世界。**

   [certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:260>) 只 hash `geom_solref` 和 `geom_friction`。质量、惯量、geom pose/size、joint damping、gravity、solver 配置、模型/XML 与引擎版本变化都不会反映在 hash 中；证书本身又没有绑定这两个 hash。

   具体补丁：

   - 定义版本化 canonical static-physics manifest，至少包括 model/XML/BDDL SHA、MuJoCo/robosuite/LIBERO 版本及所有 replay-relevant static arrays。
   - 保存 base hash、world-A hash、world-B hash 和结构化 diff。
   - verifier 强制 diff 恰好是一处允许的 parameter address。
   - [certificate.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\israc\certificate.py:148>) 也应强制 `len(changed_parameter_blocks) == 1`；目前只检查非空。

7. **NaN/Inf 可在 certifier 内部 fail-open。**

   `_max_abs` 和 envelope 没有有限性校验：[certificate.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\israc\certificate.py:109>)。与 NaN 比较通常返回 false，可能绕过 equality 或 divergence 条件；最后的 `allow_nan=False` 只能阻止落盘，不能保证判定逻辑正确。

   具体补丁：

   - 所有 trace、effect、参数值和 envelope 在判定前必须 `isfinite`。
   - envelope 必须有限且非负；activation lag、top-k 和样本数必须为合法正整数。
   - 任何非有限值直接加入 fatal failure 并令 `passed=False`。
   - analyzer 的 `json.load` 使用 `parse_constant` 拒绝 `NaN/Infinity`，递归验证所有数值。

8. **baseline 完整性和 bootstrap 实现可给出虚假 advantage。**

   [analyze_matched_compiler_pilot.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\analyze_matched_compiler_pilot.py:138>) 的字典推导会静默覆盖重复 boundary；每次 bootstrap 内又为每个 boundary 独立随机选择 baseline seed，破坏 seed 作为 cluster 的结构。`baseline=0, method=0` 也会被当作 infinite ratio。`all_selectors_have_three_complete_seeds` 只检查当前出现的 selector，不要求 candidate-contact 和 random-scene 两者都存在。

   具体补丁：

   - 显式要求 selector 集合至少包含 `candidate-contact` 与 `random-scene`，并分别验证完整 seed 集。
   - 重复 `(selector, seed, boundary_key)` 立即报错；boundary key 使用 source trajectory/rollout SHA、arrays SHA、boundary、candidate action SHA，不能只用 basename。
   - 每个 bootstrap replicate 选择一个完整 selector seed，或做 boundary × seed 的 cluster bootstrap；不要在一个 replicate 内逐 boundary 混种子。
   - `0/0` 报 undefined/tie，只有 `method>0, baseline=0` 才是 infinite。
   - 验证 `bootstrap_samples > 0`；正式 gate 至少要求 CI lower bound 超过预注册阈值，而不只是 point ratio。

## NON-BLOCKING issues

- target-WAM 隔离从当前实际数据流看基本成立，但 blacklist 只匹配少数精确字段名：[certify_continuous_contact_support.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:287>)。建议 compiler 使用严格 schema allowlist，并在 audit 前保存 artifact SHA；不要把 `compiler_target_wam_blind: true` 当作隔离证据。
- witness key 没有绑定 arrays file、snapshot、factual actions 和 action dtype/shape：[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:456>)。建议加入 rollout JSON SHA、arrays SHA、snapshot SHA、factual/candidate action canonical SHA、boundary、geom IDs 和 parameter family。
- `ISRAC` 总取排序后前 K 个 block，而两个 baseline 随机取样。这不泄漏 `|B*|`，但可能引入 geom-ID/order advantage。建议预注册统一 tie-breaking，或对 ISRAC 的 eligible blocks 也使用 seed-controlled permutation。
- 合法的 zero-witness 运行已经完成并写出结果，却以 exit code 2 退出：[同文件](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\certify_continuous_contact_support.py:551>)。建议有效负结果 exit 0，JSON 中 `passed=false`；非零退出只用于运行或协议错误。
- analyzer 输出会覆盖已有文件、不是原子写、路径无 personal-scope 检查且默认允许 NaN：[analyze_matched_compiler_pilot.py](<<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler\implementation\analyze_matched_compiler_pilot.py:336>)。应复用安全路径验证，拒绝已存在目标，`allow_nan=False`，临时文件后原子替换。

## 必须补齐的测试

现有测试主要覆盖 digest 会变化、geom subtraction、seed reproducibility 和旧 analyzer schema，未覆盖关键协议失败。部署前最低限度应加入：

- fake simulator 上断言“一次 restore、factual 后直接 candidate”，并验证 candidate 初始 state 等于 factual endpoint。
- replay endpoint 超阈值必须拒绝。
- P025 真实 fixture 的端到端 analyzer test，验证 raw pairs、unique witnesses、strength curve 和 charged cap 均非零且一致。
- RGB 单像素变化测试，证明 digest 不作为数值距离。
- factual 与 candidate repeat envelope 分离测试。
- NaN/Inf trace/envelope/JSON 全部 fail-closed。
- 两个以上 changed parameter blocks 必须拒绝。
- certificate hash 对 evidence、参数 endpoint、static hash、actions 中任一位变化都必须改变。
- 缺任一 baseline selector、缺 seed、重复 boundary、`0/0`、重复 witness 均必须明确失败。
- actual-call counter 与 fake env 的真实 `step`/restore 次数严格一致。
- 输出路径越界、已存在目标、zero-witness 正常落盘和异常中断不留下完整伪 artifact。

最小修复顺序：**先修 P025 analyzer → 重构 evidence/certificate binding 与 RGB/depth equality → 统一真实 call accounting → 加 endpoint/static-state fail-closed → 最后修 bootstrap 与测试矩阵。**
