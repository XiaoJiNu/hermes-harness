# AI Paper Reproduction Sources

日期：2026-04-29

本文件是 AI 论文复现项目的外部来源清单。它不是 source of truth；source of truth 仍是具体项目内的 spec、manifest、runbook、registry 和 reproduction report。

调研方式：2026-04-29 使用 GitHub API 和公开页面抽样核验了下列仓库的描述、许可证、更新时间和可用性。星标数不写入本文件，避免把会快速变化的 popularity 当成方法依据。

## 使用原则

1. 官方优先，但官方代码也要审计，不默认可信
2. 开源许可必须记录；无明确许可证的代码只能作为阅读参考，不能直接复制
3. 聚合平台只用于发现候选实现，不能替代 paper-vs-code audit
4. 每个外部实现都要锁定 commit、依赖版本和本地 patch
5. 发现指标差异时，优先查数据和评测协议，再查模型和训练超参

## 发现 paper 和实现的来源

| 来源 | 类型 | 用途 | 注意事项 |
|---|---|---|---|
| Papers with Code / `paperswithcode/paperswithcode-data` | 论文-代码-数据集聚合数据 | 快速查找是否已有官方或社区实现、SOTA 表格、任务定义 | GitHub API 显示仓库描述为 paperswithcode.com 背后的完整数据集；许可证需逐项确认 |
| arXiv | 论文源 | 锁定论文版本、下载 PDF/HTML、查 appendix | 必须记录版本号，例如 v1/v2，避免论文后续修改导致漂移 |
| OpenReview | 论文与 supplementary | 查审稿讨论、补充材料、作者 rebuttal 中的实现细节 | supplementary 不一定长期稳定，下载后记录 checksum |
| Semantic Scholar | 论文关系 | 查引用、相关工作、作者其它实现 | 免费 API 有速率限制；不要把摘要当作论文全文 |
| Hugging Face Hub | 模型 / 数据集 / Spaces / papers | 查模型卡、权重、数据集、训练配置、社区复现 | model card 不是完整论文实现；需核对训练和评测脚本 |
| GitHub search / topics | 代码搜索 | 查 paper title、arXiv id、方法名、作者名、任务名 | 高 stars 不等于可复现；优先看训练脚本、issue、commit 活跃度 |
| CatalyzeX | 代码发现服务 | 辅助发现论文实现 | 不作为开源 source of truth；发现后回到原始 repo 审计 |

## 论文实现和模型框架仓库

| 仓库 | 适用领域 | 复现用途 | 许可证状态 |
|---|---|---|---|
| `labmlai/annotated_deep_learning_paper_implementations` | 通用深度学习、Transformer、GAN、RL、优化器 | 学习论文到 PyTorch 代码的逐行映射；适合 clean-room 复现参考 | MIT |
| `huggingface/transformers` | NLP、语音、视觉、多模态 Transformer | 查模型定义、训练/评测示例、预训练权重加载方式 | Apache-2.0 |
| `huggingface/diffusers` | 图像、视频、音频扩散模型 | 查 diffusion pipeline、scheduler、训练脚本、权重格式 | Apache-2.0 |
| `huggingface/pytorch-image-models` / timm | 图像分类、backbone、encoder | 查 backbone、预训练权重、ImageNet 训练/评测 recipe | Apache-2.0 |
| `open-mmlab/mmdetection` | 目标检测、实例分割 | 查 detector 配置、训练 schedule、COCO 评测协议 | Apache-2.0 |
| `open-mmlab/mmsegmentation` | 语义分割 | 查 segmentation model zoo、数据 pipeline、评测配置 | Apache-2.0；使用前核验当前 repo 状态 |
| `open-mmlab/mmengine` | OpenMMLab 训练引擎 | 复用配置、runner、hook、日志和评测机制 | Apache-2.0；使用前核验当前 repo 状态 |
| `facebookresearch/detectron2` | 检测、分割、视觉识别 | 对照经典视觉论文的训练与评测实现 | Apache-2.0 |
| `facebookresearch/fairseq` | 序列建模、机器翻译、语音 | 对照 seq2seq / Transformer 训练实现；GitHub API 抽样显示仓库已 archived，优先作为历史参考而非新项目底座 | MIT |
| `google-research/google-research` | Google Research 多论文实现集合 | 查论文作者组发布的参考实现 | Apache-2.0，但子目录依赖和状态需单独审计 |
| `google-research/bert` | BERT 原始实现 | 复现 BERT 相关方法时对照原始 TensorFlow recipe | Apache-2.0 |
| `karpathy/minGPT` | GPT 教学实现 | 对照 GPT 最小实现，适合理解模块 | MIT |
| `karpathy/nanoGPT` | GPT 训练最小工程 | 复现小中型 GPT 训练 recipe、数据管线、训练 loop | MIT |
| `openai/baselines` | 强化学习 | 复现经典 RL baseline 和训练脚本 | MIT |
| `DLR-RM/stable-baselines3` | 强化学习 | 复现现代 PyTorch RL baseline | 使用前核验当前 repo 状态和许可证 |
| `microsoft/recommenders` / `recommenders-team/recommenders` | 推荐系统 | 查推荐系统论文/算法的 best practices 和 baseline；GitHub API 会重定向到当前组织名 | MIT |

## 实验复现基础设施

| 仓库 | 用途 | 在复现流程中的位置 |
|---|---|---|
| `facebookresearch/hydra` | 配置组合与实验参数管理 | 锁定训练配置、支持 ablation sweep、避免命令行参数漂移 |
| `iterative/dvc` / `treeverse/dvc` | 数据版本和实验追踪 | 管理数据 manifest、远端数据、pipeline stage 和可复跑命令；GitHub API 会重定向到当前组织名 |
| `mlflow/mlflow` | 实验、模型和评测记录 | 建立 run registry、保存指标和 artifact |
| `IDSIA/sacred` | 配置、日志和实验复现 | 轻量记录配置、seed、依赖和输出 |
| `wandb/wandb` | 实验跟踪 client | 记录训练曲线、配置和 artifact；注意服务端策略 |
| `Lightning-AI/pytorch-lightning` | PyTorch 训练组织 | 标准化训练 / 验证 loop，减少 boilerplate |
| `huggingface/accelerate` | 分布式、混精和设备适配 | 在单机/多机/GPU/CPU 间保持训练入口稳定 |
| `microsoft/DeepSpeed` / `deepspeedai/DeepSpeed` | 大模型分布式训练优化 | 复现大模型训练时管理 ZeRO、offload 和大 batch；GitHub API 会重定向到当前组织名 |
| `NVIDIA/Megatron-LM` | 大规模 Transformer 训练 | 对照大模型并行训练 recipe；GitHub API license 字段可能为 NOASSERTION，许可证和子组件需核验 |
| `replicate/cog` | ML 容器化 | 把复现实验打包成可重复运行的容器环境 |
| Docker / Apptainer | 环境隔离 | 锁定 CUDA、系统包、编译器和 runtime |

## 方法与社区规范

| 来源 | 价值 | 如何落到 harness |
|---|---|---|
| NeurIPS / ML reproducibility checklist | 提供数据、代码、实验和报告的披露清单 | 转成 spec 和 reproduction report 的必填项 |
| The Turing Way (`the-turing-way/the-turing-way`) | 可复现、伦理、协作数据科学实践 | 转成项目 README、数据治理和协作规范 |
| ReScience C (`ReScience/ReScience`) | 复现实验论文和同行评审文化 | 借鉴 reproduction report 结构和审查标准 |
| ML Reproducibility Challenge | 复现论文的社区案例 | 查同类论文的失败模式、指标容差和报告写法 |
| Papers with Code evaluation tables | 任务、指标、数据集和 SOTA 关系 | 作为 source-survey 输入；最终比较以本地 claim matrix 为准 |

## 推荐搜索查询

给定一篇 paper，按顺序搜索：

```text
"<paper title>" GitHub
"<paper title>" "official implementation"
"<paper title>" "reproduction"
"<arxiv id>" GitHub
"<method name>" PyTorch
"<method name>" "Papers with Code"
"<task name>" "<dataset name>" benchmark
site:github.com <paper title or method name>
site:huggingface.co <paper title or method name>
site:openreview.net <paper title or method name>
```

## 候选实现评分表

每个候选 repo 用 0/1/2 分评分：

| 项 | 0 | 1 | 2 |
|---|---|---|---|
| 官方性 | 无关 | 社区实现 | 作者/官方实现 |
| 许可证 | 无许可证或不兼容 | 需进一步确认 | 明确开源且兼容 |
| 可运行性 | 依赖缺失/不可安装 | 需补丁 | smoke 可运行 |
| 训练覆盖 | 只有 inference | 有部分训练 | 有完整训练和评测 |
| 数据覆盖 | 无数据说明 | 有下载说明 | 有 manifest/split/checksum |
| 指标覆盖 | 无论文指标 | 只有单个指标 | 可复现目标表/图 |
| 活跃度 | 长期无人维护 | 偶发维护 | 最近仍有 commit/issue |
| 可审计性 | 代码混乱无配置 | 有配置但记录不足 | commit/config/log 清晰 |

默认选择总分最高且许可证兼容的实现；如果官方实现低分，也要先记录原因再切换到社区实现。

## 何时判定不可复现

满足任一条件时，可以进入 R4，但必须给证据：

- 原始数据或关键预训练权重不可获得，且无公开代理数据能验证核心 claim
- paper 关键公式、训练策略或评测协议缺失，联系作者或搜索补充材料后仍不可确定
- 所需算力远超预算，缩小实验只能验证趋势不能验证目标指标
- 已排除数据、评测、模型、训练和随机性问题，仍存在超出容差的稳定差距
- 外部代码许可证不允许使用，且 clean-room 复现成本超过项目边界
