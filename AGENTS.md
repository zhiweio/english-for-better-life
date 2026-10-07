# AGENTS.md

本仓库托管一位学员的英语学习全流程(每周两次课)。任何 AI 助手(ZCode / Codex / Cursor 等)在本仓库工作前,先读完本文件。

## 学员画像

见 `profile.md`。要点:技术背景(IT 数据工程),阅读尚可、听力口语弱,需要双语支架;当前目标 B2 口头表达,专项是**嵌套从句**。

## 目录结构

| 路径 | 内容 |
|---|---|
| `lessons/YYYY-MM-DD/` | **核心**:一节课一个文件夹(material / preparation / essay-draft / essay-feedback / after-class / vocab) |
| `vocabulary/` | 跨课沉淀:`mistakes.md` 错误模式本、`anki-export.csv`(脚本生成) |
| `expression/` | 跨课表达库(短语、利弊表达模板) |
| `reading-and-listening/` | 阅读练习 + 通用听力资源清单 |
| `dashboard.md` | 进度看板(课程日志 / streak / 统计 / 薄弱点 / 下周重点) |
| `.agents/skills/` | 5 个工作流 skill(见下) |
| `assets/` | 本地听力语料(gitignored) |

## 每周工作流(5 个 skill)

| 触发语 | Skill | 做什么 |
|---|---|---|
| 「整理材料」 | `.agents/skills/organize-material/SKILL.md` | 老师材料 → `lessons/日期/material.md` |
| 「生成预习」 | `.agents/skills/prepare-lesson/SKILL.md` | material → `preparation.md`(B2 嵌套从句) |
| 「批改作文」 | `.agents/skills/review-essay/SKILL.md` | essay-draft → `essay-feedback.md` + 更新 `vocabulary/mistakes.md` |
| 「整理课后」 | `.agents/skills/after-class/SKILL.md` | 视频/阅读链接 → `after-class.md` + `vocab.md` + 打卡 |
| 「周回顾」 | `.agents/skills/weekly-review/SKILL.md` | 扫描本周 → 更新 `dashboard.md` |

**执行规则:**

1. 用户触发上述任一环节(或明显想做其中某一步)时,**先读取对应 SKILL.md 再动手**,严格按其中的步骤、模板和禁止事项执行
2. 每个环节完成后按 SKILL.md 要求更新 `dashboard.md` 对应勾选
3. 日期一律用 `YYYY-MM-DD`;找不到明确日期时询问用户,不要猜
4. 学员的历史文件(2026-04 ~ 2026-09)已迁移到 `lessons/`,不要在仓库根重建 `materials/`、`preparation/`、`composition/` 等旧目录

## 全局写作原则

- 训练内容用英文,中文只用于降低理解负担(概念解释、用法说明、复习指引),不做全文翻译
- 英文输出默认 B2,句子带从句;仅当用户明确要求时降级
- 生成的练习必须可朗读、可复述,不是仅供阅读的文章
- 改写优先于照搬:除 material 归档外,所有 AI 生成物都要用自己的话复述原材料

## 词汇与 Anki

- 每课词汇写在 `lessons/日期/vocab.md`,表头固定为 `| 英文 | 音标 | 中文 | 例句 | 来源 |`
- 积累几课后运行 `python3 scripts/build_anki_csv.py` 重新生成 `vocabulary/anki-export.csv`,导入 Anki 做间隔重复
- 作文错误沉淀在 `vocabulary/mistakes.md`,是「薄弱点 Top」和下周重点的依据
