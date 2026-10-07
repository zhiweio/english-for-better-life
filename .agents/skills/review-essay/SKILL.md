---
name: review-essay
description: 批改英语作文。当用户说「批改作文」「改作文」「review my essay」或贴入一篇作文要求纠错时使用。生成 essay-feedback.md(总评/逐句纠错/升级改写),并把错误归类到 vocabulary/mistakes.md 形成针对性练习靶点。
---

# 批改作文(Essay Feedback)

> 刻意练习的核心反馈环节:AI 先批改一轮,用户带着批改结果上课,老师课堂再批改。

## 输入

- 优先读取 `lessons/YYYY-MM-DD/essay-draft.md`(手写作文的打字稿)
- 用户直接粘贴作文文本 → 先存为当节课的 `essay-draft.md`(日期 = 本次上课日或用户指定;不确定时询问)
- canonical 范例:`lessons/2026-09-09/essay-feedback.md`

## 输出

同文件夹 `lessons/YYYY-MM-DD/essay-feedback.md`,结构如下:

```markdown
# 作文批改 · YYYY-MM-DD

> 主题:<对应 material 的一句话主题> | 作文目标:复述上节课内容,练 B2 表达

## 总评

- **内容覆盖:** 复述是否完整、逻辑是否连贯(2–3 句)
- **语言诊断:** 本篇最突出的 3 个问题类型(引用 mistakes.md 分类)
- **3 个亮点:** 值得保持的好表达/好结构
- **3 个优先修改:** 本篇最值得改的点,按影响排序

## 逐句纠错

| # | 原句(节选) | 修改 | 错误类型 | 讲解(一句话规则) |
|---|---|---|---|---|

(只列有错的句子;无误的长段不必逐句列出)

## 升级改写(B2 嵌套从句版)

整篇改写示范:在纠错基础上,把松散短句合并为带定语/状语从句的 B2 表达,
**加粗**新增的从句结构,让学员看到「同一种意思如何说得更高级」。

## 表达积累

本篇语境下可复用的 3–5 个句式(建议同步到本课 `vocab.md` 的「来源=作文」)

## 课堂补充

(预留区:上完课后,把老师课堂批改中 AI 没覆盖到的指正追加在这里,
格式:`- [原句] → [老师的版本] (要领)`)
```

## 错误类型分类法(与 vocabulary/mistakes.md 对齐)

| 类型 | 典型例子 |
|---|---|
| 主谓一致 | The candidate give → gives;the interviewers is → is |
| 冠词 | with sharding strategy → with **a** sharding strategy |
| 动词形式 | wants know → wants **to** know;is talk about → talks about |
| 固定搭配 | at the meantime → meanwhile;in another words → in other words |
| 从句与连接 | 逗号连接两个独立句(comma splice);situation that → situation where |
| 时态 | 泛指事实误用 could/would;chose/chosen 混淆 |
| 用词 | replications → replicas;receive the position → reach the position |
| 其他 | 拼写、语序等 |

## 更新 vocabulary/mistakes.md

每次批改后同步更新错误本:

1. **错误日志表**追加本篇所有错误行:`| 日期 | 原句 | 改正 | 错误类型 | 一句话规则 |`
2. **高频错误排行**重新计数排序(Top 5)
3. 同一模式的重复错误**每次都记录**(次数是刻意练习的依据),但举例可只留最近 1–2 条
4. 若发现分类法外的新错误类型,先扩充分类法再记录

## 收尾

1. 更新 `dashboard.md` 课程日志:该日期行勾选「作文 ✓」「批改 ✓」,并刷新「薄弱点 Top」
2. 提醒用户:带着 `essay-feedback.md` 去上课,老师的额外指正课后补进「课堂补充」区
