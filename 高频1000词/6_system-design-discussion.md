# System Design Discussion

## Material Goal

- 理解这篇关于系统设计讨论的短文
- 掌握 architecture、scalability、reliability 等高频系统设计词汇
- 重点练习讨论架构方案、解释技术选择和表达设计思路

## Quick Chinese Brief

这篇短文讲的是团队在会议室里讨论一个 notification service 的系统设计方案。核心问题包括高并发、消息队列、worker、database、latency、cache、retry、dead letter queue 等。

这类材料很适合练“解释架构”和“说明技术选择”。重点不是背很深的系统设计理论，而是把常见讨论表达和高频技术词练熟。

## Original Text

**Theme: Discussing the architecture of a new system**

We are in a meeting room with a whiteboard. The team is discussing the architecture for a new system. We need to build a notification service that can send emails, push notifications, and SMS messages.

"Let us start with the requirements," says Sarah. "The system needs to handle 10,000 notifications per second during peak hours."

"That is a lot of traffic," says Mike. "We need to design for scalability."

"I agree," I say. "We should use a message queue. When a user triggers a notification, we put a message in the queue. Then we have workers that pull messages from the queue and send the actual notifications."

"That is a good approach," says Tom. "It decouples the producers from the consumers. If one part fails, the rest of the system keeps working."

"Yes," I say. "And we can scale the workers horizontally. If traffic goes up, we just add more worker instances."

Sarah draws a diagram on the whiteboard. "So the flow is: Client -> API Gateway -> Queue -> Workers -> Third-party services."

"Exactly," I say.

"What about the database?" asks Mike. "We need to store notification history. Users want to see all the notifications they received."

"We can use a NoSQL database for that," I say. "Something like Cassandra. It is good for high write throughput. We will be writing a lot of data."

"What about latency?" asks Tom. "Users expect notifications to arrive quickly. We cannot have a 5-second delay."

"Good point," I say. "The queue adds some latency, but it should be less than 100 milliseconds most of the time. If we need lower latency, we can add a cache layer. Frequently sent notifications can be cached."

Sarah writes more notes on the whiteboard. "What about reliability? What if the third-party SMS service is down?"

"We need a retry mechanism with exponential backoff," I say. "If a notification fails, we put it back in the queue and try again later. After three retries, we log it as a failure and alert the on-call team."

"Let us also add a dead letter queue for messages that cannot be processed," says Tom. "That way we do not lose the data."

"This sounds solid," says Sarah. "Let me write up the design document. We will review it tomorrow."

I feel good about the design. We thought about scalability, reliability, and performance. The system will be robust.

## Core High-Frequency Words

### 1. architecture

English meaning:
the overall design of a system

中文提示：系统架构

Pronunciation hint:
AR-chi-tec-ture

Useful line:

We are discussing the architecture of the new system.

### 2. requirements

English meaning:
things the system must do

中文提示：需求

Pronunciation hint:
re-QUIRE-ments

Useful line:

Let us start with the requirements.

### 3. scalability

English meaning:
the ability to handle more traffic or data

中文提示：可扩展性

Pronunciation hint:
sca-la-BIL-i-ty

Useful line:

We need to design for scalability.

### 4. worker

English meaning:
a process or service that does background tasks

中文提示：工作进程，处理任务的服务

Pronunciation hint:
WOR-ker

Useful line:

The workers pull messages from the queue.

### 5. throughput

English meaning:
how much work or data the system can handle

中文提示：吞吐量

Pronunciation hint:
THROUGH-put

Useful line:

This database is good for high write throughput.

### 6. latency

English meaning:
the delay before a system responds

中文提示：延迟

Pronunciation hint:
LA-ten-cy

Useful line:

We want to keep the latency low.

### 7. reliability

English meaning:
the ability to keep working correctly

中文提示：可靠性

Pronunciation hint:
re-li-a-BIL-i-ty

Useful line:

Reliability is important for this system.

### 8. retry

English meaning:
to try again after a failure

中文提示：重试

Pronunciation hint:
re-TRY

Useful line:

The system should retry failed messages.

### 9. cache

English meaning:
fast storage for frequently used data

中文提示：缓存

Pronunciation hint:
`cache` 发音像 `cash`

Useful line:

We can add a cache layer to reduce latency.

### 10. robust

English meaning:
strong and reliable

中文提示：健壮的，稳定可靠的

Pronunciation hint:
ro-BUST

Useful line:

The final design should be robust.

## Useful Phrases and Collocations

### 1. message queue

中文提示：消息队列

Pronunciation hint:
MES-sage QUEUE

Useful line:

We should use a message queue.

### 2. scale horizontally

中文提示：横向扩展

Pronunciation hint:
SCALE hori-ZON-tal-ly

Useful line:

We can scale the workers horizontally.

### 3. API Gateway

中文提示：API 网关

Pronunciation hint:
A-P-I GATE-way

Useful line:

The request first goes through the API Gateway.

### 4. NoSQL database

中文提示：NoSQL 数据库

Pronunciation hint:
NO-se-quel DA-ta-base

Useful line:

We can use a NoSQL database for notification history.

### 5. good point

中文提示：说得好，这个点很好

Pronunciation hint:
GOOD point

Useful line:

Good point. We should think about latency.

### 6. cache layer

中文提示：缓存层

Pronunciation hint:
CACHE LAY-er

Useful line:

We can add a cache layer if needed.

### 7. exponential backoff

中文提示：指数退避

Pronunciation hint:
ex-po-NEN-tial BACK-off

Useful line:

We need retry with exponential backoff.

### 8. dead letter queue

中文提示：死信队列

Pronunciation hint:
DEAD LET-ter QUEUE

Useful line:

Let us add a dead letter queue.

### 9. write up the design document

中文提示：整理并写出设计文档

Pronunciation hint:
write UP the de-SIGN DOC-u-ment

Useful line:

Sarah will write up the design document.

## Pronunciation Focus

### 1. scalability

Stress hint:
sca-la-BIL-i-ty

中文提醒：重点在 `BIL`，这个词较长，先慢读再连起来。

Repeat drill:

We need to design for scalability.

### 2. throughput

Stress hint:
THROUGH-put

中文提醒：前重后轻，开头辅音组合要慢一点读清楚。

Repeat drill:

This system needs high throughput.

### 3. latency

Stress hint:
LA-ten-cy

中文提醒：重点在前面，节奏清楚。

Repeat drill:

We need lower latency.

### 4. reliability

Stress hint:
re-li-a-BIL-i-ty

中文提醒：重点还是 `BIL`，长词先拆后连。

Repeat drill:

Reliability is important for this service.

### 5. exponential backoff

Stress hint:
ex-po-NEN-tial BACK-off

中文提醒：两个词都要有重音，尤其是 `NEN` 和 `BACK`。

Repeat drill:

We use exponential backoff for retries.

### 6. dead letter queue

Stress hint:
DEAD LET-ter QUEUE

中文提醒：三个词分明地读，最后 `queue` 单独清楚。

Repeat drill:

We added a dead letter queue.

## Good Expressions and Grammar Patterns

### 1. We need to ...

Pattern:
We need to ...

中文说明：讨论设计需求和下一步动作时非常高频。

Model line:

We need to build a notification service.

Drill:

We need to __________.

### 2. We should use ...

Pattern:
We should use ...

中文说明：很适合表达你的技术建议。

Model line:

We should use a message queue.

Drill:

We should use __________.

### 3. If ..., we can ...

Pattern:
If ..., we can ...

中文说明：适合表达条件和对应方案。

Model line:

If traffic goes up, we can add more worker instances.

Drill:

If __________, we can __________.

### 4. What about ...?

Pattern:
What about ...?

中文说明：系统设计讨论里特别常见，用来引入新问题。

Model line:

What about reliability?

Drill:

What about __________?

### 5. That way, ...

Pattern:
That way, ...

中文说明：用来解释一个设计的好处和结果。

Model line:

That way, we do not lose the data.

Drill:

That way, __________.

## Retelling and Output Drill

### 3-Line Retelling

The team is discussing the architecture of a new notification service.
They use a queue, workers, and a NoSQL database to support scalability and performance.
They also add retry logic and a dead letter queue to improve reliability.

### 5-Line Retelling

This article is about a system design discussion.
The team needs a service that can send many notifications during peak hours.
They decide to use a message queue and workers so the system can scale horizontally.
They also think about latency, reliability, retry logic, and dead letter queues.
In the end, they feel good because the design is scalable, reliable, and robust.

### Output Prompts

- Why is a message queue useful in this system?
- Why do we need to think about latency and reliability?
- What makes a system design robust?

## Review Task

### 1. Read Aloud

Read the `Original Text` aloud once slowly and once at a natural speed.

### 2. Pronunciation Practice

Read all items in `Pronunciation Focus` aloud 3 times.
Pay attention to stress and long technical words.

### 3. Phrase Reuse

Use these 5 phrases to make your own short lines:

- message queue
- scale horizontally
- good point
- exponential backoff
- dead letter queue

### 4. Retelling

First say the `3-Line Retelling`.
Then try the `5-Line Retelling` without looking at the text.