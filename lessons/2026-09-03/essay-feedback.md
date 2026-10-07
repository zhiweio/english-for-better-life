# 作文批改 · 2026-09-03

> 主题:多主冲突解决——Last Write Wins 的边界 | 作文目标:复述上节课对话,练 B2 表达

## 总评

- **内容覆盖:** 技术推进完整(LWW 基本机制 → 不同字段冲突的拆 key 方案 → 同字段冲突的分级策略 → NTP 时钟偏移风险 → 共识兜底),这是三篇里技术细节最密的一篇
- **语言诊断:** **动词搭配**问题集中(discusses about、introduces that、let…redoes);**固定搭配**(prevent…losing、most of cases)和**冠词**延续了前两篇的老问题;scenario that how to handle 这种「名词 + that + 疑问句」的结构不成立
- **3 个亮点:** ① tiered approach / versioned conditional updates 等术语准确且敢用;② so that / in this way 的目的衔接意识;③ 最后一段主动总结
- **3 个优先修改:** ① 记牢一批高频动词的接法(discuss + 宾语、explain that、let + 原形);② 固定搭配成对背(meanwhile / in other words / prevent…from / such as);③ 泛指描述把 could/would 换成一般现在时

## 逐句纠错

| # | 原句(节选) | 修改 | 错误类型 | 讲解 |
|---|---|---|---|---|
| 1 | This article **discusses about** how to use | This article **discusses** how to use | 固定搭配 | discuss 是及物动词,直接接宾语,不加 about |
| 2 | the extreme scenarios **which LWW could not cover** | **that LWW cannot cover** | 时态 | 描述方案能力用现在时;限制性从句 that 更紧凑 |
| 3 | the candidate **introduces that** they simply overwrite | the candidate **explains that**… | 动词搭配 | introduce 不用于 introduce that + 从句(说「阐述」用 explain/describe) |
| 4 | overwrite the older one using the value of **later update** based on **LWW approach** | …using the value of **the** later update based on **the LWW approach** | 冠词 | 特指的后更新的值、特指的方案都要加 the |
| 5 | mentions the situation **that** two users update different fields | the situation **where** two users update… | 从句连接 | situation/case/point 后接 where(或 in which) |
| 6 | gives the fix **which is splitting** the record into separate keys | **proposes a fix: splitting** the record into separate keys | 用词 | 冒号引出方案内容更利落 |
| 7 | so that users **could** update their own keys **which would never interfere** | so that users **can** update their own keys, **which never interferes** | 时态 | 方案的一般行为用现在时;非限制性从句加逗号 |
| 8 | another scenario **that how to handle** the conflicts **on updating** the same field **from two operations** | another scenario: **how to handle conflicts when two operations update** the same field | 从句连接 | 名词后不能接 that + 疑问句;「当两个操作…」用 when 从句 |
| 9 | **the data loss** is acceptable | **some data loss** is acceptable | 冠词 | 泛指不可数名词用零冠词或 some |
| 10 | let the operators **redoes to recover** updates | let operators **redo the steps to recover the lost updates** | 动词形式 + 冠词 | let + 宾语 + 动词原形 |
| 11 | reject **the write** whose version has changed and **refresh** | reject **writes** whose version has changed**, then refresh its state** | 用词 | 泛指多次写入用复数;补出 refresh 的宾语避免悬空 |
| 12 | prevent the system **losing** data caused by NTP offset | prevent the system **from losing** data **because of NTP skew** | 固定搭配 | prevent … from doing;时钟偏移常用 clock skew/offset |
| 13 | because LWW never **check** machine clocks | never **checks** | 主谓一致 | LWW 单数概念,动词加 s |
| 14 | make sure **the gap under 5ms** | make sure **the gap stays under 5 ms** | 动词形式 | make sure 后接完整从句(主语 + 谓语) |
| 15 | a safe window for **most of cases** | **in most cases** | 固定搭配 | 泛指「多数情况」most cases 不加 of;搭配介词 in |
| 16 | they will **give up** LWW | they will **drop / move away from** LWW | 用词 | give up 多接习惯/尝试;放弃技术方案用 drop/abandon |
| 17 | adopt **consensus algorithm** to guarantee **globally ordering** | adopt **a** consensus algorithm to guarantee **global ordering** | 冠词 + 用词 | 单数可数名词加 a;名词用形容词修饰 |
| 18 | the candidate **talk about** the approaches **to resolve** write conflicts **occurring under** different circumstances | the candidate **talked about the approaches for resolving** write conflicts **under** different circumstances | 时态 + 用词 | 总结过去对话用过去时;approach for doing/to doing |

## 升级改写(B2 嵌套从句版)

> **加粗**为新增从句结构。

This article discusses how the Last Write Wins (LWW) strategy resolves write conflicts in multi-master replication, and what the team does in the extreme scenarios **that LWW cannot cover**. At first, the candidate explains **that, under LWW, they simply overwrite the older value with the one that carries the later timestamp**. However, the interviewer raises a case **where two users update different fields of the same item, which can still cause write conflicts**. The candidate proposes a fix: splitting the record into separate keys **so that each user updates their own key, which never interferes with the others**. This approach is simple and efficient.

Then the interviewer gives another scenario: **what the team does when two operations update the same field**. The candidate proposes a tiered approach **that depends on how critical the field is**. For non-critical fields, **where some data loss is acceptable**, they keep LWW and let operators redo the steps **that are needed to recover the lost updates**. For critical fields, they replace LWW with versioned conditional updates, **which means the application layer rejects any write whose version has changed, then refreshes its state**.

Finally, the interviewer asks **how they prevent the system from losing data because of NTP skew between machines, given that LWW never checks machine clocks**. The candidate says they actively monitor the NTP offset between the two data centers and keep it under 5 ms, **which is a safe window for most cases**. But for use cases **that require absolute ordering**, they drop LWW and adopt a consensus algorithm **that guarantees global ordering**.

To summarize, the interviewer and the candidate talked about **how write conflicts can be resolved under different circumstances**.

## 表达积累

- `a tiered approach that depends on how critical the field is` —— 分级策略
- `prevent … from losing data` —— 防丢数据
- `which is a safe window for most cases` —— 安全窗口
- `adopt a consensus algorithm that guarantees global ordering` —— 共识兜底

## 课堂补充

(上完课后,把老师课堂批改中 AI 没覆盖到的指正追加在这里,格式:`[原句] → [老师的版本] (要领)`)
