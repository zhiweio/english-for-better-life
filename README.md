# english-for-better-life

用 Git 和 AI 托管我的英语学习:每周两次课,材料归档、预习、作文批改、课后精听/泛听/阅读、词汇沉淀、进度跟踪,全部在一个仓库里完成。

## 每周怎么用(核心循环)

```
课前(材料到了)
  1. 把老师材料粘贴给 AI → 说「整理材料」   → lessons/日期/material.md
  2. 说「生成预习」                        → lessons/日期/preparation.md(课前读一遍+跟读)
  3. 手写作文(基于上节课)→ 打字贴给 AI
     说「批改作文」                        → lessons/日期/essay-feedback.md(带着它去上课)

课中
  4. 老师带着批改作文;老师的额外指正课后补进 essay-feedback.md 的「课堂补充」区

课后
  5. 把老师发的视频/阅读/语法作业贴给 AI → 说「整理课后」
                                          → lessons/日期/after-class.md(完成一项勾一项)
                                          → lessons/日期/grammar.md(语法作业,不一定每课都有;
                                            小测验留白自测,下节课口答)
                                          → lessons/日期/vocab.md(摘表达)

周日晚
  6. 说「周回顾」                          → dashboard.md 更新 streak/统计/薄弱点/下周重点
```

支持的 AI 工具:ZCode、Codex、Cursor 等任何读取 `AGENTS.md` 的工具(触发词在里面);5 个工作流细节定义在 `.agents/skills/`。

## 目录导航

| 路径 | 内容 |
|---|---|
| `lessons/YYYY-MM-DD/` | **一节课一个文件夹**:material(老师材料)/ preparation(预习)/ essay-draft(作文稿)/ essay-feedback(批改)/ after-class(课后任务+打卡)/ grammar(语法作业,可选)/ vocab(本课词汇) |
| `dashboard.md` | 进度看板:课程日志、streak、统计、薄弱点 Top 5、下周重点、周记 |
| `vocabulary/` | `mistakes.md` 错误模式本(刻意练习靶点)+ `anki-export.csv` |
| `expression/` | 跨课表达库(高频短语、利弊表达模板) |
| `reading-and-listening/` | 阅读练习 + 通用听力资源清单 |
| `profile.md` | 学员画像:水平、目标、练习偏好 |
| `assets/` | 本地听力语料(150 天听力教程,gitignored) |

词汇复习:`python3 scripts/build_anki_csv.py` → 把 `vocabulary/anki-export.csv` 导入 Anki(方法见 `vocabulary/README.md`)。

## 方法论

这套流程刻意对齐了几条有研究支撑的学习原则:

1. **刻意练习**(在「学习区」针对弱点、高频反馈地练,而不是舒适区重复):
   - 明确目标 → 每课预习(嵌套从句 Layer 0→4 递进,始终踩在当前能力边缘)
   - 即时反馈 → 作文 AI 批改 + 老师课堂批改,错误全部进 `mistakes.md`
   - 针对性重复 → 每周回顾把错误 Top 5 变成下周作文/跟读的具体要求,形成「暴露弱点 → 定向练习 → 复查」的闭环
2. **大量可理解输入**:泛听保量(磨耳朵,不求全懂)、精听保质(跟读模仿 + 摘表达)、阅读提表达——对应 `after-class.md` 的三类任务
3. **间隔重复**:摘出的词汇/表达导出 Anki,对抗遗忘曲线,而不是记完就忘

坚持机制:看板上的 streak 和课程日志让进度可见;每周回顾 10 分钟让下一周永远有明确的起点;git 提交历史本身就是学习日志——不断更,仓库就一直在生长。

参考:
- [Deliberate and Purposeful Practice for Second Language Learning (TESL-EJ)](https://tesl-ej.org/wordpress/issues/volume29/ej115/ej115a5)
- [The Ultimate Guide to Deliberate Practice (Farnam Street)](https://fs.blog/deliberate-practice-guide/)
- 精听/泛听结合 + 间隔重复是语言学习社区的通行做法(泛听建语感,精听挖表达,SRS 负责留存)

## 历史说明

2026-10-07 仓库重构:原 `materials/`(28 篇)、`preparation/`(15 篇)、`composition/`(3 篇)已按日期迁移进 `lessons/`,原 `preparation/RULES.md` 规则并入 `.agents/skills/prepare-lesson/SKILL.md`,过时的 `.github/` 配置已删除。git 历史可追溯全部旧路径。
