# Hard-ID Threshold Revision

**Trigger**：v3 的 2k sanity leakage audit 中，所有泄漏/接触检查通过，但 `hard_id_test_count=6 < 10`，因此 orchestrator 在生成 12k 或启动 GPU 前自动停止。

**只读诊断**：仅使用 v3 sanity 的模型无关几何量，不训练、不读取任何方法输出。heterogeneous test 共 152 episode；pose-only top-1/top-2 mean margin 的 10/20/30% 分位数为 0.0556/0.0665/0.0718 m。movement 的 10% 分位数已为 0.0999 m，因此原 `move>0.025` 不是样本不足来源。

**修订**：固定 `pose_margin < 0.065 m` 且 `max_move > 0.025 m`。它约对应独立 sanity 分布最困难的 18%，预计在 12k test heterogeneous split 中产生约 150–170 个困难 episode，足以进行 paired evaluation。

**防止事后选择**：该选择未查看 shared/oracle/system-ID/full-history 的任何正式结果；v3 未启动任何 GPU 正式训练。修订后不用旧数据重打标签，而是生成全新的 v4 2k 和 v4 12k 数据，并重新完成全部 audit。

