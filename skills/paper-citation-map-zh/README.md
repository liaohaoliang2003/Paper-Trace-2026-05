# paper-citation-map-zh Skill

## Skill 用途

`paper-citation-map-zh` 是项目内独立中文 Skill，用于把单篇学术论文转换为引用意图图谱。它面向中文用户，指导 Agent 从论文 PDF、已提取文本、引用上下文或参考文献列表出发，产出中文分析报告、结构化图谱 JSON 和中心论文放射图规范。

## 何时使用

当用户提出以下需求时使用：

- 抽取论文引用的意图，例如背景引用、核心方法引用、数据集引用、指标引用、基线引用；
- 从论文中抽取方法、数据集、指标、任务、问题、结果等实体及关系；
- 理解目标论文的贡献是如何由参考文献支撑的；
- 生成类似中心论文放射图的 SVG 或图谱布局说明。

## 文件结构

```text
skills/paper-citation-map-zh/
├── SKILL.md
├── README.md
└── references/
    ├── analysis_template.md
    ├── prompts.md
    ├── schema.md
    └── visual.md
```

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | 中文 Skill 主入口，包含触发场景、工作流、标签体系、质量检查和失败处理 |
| `references/analysis_template.md` | 用户显式要求模板或规范格式时使用的固定 `analysis.md` 模板 |
| `references/schema.md` | 中文说明版 `citation_graph.json` schema 与最小示例 |
| `references/prompts.md` | 中文 LLM 抽取、关系构建、分组、JSON 修复和质量审查 prompt |
| `references/visual.md` | 中心论文放射图的 SVG 布局、颜色、节点、边和可访问性规范 |

## 标准输出

| 输出 | 说明 |
| --- | --- |
| `analysis.md` | 中文论文阅读报告，包含目标论文概要、引用意图分析、实体/关系说明和图谱解读 |
| `citation_graph.json` | Skill、后续 CLI 和未来 Web 共用的结构化图谱数据 |
| `citation_map.svg` | 中心论文放射图，或可直接用于 SVG 渲染的布局规范 |

## 分析模板模式

默认报告可以采用灵活结构，只要覆盖标准输出要求中的内容范围。只有用户显式要求模板或规范格式时，才使用 `references/analysis_template.md` 的固定结构，例如：`使用模板`、`按模板`、`符合规范`、`标准格式`、`固定结构`、`规范化报告`、`template`、`standard format`。

模板模式仍必须生成 `citation_graph.json`，并尽可能生成 `citation_map.svg`。不得为了填满模板而编造引用；没有证据时写 `未发现可靠证据`。

## 与现有工作的关系

- `CitePrompt`：提供引用意图识别任务背景，以及 `background` / `method` / `result` 粗粒度映射思想。
- `sci_glm`：提供 LLM 优先的抽取方式，包括标签受限、只返回 JSON、引用 ID 对齐和安全解析规则。

## 验证清单

- `SKILL.md` 包含合法 frontmatter，并且 `description` 以 `Use when` 开头。
- 12 个引用意图标签完整存在且与英文 Skill 一致。
- `references/schema.md` 中的 JSON 示例可被 `json.loads()` 解析。
- 每条 citation 示例包含 `intent`、`evidence`，以及 `reference_id` 或 `unmatched_reference`。
- 文档中不包含真实 API Key、私有绝对路径或未完成占位标记。
- 模板模式压力场景通过：显式模板请求遵循 `analysis_template.md`，普通分析请求不会被过度模板化。

## 后续 CLI/Web 扩展

下一阶段可基于该 Skill 的 schema 开发 CLI：解析 PDF/文本、调用 LLM 或本地抽取器、校验 `citation_graph.json`、渲染 SVG/HTML。Web 工具暂缓，等 schema 和 CLI 输出稳定后再单独规划。
