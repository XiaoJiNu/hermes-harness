# AI Paper Reproduction Playbook

日期：2026-04-29

## 目标

给定一篇人工智能相关 paper 和可用数据，本方法把“复现论文”变成一个可审计、可回滚、可比较的工程流程。

这里的“保证复现”不是承诺任何论文都能在缺少关键细节、私有数据或不足算力时强行跑出原文数字；而是保证：

1. 先穷尽可验证的开源实现和方法来源
2. 把论文主张拆成可执行 claim
3. 对每个 claim 给出 exact / approximate / not reproducible 的证据结论
4. 如果不能复现，必须产出可定位的 gap log，而不是停在“没跑出来”

## 适用场景

- 论文没有官方开源代码，需要 clean-room 复现
- 官方代码不可运行、依赖过时、指标无法复现
- 需要比较多个社区实现后选择一个可靠基线
- 需要把论文方法迁移到自有数据
- 需要复现论文中的表格、图、消融、训练策略或评测协议

如果任务只是直接使用官方模型做推理，优先参考部署 / 推理服务方法；如果任务是建立 leaderboard，优先叠加 `docs/playbooks/benchmark-eval-repo.md`。

## 复现等级

先声明目标等级，避免把“论文级复现”和“工程可用实现”混在一起。

| 等级 | 名称 | Done 定义 |
|---|---|---|
| R0 | Exact reproduction | 同一数据、同一指标、同一协议，核心结果落入预设容差 |
| R1 | Faithful implementation | 方法细节与论文一致，但因硬件、随机种子或未公开细节导致小幅差异 |
| R2 | Behavioral reproduction | 复现趋势、相对提升和消融结论，而非逐点数字 |
| R3 | Proxy benchmark reproduction | 原数据不可得，用公开代理数据验证核心主张 |
| R4 | Not reproducible with evidence | 数据、代码、超参、算力或协议缺口被证据化记录 |

默认目标是 R1；只有当 paper、数据、评测协议和算力都满足时才承诺 R0。

## 最小控制面

每个论文复现项目至少建立这些工件：

- `docs/specs/paper-reproduction-spec.md`：论文、目标等级、核心 claims、数据和算力边界
- `docs/references/source-survey.md`：官方 / 非官方 / 框架实现 / 数据源调查
- `docs/references/paper-claim-matrix.md`：论文 claim 到代码、实验、指标的映射
- `docs/references/paper-vs-code-audit.md`：架构、loss、数据处理、训练 schedule、评测协议差异
- `docs/runbooks/train-eval.md`：从环境创建到训练 / 评测的命令
- `docs/runbooks/debug-reproduction-gap.md`：指标差异排查步骤
- `manifests/environment.lock.*`：conda / pip / docker / CUDA / driver / commit 锁定
- `manifests/data-manifest.md`：数据版本、划分、校验和、预处理参数
- `runs/registry.md`：每次实验的 seed、commit、配置、机器、指标和日志位置
- `reports/reproduction-report.md`：最终复现结论、差距和下一步

新建具体论文复现项目时，优先从 `docs/templates/ai-paper-reproduction-project-template.md` 复制控制面模板，再按项目规模拆分成上述路径。

## 阶段 0：任务 intake

快速启动：先复制 `docs/templates/ai-paper-reproduction-project-template.md` 到目标项目，填完 reproduction spec、source survey、paper-claim-matrix 和 smoke gates 后，再决定是否进入实现。

输入必须至少包含：

1. paper：标题、arXiv / DOI / OpenReview 链接、版本号
2. 目标：复现哪张表、哪个图、哪个 benchmark 或哪个训练现象
3. 数据：官方数据、自有数据、是否可公开、下载方式、许可证
4. 资源：GPU 型号、显存、训练时长预算、存储限制
5. 期望等级：R0 / R1 / R2 / R3

缺少以上信息时，先建立 assumption log；不要直接开始写训练代码。

## 阶段 1：论文拆解

把 paper 拆成可执行对象：

- problem setting：任务定义、输入输出、训练 / 测试 split
- method graph：模块、张量形状、前向路径、loss、采样策略
- training recipe：optimizer、LR schedule、batch size、epoch/steps、augmentation、初始化、precision
- evaluation protocol：metric、阈值、后处理、checkpoint selection、test-time augmentation
- result claims：主表、消融、鲁棒性、效率、显存、速度
- hidden assumptions：未说明的预处理、数据过滤、seed、硬件和实现 trick

产出 `paper-claim-matrix.md`。每个 claim 必须有：论文位置、复现命令、目标指标、容差和当前状态。

## 阶段 2：开源来源搜索

按优先级搜索并记录到 `source-survey.md`：

1. 官方来源：paper 链接、作者主页、OpenReview supplementary、arXiv HTML/PDF、项目页、GitHub/GitLab
2. 聚合来源：Papers with Code 数据、Hugging Face model / dataset / paper pages、GitHub topic/search
3. 社区实现：labml.ai annotated implementations、OpenMMLab、Hugging Face Transformers/Diffusers、timm、Detectron2、fairseq、Stable-Baselines3 等领域框架
4. 实验基础设施：Hydra、DVC、MLflow、Sacred、Weights & Biases client、Accelerate、Lightning、DeepSpeed、Cog/Docker
5. 方法规范：NeurIPS reproducibility checklist、The Turing Way、ReScience C、ML Reproducibility Challenge 文章和报告

搜索结果不要只看 stars。必须记录：license、最近更新时间、是否官方、是否有训练脚本、是否有预训练权重、是否能复现目标表格、依赖是否可安装、是否有 issue 讨论指标差异。

可参考 `docs/references/ai-paper-reproduction-sources.md` 中的来源清单。

## 阶段 3：选择复现路线

按下面顺序选择代码基础：

1. 官方代码可运行：锁定 commit，先跑官方 smoke，再跑完整复现
2. 官方代码不可运行但有社区修复：fork 并记录所有补丁
3. 无官方代码但有高质量社区实现：做 paper-vs-code audit 后采用
4. 有通用框架实现：把论文模块映射到框架配置，补缺失模块
5. 完全无实现：clean-room，从最小可测模块开始 TDD

任何路线都必须保留 paper-to-code trace：每个关键模块能回到论文公式、图或段落。

## 阶段 4：先做可失败的 smoke gates

在 full training 前必须过这些 gate：

- G0 environment gate：环境可创建，CUDA / driver / PyTorch / compiler 版本记录完整
- G1 data gate：数据下载、校验和、split、样本可视化或统计通过
- G2 forward gate：单 batch 前向、loss、反向、梯度非 NaN
- G3 overfit gate：极小子集能过拟合，证明模型和 loss 有学习信号
- G4 eval gate：评测脚本在 toy output 和小 checkpoint 上可重复
- G5 baseline gate：至少一个官方或公开 baseline 指标可跑通

任何 gate 失败都先进入 `debug-reproduction-gap.md`，不要跳到 full run。

## 阶段 5：正式复现实验

正式 run 必须固定：

- git commit 和 dirty diff
- 配置文件完整快照
- 数据 manifest 和 checksum
- seed 列表，默认至少 3 个 seed；大模型昂贵任务可降为 1 个 seed但必须说明
- 硬件、driver、CUDA、框架版本
- 日志、checkpoint、评测输出位置
- 早停 / checkpoint selection 规则

指标比较使用三层结果：

1. paper target：论文报告数字
2. public baseline：官方或社区可运行基线
3. our reproduction：当前项目复现结果

只报告 best run 是反模式；必须同时报告 mean/std、失败 run 和被排除 run 的理由。

## 阶段 6：差距定位

如果指标不一致，按顺序排查：

1. 数据：版本、split、泄漏、过滤、类别映射、预处理
2. 评测：metric 实现、阈值、后处理、TTA、rounding
3. 模型：参数量、初始化、归一化、mask、张量维度、checkpoint 加载
4. 训练：batch size 等效性、LR scaling、warmup、weight decay、梯度裁剪、AMP
5. 随机性：seed、cuDNN、分布式 all-reduce、dataloader order
6. 硬件与库：CUDA kernel、PyTorch 版本、算子实现差异
7. 论文缺口：未公开 trick、私有数据、算力不足、不可获得预训练权重

每个 gap 都要有“证据、影响范围、下一步、是否阻断 R0/R1”的记录。

## 阶段 7：自有数据适配

只有在官方或代理数据上达到 R1/R2 后，才进入自有数据适配。

适配时要新建：

- 自有数据 contract
- label / schema 映射
- domain gap 假设
- baseline comparison
- 与论文复现分离的 run registry

不要把“论文没复现出来”和“自有数据效果不好”混为一个问题。

## Done 定义

一个论文复现项目完成时，必须给出以下之一：

1. R0/R1/R2/R3 复现成功报告：包含 claim matrix、命令、环境、数据、指标和容差
2. R4 不可复现报告：明确阻断因素、已尝试路线、证据和可解除条件

同时满足：

- 所有关键命令可从 runbook 重新执行
- 结果能从 run registry 追溯到 commit、配置和数据
- paper-vs-code audit 无未解释的关键差异
- gap log 中没有未分类的核心指标差距

## 常见反模式

- 搜到一个 repo 就直接 full training
- 只复现 inference，不复现论文评测协议
- 只看 README，不审训练脚本和默认配置
- 不记录数据 split 和 checksum
- 指标低了就盲调超参，而不是先查 metric / data / preprocessing
- 在自有数据上调参后声称论文已复现
- 把不满足 R0 的实验包装成 exact reproduction

## 验证入口

在具体论文项目中，推荐提供这些命令：

```bash
python scripts/check_environment.py
python scripts/check_data_manifest.py
python scripts/smoke_forward.py
python scripts/smoke_train.py --overfit-small-batch
python scripts/eval.py --config configs/reproduction.yaml
python scripts/compare_claims.py --claims docs/references/paper-claim-matrix.md
```

本 reference repo 的结构验证仍使用：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
make test-structure
```
