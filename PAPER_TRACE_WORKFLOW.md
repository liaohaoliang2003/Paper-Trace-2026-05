# Paper Trace CLI 与 Flask Web 工作流

`paper_trace/` 用于把单篇论文 PDF、`.txt` 或 `.md` 转换为引用意图图谱，输出 `analysis.md`、`citation_graph.json`、`citation_map.svg` 与 `citation_map.html`。当前支持离线 `mock` provider，也支持 OpenAI-compatible 与智谱 GLM 原生 SDK。

## 运行原则

本项目以终端命令为主要运行方式，主入口固定为：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace ...
```

如果当前终端里的 `python` 不是已安装依赖的解释器，可显式使用 Anaconda Python：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace ...
```

`scripts/` 目录只保留两个 Windows `.cmd` 脚本作为补充入口，不作为主要运行方式：

```text
scripts\paper_trace.cmd   # CLI 补充入口，透传所有 paper_trace 子命令
scripts\web_debug.cmd     # Web 补充入口，启动 debug Web 服务
```

## 解释器检查

检查当前 `python` 指向：

```powershell
python -c "import sys; print(sys.executable)"
```

检查 Anaconda Python 是否能导入 `openai`：

```powershell
C:\ProgramData\anaconda3\Python.exe -c "import sys, openai; print(sys.executable)"
```

如果运行 OpenAI-compatible provider 时出现缺少 `openai` 包，请优先确认实际运行的解释器。

## 安装依赖

最小 Web/CLI 演示只需要 Flask：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install -r requirements-paper-trace.txt
```

按需安装可选依赖：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install openai      # OpenAI-compatible provider
C:\ProgramData\anaconda3\Python.exe -m pip install zhipuai     # 智谱 GLM 原生 provider
C:\ProgramData\anaconda3\Python.exe -m pip install pypdf       # 直接解析 PDF
```

如果需要显式安装到 Anaconda base：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install -r requirements-paper-trace.txt
C:\ProgramData\anaconda3\Python.exe -m pip install openai zhipuai pypdf
```

## API 配置

配置优先级为：构造函数显式参数（测试/注入）→ 项目本地配置 → 环境变量 → 默认模型。

项目本地配置保存在 `.paper_trace/config.json`，该目录已加入 `.gitignore`。API Key 会明文保存在本机文件中，但 CLI/Web 展示时只显示遮罩。

查看配置文件位置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config path
```

查看遮罩后的配置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config list
C:\ProgramData\anaconda3\Python.exe -m paper_trace config get --provider openai-compatible
```

配置 OpenAI-compatible provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider openai-compatible --api-key "your-key" --base-url "https://api.anyone.ai/v1" --model "gpt-5.5" --stream true --timeout 300
```

OpenAI-compatible 默认使用 `stream=true` 与 `timeout=300`。如果中转站后台显示请求已消费，但本地提示 `Connection error`，通常是长时间非流式响应在客户端或代理链路中断；优先启用流式响应，不要自动重试以免重复扣费。

配置智谱 GLM provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider zhipu-glm --api-key "your-key" --model "glm-4-flash"
```

清除某个 provider 的本地配置：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config clear --provider openai-compatible
```

如果不想落盘保存 Key，也可以继续使用环境变量：

```powershell
$env:PAPER_TRACE_OPENAI_API_KEY="your-key"
$env:PAPER_TRACE_OPENAI_BASE_URL="https://api.example.com/v1"
$env:PAPER_TRACE_OPENAI_MODEL="gpt-4o-mini"
$env:PAPER_TRACE_ZHIPU_API_KEY="your-key"
$env:PAPER_TRACE_ZHIPU_MODEL="glm-4-flash"
```

## CLI 用法

查看帮助：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace --help
```

使用 mock provider 离线跑通完整流程：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-demo --provider mock
```

使用 OpenAI-compatible provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-llm --provider openai-compatible
```

使用智谱 GLM provider：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-glm --provider zhipu-glm
```

输出目录包含：

```text
outputs/paper-demo/
├── analysis.md
├── citation_graph.json
├── citation_map.html
├── citation_map.svg
└── source.txt
```

校验图谱 JSON：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace validate outputs\paper-demo\citation_graph.json
```

从已有 `citation_graph.json` 重新生成 SVG/HTML：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered
```

## Flask Web 用法

启动 Web 调试服务：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace web --debug --host 127.0.0.1 --port 8765
```

浏览器访问：

```text
http://127.0.0.1:8765
```

Web V1 支持：

- 上传 `.txt`、`.md` 或 `.pdf`。
- 在页面选择 `mock`、`openai-compatible` 或 `zhipu-glm`。
- 点击右上角齿轮打开 API 设置面板，保存或清除真实 provider 的 API Key、Base URL、模型名、流式响应与超时秒数。
- 查看中心论文放射图。
- 编辑 citation 的 `intent`、`confidence`、`evidence`、`notes` 与 `show_on_map`。
- 保存后自动重写 `citation_graph.json` 并重新生成 `citation_map.svg` / `citation_map.html`。

## 补充脚本入口

脚本不是主要运行方式，仅作为 Windows 下的补充入口：

```powershell
scripts\paper_trace.cmd --help
scripts\paper_trace.cmd analyze path\to\paper.txt --out outputs\paper-demo --provider mock
scripts\web_debug.cmd
```

`scripts\paper_trace.cmd` 固定调用 `C:\ProgramData\anaconda3\Python.exe -m paper_trace` 并透传参数。`scripts\web_debug.cmd` 固定启动 `C:\ProgramData\anaconda3\Python.exe -m paper_trace web --debug --host 127.0.0.1 --port 8765` 的 Anaconda 版本。

## LLM 输出约束

真实 provider 会使用统一 prompt，要求模型只返回 JSON 对象。程序只使用 `json.loads()` 解析输出，并在写入前执行 schema 校验。

关键约束：

- `intent` 必须属于 12 个扩展标签之一：`background`、`problem`、`core-method`、`supporting-method`、`dataset`、`metric`、`baseline`、`tool-resource`、`theory`、`result-evidence`、`limitation`、`future-work`。
- `paper` 必须包含 `paper_id`、`title`、`authors`、`year`、`abstract` 与 `core_contributions`；真实模型漏掉 `abstract` 或 `core_contributions` 时，provider 会用输入文本做保守补全。
- 每条 citation 必须包含 `evidence`。
- 每条 citation 必须包含 `reference_id`，或设置 `unmatched_reference=true`。
- 不接受数组、解释文本或无法解析的 JSON。
- 不使用 Python 表达式求值方式解析模型输出。

## 与 Skill 的关系

CLI/Web 复用 `skills/paper-citation-map` 与 `skills/paper-citation-map-zh` 中定义的概念：

- 12 个扩展引用意图标签。
- `citation_graph.json` 顶层字段。
- 中心论文放射图视觉规则。
- “只返回 JSON、标签受限、引用 ID 对齐”的 LLM 抽取原则。

## 安全与限制

- 不在代码或文档中写入真实 API Key；文档示例只使用占位符。
- `.paper_trace/config.json` 用于本地保存配置，已通过 `.gitignore` 避免提交。
- 自动化测试不调用真实 LLM，不消耗额度。
- 第一版真实 provider 是同步单篇抽取，不做异步批处理、流式输出或重试队列。
- PDF 解析质量取决于 `pypdf`，复杂双栏或扫描版 PDF 建议先转换为 `.txt`。
- Web 编辑范围限定为标签、置信度、证据、备注和图谱显隐，不支持新增或删除节点/边。
