# VLA / WAM / VLA × WAM 三域文献总图

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**检索截止：** 2026-08-06  
**用途：** 只为母领域制图提供证据；不做具体 Idea 的 novelty claim，也不选择模型、任务或 benchmark。

## 1. 三条独立证据链

| 域 | 独立检索结果 | 核心证据 | 方向数 | 详细地图 |
|---|---|---|---:|---|
| VLA-only | 六源并集 99 篇去重候选，再做原始来源补检 | 40 篇核心/边界工作：23 E1、17 E2 | 7 | [VLA 文献地图](./VLA_LITERATURE_MAP.md) |
| WAM-only | 表示轮 91、用途轮 100 篇去重候选，再做 proceedings 核验 | 36 篇核心工作：31 E1、5 E2 | 7 | [WAM 文献地图](./WAM_LITERATURE_MAP.md) |
| VLA × WAM | 跨库 104 篇去重候选，arXiv 聚焦 70 篇 | 29 篇强交叉：3 E1、26 E2；另 7 篇弱邻域 | 6 | [交叉文献地图](./INTERSECTION_LITERATURE_MAP.md) |

这里的数量是各自查询与分类中的记录数，不可直接相加成“全领域唯一论文数”：UniPi、WorldEval 等桥接工作会为不同域承担不同证据角色。重叠被明确标注，而不是偷偷重复计数来制造密度。

证据等级统一为：**E1**＝正式同行评审原始论文；**E2**＝方法与结果可核验的原始预印本/技术报告；**E3**＝摘要、项目页或弱邻域。交叉域的 E2 比例显著更高，说明 VLA×WAM 的能见度高于成熟度。

## 2. 为什么这次不是 WAM 论文主导

### VLA 线独立回答的问题

- RT-1/RT-2、PaLM-E、VIMA、Open X/RT-X、Octo、OpenVLA、π₀/π₀.₅、RDT、FAST/OFT 等不再只作为 world-model baseline 出现。
- ACT、Diffusion Policy、flow/action chunk 被视为动作建模路线，而不是因能预测 action 就被误标为 WAM。
- VLA 地图独立覆盖数据 scaling、VLM grounding、动作接口、跨具身、适配/部署、长程交互与 RL/持续后训练。

### WAM 线独立回答的问题

- PETS、PlaNet、Dreamer、TD-MPC、DPI-Net、DINO-WM 等即使没有语言和大型 VLA，仍是 WAM 本体的承重证据。
- 表示 R1–R4 与用途 U1–U5 分开，视频、latent、结构 state、MPC 和 imagination 不被当作互斥标签。

### 交叉线采用更高门槛

- 必须同时有 VLA 接口与 learned dynamics 的实际消费路径。
- UWM/UVA、V-JEPA 2、DreamGen、LAPA 等虽高度相关，但语言端或 VLA 因果链不足，因此降为弱邻域。
- “joint”“共享 backbone”或更大模型不是耦合有效的证据；需要 matched action-only、切断 world path、外部 ground truth 或 oracle 对照。

## 3. 对称覆盖审计

| 共同轴 | VLA-only 已覆盖 | WAM-only 已覆盖 | 强交叉已覆盖 |
|---|---|---|---|
| 基本对象 | policy、action generator、层级 controller | observable/latent/structured dynamics、belief | auxiliary、cascade、joint、alternating coupling |
| 数据 | robot mixture、web/human、heterogeneous embodiment、feedback | action-conditioned transitions、online interaction、结构/触觉 state | 同时桥接 world 与 action 的视频、rollout、policy data |
| 表征 | vision/language/action/history、token/chunk/flow | R1 video、R2 video latent、R3 task latent、R4 structured state | shared、separate 或可翻译 world/action representation |
| 学习 | pretraining、SFT、adapter、RL、continual | prediction、system ID、MBRL、online update | predictive auxiliary、imagined post-training、joint/co-evolution |
| 推理 | direct/chunk/skill/reasoning/active perception | proposal、evaluation、MPC | VLA proposal → WM rollout → value/critic → action |
| 泛化 | task/object/scene/instruction/embodiment | dynamics/observation/policy shift | world knowledge 是否转成 held-out VLA 收益 |
| 证据 | action quality 与 environment success | model fidelity、planning 与 environment endpoint | matched coupling 与 model-policy-environment 三层链条 |
| 资源 | data、fine-tuning、Hz、latency、deployment | rollout、interaction、planner 与 model cost | 额外 world path 的总成本和因果边际收益 |

审计结论：三张地图都覆盖了对象、数据、表征、学习、推理、泛化、证据和资源；VLA 不是 WAM 的附录，WAM 也不是 VLA 的附加 head。

## 4. 跨域共同冲突

1. **语义正确、视频真实、动作可执行和环境成功是四个不同 endpoint。** 任一 proxy 都不能替代最后一层。
2. **规模收益与机制收益普遍混淆。** 数据、参数、训练 token、动作 horizon、候选数和推理 FLOPs 必须入账。
3. **动作接口仍碎片化。** joint、end-effector、latent、token、chunk、control frequency 和 normalization 限制跨论文与跨机器人比较。
4. **长时与 OOD 是双重分布移位。** VLA 会进入训练未覆盖的 state，WM 又要预测这类 policy-induced state，误差可能互相放大。
5. **真实失败证据最少。** 成功轨迹多，罕见危险、不可逆接触、恢复失败、拒绝/求助和 negative results 少。
6. **交叉域成熟度最低。** 29 篇强交叉中 26 篇仍是预印本；方向可以成立，但不能把新近密度误读为稳定结论。

## 5. 检索故障与剩余盲区

- Semantic Scholar 多轮 429，OpenAlex 多轮 504/429/读超时，DBLP 有 500/超时，OpenReview 对关键词检索多次为零；已用正式 proceedings、DOI 与 arXiv 原页补全，但 venue-only 长尾仍可能漏检。
- 本地没有贡献 PDF；关键工作核验到原始页面，长尾以标题—摘要—正式页筛选，未做逐篇完整复现实验审计。
- 2025–2026 的企业系统、私有数据与新预印本缺独立复现；产业网页版本更新不重复计作论文。
- manipulation 证据多于 navigation、mobile manipulation、humanoid、dexterous hand 和真实长期部署。
- 互联网视频许可、数据污染、训练 FLOPs、失败运行、能耗与 synthetic effective yield 的报告仍不完整。

## 6. 由证据支持的版图形状

最终版图固定为 **7 条 VLA + 7 条 WAM + 6 条强交叉＝20 条母方向**。详细解释见：

- [VLA 母方向版图](./VLA_DIRECTION_LANDSCAPE.md)
- [WAM 母方向版图](./WAM_DIRECTION_LANDSCAPE.md)
- [VLA × WAM 母方向版图](./INTERSECTION_DIRECTION_LANDSCAPE.md)
- [三域总版图](./DIRECTION_LANDSCAPE.md)

本阶段只完成领域发现；`selected_macro_direction` 继续为空。
