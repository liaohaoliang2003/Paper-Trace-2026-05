# 论文引用意图识别与 Paper Trace

本仓库围绕论文引用意图识别展开，当前公开/主要维护部分是 `paper_trace/` 与项目内 Skills；另外保留两份本地私有历史参考代码：

- `paper_trace/`：PDF/文本论文引用意图抽取、结构化图谱生成、CLI 与 Flask Web 工具。
- `skills/`：项目内 Citation Map Skills，用于指导 Agent 生成 `analysis.md`、`citation_graph.json` 和 `citation_map.svg`。
- `CitePrompt/`：本地私有历史参考代码，基于 OpenPrompt / SciBERT 的 citation intent 分类实验。
- `sci_glm/`：本地私有历史参考代码，面向 SciCite 的大模型提示词样本筛选、批量推理与 F1 评估。


## Paper Trace 运行命令

所有 Paper Trace 命令都建议显式使用当前 Windows 开发环境中的 Anaconda base 解释器：

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace ...
```

如果直接使用 `python`，可能会调用到未安装 LLM provider 依赖的系统解释器，导致找不到 `openai` / `zhipuai` 包。

### 1. 启动 Web 工具

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace web --debug --host 127.0.0.1 --port 8765
```

启动后访问：

```text
http://127.0.0.1:8765
```

### 2. 查看 CLI 帮助

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace --help
```

### 3. 配置 API

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace config path
C:\ProgramData\anaconda3\Python.exe -m paper_trace config list
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider openai-compatible --api-key "your-key" --base-url "https://api.anyone.ai/v1" --model "gpt-5.5" --stream true --timeout 300
C:\ProgramData\anaconda3\Python.exe -m paper_trace config set --provider zhipu-glm --api-key "your-key" --model "glm-4-flash"
C:\ProgramData\anaconda3\Python.exe -m paper_trace config clear --provider openai-compatible
```

### 4. 运行 CLI 分析

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-demo --provider mock
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-llm --provider openai-compatible
C:\ProgramData\anaconda3\Python.exe -m paper_trace analyze path\to\paper.txt --out outputs\paper-glm --provider zhipu-glm
```

标准输出目录：

```text
outputs/paper-demo/
├── analysis.md
├── citation_graph.json
├── citation_map.html
├── citation_map.svg
└── source.txt
```

### 5. 校验与重新渲染

```powershell
C:\ProgramData\anaconda3\Python.exe -m paper_trace validate outputs\paper-demo\citation_graph.json
C:\ProgramData\anaconda3\Python.exe -m paper_trace render outputs\paper-demo\citation_graph.json --out outputs\paper-rendered
```

### 6. 解释器检查

```powershell
C:\ProgramData\anaconda3\Python.exe -c "import sys, openai; print(sys.executable)"
python -c "import sys; print(sys.executable)"
```

第一条用于确认 Anaconda Python 能导入 `openai`；第二条仅用于排查系统默认 `python` 指向哪里。

### 7. 补充脚本入口

项目运行方式以 `C:\ProgramData\anaconda3\Python.exe -m paper_trace ...` 终端命令为主。`scripts/` 目录只保留两个 Windows `.cmd` 脚本作为补充入口：

```powershell
scripts\paper_trace.cmd --help
scripts\paper_trace.cmd analyze path\to\paper.txt --out outputs\paper-demo --provider mock
scripts\web_debug.cmd
```

其中 `scripts\paper_trace.cmd` 用于透传 CLI 子命令，`scripts\web_debug.cmd` 用于启动 Web 调试服务。

## Paper Trace 功能概览

`paper_trace/` 支持：

- 输入 `.txt`、`.md` 或可解析文本的 `.pdf`。
- 通过 `mock`、`openai-compatible` 或 `zhipu-glm` provider 生成引用意图图谱。
- 输出 `analysis.md`、`citation_graph.json`、`citation_map.svg`、`citation_map.html` 与 `source.txt`。
- Web 端上传论文、选择 provider、设置 API、查看图谱并编辑 citation 的 `intent`、`confidence`、`evidence`、`notes`、`show_on_map`。
- OpenAI-compatible provider 默认启用流式响应；如果中转站后台已消费但本地报 `Connection error`，优先确认 `stream=true` 与 `timeout=300`。
- 真实模型漏掉 `paper.abstract` 或 `paper.core_contributions` 时会在 provider 边界做保守补全，避免图谱生成被非核心元数据字段中断。
- 统一使用 12 类扩展引用意图标签：`background`、`problem`、`core-method`、`supporting-method`、`dataset`、`metric`、`baseline`、`tool-resource`、`theory`、`result-evidence`、`limitation`、`future-work`。

更完整的工作流说明见 `PAPER_TRACE_WORKFLOW.md`。

## Citation Map Skills 与规范化报告模板

项目内包含两个论文引用图谱 Skill：

- `skills/paper-citation-map/`：英文说明版 Skill，面向通用 citation intent extraction 请求。
- `skills/paper-citation-map-zh/`：中文说明版 Skill，面向中文用户的论文引用意图分析请求。

两个 Skill 默认都会尽可能落盘生成：

```text
analysis.md
citation_graph.json
citation_map.svg
```

当用户只是要求“分析论文引用意图”时，`analysis.md` 可以采用灵活结构，但必须覆盖目标论文概要、引用意图发现、实体/关系说明、图谱解读、覆盖范围和不确定性说明。

当用户明确要求“使用模板”“按模板”“符合规范”“标准格式”“固定结构”“规范化报告”或英文 `template` / `standard format` 时，Agent 必须读取对应 Skill 的 `references/analysis_template.md`，并按固定章节顺序生成 `analysis.md`。模板模式固定包含：

1. 结论先行
2. 目标论文核心内容
3. 引用意图总览
4. 按意图分组的引用分析
5. 核心方法引用链
6. 数据集、指标与基线引用
7. 实体与关系图谱解读
8. 覆盖范围、噪声与不确定性
9. 输出文件清单

模板模式不会改变 `citation_graph.json` 的 schema，也不会要求编造缺失引用；没有可靠证据的 intent 应写为“未发现可靠证据”。

## CitePrompt：论文引用意图识别

`CitePrompt/` 是本地私有历史参考代码，已被 `.gitignore` 忽略；它主要用于基于 SciCite / ACL-ARC 等数据集进行引用意图分类实验，包含 zero-shot、few-shot 和 fully supervised 相关入口。公开协作或重新克隆仓库时，该目录可能不存在。

常见入口示例：

```bash
cd CitePrompt
bash run_fewshot.sh
```

可通过修改脚本中的 `shot` 等参数改变 few-shot 微调样本数量。具体依赖、数据路径和模型路径请参考 `CitePrompt/README.md`。

## sci_glm：GLM 提示词样本筛选与评估

`sci_glm/` 是本地私有历史参考代码，已被 `.gitignore` 忽略；它面向 SciCite 的大模型提示词样本筛选与评估，用于构造提示词、批量调用模型并根据 macro/micro F1 选择较优 few-shot 示例组合。公开协作或重新克隆仓库时，该目录可能不存在。

常见入口示例：

```bash
cd sci_glm
python async_glm.py
python sci_glm.py
```

历史数据目录约定：

```text
/workspace/sci_glm/scicite/glm_input/
/workspace/sci_glm/scicite/glm_output/
```

注意：`CitePrompt/` 与 `sci_glm/` 都是私有历史参考代码，不应上传；`sci_glm/` 中的历史脚本可能包含硬编码路径或旧式 API 调用方式。新的 `paper_trace/` 工具使用环境变量或 `.paper_trace/config.json` 管理配置，不应在代码中写入真实 API Key。

## 依赖说明

Paper Trace 的轻量依赖见：

```text
requirements-paper-trace.txt
```

最小安装：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install -r requirements-paper-trace.txt
```

按需安装：

```powershell
C:\ProgramData\anaconda3\Python.exe -m pip install openai
C:\ProgramData\anaconda3\Python.exe -m pip install zhipuai
C:\ProgramData\anaconda3\Python.exe -m pip install pypdf
```
