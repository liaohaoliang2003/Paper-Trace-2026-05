# Citation Map Skill 分析深度优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化 `paper-citation-map` 与 `paper-citation-map-zh`，让 Agent 使用 Skill 时稳定产出证据链清楚、引用角色明确、能帮助理解论文核心内容的引用意图分析。

**Architecture:** 只修改 Skill 文档与 references，不修改 `paper_trace/`、`CitePrompt/`、`sci_glm/` 源码。新增证据协议作为抽取与报告之间的中间约束，再增强模板、prompt 和 schema 说明。

**Tech Stack:** Markdown Skill 文档、Codex installed skills、UTF-8 文本校验。

---

### Task 1: Evidence Protocol

**Files:**
- Create: `skills/paper-citation-map/references/evidence_protocol.md`
- Create: `skills/paper-citation-map-zh/references/evidence_protocol.md`

- [x] Add evidence-source, citation-context, section, cited-work role, intent-rationale, confidence, no-evidence, and anti-fabrication rules.
- [x] Ensure the Chinese version includes `引用上下文`、`意图判据`、`置信度`、`未发现可靠证据`.

### Task 2: Skill Workflow Updates

**Files:**
- Modify: `skills/paper-citation-map/SKILL.md`
- Modify: `skills/paper-citation-map-zh/SKILL.md`

- [x] Add an evidence-chain step before writing `analysis.md`.
- [x] Link `references/evidence_protocol.md` from reference files.
- [x] Add quality checks for traceable citation context and lower confidence when evidence is weak.

### Task 3: Template Depth Updates

**Files:**
- Modify: `skills/paper-citation-map/references/analysis_template.md`
- Modify: `skills/paper-citation-map-zh/references/analysis_template.md`

- [x] Keep the existing 9-section template order.
- [x] Add reader-priority citation chains to section 1.
- [x] Strengthen method-chain and experiment-chain tables.

### Task 4: Prompt and Schema Updates

**Files:**
- Modify: `skills/paper-citation-map/references/prompts.md`
- Modify: `skills/paper-citation-map-zh/references/prompts.md`
- Modify: `skills/paper-citation-map/references/schema.md`
- Modify: `skills/paper-citation-map-zh/references/schema.md`

- [x] Ask extraction and review prompts for intent rationale, cited-work role, and confidence reason.
- [x] Document optional explanatory fields without making them required.

### Task 5: Installed Skill Sync

**Files:**
- Copy project skill docs to `C:\Users\Haoliang Liao\.codex\skills\paper-citation-map\`
- Copy project skill docs to `C:\Users\Haoliang Liao\.codex\skills\paper-citation-map-zh\`

- [x] Sync only `SKILL.md`, `README.md`, and `references/*.md`.
- [x] Verify installed copies match project copies.

### Task 6: Verification

**Checks:**
- [x] UTF-8 replacement count is zero for modified Markdown files.
- [x] No real API key, `api_key=`, `sk-`, or `eval(` appears in modified Skill files.
- [x] Template-trigger behavior remains explicit and does not affect ordinary citation analysis requests.
