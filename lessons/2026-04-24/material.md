# 【初级】Requirement Review - Defining "Daily Active Users" [会议]

## 角色及场景

- **Product Manager（产品经理）**：提出“日活用户”指标，需要数据团队支持。
- **Data Engineer（数据工程师）**：负责数据口径定义，追问具体规则。

**场景**：需求评审会上，产品经理提出需要统计“日活用户”作为核心指标。数据工程师追问三个关键定义：活跃行为（打开 App vs 登录）、时间窗口（自然日 vs 滚动 24 小时）、去重粒度（设备 ID vs 用户 ID）。双方最终达成一致。

---

## 会议对话（初级难度，约395词）

**PM:**

We need a new metric for the dashboard: **Daily Active Users**, or DAU.

**DE:**

I have a few questions to clarify the **definition**. First, what **counts as** an **active** user?

**PM:**

Good question. A user is active if they open the app.

**DE:**

Does that include users who just open and close quickly?

**PM:**

Yes, any app open counts.

**DE:**

Second question: what is the **time window** for “daily”? Do we use a **natural day** (midnight to midnight) or a **rolling 24 hours** (last 24 hours from now)?

**PM:**

Let's use natural day based on UTC. It is simpler for reporting.

**DE:**

Third question: how do we **deduplicate** users? Do we use **device ID** or **user ID**?

**PM:**

What is the difference?

**DE:**

Device ID is **tied to** a phone. One person with two phones would be counted twice. User ID is tied to a login account. One person with two phones would be counted once.

**PM:**

We want unique people, not devices. Use **user ID**. But **what if** a user is not logged in?

**DE:**

We can use device ID as a **fallback** for anonymous users. Then merge them later if they log in.

**PM:**

That sounds good. So final definition: active = opens app, time window = natural day (UTC), deduplication = user ID (with device ID as fallback).

**DE:**

I will write this **data specification** in our wiki. The team will use it to build the **ETL pipeline**.

**PM:**

Perfect. Let's move to the next requirement.

---

## 词汇表（25个高频数据工程师词汇）

| **词汇** | **音标** | **中文释义** |
| --- | --- | --- |
| Daily Active Users (DAU) | /ˈdeɪli ˈæktɪv ˈjuːzəz/ | 日活跃用户 |
| definition | /ˌdefɪˈnɪʃən/ | 定义 |
| active | /ˈæktɪv/ | 活跃的 |
| time window | /taɪm ˈwɪndəʊ/ | 时间窗口 |
| natural day | /ˈnætʃərəl deɪ/ | 自然日 |
| rolling 24 hours | /ˈrəʊlɪŋ ˌtwɛnti fɔːr ˈaʊəz/ | 滚动24小时 |
| deduplicate | /ˌdiːˈdjuːplɪkeɪt/ | 去重 |
| device ID | /dɪˈvaɪs aɪ diː/ | 设备ID |
| user ID | /ˈjuːzər aɪ diː/ | 用户ID |
| fallback | /ˈfɔːlbæk/ | 后备方案 |
| anonymous | /əˈnɒnɪməs/ | 匿名的 |
| data specification | /ˈdeɪtə ˌspesɪfɪˈkeɪʃən/ | 数据规范 |
| ETL pipeline | /ˌiː tiː ˈel ˈpaɪplaɪn/ | ETL流水线 |
| metric | /ˈmetrɪk/ | 指标 |
| dashboard | /ˈdæʃbɔːd/ | 仪表盘 |
| clarify | /ˈklærɪfaɪ/ | 澄清 |
| count | /kaʊnt/ | 计数 |
| report | /rɪˈpɔːt/ | 报告 |
| unique | /juːˈniːk/ | 唯一的 |
| merge | /mɜːdʒ/ | 合并 |
| log in | /lɒɡ ɪn/ | 登录 |
| app | /æp/ | 应用程序 |
| requirement | /rɪˈkwaɪəmənt/ | 需求 |
| wiki | /ˈwɪki/ | 维基文档 |
| build | /bɪld/ | 构建 |

- ***What three questions did the Data Engineer ask about DAU?***

  参考答案：*1) What counts as active? 2) What is the time window? 3) How to deduplicate (device ID or user ID)?*

- ***Why does the Data Engineer suggest using user ID instead of device ID for deduplication?***

  参考答案：*Because one person with two phones would be counted twice with device ID, but user ID counts unique people.*

- ***What does “fallback” mean when a user is not logged in?***

  参考答案：*Use device ID for anonymous users, then merge later if they log in.*

- ***What time window did the PM finally choose?***

  参考答案：*Natural day based on UTC.*

- ***What will the Data Engineer do after the meeting?***

  参考答案：*Write the data specification in the wiki for the ETL pipeline.*
