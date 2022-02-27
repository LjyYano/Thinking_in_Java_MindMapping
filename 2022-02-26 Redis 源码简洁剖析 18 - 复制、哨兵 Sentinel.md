- [复制](#%E5%A4%8D%E5%88%B6)
    - [什么是复制](#%E4%BB%80%E4%B9%88%E6%98%AF%E5%A4%8D%E5%88%B6)
    - [为什么需要复制](#%E4%B8%BA%E4%BB%80%E4%B9%88%E9%9C%80%E8%A6%81%E5%A4%8D%E5%88%B6)
    - [复制的实现](#%E5%A4%8D%E5%88%B6%E7%9A%84%E5%AE%9E%E7%8E%B0)
        - [同步](#%E5%90%8C%E6%AD%A5)
        - [命令传播](#%E5%91%BD%E4%BB%A4%E4%BC%A0%E6%92%AD)
    - [新版复制功能实现](#%E6%96%B0%E7%89%88%E5%A4%8D%E5%88%B6%E5%8A%9F%E8%83%BD%E5%AE%9E%E7%8E%B0)
- [哨兵 Sentinel](#%E5%93%A8%E5%85%B5-sentinel)
    - [什么是 Sentinel](#%E4%BB%80%E4%B9%88%E6%98%AF-sentinel)
    - [简易工作原理](#%E7%AE%80%E6%98%93%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86)
    - [Sentinel 系统选举](#sentinel-%E7%B3%BB%E7%BB%9F%E9%80%89%E4%B8%BE)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)

# 复制

## 什么是复制

在 Redis 中，可以通过设置 `slaveof` 选项，让一个服务器去复制（replicate）另一个服务器：
- 主服务器（master）
- 从服务器（slave）

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220226162201.png?x-oss-process=style/yano)

## 为什么需要复制

在 Redis 集群中，保证在单机故障情况下，能够有副本，可通过哨兵（Sentinel）机制实现 `Redis 集群的高可用`。

## 复制的实现

Redis 的复制分为两个操作：
1. `同步操作（sync）`：从服务器的数据库状态更新至主服务器当前的状态
2. `命令传播（command propagate）`：主服务器上的写命令，传播给从服务器

### 同步

当客户端向从服务器发送 SLAVEOF 命令，要求从服务器复制主服务器时，从服务器首先需要执行同步操作，将从服务器的数据库状态更新至主服务器当前的数据库状态。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220226163421.png?x-oss-process=style/yano)

### 命令传播

在同步之后，主服务器的所有写命令，都需要传播给从服务器，以保证主从服务器数据库状态的一致。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220226163936.png?x-oss-process=style/yano)

## 新版复制功能实现

Redis 从 2.8 版本开始，使用 `PSYNC` 命令代替 SYNC 命令来执行复制时的同步操作。PSYNC 命令有完整重同步和部分重同步两种模式。
- `完整重同步`：和 SYNC 命令执行的步骤一样
- `部分重同步`：处理断线后重复制的情况。当从服务器在断线后重新连接主服务器时，如果条件允许，主服务器可以将主从服务器连接断开期间执行的写命令发送给从服务器，从服务器只接收并执行这些命令，就可以将数据库更新至主服务器的最新状态。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220226164739.png?x-oss-process=style/yano)

# 哨兵 Sentinel

## 什么是 Sentinel 

Sentinel（哨兵）是 `Redis 的高可用解决方案`：由一个或多个 Sentinel 实例组成的 Sentinel 系统可以监视任意多个主服务器及从服务器，并在被监视的主服务器进入下线状态时，自动将下线主服务器属下的某个从服务器升级为新的主服务器，然后由新的主服务器代替已下线的主服务器继续处理命令。

Sentinel 本质上只是运行在特殊模式下的 Redis 服务器，具体细节可参考：[Redis Sentinel Documentation](https://redis.io/topics/sentinel)

## 简易工作原理

下图展示了服务器与 Sentinel 系统：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220227111134.png?x-oss-process=style/yano)

下图展示了主服务器下线时的情况：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220227111237.png?x-oss-process=style/yano)

下图展示了故障转移：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220227111611.png?x-oss-process=style/yano)

下图展示原主服务器（Server1）再次上线后，降级为从服务器的流程：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220227111810.png?x-oss-process=style/yano)

## Sentinel 系统选举

Sentinel 系统选举领头 Sentinel 的方法是 `Raft` 算法。

具体参考：[Raft 算法分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-01-24%20Raft%E7%AE%97%E6%B3%95%E5%88%86%E6%9E%90.md)
生动形象的网站：http://thesecretlivesofdata.com/raft/
论文：https://raft.github.io/raft.pdf

# 参考链接

- 《Redis 设计与实现》- 第 14 章 服务器
- [Redis 官方文档：Replication](https://redis.io/topics/replication)
- [Redis 官方文档：Redis Sentinel Documentation](https://redis.io/topics/sentinel)
- [Raft 算法分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-01-24%20Raft%E7%AE%97%E6%B3%95%E5%88%86%E6%9E%90.md)
- https://raft.github.io/raft.pdf
- http://thesecretlivesofdata.com/raft/

# Redis 源码简洁剖析系列

[最简洁的 Redis 源码剖析系列文章](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-11-17%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2001%20-%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。