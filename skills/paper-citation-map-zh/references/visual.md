# 引用图谱图像模式

本 Skill 声明三种图像模式；当前只实现两种静态 SVG 模式。

## 模式判断

| 用户要求 | 输出行为 |
| --- | --- |
| `当前模式`、`原 SVG`、`原编排`、`current`、`current mode`、`original SVG` | 只生成 current 模式，写为 `citation_map.svg` |
| `例图`、`参考图`、`思维导图`、`example`、`reference image`、`mind map` | 只生成 example 模式，写为 `citation_map.svg` |
| `混合`、`可展开知识图谱`、`hybrid`、`expandable knowledge graph` | 说明 hybrid 预留给未来 Web 交互图谱，不输出固定 SVG |
| 未显式指定且可以询问 | 询问用户选择哪种图像模式 |
| 未显式指定且无法询问 | 同时生成 current 与 example |

文件约定：

- `visual_mode=current`：输出 `citation_map.svg` 和 `citation_map.html`。
- `visual_mode=example`：输出 `citation_map.svg` 和 `citation_map.html`，其中 SVG 内容为例图布局。
- `visual_mode=all`：`citation_map.svg` 为当前模式，`citation_map_example.svg` 为例图模式，`citation_map.html` 同时包含两种图。
- `visual_mode=hybrid`：不输出静态 SVG；如相关则在 `analysis.md` 中说明缺口。

## Current 模式：当前分组放射图

用户选择 current 时保持现有布局逻辑不变。

- 目标论文位于中心。
- 引用意图分组围绕目标论文排列。
- 分组 hub 使用稳定颜色和确定性坐标。
- 组内优先展示高价值 citation。
- `show_on_map=false` 的 citation 不出现在 SVG 中，但仍保留在 JSON。
- 图谱过密时，每组只渲染 3 到 5 个高优先级节点，并用 `+N citations` 汇总。

建议分组位置：

| 分组 | 位置 | intents |
| --- | --- | --- |
| 问题/背景 | 左上 | `background`, `problem` |
| 核心/辅助方法 | 右上 | `core-method`, `supporting-method`, `theory` |
| 数据/评估 | 右侧或中部 | `dataset`, `metric` |
| 基线/结果 | 左下 | `baseline`, `result-evidence` |
| 局限/资源/未来 | 底部或更左侧 | `limitation`, `tool-resource`, `future-work` |

## Example 模式：参考例图式思维导图

此模式参考用户给出的例图：右侧目标论文，左侧多层引用链。

推荐画布：从 `2400 x 1000` 这类宽画布开始，并随 citation 数量动态增加高度。

可读性与信息保留规则：

- 不要把“减少节点”作为解决拥挤的主要方案。只要静态 SVG 仍可读，就尽量保留所有 `show_on_map` 不为 `false` 的 citation。
- 优先使用动态高度、宽泳道、多列排布、足够节点间距和可滚动 HTML 容器，而不是直接用 `+N citations` 折叠信息。
- 只有当图谱规模大到静态 SVG 难以承载时，才把 `+N citations` 作为极端兜底；完整记录仍必须保留在 `citation_graph.json` 中。
- 边应绘制在节点下层；边标签放在链路 hub 附近的小徽章或空白区域，不要压在 citation 节点上。
- 节点标题应换行显示，副标题保持简短，不要通过把字体缩到不可读来容纳文字。

必需结构：

- 目标论文节点位于右侧中部。
- 左侧一级链固定为：
  - `问题链`：`background`, `problem`
  - `方法链`：`core-method`, `supporting-method`, `theory`
  - `数据链`：`dataset`, `metric`
  - `基线链`：`baseline`, `result-evidence`
  - `局限/资源链`：`limitation`, `tool-resource`, `future-work`
- 主边使用中文语义标签：`问题`、`方法`、`数据集`、`基线`、`局限`。
- 二级节点展示方法组件、数据集、基线或关键作者年份引用。
- 虚线可表达跨组辅助关系，例如某项工作同时是 baseline 与方法参照。
- 每条链 citation 较多时，先纵向扩展该链所在泳道，或拆成多列展示，再考虑使用汇总节点。

节点文本优先级：

1. `target_claim`
2. `cited_work_role`
3. 缩短后的 `evidence`
4. 缩短后的 `citation_sentence`
5. 从 `reference_id` 推断的参考文献标签

## 共享配色

| 意图组 | 颜色 |
| --- | --- |
| 问题/背景 | `#cf6f6f` |
| 核心/辅助方法 | `#ef6c2f` |
| 数据/指标 | `#8a5cf6` |
| 基线/结果 | `#d18a19` |
| 局限/资源/未来 | `#4f9c56` |
| 未匹配/不确定 | `#9aa3ad` |

## SVG 要求

- 必须包含可见目标论文节点，标签使用论文标题或短标题。
- 必须包含图例，解释颜色与 intent 分组的对应关系。
- 使用确定性布局，不使用随机力导向布局。
- 同时使用颜色和文字标签，不只依赖颜色。
- 主标签字号至少 `16px`，次级标签至少 `12px`。
- 节点不要放完整长引用句，使用短证据标签。

## Hybrid 模式预留

Hybrid 指可展开、可交互、按需展示细节的知识图谱，不是当前的固定 SVG 模式。当前被请求时：

- 不要生成伪静态 hybrid SVG。
- 说明该模式预留给未来 Web 联动展示。
- 仍然输出 `citation_graph.json`，因为它是未来 hybrid 图谱的数据源。
