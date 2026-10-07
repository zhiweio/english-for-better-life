# 作文批改 · 2026-09-09

> 主题:分区面试——从读写分离到写扩展(为什么需要 Sharding) | 作文目标:复述上节课对话,练 B2 表达

## 总评

- **内容覆盖:** 复述完整,面试问答的推进结构清晰(读写分离的局限 → 垂直扩展为什么不行 → 分片策略选择 → partition pruning),逻辑链没有断
- **语言诊断:** 最突出的问题是**冠词缺失**(a/the/零冠词不分)和**主谓一致**(give/is/retrieve 少 s);另有几处固定搭配(at the meantime、in another words、such user_id)和逗号连接独立句
- **3 个亮点:** ① 段落按对话推进分段,结构感好;② "partition pruning" 等术语使用准确;③ 结尾有总结段
- **3 个优先修改:** ① 单数可数名词前加 a/the(sharding strategy → a sharding strategy);② 写完检查第三人称单数 s;③ 两个独立句不要用逗号硬连

## 逐句纠错

| # | 原句(节选) | 修改 | 错误类型 | 讲解 |
|---|---|---|---|---|
| 1 | This article is talking about improving write scalability with sharding strategy. | This article talks about improving write scalability with **a** sharding strategy. | 动词形式 + 冠词 | 描述文章内容用一般现在时;泛指单数可数名词加 a |
| 2 | agrees that read-write splitting strategy could significantly improve | agrees that **the** read-write splitting strategy **can** significantly improve | 冠词 + 时态 | 双方正在讨论的那个策略是特指;描述规律用现在时 |
| 3 | **at the meantime**, he notices | **Meanwhile**, he notices | 固定搭配 | 没有 at the meantime;句首用 Meanwhile 或 at the same time |
| 4 | write throughput is limited by **the single machine** | limited by **a single machine** | 冠词 | 泛指「任何一台单机」用 a |
| 5 | wants **know that why** master-slave replication could not achieve | wants **to know why** master-slave replication cannot achieve | 动词形式 | want to do;know 后接 why 不加 that |
| 6 | **why need to** introduce the sharding approach | **why they need to** introduce sharding | 动词形式 + 冠词 | 疑问从句是完整句子,不能缺主语 |
| 7 | The candidate **give** his answer | The candidate **gives** his answer | 主谓一致 | 第三人称单数动词加 s |
| 8 | all of write **traffics would be** routed | all write **traffic is** routed | 主谓一致 + 时态 | traffic 不可数;架构规律用现在时 |
| 9 | can not improve | **cannot** improve | 固定搭配 | cannot 写成一个词 |
| 10 | **the interviewers is** curious | **the interviewer is** curious | 主谓一致 | 本次对话是单一面试官;主谓要一致 |
| 11 | **in another words**, why not choose | **in other words** | 固定搭配 | 固定短语:in other words |
| 12 | this approach could only improve for a while because there is the ceiling of hard physical resources of single machine | this approach **helps** only for a while because a single machine **has a hard ceiling of** physical resources | 用词 + 冠词 | improve 不及物,「方案起作用」用 help/work;泛指单机加 a |
| 13 | which sharding strategy the candidate **chosen** | which sharding strategy the candidate **chose** | 时态 | choose–chose–chosen;这里要过去式 |
| 14 | they **choose** the physical sharding | they **chose** physical sharding | 时态 | 与上文过去式保持一致;策略名前不加 the |
| 15 | across multiple machines, **in this way, it will reduce** the write pressure **of** each machine | across multiple machines**; this reduces** the write pressure **on** each machine | 从句连接 + 固定搭配 | 逗号不能连接两个独立句;pressure on |
| 16 | **the interviewers wants** to know | **the interviewer wants** to know | 主谓一致 | 同 #10 |
| 17 | the work details of query performance **improving** and partition pruning | **how query performance improves and how partition pruning works** | 用词 | 疑问从句比名词堆叠自然得多 |
| 18 | a sharding key **such user_id** | a sharding key **such as** user_id | 固定搭配 | such as(举例) |
| 19 | the query with **sharding number** only **retrieve** the target shard and **skip** the others | the query with **the shard number** only **retrieves** … and **skips** | 冠词 + 主谓一致 | 主语 the query 单数 |
| 20 | That is the mechanism of partition pruning and also **could improve** query performance **better** | That is how partition pruning works, and it also **improves** query performance | 时态 + 用词 | improve 已含「变好」,不与 better 连用 |
| 21 | then **interviewer** and the candidate discuss | then **the** interviewer and the candidate discuss | 冠词 | 特指本对话的面试官加 the |

## 升级改写(B2 嵌套从句版)

> 在纠错基础上示范「同样内容如何说成 B2」;**加粗**为新增从句结构。

This article talks about how write scalability improves with a sharding strategy. At first, the interviewer agrees **that the read-write splitting strategy significantly improves read scalability**, but notices **that write throughput is still limited because it depends on a single machine**, so he wants to know **why master-slave replication cannot achieve good write scalability and why sharding is needed**. The candidate explains **that all write traffic is routed to the master node in a master-slave architecture, which is exactly why this approach cannot improve write throughput**.

Then the interviewer asks **why they do not simply upgrade the master to a bigger machine** — in other words, **why vertical scaling is not the answer**. The candidate explains **that this approach only helps for a while, because a single machine has a hard ceiling of physical resources**, which makes sharding necessary **if the team wants to relieve write pressure**.

Next, the interviewer wants to know **which sharding strategy the candidate chose**: logical or physical. The candidate says they chose physical sharding, **which means data shards are evenly distributed across multiple machines so that the write pressure on each machine drops**. Finally, they discuss how query performance improves: **when a query carries the shard number, which is computed by hashing the sharding key such as user_id, it only retrieves the target shard and skips the others**. That is how partition pruning works, and **it is also the reason why query performance improves**.

To summarize, the interviewer and the candidate discussed the problem of write scalability and **how sharding solves it**.

## 表达积累

- `X is limited by a single machine` —— 单机瓶颈的万能句式
- `a hard ceiling of physical resources` —— 垂直扩展天花板
- `reduce the write pressure on each machine` —— 写压力分摊
- `partition pruning, which lets the query skip the other shards` —— 分区裁剪

## 课堂补充

(上完课后,把老师课堂批改中 AI 没覆盖到的指正追加在这里,格式:`[原句] → [老师的版本] (要领)`)
