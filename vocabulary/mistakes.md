# 错误模式本(Mistakes)

> 作文错误的结构化沉淀,由「批改作文」环节自动维护。刻意练习的靶点:每周回顾取 Top 5 生成针对性练习,反哺下一周作文。

**数据来源:** 2026-09-03 / 09-05 / 09-09 三篇历史作文(2026-10-07 批改播种)

## 高频错误排行

| 排名 | 错误类型 | 次数 | 一句话要领 |
|---|---|---|---|
| 1 | 冠词 | 15 | 写名词时先判断:泛指可数单数加 a/an,特指/前文提过加 the,泛指复数/不可数用零冠词 |
| 2 | 动词形式 | 8 | want **to** do、know **how to** do、let + **原形**、情态/助动词后接**原形** |
| 3 | 固定搭配 | 8 | 成对记:meanwhile(≠at the meantime)、in other words、such as、prevent…**from** doing、pressure **on**、hint **at**、discuss(及物,不加 about) |
| 4 | 主谓一致 | 6 | 单数主语动词加 s;traffic / information 不可数;写完回头核对 |
| 5 | 时态 | 6 | 泛指事实/常规用一般现在时,不用 could/would;choose–chose–chosen 别混 |
| 6 | 从句连接 | 5 | 两个独立句不能只用逗号连接(改句号/分号/连词);situation/case 后接 where |
| 7 | 用词 | 5 | replica(副本实例)≠replication(过程);reach a position;名词用形容词修饰(global ordering) |

## 错误日志

| 日期 | 原句(节选) | 改正 | 错误类型 | 一句话规则 |
|---|---|---|---|---|
| 09-03 | discusses **about** how to use | discusses how to use | 固定搭配 | discuss 及物动词,直接接宾语 |
| 09-03 | introduces that they simply overwrite | explains that… | 动词形式 | introduce 不接 that 从句表「阐述」 |
| 09-03 | the value of later update | the value of **the** later update | 冠词 | 特指某次更新要加 the |
| 09-03 | based on LWW approach | based on **the** LWW approach | 冠词 | 带缩写名的方案名前加 the |
| 09-03 | the situation **that** two users update | the situation **where** two users update | 从句连接 | situation/case + where 引导定语从句 |
| 09-03 | users **could** update their own keys | users can update… | 时态 | 描述方案的一般行为用现在时 |
| 09-03 | another scenario **that how to handle** | another scenario: how to handle… | 从句连接 | scenario 后不能接 that + 疑问句,用冒号或 of doing |
| 09-03 | **the** data loss is acceptable | some data loss is acceptable | 冠词 | 泛指不可数名词用零冠词或 some |
| 09-03 | let the operators **redoes** | let operators **redo** | 动词形式 | let + 宾语 + 动词原形 |
| 09-03 | prevent the system **losing** data | prevent the system **from losing** data | 固定搭配 | prevent … from doing |
| 09-03 | LWW never **check** machine clocks | never **checks** | 主谓一致 | LWW(单数概念)动词加 s |
| 09-03 | make sure the gap under 5ms | make sure the gap **stays** under 5 ms | 动词形式 | make sure 后接完整从句(主语+谓语) |
| 09-03 | a safe window for **most of cases** | in **most cases** | 固定搭配 | most cases 泛指不加 of;「在多数情况下」用 in |
| 09-03 | adopt **consensus algorithm** | adopt **a** consensus algorithm | 冠词 | 单数可数名词第一次泛指用 a |
| 09-03 | guarantee **globally ordering** | guarantee **global** ordering | 用词 | 名词用形容词修饰 |
| 09-05 | This article **is talk about** | This article talks about / is about | 动词形式 | 谓语只能有一个限定动词 |
| 09-05 | read-write splitting **would break** | breaks | 时态 | 架构的一般规律用一般现在时 |
| 09-05 | routed to different **replications** | different **replicas** | 用词 | replica=副本实例;replication=复制过程 |
| 09-05 | wants to know **routing approach which the candidate choses** | the routing approach **that the candidate chose** | 冠词 | know the + 名词 + 从句;choses 拼写错(chose/chosen) |
| 09-05 | hash routing which would ensure **user's requests** | , which ensures that **a user's** requests | 冠词 | 泛指「某个用户」用 a user's;非限制性从句加逗号 |
| 09-05 | cannot cover **case when replica fails** | **the case where a** replica fails | 冠词 | case 前加 the;a replica 泛指单台 |
| 09-05 | would like to know **guarantee** monotonic reads | know **how to guarantee** | 动词形式 | know + how to do |
| 09-05 | increase **pressure of** the master | increase **the pressure on** the master | 固定搭配 | pressure on + 对象 |
| 09-05 | **hints** another approach **which is use** | hints **at** another approach: **using** | 固定搭配 | hint at;介词后用动名词 |
| 09-05 | to **receive** the position the user last saw | to **reach** the position… | 用词 | 追平到某位置用 reach |
| 09-05 | …to limit the wait loop**,** once the loop exceeds 200ms**,** and it will fall back | …to limit the wait loop**;** once the loop exceeds 200ms**, the request falls back** | 从句连接 | 逗号不能连接两个独立句(comma splice) |
| 09-05 | …guarantee monotonic read**,** these solutions could cover… | …monotonic reads**. These** solutions cover… | 从句连接 | 同上;泛指结论用现在时 |
| 09-09 | This article **is talking about** | This article talks about | 动词形式 | 描述文章内容用一般现在时 |
| 09-09 | with **sharding strategy** | with **a** sharding strategy | 冠词 | 单数可数名词泛指加 a |
| 09-09 | **at the meantime** | **meanwhile** / at the same time | 固定搭配 | 没有at the meantime 这个搭配 |
| 09-09 | limited by **the single machine** | by **a** single machine | 冠词 | 泛指「任何单机」用 a |
| 09-09 | wants **know that why** | wants **to know why** | 动词形式 | want to do;know why 直接连用不加 that |
| 09-09 | **why need to** introduce the sharding approach | **why they need to** introduce sharding | 动词形式 | 疑问从句里不能缺主语 |
| 09-09 | The candidate **give** his answer | **gives** | 主谓一致 | 单数第三人称动词加 s |
| 09-09 | all of write **traffics** would be routed | all write **traffic** is routed | 主谓一致 | traffic 不可数,无复数 |
| 09-09 | **the interviewers is** curious | **the interviewer is** | 主谓一致 | 面试官是单数概念;主语和动词一致 |
| 09-09 | **in another words** | **in other words** | 固定搭配 | 固定短语 |
| 09-09 | there is **the ceiling** … of **single machine** | a single machine **has a hard ceiling** of… | 冠词 | 泛指单机用 a;「有一个天花板」用 a |
| 09-09 | which sharding strategy the candidate **chosen** | **chose** | 时态 | choose–chose–chosen;定语从句里用过去式 |
| 09-09 | …across multiple machines**,** in this way, it will reduce… | …machines**; this** reduces the write pressure **on** each machine | 从句连接 | 独立句用分号;pressure on |
| 09-09 | the **interviewers wants** to know | the **interviewer wants** | 主谓一致 | 同上 |
| 09-09 | the work details of query performance **improving** | **how query performance improves** | 用词 | 疑问从句比名词堆叠自然 |
| 09-09 | a sharding key **such user_id** | **such as** user_id | 固定搭配 | such as(缺 as) |
| 09-09 | the query … only **retrieve** … and **skip** the others | only **retrieves** … and **skips** | 主谓一致 | 主语 the query 单数 |
| 09-09 | also **could improve** query performance **better** | also **improves** query performance | 时态 | improve 已含「更好」,无需 better;泛指用现在时 |
| 09-09 | then **interviewer** and the candidate | then **the** interviewer… | 冠词 | 特指的 interviewer 加 the |

## 复习方法

1. 每周回顾时看 Top 5,选 1–2 个类型做专项(在下一周跟读材料里**主动使用**正确形式)
2. 新作文动笔前,扫一遍本页 Top 3 的「一句话要领」
3. 同类错误连续 2 周下降后,从 Top 5 移出关注,换下一个类型上位
