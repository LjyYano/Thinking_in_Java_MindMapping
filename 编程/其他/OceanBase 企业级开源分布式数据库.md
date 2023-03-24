---
date: 2021-11-17
---

# 是什么

企业级的开源`分布式数据库`。

# 有什么特点

- 高可用：支持跨城多机房容灾，满足金融行业 6 级容灾标准（RPO=0，RTO<=30 秒）。
- 线性扩展：自动负载均衡，`应用透明的水平扩展`，集群规模可超过 1500 节点，数据量可达 PB 级，`单表记录万亿行`。
- MySQL 高度兼容：`兼容 MySQL 协议`，MySQL 客户端工具可以直接访问 OceanBase。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117142632.png?x-oss-process=style/yano)

目前 OceanBase 数据库只支持 Linux 内核，暂无 Windows 和 Mac 版本。

# 官方文档

https://open.oceanbase.com/

# 数据库概览

## 整体架构

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117142934.png?x-oss-process=style/yano)

OceanBase 采用了 Zone（可用区）的概念，每个 Zone 是一个机房内的一组服务器，包含多台 OceanBase 数据库服务器（OBServer）。每台 OBServer 包含：
- SQL 引擎
- 事务引擎
- 存储引擎

对于跨服务器操作，OCeanBase 数据库还会执行强一致的分布式事务，从而实现分布式集群上的数据库事务 ACID。

OceanBase 数据库采用 Shared-Noting 架构，各个节点之间完全对等。

## 数据分布

OceanBase 数据库集群由一个或多个 Region 组成，Region 由一个或多个 Zone 组成，Zone 由一台或多台服务器组成。
- Region：物理上的一个城市或地域
- Zone：独立网络和供电容灾能力的数据中心

OceanBase 数据库集群的每台服务器上会运行 observer 进程，observer 进程负责整个数据库服务的各项功能，包括资源管理与租户创建，数据分布的管理，数据副本之间的 Paxos 协议，单机或分布式的数据查询与修改等。

OceanBase 是通过`分区表`实现单表亿行数据的。当表格的容量或服务能力不足时，只需要通过 OceanBase 管理命令增加更多表格分区。

## 高可用

高可用主要体现在 2 个方面：

- 当数据库节点发生宕机或意外中断时，能够自动恢复数据库的可用性，减少业务受影响时间，避免业务因为数据库节点故障而中断。
- 数据库少数节点故障，导致这部分节点数据无法读取时，保证业务数据不会丢失。

OceanBase 采用了性价比较高、可靠性略低的服务器，同一数据保存在多台（>=3）服务器中的半数以上服务器上，每一笔写事务必须达到半数以上服务器才生效，因此当少数服务器故障时不会有任何数据丢失。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117145810.png?x-oss-process=style/yano)

传统数据库主备镜像的主库发生故障时，通常需要外部工具或人工把备库升级成主库，而 OceanBase 数据库底层实现了 Paxos 高可用协议，在主库故障后，剩余的服务器会很快自动选举出新的主库，并继续提供服务。

```java
分布式选举、多副本日志同步等，限于篇幅，本文就不展开了。
```

那为了实现高可用，数据库集群应该如何部署呢？OceanBase 数据库集群由一个或多个 Region 组成，Region 由一个或多个 Zone 组成，Zone 由一台或多台服务器组成。Region 通常就是同城，Zone 是同机房的多个独立单元。在部署时可以采用两地三中心三副本模式，能够实现高可用和异地容灾。通过在两地的三个中心分别部署一个副本，其中两个副本位于同一个城市，正常情况下事务提交在同城的两个副本完成同步即可，所以具备和同城三机房同样的性能。同时当少数副本所在的城市发生地域级故障时，整个 OceanBase 数据库集群的服务不受影响，并且不丢数据。但是当多数副本所在城市发生地域级故障时，会导致 OceanBase 数据库停服务。所以相对于同城三机房可用性虽然有大幅的提升，但是本质上这还是一个机房级容灾方案。

## 分布式事务

OceanBase 数据库使用`两阶段提交协议`来实现分布式事务，以分布式转账为例，假设服务器节点 A 上的账户 UA 向服务器节点 B 上的账户 UB 转账，则两阶段提交的步骤是：

第一阶段，即 `prepare` 阶段，节点 A 和节点 B 分别检查账户 UA 和 UB 的状态是否正常、账户 UA 的余额充足且可以转出（没有超限）、账户 UB 可以转入（没有被冻结），检查通过则锁定账户 UA 和 UB。

第二阶段，即 `commit` 阶段，如果在第一阶段账户 UA 和 UB 的 prepare 操作都成功，则通知节点 A 对账户 UA 的余额进行扣减和通知节点 B 对账户 UB 的余额进行添加，转账成功；否则通知节点 A 和节点 B 对相应账户的操作进行回滚，转账取消。

OceanBase 由于采用了 Paxos 高可用协议，节点 A 并不会因为参与者的单点故障而中断，因为当某个参与者发生故障，可以秒级选举出副本继续提供服务。

Paxos + 两阶段提交协议：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117150820.png?x-oss-process=style/yano)

## 存储架构

OceanBase 数据库底层存储的数据结构是什么样的呢？同时读写流程是什么样的？

### LSM Tree 架构

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117151453.png?x-oss-process=style/yano)

OceanBase 数据库的存储引擎基于 `LSM Tree 架构`，数据分为：
- 静态基线数据（放在 SSTable 中）是只读的，一旦生成就不再被修改，存储于磁盘
- 动态增量数据（放在 MemTable 中）支持读写，存储于内存

数据库 DML 操作插入、更新、删除等首先写入 MemTable，等到 MemTable 达到一定大小时转储到磁盘成为 SSTable。在进行查询时，需要分别对 SSTable 和 MemTable 进行查询，并将查询结果进行归并，返回给 SQL 层归并后的查询结果。同时在内存实现了 Block Cache 和 Row cache，来避免对基线数据的随机读。

当内存的增量数据达到一定规模的时候，会触发增量数据和基线数据的`合并`，把增量数据落盘。同时每天晚上的空闲时刻，系统也会自动每日合并。

OceanBase 本质上是一个`基线加增量`的存储引擎，跟关系数据库差别很大，同时也借鉴了部分传统关系数据库存储引擎的优点。

### 内存表 MEMTable

OceanBase 数据库的内存存储引擎 MEMTable 由 BTree 和 Hashtable 组成，在插入/更新/删除数据时，数据被写入内存块，在 HashTable 和 BTree 中存储的均为指向对应数据的指针。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117151846.png?x-oss-process=style/yano)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211117151913.png?x-oss-process=style/yano)

### 块存储 SSTable

当 MemTable 的大小达到某个阈值后，OceanBase 数据库会将 MemTable 中的数据转存于磁盘上，转储后的结构称之为 SSTable。在转存磁盘时也会进行各种压缩编码。

### 转储和合并

当 MEMTable 的内存使用达到一定阈值时，就需要将 MEMTable 中的数据存储到磁盘上以释放内存空间，这个过程称之为转储。在转储之前首先需要保证被转储的 MEMTable 不再进行新的数据写入，这个过程称之为冻结（Minor Freeze），冻结会阻止当前活跃的 MEMTable 再有新的写入，并同时生成新的活跃 MEMTable。

在对冻结 MEMTable 进行转储时，会扫描冻结 MEMTable 中的数据行，并将这些数据行存储到 SSTable 中，当一条数据被多个不同事务反复修改时，可能会有多个不同版本的数据行存储到转储 SSTable 中。

转储发生在 MEMTable 的大小满足一定条件时，任何分区副本可以独立决定冻结当前 MEMTable，并转储到磁盘上。转储出的 SSTable 只与相同大版本的增量数据做数据归并，不与全局静态数据合并。这样设计是基于增量数据远小于全局数据的考虑，使得转储会比较快。

### 合并

生成一个全局快照，将动静态数据做归并，比较费时，通过 Major Freeze（类似于 Java 的 Full GC）。全量合并、增量合并、渐进合并。

# 类比

- 渐进式合并，就类似于 Redis 的渐进式 rehash
- OceanBase 整体上和 Tidb 一样，架构也较为类似，都是分布式数据库，采用一致性算法，自动选举。本质上更像是一个服务
- 整体数据 = 基线数据 + 内存数据，内存数据到一定量时，转换为基线数据。基线数据可以在某些时候合并
- 数据库也有冻结操作，类似于 Java 的 minor gc 和 full gc
- OceanBase 的分布式协议是 Paxos，Tidb 是 Raft
- 分布式协议
	- OceanBase：Paxos
	- Tidb：Raft
	- Kafka：ZooKeeper ZAB