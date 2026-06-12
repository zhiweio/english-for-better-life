# 作业5：提前预习｜【中级】Technical Investigation - Assessing AI-Driven Data Quality Tools [会议]

## Background

### 文章技术干点

这篇对话围绕"如何用自动化工具解决数据质量问题"展开，从传统规则引擎的局限性，到 AI 驱动的智能发现，最终推导出一套"AI 探索 + 规则引擎执行"的混合架构。

**Deequ** 是 Amazon 开源的一个基于 Apache Spark 的数据质量验证库。它允许用声明式方式定义质量检查（如 `amount >= 0`、`order_id is not null`），可靠且可版本化管理，但每条规则都需人工手写，只能校验已知问题。

**AI 驱动的数据质量平台**能自动发现规则——通过数据画像（Profiling）、统计分布分析、异常检测，自主推荐验证规则并附上置信度分数。

**混合架构**：AI 在离线环境探索未知问题生成候选规则，经过人工审核后，将稳定的规则固化为 Deequ 校验嵌入生产 ETL 管线。

---

## 角色及场景

- **Li（数据工程师 - 小李）**：调研并演示 AI 数据质量工具，展示其自动异常发现与规则生成能力。
- **Zhang（技术负责人）**：主持讨论，决策工具选型与落地路径。

**场景**：会议。数据工程师小李汇报数据质量工具调研结果：开源 Deequ 需手动编写规则，前期成本高；而集成 LLM 的 AI 平台能自动分析数据分布并推荐异常检测规则。小李用历史订单表演示 AI 工具自动发现"金额为负"的隐藏问题并生成校验 SQL。团队最终决定先用 AI 平台快速探索未知问题，成熟规则再沉淀到 Deequ 中。

---

## 对话脚本（中级，正文约 448 词）

**Zhang:**

We've been seeing data quality issues slip into production. Li, what did you find for automated quality tooling?

**Li:**

I compared two approaches. On one side, we have **Deequ** — an open-source library that allows us to define declarative quality checks on top of Spark DataFrames. It's solid and integrates well with our existing pipeline. The downside is that every constraint like `amount >= 0` or `order_id is not null` must be hand-coded. That's time-consuming, and we can only enforce rules we've already thought of.

**Zhang:**

So we'd still be playing catch-up with unknown issues.

**Li:**

Exactly. That's why I also evaluated an AI-powered data quality platform — similar to Great Expectations but with a built-in LLM. You point it at a sample table, and it automatically profiles the data distribution, detects statistical anomalies, and recommends validation rules. I ran a quick spike on our historical order table, and within minutes it flagged negative values in the `order_amount` column — something our existing checks had never caught.

**Zhang:**

Negative amounts? That's a serious data integrity issue.

**Li:**

Yes, and the AI tool didn't just flag the anomaly — it also generated a validation SQL snippet like `SELECT * FROM orders WHERE amount < 0`, and gave each recommended rule a confidence score.

**Zhang:**

A confidence score? How reliable are these AI recommendations?

**Li:**

The score is based on how far the data deviates from the expected distribution. High-scoring rules are usually solid, but some can be noisy. The false-positive rate is around 5% to 10%, so manual review is still necessary before promoting a rule to production.

**Zhang:**

So what do you recommend as the final approach?

**Li:**

A hybrid approach. Use the AI tool in an offline discovery phase — it scans historical snapshots, finds hidden problems, and builds a candidate rule catalog. After human review, the stable rules get hardcoded into Deequ for production enforcement.

**Zhang:**

AI as the detective and Deequ as the guard?

**Li:**

Exactly. AI finds unknown problems fast, and Deequ ensures reliable execution. We can also integrate the final Deequ checks into our CI pipeline. That way, every ETL run triggers automated quality gates.

**Zhang:**

I like this path. What's the next step?

**Li:**

I'll set up the AI tool on a snapshot of our order table, generate a candidate rule catalog, and review the top anomalies with the analytics team. After that, we can start hardening the confirmed rules into Deequ checks.

**Zhang:**

Good. Let's proceed with this phased approach. Please document every rule with its coverage, false-positive rate, and business justification.

**Li:**

Agreed. By the end of next sprint, we should have a solid rule catalog running in production.

---

## 词汇表（25 个高频数据工程技术词汇）

| **Word** | **Phonetic** | **Meaning** |
| --- | --- | --- |
| data quality | /ˈdeɪtə ˈkwɒləti/ | 数据质量 |
| anomaly detection | /əˈnɒməli dɪˈtekʃən/ | 异常检测 |
| declarative check | /dɪˈklærətɪv tʃek/ | 声明式检查 |
| constraint | /kənˈstreɪnt/ | 约束 |
| Deequ | /diːk/ | 开源数据质量库 |
| Great Expectations | /ɡreɪt ˌekspekˈteɪʃənz/ | 数据质量框架 |
| LLM | /ˌel el ˈem/ | 大语言模型 |
| data profiling | /ˈdeɪtə ˈproʊfaɪlɪŋ/ | 数据画像 |
| statistical distribution | /stəˈtɪstɪkəl ˌdɪstrɪˈbjuːʃən/ | 统计分布 |
| validation rule | /ˌvælɪˈdeɪʃən ruːl/ | 校验规则 |
| confidence score | /ˈkɒnfɪdəns skɔːr/ | 置信度评分 |
| false-positive rate | /fɔːls ˈpɒzətɪv reɪt/ | 误报率 |
| data integrity | /ˈdeɪtə ɪnˈteɡrəti/ | 数据完整性 |
| SQL snippet | /ˌes kjuː ˈel ˈsnɪpɪt/ | SQL 代码片段 |
| ETL pipeline | /ˌiː tiː ˈel ˈpaɪplaɪn/ | ETL 管道 |
| production-ready | /prəˈdʌkʃən ˈredi/ | 可投产的 |
| hybrid approach | /ˈhaɪbrɪd əˈproʊtʃ/ | 混合方案 |
| CI pipeline | /ˌsiː ˈaɪ ˈpaɪplaɪn/ | 持续集成管道 |
| manual review | /ˈmænjuəl rɪˈvjuː/ | 人工审核 |
| coverage | /ˈkʌvərɪdʒ/ | 覆盖率 |
| rule catalog | /ruːl ˈkætəlɒɡ/ | 规则目录 |
| data owner | /ˈdeɪtə ˈoʊnər/ | 数据负责人 |
| automation | /ˌɔːtəˈmeɪʃən/ | 自动化 |
| statistical anomaly | /stəˈtɪstɪkəl əˈnɒməli/ | 统计异常 |
| quality gate | /ˈkwɒləti ɡeɪt/ | 质量门禁 |

---

## 五个提问及参考答案

**1. What are the main limitations of using Deequ alone for data quality according to Li?**

> **Answer:** Deequ requires manually writing every constraint, which is time-consuming and only covers issues the team already knows about.

**2. How did the AI-powered tool help Li discover a hidden data problem?**

> **Answer:** It automatically profiled the order table, detected negative values in the `order_amount` column, flagged the anomaly, and generated a validation SQL snippet with a confidence score.

**3. Why does Li not recommend relying solely on AI-generated rules in production?**

> **Answer:** Some AI-recommended rules can be noisy or context-blind, with a false-positive rate of 5% to 10%, so they need human review before becoming permanent checks.

**4. What is the hybrid approach the team decides to adopt?**

> **Answer:** Use the AI tool in a discovery phase to find unknown anomalies and suggest rules, then implement the stable and reviewed rules in Deequ for production enforcement.

**5. What will Li do in the next step after the meeting?**

> **Answer:** Set up the AI tool on a snapshot of the order table, generate a candidate rule catalog, and review the top anomalies with the analytics team.

---

## 正文单词统计

- **对话脚本正文自然语言单词数：448 词**（不含角色标签，逐词计数）
- **偏差：-0.4%**（符合 450±5% 要求）

## 难度自评

- **等级：中级**
- **理由**：对话围绕数据工程师技术调研展开，涵盖了数据质量工具选型、AI 辅助分析与人工审查的权衡，使用了如 profiling、anomaly detection、constraint、validation rule、false-positive rate 等专业术语。句子逻辑清晰，适合 B1-B2 学员在数据工程会议场景中练习专业英语表达。
