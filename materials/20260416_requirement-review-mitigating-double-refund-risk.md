# 【中级】Requirement Review - Mitigating Double Refund Risk

## 角色及场景

- **PM（产品经理）**：提出订单超时后自动取消并退款的业务需求。
- **Backend Dev（后端开发）**：识别技术风险，建议先增加幂等性设计。

**场景**：需求评审会上，产品经理介绍了自动退款功能。后端开发指出当前系统缺乏幂等性保护，存在重复退款的风险，并建议先实现分布式锁和状态机校验。产品经理认同该方案，决定将需求拆分为两个迭代：先完成防重机制，再上线自动退款功能。

---

## 对话脚本（中级难度）

**PM:**

Today we review the auto-refund requirement. When a paid order times out without confirmation, the system will automatically **cancel** the order and trigger a **refund** to the user.

**Backend Dev:**

I see a **technical risk**. Our current payment **callback** handler has no **idempotency** control. If the refund API gets called twice - for example, due to a network **retry** - the user would receive a **double refund**. That would directly impact our **revenue** and user trust.

**PM:**

That sounds serious. What do you propose?

**Backend Dev:**

We need to introduce a **distributed lock** before processing any refund. The lock will ensure only one **thread** can execute the refund for a given order. Additionally, we should implement a **state machine** for the order lifecycle: `PAID -> CANCELLING -> REFUNDED`. The state machine will **reject** any duplicate transition.

**PM:**

How much extra **effort** are we looking at?

**Backend Dev:**

The lock and state machine will take about two days, including **unit tests** and **integration** with our existing **order service**. The auto-refund logic itself will take one more day.

**PM:**

Okay, let's **split** this requirement into two **iterations**. Iteration one: implement the distributed lock and state machine - deploy them without enabling auto-refund. Iteration two: add the auto-refund trigger and monitor it on a small **percentage** of traffic first.

**Backend Dev:**

Agreed. I will also add **metrics** to track lock **contention** and state transition **failures**. That will help us validate the solution before full rollout.

**PM:**

Great. I will update the **PRD** and mark the first iteration as **high priority**. Let's aim to complete iteration one by the end of next sprint.

**Backend Dev:**

Sounds good. This upfront investment will save us from **production incidents** later.

---

## 词汇表（25个高频技术词汇）

| **词汇** | **音标** | **中文释义** |
| -------- | -------- | ------------ |
| cancel | /ˈkænsəl/ | 取消 |
| refund | /ˈriːfʌnd/ | 退款 |
| technical risk | /ˈteknɪkəl rɪsk/ | 技术风险 |
| callback handler | /ˈkɔːlbæk ˈhændlər/ | 回调处理器 |
| idempotency | /ˌaɪdəmˈpəʊtənsi/ | 幂等性 |
| retry | /ˈriːtraɪ/ | 重试 |
| double refund | /ˈdʌbəl ˈriːfʌnd/ | 重复退款 |
| revenue | /ˈrevənjuː/ | 收入 |
| distributed lock | /dɪˈstrɪbjuːtɪd lɒk/ | 分布式锁 |
| thread | /θred/ | 线程 |
| state machine | /steɪt məˈʃiːn/ | 状态机 |
| lifecycle | /ˈlaɪfsaɪkl/ | 生命周期 |
| reject | /rɪˈdʒekt/ | 拒绝 |
| effort | /ˈefət/ | 工作量 |
| unit tests | /ˈjuːnɪt tests/ | 单元测试 |
| integration | /ˌɪntɪˈɡreɪʃən/ | 集成 |
| order service | /ˈɔːdər ˈsɜːrvɪs/ | 订单服务 |
| split | /splɪt/ | 拆分 |
| iterations | /ˌɪtəˈreɪʃənz/ | 迭代 |
| percentage | /pərˈsentɪdʒ/ | 百分比 |
| metrics | /ˈmetrɪks/ | 度量指标 |
| contention | /kənˈtenʃən/ | 竞争 |
| failures | /ˈfeɪljərz/ | 失败 |
| PRD (Product Requirements Document) | /ˌpiː ɑːr ˈdiː/ | 产品需求文档 |
| high priority | /haɪ praɪˈɒrəti/ | 高优先级 |
| production incidents | /prəˈdʌkʃən ˈɪnsɪdənts/ | 生产事故 |

- ***What is the main technical risk of the auto-refund requirement?***

  参考答案：*Lack of idempotency control could cause double refund if the refund API is called twice.*

- ***What two mechanisms does the backend developer propose to prevent duplicate refunds?***

  参考答案：*A distributed lock and a state machine for the order lifecycle.*

- ***Why does the developer suggest splitting the requirement into two iterations?***

  参考答案：*To deploy the lock and state machine first without enabling auto-refund, validate them, then add the refund trigger later - reducing risk.*

- ***What will the developer add to monitor the new mechanisms?***

  参考答案：*Metrics to track lock contention and state transition failures.*

- ***What will the PM do after the meeting regarding the requirement?***

  参考答案：*Update the PRD and mark the first iteration as high priority.*
