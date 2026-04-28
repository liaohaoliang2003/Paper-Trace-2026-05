# Paper Trace：论文引用意图图谱

Paper Trace 用于从论文文本或 PDF 中抽取引用意图，生成结构化 `citation_graph.json`、中文分析报告和 SVG/HTML 引用图谱。

当前公开维护的主要部分：

- `paper_trace/`：CLI、Flask Web、provider、schema、渲染器。
- `skills/`：指导 Agent 生成引用意图分析、JSON 图谱和 SVG 图像的 Citation Map Skills。
- `CitePrompt/` 与 `sci_glm/`：本地私有历史参考代码，已按 private code 规则从 Git 上传中排除。

## 运行命令

本项目在当前 Windows 开发环境中主推显式 Anaconda 解释器：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace ...
```

不要优先使用裸 `python -m paper_trace ...`，因为系统默认 `python` 可能指向未安装 `openai` / `zhipuai` 的解释器。

### 启动 Web

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace web --debug --host 127.0.0.1 --port 8765
```

打开：

```text
http://127.0.0.1:8765
```

### 配置 API

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config path
C:\ProgramData\anaconda3\Python.exe -m paper_trace config list
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider openai-compatible --api-key "your-key" --base-url "https://api.anyone.ai/v1" --model "gpt-5.5" --stream true --timeout 300
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider zhipu-glm --api-key "your-key" --model "glm-4-flash"
C:\ProgramData\anaconda3\Python.exe -m paper_trace config clear --provider openai-compatible
```

真实 API Key 只应保存到本机 `.paper_trace/config.json`，不要写入代码、README、测试或输出样例。

### 运行 CLI 分析

默认 `--visual-mode all`，会同时生成当前分组视图和例图引用链视图。

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-demo --provider mock
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-llm --provider openai-compatible --visual-mode all
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-example --provider mock --visual-mode example
```

`--visual-mode` 可选值：

- `all`：默认，同时输出当前模式和例图模式。
- `current`：只输出当前分组放射图。
- `example`：只输出参考例图式引用链/思维导图。
- `hybrid`：预留给未来 Web 可展开知识图谱；当前会返回明确错误，不生成静态 SVG。

标准输出目录示例：

```text
outputs/paper-demo/
├── analysis.md
├── citation_graph.json
├── citation_map.html
├── citation_map.svg
├── citation_map_example.svg   # visual-mode=all 时生成
└── source.txt
```

### 校验与重新渲染

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace validate outputs\paper-demo\citation_graph.json
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered --visual-mode all
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered-example --visual-mode example
```

### 补充脚本入口

脚本不是主入口，只作为 Windows 下的补充：

```powershell
scripts\paper_trace.cmd --help
scripts\paper_trace.cmd analyze path\to\paper.txt --out outputs\paper-demo --provider mock --visual-mode all
scripts\web_debug.cmd
```

`scripts\paper_trace.cmd` 固定调用 `C:\ProgramData\anaconda3\Python.exe -m paper_trace` 并透传参数；`scripts\web_debug.cmd` 固定启动 Anaconda 版本的 Web 调试服务。

## 图像模式

Paper Trace 当前支持两种静态 SVG，并预留一种未来交互模式：

- `current`：当前分组放射图，目标论文在中心，引用意图分组环绕展示。
- `example`：参考例图式引用链图，目标论文在右侧，左侧按问题链、方法链、数据链、基线链、局限/资源链展开。
- `all`：同时生成 `citation_map.svg`（current）和 `citation_map_example.svg`（example）。这是 CLI/Web 默认行为。
- `hybrid`：预留给未来 Web 可展开知识图谱，目前不输出固定 SVG。

Web 首页提供“图像模式”下拉框。编辑 citation 后会按照该 run 的原始 `visual_mode` 重新渲染。

## Provider 与中转站建议

OpenAI-compatible provider 默认启用流式响应，适合中转站长请求：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider openai-compatible --api-key "your-key" --base-url "https://api.anyone.ai/v1" --model "gpt-5.5" --stream true --timeout 300
```

如果中转站后台显示已消费但本地报 `Connection error`，优先确认：

- `stream=true`
- `timeout=300` 或更高
- `base_url` 以 `/v1` 结尾并兼容 OpenAI Chat Completions
- 当前运行命令使用 `C:\ProgramData\anaconda3\Python.exe`

## Citation Map Skills

仓库内提供两个 Skill：

- `skills/paper-citation-map/`：英文说明，默认生成中文分析产物。
- `skills/paper-citation-map-zh/`：中文说明，适合中文用户。

Skill 默认尽可能落盘：

- `analysis.md`
- `citation_graph.json`
- `citation_map.svg`
- `citation_map_example.svg`（未指定图像模式时或选择 `all` 时）

当用户明确说“规范地 / 使用模板 / 标准格式 / 固定结构 / template / standard format”时，Skill 会使用固定 `analysis.md` 模板；普通“分析引用意图”不会强制固定章节。

## 安装依赖

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install -r requirements-paper-trace.txt
```

按需安装：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install openai
C:\ProgramData\anaconda3\Python.exe -m pip install zhipuai
C:\ProgramData\anaconda3\Python.exe -m pip install pypdf
```

## 本地文件与安全

- `.paper_trace/`：本机 provider 配置，可能包含 API Key，已忽略。
- `outputs/`：本地运行产物，已忽略。
- `.omx/`：本地 agent 状态与日志，已忽略。
- `CitePrompt/`、`sci_glm/`：私有历史参考代码，已按 private code 规则忽略。
- 文档示例只使用 `your-key` 占位符，不应提交真实密钥。

## 验证

```powershell
C:\ProgramData\anaconda3\Python.exe -m unittest tests.test_paper_trace -v
Get-ChildItem -Recurse paper_trace -Filter *.py | ForEach-Object { C:\ProgramData\anaconda3\Python.exe -m py_compile $_.FullName }
cmd /c scripts\paper_trace.cmd --help
```
