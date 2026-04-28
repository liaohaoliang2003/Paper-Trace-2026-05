---
name: paper-citation-map-zh
description: Use when a Chinese-speaking user provides an academic paper PDF, extracted paper text, citation contexts, or references and asks for citation intent extraction, entity/relation extraction, paper contribution mapping, or a visual citation graph.
---

# 中文论文引用图谱

## 概览

使用本 Skill 将单篇学术论文转成有证据链的引用意图图谱：中文 `analysis.md`、机器可读 `citation_graph.json`，以及一种或多种 SVG 引用图。只要当前环境可写，就默认落盘文件，不要只在聊天中给一段总结。

## 必需输出

默认输出目录优先级：

1. 用户显式指定的输出目录。
2. 当前工作区内的 `outputs/paper-citation-map/<safe-paper-stem>/`。
3. 如果工作区不可写但源文件目录可写，则使用源文件旁的 `<safe-paper-stem>-citation-map/`。
4. 如果没有任何可写位置，最终回复必须明确说明未能写文件，并内联给出 Markdown、JSON 与 SVG-ready 内容。

标准产物：

- `analysis.md`：必写中文报告，覆盖目标论文、引用意图分组、证据链、实体关系解读、覆盖范围和不确定性。
- `citation_graph.json`：必写结构化图谱，遵循 `references/schema.md`。这是最低必需产物，即使 SVG 失败也必须存在。
- `citation_map.svg`：只要可以生成 SVG 就必须写出；内容取决于图像模式。
- `citation_map_example.svg`：仅在图像模式为 `all` 时写出。
- `citation_map_spec.md`：仅当 SVG 无法生成时作为可选降级产物，说明可渲染布局和失败原因。

## 图像模式选择

生成 SVG 前先判断用户是否显式要求模式：

- 仅生成当前模式：用户说 `当前模式`、`原 SVG`、`原编排`、`current`、`current mode`、`original SVG`、`original layout`。
- 仅生成例图模式：用户说 `例图`、`参考图`、`思维导图`、`example`、`reference image`、`mind map`。
- 混合模式：用户说 `混合`、`可展开知识图谱`、`hybrid`、`expandable knowledge graph`。该模式目前仅预留给未来 Web 交互图谱，不输出固定 SVG。
- 用户未显式指定且可以询问时，先询问用户选择模式。
- 用户未显式指定且无法询问时，默认生成 `current + example` 两种静态 SVG。

文件命名：

- `current`：`citation_map.svg`，使用当前分组放射图布局。
- `example`：`citation_map.svg`，使用参考例图式思维导图布局。
- `all`：`citation_map.svg` 为当前模式，`citation_map_example.svg` 为例图模式。
- `hybrid`：说明暂未实现，不要编造静态 SVG。

绘图前读取 `references/visual.md`。

## 规范化报告模板模式

只有当用户明确要求“使用模板 / 按模板 / 符合规范 / 标准格式 / 固定结构 / 规范化报告 / template / standard format”时，才强制 `analysis.md` 使用固定模板。

- 触发后读取 `references/analysis_template.md`，按其中章节顺序和表格字段写 `analysis.md`。
- 未触发时不要强行套固定章节，但仍要覆盖必需内容范围。
- 不得为了填满模板而编造引用；没有可靠证据的 intent 写“未发现可靠证据”。

## 引用意图标签

除非用户明确扩展标签，否则只使用以下 12 类：

| Intent | 用途 |
| --- | --- |
| `background` | 相关工作、一般背景、动机或领域事实 |
| `problem` | 问题定义、挑战、瓶颈或已有局限 |
| `core-method` | 直接构成目标论文方法的关键思想或方法 |
| `supporting-method` | 辅助方法、组件、算法或实现技巧 |
| `dataset` | 数据集、语料、benchmark、testbed 或数据来源 |
| `metric` | 评估指标、评分方法、评测协议或测量设置 |
| `baseline` | 对比方法、已有系统、SOTA 结果或消融参照 |
| `tool-resource` | 库、工具包、预训练模型、标注工具或外部资源 |
| `theory` | 理论定义、公式、框架或形式化分析 |
| `result-evidence` | 实验结果、观察现象、经验证据或结论 |
| `limitation` | 失败案例、弱点、注意事项或负面证据 |
| `future-work` | 开放问题、未来方向或待解决机会 |

## 工作流

1. 抽取可靠论文文本：标题、作者、摘要、章节、参考文献和引用标记。
2. 定位引用上下文：引用句以及可获得的前后邻句，保留章节名和引用标记。
3. 按 `references/evidence_protocol.md` 建立证据链：引用上下文、章节位置、目标论文论点、被引工作角色、意图判据、置信度理由和不确定性。
4. 用 12 类标签判断每条 citation 的引用意图。
5. 抽取有助于理解目标论文的实体与关系。
6. 按 `references/schema.md` 写 `citation_graph.json`；必要时保留 `section`、`target_claim`、`cited_work_role`、`intent_rationale`、`confidence_reason` 等可选深度字段。
7. 写 `analysis.md`；只有显式触发时才使用固定模板。
8. 按选择的图像模式和 `references/visual.md` 生成 SVG。
9. 最终回复前验证产物是否存在、JSON 是否可解析、SVG 是否可读。

## 参考文件

- `references/evidence_protocol.md`：证据链和不确定性规则。
- `references/schema.md`：JSON 必填字段和可选深度字段。
- `references/prompts.md`：LLM 辅助抽取和质量审查提示。
- `references/visual.md`：当前模式、例图模式和预留 hybrid 模式的视觉规则。
- `references/analysis_template.md`：显式模板模式下的固定报告模板。

## 质量检查

- 每条 citation 必须有 `intent`、`evidence`、`confidence`，并且有 `reference_id` 或 `unmatched_reference: true`。
- 关键引用必须能追溯到引用句或上下文；无法确认时降低置信度并说明不确定性。
- 不用领域常识补全无证据引用，不编造参考文献信息。
- `citation_graph.json` 保留完整记录，Markdown 可以摘要但不能省略关键不确定性。
- SVG 失败时仍必须写出 `citation_graph.json`，并在 `analysis.md` 中说明缺口。
