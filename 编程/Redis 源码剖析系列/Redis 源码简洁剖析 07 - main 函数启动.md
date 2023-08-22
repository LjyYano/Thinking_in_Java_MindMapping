---
date: 2022-02-05
---


- [前言](#%E5%89%8D%E8%A8%80)
- [问题](#%E9%97%AE%E9%A2%98)
- [阶段 1：基本初始化](#%E9%98%B6%E6%AE%B5-1%E5%9F%BA%E6%9C%AC%E5%88%9D%E5%A7%8B%E5%8C%96)
- [阶段 2：检查哨兵模式，执行 RDB 或 AOF 检测](#%E9%98%B6%E6%AE%B5-2%E6%A3%80%E6%9F%A5%E5%93%A8%E5%85%B5%E6%A8%A1%E5%BC%8F%E6%89%A7%E8%A1%8C-rdb-%E6%88%96-aof-%E6%A3%80%E6%B5%8B)
- [阶段 3：运行参数解析](#%E9%98%B6%E6%AE%B5-3%E8%BF%90%E8%A1%8C%E5%8F%82%E6%95%B0%E8%A7%A3%E6%9E%90)
- [阶段 4：初始化 server](#%E9%98%B6%E6%AE%B5-4%E5%88%9D%E5%A7%8B%E5%8C%96-server)
    - [资源管理](#%E8%B5%84%E6%BA%90%E7%AE%A1%E7%90%86)
    - [初始化数据库](#%E5%88%9D%E5%A7%8B%E5%8C%96%E6%95%B0%E6%8D%AE%E5%BA%93)
    - [创建事件驱动框架](#%E5%88%9B%E5%BB%BA%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E6%A1%86%E6%9E%B6)
- [阶段 5：执行事件驱动框架](#%E9%98%B6%E6%AE%B5-5%E6%89%A7%E8%A1%8C%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E6%A1%86%E6%9E%B6)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)
- [我的公众号](#%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7)

# 前言

main 函数是 Redis 整个运行程序的入口。源码主要在 `server.c` 文件中。

前面 6 篇文章分析了 Redis 的基础数据结构。

- [Redis 源码简洁剖析 01 - 环境配置](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-11-17%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2001%20-%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)
- [Redis 源码简洁剖析 02 - SDS 字符串](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-11-18%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2002%20-%20SDS%20%E5%AD%97%E7%AC%A6%E4%B8%B2.md)
- [Redis 源码简洁剖析 03 - Dict Hash 基础](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-12-03%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2003%20-%20Dict%20Hash%20%E5%9F%BA%E7%A1%80.md)
- [Redis 源码简洁剖析 04 - Sorted Set 有序集合](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-01-29%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2004%20-%20Sorted%20Set%20%E6%9C%89%E5%BA%8F%E9%9B%86%E5%90%88.md)
- [Redis 源码简洁剖析 05 - ziplist 压缩列表](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-02%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2005%20-%20ziplist%20%E5%8E%8B%E7%BC%A9%E5%88%97%E8%A1%A8.md)
- [Redis 源码简洁剖析 06 - quicklist 和 listpack](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-02-04%20Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2006%20-%20quicklist%20%E5%92%8C%20listpack.md)

# 问题

- Redis server 启动后具体会做哪些初始化操作？
- Redis server 初始化时有哪些关键配置项？
- Redis server 如何开始处理客户端请求？

# 阶段 1：基本初始化

基本的初始化工作，包括设置 server 运行的时区等。

```c
//设置时区
setlocale(LC_COLLATE,"");
tzset();
...
//设置随机种子
char hashseed[16];
getRandomHexChars(hashseed,sizeof(hashseed));
dictSetHashFunctionSeed((uint8_t*)hashseed);
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220205171445.png)

# 阶段 2：检查哨兵模式，执行 RDB 或 AOF 检测

Redis Server 可能以`哨兵模式`运行。哨兵模式需要额外的参数配置及初始化。

```c
// 判断 server 是否为「哨兵模式」
if (server.sentinel_mode) {
    // 初始化哨兵配置
    initSentinelConfig();
    // 初始化哨兵模式
    initSentinel();
}
```

此外还会检查是否要执行 RDB 检测或 AOF 检查，这对应了实际运行的程序是 redis-check-rdb 或 redis-check-aof。

```c
// 运行的是 redis-check-rdb
if (strstr(argv[0],"redis-check-rdb") != NULL)
    // 检测 RDB 文件
    redis_check_rdb_main(argc,argv,NULL);
    // 运行的是 redis-check-aof
else if (strstr(argv[0],"redis-check-aof") != NULL)
    // 检测 AOF 文件
    redis_check_aof_main(argc,argv);
```

# 阶段 3：运行参数解析

main 函数会对命令行传入的参数进行解析，并且调用 loadServerConfig 函数，对命令行参数和配置文件中的参数进行合并处理，然后为 Redis 各功能模块的关键参数设置合适的取值。

```c
int main(int argc, char **argv) {
    …
    //保存命令行参数
    for (j = 0; j < argc; j++) server.exec_argv[j] = zstrdup(argv[j]);
    …
    if (argc >= 2) {
    …
        //对每个运行时参数进行解析
        while(j != argc) {
            …
        }
    …
    loadServerConfig(configfile,options);
}
```

loadServerConfig 函数是在 config.c 文件中实现的，该函数是以 Redis 配置文件和命令行参数的解析字符串为参数，将配置文件中的所有配置项读取出来，形成字符串。

# 阶段 4：初始化 server

调用 `initServer` 函数，对 server 运行时的各种资源进行初始化工作。这主要包括：
- server 资源管理所需的数据结构初始化
- 键值对数据库初始化
- server 网络框架初始化

接着会再次判断是否为「哨兵模式」：
- 是哨兵模式，调用 sentinelIsRunning 函数，设置启动哨兵模式
- 不是哨兵模式，调用 loadDataFromDisk 函数，从磁盘加载 AOF 或 RDB 文件，恢复之前的数据

```c
// 初始化 server
initServer();
……

if (!server.sentinel_mode) {
    ……
    InitServerLast();
    // 从磁盘加载数据
    loadDataFromDisk();
    ……
} else {
    ……
    sentinelIsRunning();
    ……
}
```

## 资源管理

和 server 连接的客户端、从库等，Redis 用作缓存时的替换候选集，以及 server 运行时的状态信息，这些资源的管理信息都会在 initServer 函数中进行初始化。

## 初始化数据库

因为一个 Redis 实例可以同时运行多个数据库，所以 initServer 函数会使用一个循环，依次为每个数据库创建相应的数据结构。

```c
for (j = 0; j < server.dbnum; j++) {
    // 创建全局哈希表
    server.db[j].dict = dictCreate(&dbDictType,NULL);
    // 创建过期 key 的信息表
    server.db[j].expires = dictCreate(&dbExpiresDictType,NULL);
    server.db[j].expires_cursor = 0;
    // 为被 BLPOP 阻塞的 key 创建信息表
    server.db[j].blocking_keys = dictCreate(&keylistDictType,NULL);
    // 为将执行 PUSH 的阻塞 key 创建信息表
    server.db[j].ready_keys = dictCreate(&objectKeyPointerValueDictType,NULL);
    // 为被 MULTI/WATCH 操作监听的 key 创建信息表
    server.db[j].watched_keys = dictCreate(&keylistDictType,NULL);
    ……
}
```

## 创建事件驱动框架

针对每个监听 IP 上可能发生的客户端连接，都创建了监听事件，用来监听客户端连接请求。同时，initServer 为监听事件设置了相应的处理函数 acceptTcpHandler。

这样一来，只要有客户端连接到 server 监听的 IP 和端口，事件驱动框架就会检测到有连接事件发生，然后调用 acceptTcpHandler 函数来处理具体的连接。

```c
//创建事件循环框架
server.el = aeCreateEventLoop(server.maxclients+CONFIG_FDSET_INCR);
…
//开始监听设置的网络端口
if (server.port != 0 &&
        listenToPort(server.port,server.ipfd,&server.ipfd_count) == C_ERR)
        exit(1);
…
//为 server 后台任务创建定时事件
if (aeCreateTimeEvent(server.el, 1, serverCron, NULL, NULL) == AE_ERR) {
        serverPanic("Can't create event loop timers.");
        exit(1);
}
…
```

# 阶段 5：执行事件驱动框架

高效处理高并发的客户端连接请求，Redis 采用了事件驱动框架，来并发处理不同客户端的连接和读写请求。main 函数最后会调用 `aeMain` 函数进入事件驱动框架，循环处理各种触发的事件。

```c
// 事件驱动框架，循环处理各种触发的事件
aeMain(server.el);
// 循环结束，删除 eventLoop
aeDeleteEventLoop(server.el);
```

`aeMain` 函数核心调用了 `aeProcessEvents` 函数。aeProcessEvents 函数的具体源码将在之后的文章中分析。

```c
void aeMain(aeEventLoop *eventLoop) {
    eventLoop->stop = 0;
    // 循环调用
    while (!eventLoop->stop) {
        // 核心函数，处理事件的逻辑
        aeProcessEvents(eventLoop, AE_ALL_EVENTS|
                                   AE_CALL_BEFORE_SLEEP|
                                   AE_CALL_AFTER_SLEEP);
    }
}
```

# 参考链接

- [极客时间：08 | Redis server 启动后会做哪些操作？](https://time.geekbang.org/column/article/406556)

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

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)