# 作文批改 · 2026-09-05

> 主题:一致性面试——读写分离架构下保证单调读(Monotonic Reads) | 作文目标:复述上节课对话,练 B2 表达

## 总评

- **内容覆盖:** 技术主线完整(读扩散问题 → 用户哈希路由 → 副本故障回退主库 → 复制位点多耐等 200ms),这篇比 09-03 流畅,句式开始有变化
- **语言诊断:** 第一句就出现的 **is talk about** 是本篇最典型问题(谓语动词形式);**冠词**仍是重灾区(the routing approach / a replica / the case);两处**逗号连接独立句**(comma splice)在结尾段
- **3 个亮点:** ① user-ID-based hash routing 这类复合修饰语用得地道;② progressively / immediately 等副词准确;③ 段落之间有 And then / In the end 的衔接意识
- **3 个优先修改:** ① 动笔先确认每句只有一个限定动词(talks about ≠ is talk about);② 名词前先过一遍冠词;③ 长句收尾时检查是不是两个句子被逗号连住了

## 逐句纠错

| # | 原句(节选) | 修改 | 错误类型 | 讲解 |
|---|---|---|---|---|
| 1 | This article **is talk about** how to guarantee | This article **talks about / is about** how to guarantee | 动词形式 | 一个句子只能有一个限定动词;is 后不能接动词原形 |
| 2 | read-write splitting plus load balancing **would break** Monotonic Read | **breaks** monotonic reads | 时态 | 架构的一般规律用一般现在时,不用 would |
| 3 | two requests would be routed to different **replications** | different **replicas** | 用词 | replica=副本实例;replication=复制这个动作 |
| 4 | wants to know **routing approach which the candidate choses** | **the routing approach that the candidate chose** | 冠词 + 时态 | know the + 名词;过去动作 chose(注意拼写) |
| 5 | gives the user-ID-based hash routing **which would ensure user's requests** | , **which ensures that a user's requests** | 冠词 + 时态 | 泛指某用户用 a user's;非限制性定语从句前加逗号 |
| 6 | this approach cannot cover **case when replica fails** | **the case where a replica** fails | 冠词 + 从句连接 | case 前加 the;case/situation 接 where;a replica 泛指 |
| 7 | would like to know **guarantee** monotonic reads | know **how to guarantee** | 动词形式 | know + how to do |
| 8 | increase **pressure of** the master when **replica is** unavailable | increase **the pressure on** the master when **a replica is** unavailable | 固定搭配 + 冠词 | pressure on + 对象;泛指单台副本加 a |
| 9 | the interviewer **hints** another approach **which is use** replication position | hints **at** another approach: **using the** replication position | 固定搭配 + 动词形式 | hint at;which is 后不能接动词原形 |
| 10 | gives **the solution to handle checking timeout** | **a solution for handling the check timeout** | 冠词 | 泛指一个方案用 a;solution for doing |
| 11 | to **receive** the position the user last saw | to **reach** the position… | 用词 | 追平到某个位点用 reach |
| 12 | they use the maximum timeout which is 200ms to limit the wait loop**,** once the loop exceeds 200ms**,** and it will fall back to the master immediately | …to bound the wait loop**;** once the loop exceeds 200 ms**, the request falls back** to the master immediately | 从句连接 + 时态 | 逗号不能连接两个独立句(comma splice);规律行为用现在时 |
| 13 | …to guarantee monotonic read**,** these solutions **could cover** various scenarios | …monotonic reads**. These solutions cover**… | 从句连接 + 时态 | 同 #12;总结性结论用一般现在时 |

## 升级改写(B2 嵌套从句版)

> **加粗**为新增从句结构。

This article is about how to guarantee read consistency in a read-write splitting architecture. The classic problem is **that read-write splitting with load balancing breaks monotonic reads**: two requests **that belong to the same user** may be routed to different replicas. The interviewer wants to know **which routing approach the candidate chose so that the same user always reads from the same replica**.

The candidate first proposes user-ID-based hash routing, **which ensures that all of a user's requests hit the same replica**. However, this approach does not cover the case **where a replica fails**, so the interviewer asks **how monotonic reads can still be guaranteed in that situation**. The candidate says they simply fall back to the master, **although this may increase the pressure on the master whenever a replica is unavailable**.

Then the interviewer hints at another approach, **which is to track the replication position**. The candidate explains how this design works and offers a solution for the check timeout: the replica keeps checking whether it has reached the replication position **that the user last saw**, and **because this check must not block forever**, they set a maximum timeout of 200 ms — **once the wait loop exceeds 200 ms**, the request falls back to the master immediately.

To summarize, the candidate progressively gives different solutions **that guarantee monotonic reads**, and **together they cover various scenarios**.

## 表达积累

- `fall back to the master` —— 副本故障回退主库
- `increase the pressure on the master` —— 主库压力上升
- `keeps checking whether it has reached the position that the user last saw` —— 复制位点等耐
- `set a maximum timeout of 200 ms to bound the wait loop` —— 兜底超时

## 课堂补充

(上完课后,把老师课堂批改中 AI 没覆盖到的指正追加在这里,格式:`[原句] → [老师的版本] (要领)`)
