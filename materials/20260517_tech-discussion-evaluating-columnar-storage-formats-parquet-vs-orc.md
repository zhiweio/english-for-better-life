# 作业3：预习｜【中级】Tech Discussion – Evaluating Columnar Storage Formats – Parquet vs ORC [会议]

## background

## 角色及场景

- **Zhou (数据工程师 - 小周)**：对比 Parquet 和 ORC 的存储格式特性，根据团队技术栈和数据类型做出选择。
- **Tech Lead (技术负责人)**：参与讨论并确认最终方案。

**场景**：技术方案评审中，小周对比 Parquet 和 ORC：Parquet 在 Spark 下的谓词下推更高效，ORC 在 Hive 下的 ACID 支持更好。考虑到团队主要使用 Spark 做批处理，且数据以宽表为主，最终选定 Parquet 格式，并启用 ZSTD 压缩，存储成本降低 30%。

---

## 对话脚本（中级，正文约 424 词）

Tech Lead:

We need to standardise the storage format for our data lake. What do you recommend between Parquet and ORC?

Zhou:

Both are columnar formats with good compression and predicate pushdown. However, they have different strengths depending on the execution engine and use case.

Tech Lead:

Start with Parquet.

Zhou:

Parquet is the default format for Spark. It implements predicate pushdown very efficiently - Spark can skip entire row groups that don't match the filter condition. This significantly reduces I/O for selective queries. Parquet also handles wide tables (many columns) well because you only read the columns needed.

Tech Lead:

What about ORC?

Zhou:

ORC also supports predicate pushdown, but its main advantage is ACID transaction support in Hive. With ORC, Hive can perform `INSERT`, `UPDATE`, and `DELETE` operations while maintaining consistency. Parquet does not have built-in ACID in Hive.

Tech Lead:

Do we need ACID capabilities?

Zhou:

Our workloads are predominantly batch reads and append-only writes. We rarely update or delete individual rows. So ACID is not a critical requirement for us.

Tech Lead:

What is our primary processing engine?

Zhou:

We use Spark for almost all ETL jobs. We also store wide fact tables with dozens of columns, and our queries often filter on a subset of columns.

Tech Lead:

That suggests Parquet is a better fit.

Zhou:

Exactly. Parquet's predicate pushdown is more mature in Spark, and it's the community standard for Spark-based data lakes. ORC would be a stronger candidate if we heavily used Hive, but that's not our case.

Tech Lead:

What about compression and storage costs?

Zhou:

We can enable ZSTD (Zstandard) compression, which offers a better compression ratio than Snappy or Gzip while maintaining good decompression speed. With ZSTD, we can reduce storage costs by about 30% compared to Snappy.

Tech Lead:

That's significant. Let's adopt Parquet with ZSTD compression.

Zhou:

Agreed. I will update the data ingestion specs. All new tables will be created as Parquet, partitioned by date, with ZSTD compression. We will also gradually migrate existing tables to this format.

Tech Lead:

Make sure to document the compression settings and partition strategy together.

Zhou:

Will do. The combination of partitioning, columnar storage, and high-ratio compression will give us fast queries and lower storage bills.

---

### 词汇表（25 个高频数据工程技术词汇）

| **Word** | **Phonetic** | **Meaning** |
| --- | --- | --- |
| columnar format | /kəˈlʌmnər ˈfɔːmæt/ | 列式格式 |
| predicate pushdown | /ˈpredɪkət ˈpʊʃdaʊn/ | 谓词下推 |
| execution engine | /ˌeksɪˈkjuːʃən ˈendʒɪn/ | 执行引擎 |
| row group | /rəʊ ɡruːp/ | 行组 |
| I/O | /aɪ əʊ/ | 输入/输出 |
| selective query | /sɪˈlektɪv ˈkwɪəri/ | 选择查询 |
| wide table | /waɪd ˈteɪbəl/ | 宽表 |
| ACID transaction | /ˈæsɪd trænˈzækʃən/ | ACID 事务 |
| batch read | /bætʃ riːd/ | 批量读取 |
| append-only | /əˈpend ˈəʊnli/ | 只追加的 |
| fact table | /fækt ˈteɪbəl/ | 事实表 |
| community standard | /kəˈmjuːnəti ˈstændəd/ | 社区标准 |
| compression ratio | /kəmˈpreʃən ˈreɪʃiəʊ/ | 压缩比 |
| ZSTD (Zstandard) | /ˈzɛd ˈstændəd/ | Zstandard 压缩 |
| Snappy | /ˈsnæpi/ | Snappy 压缩 |
| Gzip | /ˈdʒiː zɪp/ | Gzip 压缩 |
| decompression speed | /ˌdiːkəmˈpreʃən spiːd/ | 解压速度 |
| storage cost | /ˈstɔːrɪdʒ kɒst/ | 存储成本 |
| data ingestion | /ˈdeɪtə ɪnˈdʒestʃən/ | 数据接入 |
| partition by date | /pɑːˈtɪʃən baɪ deɪt/ | 按日期分区 |
| migration | /maɪˈɡreɪʃən/ | 迁移 |
| compression setting | /kəmˈpreʃən ˈsetɪŋ/ | 压缩设置 |
| data lake | /ˈdeɪtə leɪk/ | 数据湖 |
| default format | /dɪˈfɔːlt ˈfɔːmæt/ | 默认格式 |
| standardise | /ˈstændədaɪz/ | 标准化 |

---

### 五个提问及参考答案

**1. What are the two columnar storage formats compared in the discussion?**

-> Parquet and ORC.

**2. Which format has better predicate pushdown efficiency in Spark?**

-> Parquet.

**3. Which format provides ACID transaction support in Hive?**

-> ORC.

**4. Why did the team choose Parquet over ORC?**

-> Because they primarily use Spark for batch processing and wide tables, and ACID transactions are not a requirement.

**5. What compression format did they enable, and what storage cost reduction did they achieve?**

-> ZSTD compression; they achieved about 30% storage cost reduction compared to Snappy.

### 一、表达"适应、习惯"

**get used to + 名词/动词ing** — 强调从不习惯到习惯的过程

- I'm still getting used to the new codebase. (我还在适应新代码库)
- She is getting used to the early morning meetings. (她正逐渐适应早晨的会议)
- It took me a few weeks to get used to working from home. (花了我几周时间才适应居家办公)
- We're getting used to the new project management tool. (我们正在适应新的项目管理工具)

**be used to + 名词/动词ing** — 强调已经习惯了的状态

- I'm used to working remotely. (我已习惯远程工作)
- Are you used to the pressure in this job? (你已经习惯这份工作的压力了吗？)
- She's used to presenting in front of large audiences. (她已经习惯在大众面前演讲)
- Most developers are used to code reviews. (大多数开发者已习惯代码审查)

**used to + 动词原形** — 过去常做，现在不做了

- We used to deploy manually, but now we have CI/CD. (我们过去手动部署，现在有 CI/CD 了)
- I used to write everything in Python; now I'm learning Go. (我过去用 Python 写一切，现在在学 Go)
- They used to have daily standup meetings, but now it's twice a week. (他们过去每天站会，现在改成一周两次)

---

### 二、表达"开始、着手、参与"

**kick off** — 启动（项目/会议）

- We'll kick off the sprint with a planning meeting. (我们将以计划会议启动冲刺)
- Tomorrow we kick off the migration project. (明天我们启动迁移项目)
- Let's kick off the presentation with a quick demo. (让我们以快速演示开始演讲)
- The conference will kick off at 9 AM with the keynote speech. (大会将在 9 点以主题演讲开始)

**dive into** — 深入进去（暗示投入）

- Tomorrow I'll dive into the refactoring. (明天我将深入进行重构)
- She dove into the code and found the bug within an hour. (她深入代码，一小时内找到了 bug)
- Let's dive into the requirements document. (让我们深入阅读需求文档)
- I'm excited to dive into this new technology. (我很兴奋能深入学习这项新技术)

**get involved in** — 参与进去

- I'd like to get more involved in architecture decisions. (我想参与更多的架构决策)
- Everyone should get involved in the code review process. (每个人都应参与代码审查流程)
- Would you like to get involved in the mentorship program? (你想参与导师项目吗？)

**get started** — 开始动手做

- Let's get started on the migration plan. (让我们开始制定迁移计划)
- When can you get started on the documentation? (你什么时候能开始写文档？)
- I want to get started as soon as possible. (我想尽快开始)

**jump into** — 快速加入/开始

- Feel free to jump into the discussion. (尽管加入讨论)
- He jumped into the project without reading the requirements. (他没读需求就匆忙开始项目)
- Don't jump into coding before understanding the problem. (在理解问题前别匆忙编码)

---

### 三、表达"搞清楚、解决、处理"

**work out** — 解决、算出、事情有结果

- We still haven't worked out a solution for the performance issue. (我们还没想出性能问题的解决方案)
- It will work out in the end. (最后都会好的)
- Let's work out the details in the next meeting. (让我们在下次会议上敲定细节)
- The team worked out a compromise that satisfied everyone. (团队想出了一个让所有人满意的折中方案)

**sort out** — 理清、整理、解决（混乱）

- Let's sort out the merge conflicts first. (让我们先整理合并冲突)
- We need to sort out the team structure before the project starts. (项目启动前我们要理清团队结构)
- Have you sorted out your calendar for tomorrow? (你整理好明天的日程了吗？)

**point out** — 指出、点名

- Thanks for pointing out the security risk. (谢谢你指出安全隐患)
- He pointed out that we missed an important requirement. (他指出我们遗漏了一个重要需求)
- Can you point out where the error occurs? (你能指出错误发生的位置吗？)

**deal with** — 处理（常指麻烦事）

- I'll deal with that bug after lunch. (午餐后我来处理那个 bug)
- How do we deal with the increased load? (我们如何应对增加的负载？)
- She deals with customer complaints all day. (她整天处理客户投诉)

**end up + 动词ing** — 最终（意外）到了某一步

- I ended up rewriting the whole module. (我最后重写了整个模块)
- If we don't plan carefully, we'll end up missing the deadline. (如果我们不仔细计划，最终会错过截止日期)
- He ended up staying until midnight to fix the issue. (他最后一直留到午夜来修复问题)

**look into** — 调查、查看

- Could you look into the error logs? (你能看一下错误日志吗？)
- I'll look into that tomorrow. (我明天会查看这个)
- The team is looking into why the test failed. (团队在调查测试为何失败)

**figure out** — 想通、搞明白、算出来

- I need to figure out why the API returns 500. (我需要搞明白为什么 API 返回 500)
- Did you figure out the bug? (你搞明白 bug 了吗？)
- Let's figure out the best approach together. (让我们一起想出最佳方案)

**find out** — 查明、发现（事实）

- We need to find out when the outage started. (我们需要查明故障何时开始的)
- I found out that the server ran out of disk space. (我发现服务器磁盘空间已满)
- Have you found out who made that change? (你查明谁做的那个改动吗？)

---

### 四、表达"产生、想出、提出"

**come up with** — 想出（办法/方案）

- Who came up with this architecture? (谁想出的这个架构？)
- We need to come up with a solution by Friday. (我们需要在周五前想出一个解决方案)
- She came up with a creative way to optimize the query. (她想出了一个创意的方式来优化查询)

**bring up** — 提出（议题/问题）

- I'll bring that up in the next stand-up. (我将在下次站会提起这个)
- Can we bring up the budget discussion later? (我们能稍后再讨论预算吗？)
- Don't bring up politics in the meeting. (不要在会议上提起政治话题)

**think through** — 彻底想清楚

- We need to think through the error-handling logic. (我们需要彻底想清楚错误处理逻辑)
- Have you thought through the implications? (你仔细考虑过后果了吗？)
- Let's think through this decision one more time. (让我们再彻底想一遍这个决定)

**bring in** — 拉入(会议/讨论)

- I'll bring in the PM to discuss the PRD. (我会把项目经理拉进来讨论需求文档)
- We should bring in the security team for this discussion. (我们应该把安全团队拉进这个讨论)

**run out of** — 用完、耗尽

- We're running out of disk space on the server. (我们的服务器磁盘空间快要用完了)
- We're running out of time. (我们快没时间了)
- If we don't act now, we'll run out of budget. (如果我们现在不采取行动，预算就会用完)

---

### 五、表达"推进、继续、坚持"

**go ahead** — 继续、开始吧（征求许可或推动）

- Can I go ahead and merge this PR? (我可以继续合并这个 PR 吗？)
- Go ahead with the deployment. (继续部署)
- Please go ahead and schedule the meeting. (请继续安排会议)

**move on to** — 进入下一项

- Let's move on to the testing phase. (让我们进入测试阶段)
- Can we move on to the next agenda item? (我们可以进入下一个议题吗？)
- Once this is done, we'll move on to optimization. (完成这个后，我们将进入优化阶段)

**stick with** — 坚持用/不放弃

- Let's stick with PostgreSQL for now. (现在让我们继续坚持使用 PostgreSQL)
- I think we should stick with this approach. (我认为我们应该坚持这个方法)
- Stick with it; you'll improve with practice. (坚持下去，你会随着练习而进步)

**keep up with** — 跟上（进度/技术）

- I'm trying to keep up with the latest frontend trends. (我在努力跟上最新的前端趋势)
- It's hard to keep up with all the meetings. (很难跟上所有的会议)
- Can the team keep up with this pace? (团队能跟上这个速度吗？)

**catch up with** — 补上、追上

- I need to catch up with what the team discussed yesterday. (我需要了解团队昨天讨论了什么)
- I'll catch up with you after the meeting. (会议后我来和你聊一下)
- Let's catch up over coffee. (让我们约咖啡聊天)

**push forward (with)** — 推进（克服困难）

- We'll push forward with the release despite the delay. (尽管延迟，我们将继续推进发布)
- Let's push forward and fix the remaining issues. (让我们继续推进并修复剩余问题)
- We need to push forward to meet the deadline. (我们需要推进以赶上截止日期)

---

### 六、表达"沟通、一致、确认"

**get back to sb** — 回复某人

- I'll get back to you after I check the data. (我检查完数据后会回复你)
- Can you get back to me by EOD? (你能在下班前回复我吗？)
- She got back to me with the answers I needed. (她用我需要的答案回复了我)

**check in with sb** — 与某人碰头确认

- I'll check in with the DevOps team. (我会和 DevOps 团队碰头)
- Let's check in weekly to see how it's going. (让我们每周碰头看看进展)
- Can you check in with the client about the timeline? (你能和客户确认一下时间表吗？)

**follow up** — 跟进

- I'll follow up on the feedback. (我会跟进反馈)
- Let's follow up on the action items from last meeting. (让我们跟进上次会议的行动项)
- I need to follow up with the bug fix. (我需要跟进 bug 修复)

**make sure** — 确保、弄清楚

- Always make sure the tests pass before pushing. (推送前一定要确保测试通过)
- Make sure everyone has the right permissions. (确保每个人都有正确的权限)
- Can you make sure the documentation is up to date? (你能确保文档是最新的吗？)

**keep sb posted** — 随时通知某人

- Keep me posted on the deployment status. (随时告诉我部署状态)
- I'll keep you posted about the meeting results. (我会随时告诉你会议结果)
- Please keep the team posted on any changes. (请随时告诉团队任何变化)

**on the same page** — 共识、理解一致

- Let's make sure we're all on the same page about the scope. (让我们确保在范围上的理解一致)
- Are we on the same page about the deadline? (我们对截止日期的理解一致吗？)
- I want to make sure we're on the same page before we start. (开始前我想确保我们的理解一致)

---

### 七、表达"延迟、取消、暂停"

**put off** — 推迟

- The demo was put off until Friday. (演示被推迟到了周五)
- We can't keep putting off the decision. (我们不能继续推迟这个决定)
- The meeting was put off by a week. (会议推迟了一周)

**hold off** — 暂缓、先别做

- We should hold off on refactoring until after the launch. (我们应该在发布后再进行重构)
- Let's hold off on making that change for now. (现在让我们先暂缓做这个改动)
- Can you hold off on sending that email? (你能先暂缓发送那封邮件吗？)

**hold on** — 等一下（电话/对话中）

- Hold on, I'm checking the log now. (等一下，我现在在查看日志)
- Hold on, let me find the file. (等一下，让我找一下文件)
- Hold on, someone is at the door. (等一下，有人在敲门)

**call off** — 取消

- They called off the meeting due to the incident. (由于事件，他们取消了会议)
- Should we call off the deployment? (我们应该取消部署吗？)
- The event was called off because of bad weather. (由于天气原因，活动被取消了)

**give up** — 放弃

- I'm not giving up on this approach yet. (我还没放弃这个方法)
- Don't give up; we're close to solving it. (别放弃，我们快要解决了)
- Never give up on improving your skills. (永远别放弃提高自己的技能)

**break down** — 拆分；或（系统）崩溃

- Let's break down the task into subtasks. (让我们把任务拆分成小任务)
- The build broke down again this morning. (今天早上构建又崩溃了)
- Can you break down the requirements for me? (你能给我拆解一下需求吗？)

---

### 八、表达"出现、发生、结果是"

**turn out** — 结果证明是

- The error turned out to be a missing environment variable. (结果这个错误是缺少一个环境变量)
- It turned out that we had the wrong version of the library. (结果我们有错误版本的库)
- The project turned out better than expected. (项目最终比预期好)

**show up** — 出现、露面

- The bug decided to show up only in production. (这个 bug 只在生产环境出现了)
- Half the team didn't show up for the meeting. (有一半的团队成员没有出席会议)
- The issue doesn't show up in the test environment. (这个问题在测试环境中没有出现)

**come up** — 出现（话题/问题）

- Something urgent has come up, I need to drop off. (突然出现了一些紧急事情，我需要离开)
- A new issue came up during testing. (测试过程中出现了一个新问题)
- The topic of migration came up in the meeting. (在会议中提到了迁移的话题)

---

### 九、表达"依赖、基于、根据"

**depend on** — 依赖

- That approach depends on the microservice being stable. (那个方法依赖于微服务的稳定性)
- The success of the project depends on good planning. (项目的成功取决于好的计划)
- It depends on the requirements. (这取决于需求)

**rely on** — 依靠（信任）

- We rely on Redis for session storage. (我们依靠 Redis 来存储会话)
- The system relies on a stable internet connection. (系统依靠稳定的网络连接)
- I rely on the team to deliver on time. (我相信团队会按时交付)

**based on** — 基于

- The decision is based on the performance test results. (这个决定是基于性能测试结果)
- This recommendation is based on industry best practices. (这个建议是基于行业最佳实践)
- Based on your feedback, we'll make changes. (基于你的反馈，我们会做出改变)

**take into account/consideration** — 考虑到

- You need to take latency into account. (你需要考虑延迟)
- We should take the cost into consideration. (我们应该考虑成本)
- Have you taken security into account in your design? (你在设计中考虑了安全性吗？)

**lead to sth** — 导致sth

- A small misconfiguration can lead to major data loss. (一个小的错误配置可能导致重大数据丢失)
- Poor planning leads to missed deadlines. (计划不周会导致错过截止日期)
- This change will lead to better performance. (这个改动会导致性能提升)
