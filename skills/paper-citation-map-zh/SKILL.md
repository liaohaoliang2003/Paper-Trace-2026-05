---
name: paper-citation-map-zh
description: Use when a Chinese-speaking user provides an academic paper PDF, extracted paper text, citation contexts, or references and asks for citation intent extraction, entity/relation extraction, paper contribution mapping, or a visual citation graph.
---

# 论文引用图谱

## 概览

使用本 Skill 将单篇学术论文转化为可解释的引用意图图谱：中文分析报告、机器可读的 `citation_graph.json`，以及中心论文放射图的 SVG 图像。本 Skill 与英文版 `paper-citation-map` 同构，并参考本仓库已有两条工作线：`CitePrompt` 的引用意图分类思想，以及 `sci_glm` 的 LLM 优先结构化 JSON 抽取方式。

## 输入

支持以下任一输入形式：

- 单篇论文 PDF 路径或附件。
- 单篇论文的已提取全文。
- 引用上下文与参考文献列表。
- 已有的局部分析，需要规范化为图谱 schema。

如果 PDF 文本抽取质量较差，应要求用户提供抽取文本，或只分析可靠片段。不要编造缺失的参考文献、标题、作者、年份或引用上下文。

## 标准输出

只要当前工作区可写，默认将结果落盘为文件；不要只在对话中输出自然语言总结，除非文件系统不可写。

- `analysis.md`：必需的中文阅读报告，包含目标论文概要、引用意图发现、实体/关系说明、图谱解读、覆盖范围和不确定性说明。
- `citation_graph.json`：必需的结构化图谱数据，遵循 `references/schema.md`。这是最低文件产物，即使 SVG 渲染失败也必须写出。
- `citation_map.svg`：优先生成的中心论文放射图，遵循 `references/visual.md`。如果无法可靠生成 SVG，仍必须写出 `citation_graph.json`，并在 `analysis.md` 中说明缺口。
- `citation_map_spec.md`：仅在无法生成 SVG 时作为可选替代，记录可渲染的 SVG 布局规范和未生成 SVG 的原因。

默认输出目录优先级：

1. 用户显式指定输出目录时使用该目录。
2. 否则使用当前工作区内的 `outputs/paper-citation-map/<safe-paper-stem>/`。
3. 如果该路径不可写但源文件目录可写，则使用源文件旁的 `<safe-paper-stem>-citation-map/`。
4. 如果没有任何可写位置，在最终回复中明确说明无法写文件，并内联给出 Markdown、JSON 和 SVG-ready 内容。

## 规范化分析模板模式

仅当用户显式要求模板或规范格式时，才强制使用固定 `analysis.md` 模板。触发词包括：`使用模板`、`按模板`、`符合规范`、`标准格式`、`固定结构`、`规范化报告`、`template`、`standard format`。

- 触发模板模式时，必须读取 `references/analysis_template.md`，并按其中固定章节顺序和必需表格写出 `analysis.md`。
- 未触发模板模式时，不要强制套用固定模板；只需覆盖上方标准输出要求中的内容范围。
- 不得为了填满模板而编造引用。某个 intent 没有可靠证据时，应在对应章节说明“未发现可靠证据”。

## 引用意图标签

除非用户明确扩展标签体系，只使用以下 12 个标签：

| Intent | 使用场景 |
| --- | --- |
| `background` | 背景、相关工作、动机或领域事实 |
| `problem` | 问题定义、挑战、瓶颈或已知限制 |
| `core-method` | 直接构成目标论文核心方法的关键引用 |
| `supporting-method` | 辅助方法、组件、算法或实现技术 |
| `dataset` | 数据集、语料、benchmark、测试集或数据来源 |
| `metric` | 评价指标、评分方法、评估协议或测量设置 |
| `baseline` | 对比方法、已有系统、SOTA 结果或消融参照 |
| `tool-resource` | 工具库、工具包、预训练模型、标注工具或外部资源 |
| `theory` | 理论定义、公式、分析框架或形式化依据 |
| `result-evidence` | 实验结果、观察现象、经验证据或结论引用 |
| `limitation` | 失败案例、弱点、约束、负面证据或不足 |
| `future-work` | 开放问题、未来方向或未解决机会 |

需要和 `CitePrompt` 风格的三分类对齐时，使用以下粗粒度映射：

- `background`：`background`、`problem`、`theory`、`future-work`
- `method`：`core-method`、`supporting-method`、`tool-resource`
- `result`：`dataset`、`metric`、`baseline`、`result-evidence`、`limitation`

## 工作流

1. **抽取可靠论文文本**
   - 识别标题、作者、摘要、章节、参考文献和引用标记。
   - 保留原始引用标记形式，例如 `[12]`、`(Smith et al., 2020)` 或 `Smith et al. [7]`。

2. **定位引用上下文**
   - 抽取包含引用的句子，并在可用时加入前后各一句作为局部上下文。
   - 保留章节名和引用标记。
   - 如果一句话引用多篇文献，为每个匹配参考文献创建单独 citation 记录，共享同一上下文。

3. **匹配参考文献**
   - 将文中引用标记链接到参考文献条目。
   - 如果匹配不确定，设置 `unmatched_reference: true`，并在 `evidence` 中说明不确定性。

4. **抽取实体和关系**
   - 抽取方法、数据集、指标、任务、问题、组件、结果和资源。
   - 只有在证据文本支持时，才把实体链接到 citation 记录。

5. **分类引用意图**
   - 使用上方 12 个标签。
   - 优先选择更具体的标签：如果引用提供数据集，使用 `dataset`，不要泛化为 `background`。
   - 对模糊案例设置 `confidence < 0.7`，并说明歧义来源。

6. **构建图谱分组**
   - 按语义角色组织节点：问题/背景、方法、数据/评估、基线/结果、局限/未来。
   - 将 `core-method`、`dataset`、`metric`、`baseline` 作为可视化优先展示的意图。

7. **生成输出**
   - 按上述默认优先级创建输出目录。
   - 写出 `analysis.md`，用中文给出简洁解释和证据锚点；若触发模板模式，遵循 `references/analysis_template.md`。
   - 写出符合 `references/schema.md` 的 `citation_graph.json`；不得省略该文件。
   - 尽可能按 `references/visual.md` 渲染 `citation_map.svg`。
   - 如果 SVG 无法生成，写出 `citation_map_spec.md`，并在 `analysis.md` 中说明 SVG 缺口。

## LLM 抽取规则

在编写抽取 prompt 或调用 LLM 前，先阅读 `references/prompts.md`。

硬性规则：

- 要求模型只返回 JSON，不返回 Markdown 代码块。
- 使用 JSON 解析器校验输出，禁止使用不安全的代码求值方式解析。
- 拒绝标签集合之外的 `intent`。
- 最终产物不得包含 API Key、模型私有追踪信息或供应商原始元数据。
- 所有判断必须落在引用上下文、摘要、章节文本或参考文献条目上。

## 质量检查

最终输出前检查：

- 每条 `citation` 都有 `intent`、`evidence`，并且有 `reference_id` 或 `unmatched_reference: true`。
- 每个 `intent` 都属于允许标签集合。
- 每个高优先级可视化节点至少有一句证据。
- 图谱不依赖全文也能帮助读者理解论文核心内容。
- 当存在可写位置时，已经保存 `analysis.md` 和 `citation_graph.json`。
- 能生成 SVG 时已经保存 `citation_map.svg`；不能生成时已经用 `citation_map_spec.md` 记录替代方案。
- 输出不包含硬编码 API Key、私有绝对路径或编造的文献信息。

## 常见失败处理

- **PDF 抽取失败**：要求用户提供抽取文本，或只分析可靠片段，并在 `analysis.md` 中标注覆盖范围。
- **参考文献无法匹配**：保留引用标记和上下文，设置 `unmatched_reference: true`，不要猜测标题。
- **单条引用有多个意图**：选择主意图，把次要意图写入 `secondary_intents`。
- **LLM 返回非法 JSON**：使用 `references/prompts.md` 中的修复 prompt 重试，禁止使用不安全的代码求值方式解析。
- **图谱过于拥挤**：JSON 保留全部记录，SVG 只展示优先引用，并按组汇总其余引用数量。
- **文件系统不可写**：不要静默跳过产物；在最终回复中说明写入失败，并内联 `analysis.md`、`citation_graph.json` 和 SVG-ready 布局内容。

## 参考文件

- `references/schema.md`：`citation_graph.json` 的标准 schema 和最小示例。
- `references/prompts.md`：抽取、分类、修复和质量审查的中文 LLM prompt。
- `references/visual.md`：中心论文放射图的 SVG 布局、颜色、边类型和可访问性规范。
- `references/analysis_template.md`：用户显式要求模板或规范格式时使用的固定 `analysis.md` 模板。
