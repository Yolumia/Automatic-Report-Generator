# 自动报告生成器

一个面向 AI 协作的本地报告生成器项目。

它解决两件事：
1. 把用户放进 `data/sources/` 的参考资料读取并整理成可追溯证据包。
2. 提供一套可直接给 AI 使用的提示词与流程说明，让 AI 基于证据生成“可行、可信、有依据”的报告。

## 当前能力

- 支持扫描资料目录并读取以下常见格式：
  - `.txt`
  - `.md`
  - `.pdf`
  - `.docx`
  - `.pptx`
  - `.xlsx`
- 自动生成：
  - 标准化证据包 `outputs/evidence.json`
  - 报告草稿 `outputs/report.md`
  - AI 执行提示词包 `outputs/ai_prompt_package.md`
- 内置可复用 skills 设计与调用说明。
- 内置生成流程指导文档，可直接复制给 AI 工具执行。
- 支持可选的联网搜索与网页正文抓取能力（默认关闭，启用后仅作补充线索，必须二次核验）。

## 项目结构

- `src/report_generator/`：主程序
- `data/sources/`：用户放置原始资料
- `data/processed/`：可选的中间处理结果
- `outputs/`：生成结果
- `docs/`：流程指导、skill 说明
- `prompts/`：系统提示词、任务提示词、检查清单
- `tests/`：自动化测试

## 快速开始

### 1) 安装

```powershell
python -m pip install -e .[dev]
```

### 2) 放入资料

将参考资料放入：

```text
data/sources/
```

支持常见文本、文档、演示文稿、表格、PDF。

### 3) 生成报告素材

```powershell
python -m report_generator.cli --topic "年度经营分析报告"
```

或指定目录：

```powershell
python -m report_generator.cli --topic "行业研究报告" --sources-dir "data/sources" --output-dir "outputs"
```

### 4) 交给 AI 继续生成最终报告

把以下两个文件一起交给你的 AI 工具：

- `docs/process_guide.md`
- `outputs/ai_prompt_package.md`

通常只要再补一句你的任务目标，比如：

> 请根据流程指导和提示词包，生成一份正式报告，保留引用、注明不确定项，并输出可执行建议。

## 开发与测试

```powershell
python -m pytest
```

## 可选：启用免费联网搜索与网页抓取

项目默认**不联网**。如果你需要补充公开网页线索，可以显式启用：

```powershell
$env:REPORT_GENERATOR_ENABLE_WEB="1"
$env:REPORT_GENERATOR_WEB_SEARCH_URL="https://www.baidu.com/s"
$env:REPORT_GENERATOR_WEB_RESULT_SELECTOR="h3 a"
```

启用后：
- `web_search` 会抓取搜索结果页中的候选链接。
- `fetch_web_page` 会抓取网页正文文本。
- 所有联网结果都只能作为补充线索，不能直接替代本地原始资料。
- 写入正式报告前，必须回到权威原始来源完成二次核验。

不建议把新闻转载、论坛、博客、二手摘要直接写入正式报告。

## 设计原则

- **只基于证据写作**：没有依据就明确说明不足。
- **引用可追溯**：每条关键结论尽量关联来源文件和片段。
- **不编造数字与事实**：无法验证时标记为“待确认”或“推断”。
- **先提炼证据，再组织结论**：避免直接从原始资料跳到结论。

## 后续扩展建议

- 增加 `.doc`、`.xls` 等旧格式转换支持
- 接入 OCR 处理扫描版 PDF
- 对接特定 LLM API 或本地模型
- 增加行业报告模板（尽调、投研、复盘、方案、招投标等）
