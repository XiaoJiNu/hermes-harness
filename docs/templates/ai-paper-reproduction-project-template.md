# AI Paper Reproduction Project Template

日期：YYYY-MM-DD
状态：draft / running / reproduced / blocked

本模板用于在具体项目仓库中快速建立 AI 论文复现控制面。复制本文件后，把每一节拆到对应路径，或保留为单文件直到项目变大。

## 0. Reproduction Spec

推荐路径：`docs/specs/paper-reproduction-spec.md`

| 项 | 内容 |
|---|---|
| Paper 标题 | TBD |
| Paper URL / DOI / arXiv / OpenReview | TBD |
| Paper 版本 | 例如 arXiv v1/v2；OpenReview revision；PDF checksum |
| 目标复现等级 | R0 / R1 / R2 / R3 / R4 |
| 目标 claim | 表 / 图 / 指标 / 消融 / 训练现象 |
| 数据来源 | 官方数据 / 公开代理数据 / 自有数据 |
| 数据许可证 | TBD |
| 算力预算 | GPU 型号、显存、卡数、最长训练时长、存储 |
| 成功容差 | 指标绝对差、相对差、排名或趋势容差 |
| 非目标 | 本轮明确不做的表、图、数据集或大规模 run |

Assumption log：

| 假设 | 原因 | 验证方式 | 是否阻断 R0/R1 |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

## 1. Source Survey

推荐路径：`docs/references/source-survey.md`

搜索顺序：官方来源 -> Papers with Code / Hugging Face / GitHub -> 社区实现 -> 框架实现 -> 基础设施 -> 复现规范。

| 候选来源 | 类型 | URL / commit | License | 训练脚本 | Eval 脚本 | 权重 | 数据说明 | 目标 claim 覆盖 | 风险 / issue | 结论 |
|---|---|---|---|---|---|---|---|---|---|---|
| TBD | official / community / framework / infra | TBD | TBD | yes/no | yes/no | yes/no | yes/no | TBD | TBD | adopt / reference / reject |

候选实现评分：

| repo | 官方性 0-2 | license 0-2 | 可运行性 0-2 | 训练覆盖 0-2 | 数据覆盖 0-2 | 指标覆盖 0-2 | 活跃度 0-2 | 可审计性 0-2 | 总分 | 选择理由 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TBD | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | TBD |

## 2. Paper Claim Matrix

推荐路径：`docs/references/paper-claim-matrix.md`

| Claim ID | Paper 位置 | Claim 描述 | 数据 / split | Metric | Paper target | 容差 | 本地命令 | 输出 artifact | 状态 | 结论 |
|---|---|---|---|---|---|---|---|---|---|---|
| C01 | Table/Figure/Section | TBD | TBD | TBD | TBD | TBD | `python ...` | TBD | unknown / smoke / running / reproduced / gap / blocked | TBD |

状态定义：
- unknown：尚未执行
- smoke：只通过小样本或单 batch
- running：正式 run 进行中
- reproduced：达到 R0/R1/R2/R3 对应容差
- gap：存在差距但可继续定位
- blocked：外部条件阻断，需要 R4 证据

## 3. Paper-vs-Code Audit

推荐路径：`docs/references/paper-vs-code-audit.md`

| 维度 | Paper 描述 | 代码 / 配置位置 | 是否一致 | 差异影响 | 处理方式 |
|---|---|---|---|---|---|
| Architecture | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |
| Loss | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |
| Data preprocessing | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |
| Training schedule | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |
| Evaluation protocol | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |
| Checkpoint selection | TBD | TBD | yes/no/unknown | TBD | keep / patch / document |

关键 paper-to-code trace：

| Paper 公式 / 图 / 段落 | 模块 / 函数 / 配置 | 测试或 smoke gate |
|---|---|---|
| TBD | TBD | TBD |

## 4. Data Manifest

推荐路径：`manifests/data-manifest.md`

| 数据集 | 来源 URL | 版本 | License | checksum | split 规则 | 样本数 | 预处理 | 状态 |
|---|---|---|---|---|---|---:|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | 0 | TBD | pending / verified |

必须记录：下载命令、过滤规则、类别映射、随机 split seed、任何删除样本的原因。

## 5. Environment Manifest

推荐路径：`manifests/environment.lock.md`

| 项 | 值 |
|---|---|
| OS | TBD |
| GPU | TBD |
| Driver | TBD |
| CUDA / cuDNN | TBD |
| Python | TBD |
| PyTorch / TensorFlow / JAX | TBD |
| Compiler | TBD |
| Git commit | TBD |
| Dirty diff | clean / attached |
| Dependency lock | conda env / requirements / uv lock / docker digest |

## 6. Smoke Gates

推荐路径：`docs/runbooks/train-eval.md`

在 full training 前必须全部通过或明确豁免：

| Gate | 命令 | 通过标准 | Artifact | 状态 |
|---|---|---|---|---|
| G0 environment | `python scripts/check_environment.py` | 版本记录完整、GPU 可见 | logs/env.txt | pending |
| G1 data | `python scripts/check_data_manifest.py` | checksum、split、样本统计通过 | logs/data_check.txt | pending |
| G2 forward | `python scripts/smoke_forward.py` | 单 batch forward/loss/backward 无 NaN | logs/forward.txt | pending |
| G3 overfit | `python scripts/smoke_train.py --overfit-small-batch` | tiny subset loss 明显下降 | logs/overfit.txt | pending |
| G4 eval | `python scripts/eval.py --toy` | toy output 指标符合预期 | logs/eval_toy.txt | pending |
| G5 baseline | `python scripts/run_baseline.py` | 官方或公开 baseline 可运行，或有 R4 解释 | logs/baseline.txt | pending |

## 7. Run Registry

推荐路径：`runs/registry.md`

| Run ID | 日期 | commit | config | data manifest | seed | hardware | 命令 | checkpoint | metric | 日志 | 结论 |
|---|---|---|---|---|---:|---|---|---|---|---|---|
| run-YYYYMMDD-001 | YYYY-MM-DD | TBD | TBD | TBD | 0 | TBD | `python ...` | TBD | TBD | TBD | TBD |

规则：默认 3 seeds；昂贵任务可 1 seed，但必须写明原因。禁止只报告 best run。

## 8. Gap Log

推荐路径：`docs/runbooks/debug-reproduction-gap.md` 或 `reports/gap-log.md`

| Gap ID | 关联 claim | 现象 | 证据 | 可能原因 | 排查顺序 | 下一步 | 是否阻断 R0/R1 | 状态 |
|---|---|---|---|---|---|---|---|---|
| G-C01-001 | C01 | TBD | log / metric / diff | data / metric / model / training / randomness / hardware / paper gap | TBD | TBD | yes/no | open |

排查顺序固定为：数据 -> 评测 -> 模型 -> 训练 -> 随机性 -> 硬件/库 -> 论文缺口。

## 9. Reproduction Report

推荐路径：`reports/reproduction-report.md`

| Claim ID | Paper target | Public baseline | Our result mean/std | Reproduction level | Evidence |
|---|---|---|---|---|---|
| C01 | TBD | TBD | TBD | R0/R1/R2/R3/R4 | logs / artifacts / config |

最终结论必须二选一：

1. R0/R1/R2/R3 reproduced：给出命令、环境、数据、指标、容差和 artifact。
2. R4 not reproducible with evidence：给出阻断因素、已尝试路线、gap log 和解除条件。

## 10. Own-Data Adaptation Boundary

只有在官方或代理数据达到 R1/R2，或已经形成 R4 证据后，才开始自有数据适配。

| 自有数据项 | 内容 |
|---|---|
| data contract | TBD |
| schema / label mapping | TBD |
| domain gap 假设 | TBD |
| baseline | TBD |
| 独立 run registry | TBD |

不要用自有数据实验替代论文复现结论。
