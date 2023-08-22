---
date: 2022-06-04
---


- [新特性概述](#新特性概述)
  - [安装 7.0](#安装-70)
  - [核心特性](#核心特性)
- [Function](#function)
- [Multi-part AOF](#multi-part-aof)
- [Sharded-pubsub](#sharded-pubsub)
- [参考链接](#参考链接)
- [Redis 源码简洁剖析系列](#redis-源码简洁剖析系列)
- [我的公众号](#我的公众号)

# 新特性概述

## 安装 7.0

https://redis.io/download/

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-06-04-12-06-34.png?x-oss-process=style/yano)

## 核心特性

[https://github.com/redis/redis/blob/7.0/00-RELEASENOTES](https://github.com/redis/redis/blob/7.0/00-RELEASENOTES)

- Function
- Multi-part AOF
- Sharded-pubsub

# Function

[Redis functions](https://redis.io/docs/manual/programmability/functions-intro/)

Function 是 Redis 脚本方案的全新实现，在 Redis 7.0 之前用户只能使用 EVAL 命令族来执行 Lua 脚本，但是 **Redis 对 Lua 脚本的持久化和主从复制一直是 undefined 状态，在各个大版本甚至 release 版本中也都有不同的表现。** 因此社区也直接要求用户在使用 Lua 脚本时必须在本地保存一份（这也是最为安全的方式），以防止实例重启、主从切换时可能造成的 Lua 脚本丢失，维护 Redis 中的 Lua 脚本一直是广大用户的痛点。

Function 的出现很好的对 Lua 脚本进行了补充，它允许用户向 Redis 加载自定义的函数库，一方面相对于 EVALSHA 的调用方式用户自定义的函数名可以有更为清晰的语义，另一方面 Function **加载的函数库明确会进行主从复制和持久化存储，彻底解决了过去 Lua 脚本在持久化上含糊不清的问题。**

那么自 7.0 开始，Function 命令族和 EVAL 命令族有了各自明确的定义：FUNCTION LOAD 会把函数库自动进行主从复制和持久化存储；而 SCRIPT LOAD 则不会进行持久化和主从复制，脚本仅保存在当前执行节点。并且社区也在计划后续版本中让 Function 支持更多语言，例如 JavaScript、Python 等，敬请期待。

总的来说，**Function 在 7.0 中被设计为数据的一部分，因此能够被保存在 RDB、AOF 文件中，也能通过主从复制将 Function 由主库复制到所有从库，可以有效解决之前 Lua 脚本丢失的问题**，我们也非常建议大家逐步将 Redis 中的 Lua 脚本替换为 Function。

# Multi-part AOF

[Redis persistence # Append-only file](https://redis.io/docs/manual/persistence/#append-only-file)

6.0 AOF 实现：[Redis 源码简洁剖析 15 - AOF](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-15%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2015%20-%20AOF.md)

> Since Redis 7.0.0, Redis uses a multi part AOF mechanism. That is, the original single AOF file is split into base file (at most one) and incremental files (there may be more than one). The base file represents an initial (RDB or AOF format) snapshot of the data present when the AOF is [rewritten](https://redis.io/docs/manual/persistence/#log-rewriting). The incremental files contains incremental changes since the last base AOF file was created. All these files are put in a separate directory and are tracked by a manifest file.

AOF 是 Redis 数据持久化的核心解决方案，其本质是不断追加数据修改操作的 redo log，那么既然是不断追加就需要做回收也即 compaction，在 Redis 中称为 AOF rewrite。

然而 AOF rewrite 期间的增量数据如何处理一直是个问题，在过去 rewrite 期间的增量数据需要在内存中保留，rewrite 结束后再把这部分增量数据写入新的 AOF 文件中以保证数据完整性。可以看出来 **AOF rewrite 会额外消耗内存和磁盘 IO，这也是 Redis AOF rewrite 的痛点**，虽然之前也进行过多次改进但是资源消耗的本质问题一直没有解决。

阿里云的 Redis 企业版在最初也遇到了这个问题，在内部经过多次迭代开发，实现了 Multi-part AOF 机制来解决，同时也贡献给了社区并随此次 7.0 发布。具体方法是**采用 base（全量数据）+inc（增量数据）独立文件存储的方式，彻底解决内存和 IO 资源的浪费，同时也支持对历史 AOF 文件的保存管理，结合 AOF 文件中的时间信息还可以实现 PITR 按时间点恢复（阿里云企业版 Tair 已支持）**，这进一步增强了 Redis 的数据可靠性，满足用户数据回档等需求。

# Sharded-pubsub

[Redis Pub/Sub # sharded-pubsub](https://redis.io/docs/manual/pubsub/#sharded-pubsub)

Redis 自 2.0 开始便支持发布订阅机制，使用 pubsub 命令族用户可以很方便地建立消息通知订阅系统，但是 **在 cluster 集群模式下 Redis 的 pubsub 存在一些问题，最为显著的就是在大规模集群中带来的广播风暴。**

Redis 的 pubsub 是按 channel 频道进行发布订阅，然而在集群模式下 channel 不被当做数据处理，也即不会参与到 hash 值计算无法按 slot 分发，所以在集群模式下 Redis 对用户发布的消息采用的是在集群中广播的方式。

那么问题显而易见，假如一个集群有 100 个节点，用户在节点 1 对某个 channel 进行 publish 发布消息，该节点就需要把消息广播给集群中其他 99 个节点，如果其他节点中只有少数节点订阅了该频道，那么绝大部分消息都是无效的，这对网络、CPU 等资源造成了极大的浪费。

Sharded-pubsub 便是用来解决这个问题，意如其名，sharded-pubsub 会把 channel 按分片来进行分发，一个分片节点只负责处理属于自己的 channel 而不会进行广播，以很简单的方法避免了资源的浪费。

# 参考链接

- [Redis 7.0 Is Out!](https://redis.com/blog/redis-7-generally-available/)
- [Redis 7.0: An Evolution Across Multiple Fronts](https://redis.com/blog/introducing-redis-7/)
- [从 Redis7.0 发布看 Redis 的过去与未来](https://mp.weixin.qq.com/s/RnoPPL7jiFSKkx3G4p57Pg)

# Redis 源码简洁剖析系列

- [Redis 源码简洁剖析 01 - 环境配置](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-11-17%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2001%20-%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)
- [Redis 源码简洁剖析 02 - SDS 字符串](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-11-18%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2002%20-%20SDS%20%E5%AD%97%E7%AC%A6%E4%B8%B2.md)
- [Redis 源码简洁剖析 03 - Dict Hash 基础](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-12-03%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2003%20-%20Dict%20Hash%20%E5%9F%BA%E7%A1%80.md)
- [Redis 源码简洁剖析 04 - Sorted Set 有序集合](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-01-29%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2004%20-%20Sorted%20Set%20%E6%9C%89%E5%BA%8F%E9%9B%86%E5%90%88.md)
- [Redis 源码简洁剖析 05 - ziplist 压缩列表](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-02%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2005%20-%20ziplist%20%E5%8E%8B%E7%BC%A9%E5%88%97%E8%A1%A8.md)
- [Redis 源码简洁剖析 06 - quicklist 和 listpack](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-04%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2006%20-%20quicklist%20%E5%92%8C%20listpack.md)
- [Redis 源码简洁剖析 07 - main 函数启动](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-05%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2007%20-%20main%20%E5%87%BD%E6%95%B0%E5%90%AF%E5%8A%A8.md)
- [Redis 源码简洁剖析 08 - epoll](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-05%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2008%20-%20epoll.md)
- [Redis 源码简洁剖析 09 - Reactor 模型](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-06%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2009%20-%20Reactor%20%E6%A8%A1%E5%9E%8B.md)
- [Redis 源码简洁剖析 10 - aeEventLoop 及事件](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-06%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2010%20-%20aeEventLoop%20%E5%8F%8A%E4%BA%8B%E4%BB%B6.md)
- [Redis 源码简洁剖析 11 - 主 IO 线程及 Redis 6.0 多 IO 线程](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-08%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2011%20-%20%E4%B8%BB%20IO%20%E7%BA%BF%E7%A8%8B%E5%8F%8A%20Redis%206.0%20%E5%A4%9A%20IO%20%E7%BA%BF%E7%A8%8B.md)
- [Redis 源码简洁剖析 12 - 一条命令的处理过程](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-09%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2012%20-%20%E4%B8%80%E6%9D%A1%E5%91%BD%E4%BB%A4%E7%9A%84%E5%A4%84%E7%90%86%E8%BF%87%E7%A8%8B.md)
- [Redis 源码简洁剖析 13 - RDB 文件](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-10%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2013%20-%20RDB%20%E6%96%87%E4%BB%B6.md)
- [Redis 源码简洁剖析 14 - Redis 持久化](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-15%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2014%20-%20Redis%20%E6%8C%81%E4%B9%85%E5%8C%96.md)
- [Redis 源码简洁剖析 15 - AOF](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-15%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2015%20-%20AOF.md)
- [Redis 源码简洁剖析 16 - 客户端](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-20%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2016%20-%20%E5%AE%A2%E6%88%B7%E7%AB%AF.md)
- [Redis 源码简洁剖析 17 - 服务器](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-21%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2017%20-%20%E6%9C%8D%E5%8A%A1%E5%99%A8.md)
- [Redis 源码简洁剖析 18 - 复制、哨兵 Sentinel](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-26%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2018%20-%20%E5%A4%8D%E5%88%B6%E3%80%81%E5%93%A8%E5%85%B5%20Sentinel.md)

[Java 编程思想-最全思维导图-GitHub](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)