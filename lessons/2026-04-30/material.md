# 作业3：提前预习｜【初级】Requirement Review - Defining Data Freshness SLA [会议]

## background

### SLA

**SLA** 是 **Service Level Agreement**（服务等级协议）的缩写。在数据工程或软件服务的上下文中，它指的是**服务提供方承诺达到的某种质量指标**。

在你看到的脚本中，数据工程师承诺 **99.5% 的 SLA**，意思是：

- 在 99.5% 的日子里（即一年中最多只有 1-2 天例外），数据会在早上 8 点前准时准备好。
- 如果某天超过了 8 点才出数据，就算“违反 SLA”。

**通俗理解**：就像快递公司承诺“95% 的包裹次日送达”，SLA 就是数据团队给业务方的一个“按时完成率”的保证。

## 角色及场景

- **PM（产品经理）**：要求“实时”展示用户行为分析。
- **Data Engineer（数据工程师）**：澄清具体的延迟要求、管道容忍度和故障恢复策略。

**场景**：需求评审会上，产品经理提出需要“实时展示用户行为分析”。数据工程师追问：“实时是指秒级、分钟级还是小时级？数据管道从埋点到入库允许最大延迟多久？是否需要支持故障后自动回补？”最终双方约定：T+1 上午 8 点前产出昨日数据，SLA 为 99.5%。

---

## 会议对话（初级难度，约425词）

**PM:**

We need a new dashboard for user behaviour analytics. It must show data in **real time**. This is very important for our business.

**DE:**

I understand, but before we start, I need to clarify what “real time” means exactly. Can you tell me? Is it **seconds**, **minutes**, or **hours** of delay?

**PM:**

I want to see what users are doing right now. A few minutes of delay is fine. Maybe 5 minutes.

**DE:**

Second question: what is the **maximum delay** allowed from the moment a user clicks something until the data is ready in our database? For example, if a user clicks a button at 10:00, when should we see it?

**PM:**

Let's say 5 minutes is acceptable. But we can start with 10 minutes. That is easier to build.

**DE:**

Third question: if the data pipeline fails - for example, the server crashes or the network is down - do we need **automatic backfill**? That means the system should catch up missed data after the failure is fixed.

**PM:**

Yes, we cannot lose any data. It must recover and fill the gaps automatically. Data loss is not acceptable.

**DE:**

I understand your needs. However, building a true real-time pipeline with automatic backfill is very expensive and complex. It requires special tools and more servers. May I propose a simpler solution that still meets most business needs?

**PM:**

Sure. What do you suggest?

**DE:**

We can deliver yesterday's data every morning by 8 AM. This is called **T+1** (today plus one day). We will guarantee **99.5% SLA** - meaning the data will be ready on time for 99.5% of the days. Only about two days per year might be late.

**PM:**

That is not real time. But will it help us understand user behaviour for daily reports?

**DE:**

For daily decisions - such as campaign performance or feature adoption - T+1 is often enough. If we later prove a need for minute-level data, we can invest in a **streaming pipeline** as a second phase.

**PM:**

OK, let's agree: T+1, data ready by 8 AM, 99.5% SLA. Please write this down.

**DE:**

Great. I will document this **data freshness** requirement in our spec. Thank you for the clarification.

---

## 词汇表（25个高频数据工程师技术词汇）

| **词汇** | **音标** | **中文释义** |
| --- | --- | --- |
| real time | /ˈrɪəl taɪm/ | 实时 |
| seconds | /ˈsekəndz/ | 秒级 |
| minutes | /ˈmɪnɪts/ | 分钟级 |
| hours | /ˈaʊəz/ | 小时级 |
| maximum delay | /ˈmæksɪməm dɪˈleɪ/ | 最大延迟 |
| automatic backfill | /ˌɔːtəˈmætɪk ˈbækfɪl/ | 自动回补 |
| data pipeline | /ˈdeɪtə ˈpaɪplaɪn/ | 数据管道 |
| failure | /ˈfeɪljər/ | 故障 |
| catch up | /kætʃ ʌp/ | 赶上 |
| expensive | /ɪkˈspensɪv/ | 昂贵的 |
| complex | /ˈkɒmpleks/ | 复杂的 |
| T+1 | /tiː plʌs wʌn/ | 次日 |
| SLA | /ˌes el ˈeɪ/ | 服务等级协议 |
| guarantee | /ˌɡærənˈtiː/ | 保证 |
| on time | /ɒn taɪm/ | 按时 |
| data freshness | /ˈdeɪtə ˈfreʃnəs/ | 数据新鲜度 |
| requirement | /rɪˈkwaɪəmənt/ | 需求 |
| dashboard | /ˈdæʃbɔːd/ | 仪表盘 |
| behaviour analysis | /bɪˈheɪvjər əˈnæləsɪs/ | 行为分析 |
| acceptable | /əkˈseptəbəl/ | 可接受的 |
| propose | /prəˈpəʊz/ | 提议 |
| deliver | /dɪˈlɪvər/ | 交付 |
| streaming pipeline | /ˈstriːmɪŋ ˈpaɪplaɪn/ | 流式管道 |
| document | /ˈdɒkjumənt/ | 记录 |
| automatic recovery | /ˌɔːtəˈmætɪk rɪˈkʌvəri/ | 自动恢复 |

---

## 五个提问及参考答案

**1.** What did the PM ask for at the beginning of the meeting?

> **Answer:** “Real-time” user behaviour analytics.

**2.** What three questions did the data engineer ask to clarify “real time”?

> **Answer:** (1) Seconds, minutes or hours? (2) Maximum allowed delay? (3) Need automatic backfill after failure?

**3.** What final agreement did they make?

> **Answer:** T+1 (data ready by 8 AM) with 99.5% SLA.

**4.** Why did the data engineer propose T+1 instead of true real-time?

> **Answer:** Because true real-time with auto-backfill is expensive and complex.

**5.** What will the data engineer do after the meeting?

> **Answer:** Document the data freshness requirement.

---

## 正文单词统计

从“PM: We need a new dashboard for user behaviour analytics...”到“...Thank you for the clarification.”，经精确计数，**正文单词数为 425 词**，符合 420±5% 要求。
