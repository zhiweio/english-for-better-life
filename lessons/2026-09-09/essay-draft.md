This article is talking about improving write scalability with sharding strategy.
At first, the interviewer agrees that read-write splitting strategy could significantly improve read scalability, at the meantime, he notices that the write throughput is limited by the single machine, so the interviewer wants know that why master-slave replication could not achieve the scalability well and why need to introduce the sharding approach.
The candidate give his answer: all of write traffics would be routed to the master node in master-slave replication architecture, so master-slave replication can not improve write throughput.
And then the interviewers is curious about why not upgrade the master to a bigger machine, in another words, why not choose the vertical scaling to solve write scalability limitation. The candidate explains that this approach could only improve for a while because there is the ceiling of hard physical resources of single machine. So it is necessary to introduce sharding to reduce the write pressure.
Move next, the interviewer wants to know which sharding strategy the candidate chosen: logical sharding or physical sharding. The candidate says that they choose the physical sharding, that means they will evenly distribute data shards across multiple machines, in this way, it will reduce the write pressure of each machine.
In the end, the interviewers wants to know the work details of query performance improving and partition pruning.
The candidate explains that, for example, they will choose a sharding key such user_id, and then compute the target shard by hashing user_id, so the query with sharding number only retrieve the target shard and skip the others. That is the mechanism of partition pruning and also could improve query performance better.
To summarize, then interviewer and the candidate discuss the problem of write scalability and how to solve it.


