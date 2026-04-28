# Paper Trace 工作流

本文档记录 Paper Trace 的常用运行方式、配置、图像模式和验证流程。当前 Windows 开发环境统一使用 Anaconda Python：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace ...
```

如果使用裸 `python`，可能会调用到 `C:\Program Files\Python38\python.exe` 等系统解释器，从而缺少 `openai` / `zhipuai` 依赖。

## 1. 环境检查

```powershell
C:\ProgramData\anaconda3\Python.exe -c "import sys; print(sys.executable)"
C:\ProgramData\anaconda3\Python.exe -m pip install -r requirements-paper-trace.txt
```

按需安装真实 provider 依赖：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install openai zhipuai pypdf
```

## 2. API 配置

查看配置位置和当前遮罩配置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config path
C:\ProgramData\anaconda3\Python.exe -m paper_trace config list
```

OpenAI-compatible 中转站推荐配置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider openai-compatible --api-key "your-key" --base-url "https://api.anyone.ai/v1" --model "gpt-5.5" --stream true --timeout 300
```

智谱 GLM 配置示例：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider zhipu-glm --api-key "your-key" --model "glm-4-flash"
```

清除配置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config clear --provider openai-compatible
```

## 3. CLI 分析

Mock provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-demo --provider mock
```

OpenAI-compatible provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-llm --provider openai-compatible --visual-mode all
```

智谱 GLM provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-glm --provider zhipu-glm --visual-mode current
```

输出目录通常包含：

```text
outputs/paper-demo/
├── analysis.md
├── citation_graph.json
├── citation_map.html
├── citation_map.svg
├── citation_map_example.svg   # visual-mode=all 时生成
└── source.txt
```

## 4. 图像模式

`analyze` 和 `render` 都支持：

```text
--visual-mode current|example|all|hybrid
```

- `all`：默认，同时输出 current 与 example 两张静态 SVG。
- `current`：当前分组放射图，目标论文位于中心。
- `example`：参考例图式引用链图，目标论文位于右侧，左侧展开问题链、方法链、数据链、基线链、局限/资源链。
- `hybrid`：预留给未来 Web 可展开知识图谱；当前会返回明确错误，不生成固定 SVG。

重新渲染已有 JSON：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered --visual-mode all
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered-example --visual-mode example
```

## 5. 校验

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace validate outputs\paper-demo\citation_graph.json
```

关键 schema 约束：

- 顶层包含 `paper`、`references`、`citations`、`entities`、`relations`、`visual_groups`、`metadata`。
- `paper` 包含 `paper_id`、`title`、`authors`、`year`、`abstract`、`core_contributions`。
- 每条 citation 包含 `intent`、`evidence`、`confidence`，并且有 `reference_id` 或 `unmatched_reference=true`。
- `intent` 只能属于 12 类标签：`background`、`problem`、`core-method`、`supporting-method`、`dataset`、`metric`、`baseline`、`tool-resource`、`theory`、`result-evidence`、`limitation`、`future-work`。

真实 LLM 偶发漏掉 `paper.abstract` 或 `paper.core_contributions` 时，provider 边界会做保守补全；schema 本身不放宽。

## 6. Flask Web

启动：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace web --debug --host 127.0.0.1 --port 8765
```

访问：

```text
http://127.0.0.1:8765
```

Web 支持：

- 上传 `.txt`、`.md` 或可解析文本的 `.pdf`。
- 选择 `mock`、`openai-compatible` 或 `zhipu-glm`。
- 选择图像模式：`all`、`current`、`example`；`hybrid` 只显示预留错误。
- 右上角齿轮保存 API Key、Base URL、模型、流式响应和超时秒数。
- 结果页查看 SVG 图谱和 `analysis.md`。
- 编辑 citation 的 `intent`、`confidence`、`evidence`、`notes`、`show_on_map`，保存后按原 `visual_mode` 重新渲染。

## 7. 补充脚本入口

脚本不是主入口，只作为 Windows 下的补充：

```powershell
scripts\paper_trace.cmd --help
scripts\paper_trace.cmd analyze path\to\paper.txt --out outputs\paper-demo --provider mock --visual-mode all
scripts\web_debug.cmd
```

只保留两个脚本：

- `scripts\paper_trace.cmd`：透传 CLI 子命令。
- `scripts\web_debug.cmd`：启动 Web debug 服务。

## 8. Skill 行为

`paper-citation-map` 与 `paper-citation-map-zh` 默认尽可能写出：

- `analysis.md`
- `citation_graph.json`
- `citation_map.svg`
- `citation_map_example.svg`（未指定图像模式或选择 `all` 时）

Skill 图像模式规则：

- 用户明确要求当前模式或原 SVG：只输出 current。
- 用户明确要求例图、参考图或思维导图：只输出 example。
- 用户要求 hybrid 或可展开知识图谱：说明当前预留，不输出固定 SVG。
- 用户未指定且无法询问：输出 current + example。

当用户明确说“规范地 / 使用模板 / 标准格式 / 固定结构 / template / standard format”时，`analysis.md` 使用固定模板；普通分析不强制模板。

## 9. 回归验证

```powershell
C:\ProgramData\anaconda3\Python.exe -m unittest tests.test_paper_trace -v
Get-ChildItem -Recurse paper_trace -Filter *.py | ForEach-Object { C:\ProgramData\anaconda3\Python.exe -m py_compile $_.FullName }
cmd /c scripts\paper_trace.cmd --help
```

安全检查：文档、脚本和测试中不应出现真实 API Key、私有 token、明文 API 参数示例、OpenAI 私钥前缀片段或 Python 表达式求值调用。
