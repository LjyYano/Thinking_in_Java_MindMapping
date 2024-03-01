---
date: 2022-02-05
---


# IO 多路复用

关于 select, poll, epoll，[​网络 IO 演变发展过程和模型介绍](https://mp.weixin.qq.com/s/EDzFOo3gcivOe_RgipkTkQ) 这篇文章讲得很好，本文就不浪费笔墨了。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-02-19-11-29-26.png)

Redis 针对不同操作系统，选择不同的 IO 多路复用机制，具体代码在 `ae.c`。

```c
/* Include the best multiplexing layer supported by this system.
 * The following should be ordered by performances, descending. */
#ifdef HAVE_EVPORT
#include "ae_evport.c"
#else
    #ifdef HAVE_EPOLL
    #include "ae_epoll.c"
    #else
        #ifdef HAVE_KQUEUE
        #include "ae_kqueue.c"
        #else
        #include "ae_select.c"
        #endif
    #endif
#endif
```

从代码中可看到，有 epoll 就会使用 `epoll`（Linux）；没有的话则会使用 `kqueue`（MacOS）或 `select`（Windows）。

# 源码分析

由于我的开发环境是 Mac，所以分析 `ae_kqueue.c` 文件。在 Linux 系统下可以分析 `ae_epoll.c` 文件。kqueue 的详细介绍 👉 [Kernel Queues and Events](https://people.freebsd.org/~jmg/kq.html)。

```c
typedef struct aeApiState {
    int kqfd;
    struct kevent *events;

    /* Events mask for merge read and write event.
     * To reduce memory consumption, we use 2 bits to store the mask
     * of an event, so that 1 byte will store the mask of 4 events. */
    char *eventsMask;
} aeApiState;
```

`kevent` 定义在 `event.h` 源文件中。

```c
struct kevent {
	uintptr_t       ident;  /* identifier for this event */
	int16_t         filter; /* filter for event */
	uint16_t        flags;  /* general flags */
	uint32_t        fflags; /* filter-specific flags */
	intptr_t        data;   /* filter-specific data */
	void            *udata; /* opaque user data identifier */
};
```

具体源码 // todo。

# 参考链接

- [极客时间：09 | Redis 事件驱动框架（上）：何时使用 select、poll、epoll？](https://time.geekbang.org/column/article/407901)
- [深入剖析 Netty 源码设计（一）——深入理解 select poll epoll 机制](https://www.6aiq.com/article/1548222475606)
- [​网络 IO 演变发展过程和模型介绍](https://mp.weixin.qq.com/s/EDzFOo3gcivOe_RgipkTkQ)
- [Kernel Queues and Events](https://people.freebsd.org/~jmg/kq.html)
- [Kernel Queues: An Alternative to File System Events](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/KernelQueues/KernelQueues.html#//apple_ref/doc/uid/TP40005289-CH5-SW2)

# Redis 源码简洁剖析系列

- [Redis 7.0.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%207.0.md)
- [Redis 源码简洁剖析 01 - 环境配置. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2001%20-%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)
- [Redis 源码简洁剖析 02 - SDS 字符串. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2002%20-%20SDS%20%E5%AD%97%E7%AC%A6%E4%B8%B2.md)
- [Redis 源码简洁剖析 03 - Dict Hash 基础. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2003%20-%20Dict%20Hash%20%E5%9F%BA%E7%A1%80.md)
- [Redis 源码简洁剖析 04 - Sorted Set 有序集合. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2004%20-%20Sorted%20Set%20%E6%9C%89%E5%BA%8F%E9%9B%86%E5%90%88.md)
- [Redis 源码简洁剖析 05 - ziplist 压缩列表. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2005%20-%20ziplist%20%E5%8E%8B%E7%BC%A9%E5%88%97%E8%A1%A8.md)
- [Redis 源码简洁剖析 06 - quicklist 和 listpack.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2006%20-%20quicklist%20%E5%92%8C%20listpack.md)
- [Redis 源码简洁剖析 07 - main 函数启动. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2007%20-%20main%20%E5%87%BD%E6%95%B0%E5%90%AF%E5%8A%A8.md)
- [Redis 源码简洁剖析 08 - epoll.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2008%20-%20epoll.md)
- [Redis 源码简洁剖析 09 - Reactor 模型. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2009%20-%20Reactor%20%E6%A8%A1%E5%9E%8B.md)
- [Redis 源码简洁剖析 10 - aeEventLoop 及事件. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2010%20-%20aeEventLoop%20%E5%8F%8A%E4%BA%8B%E4%BB%B6.md)
- [Redis 源码简洁剖析 11 - 主 IO 线程及 Redis 6.0 多 IO 线程. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2011%20-%20%E4%B8%BB%20IO%20%E7%BA%BF%E7%A8%8B%E5%8F%8A%20Redis%206.0%20%E5%A4%9A%20IO%20%E7%BA%BF%E7%A8%8B.md)
- [Redis 源码简洁剖析 12 - 一条命令的处理过程. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2012%20-%20%E4%B8%80%E6%9D%A1%E5%91%BD%E4%BB%A4%E7%9A%84%E5%A4%84%E7%90%86%E8%BF%87%E7%A8%8B.md)
- [Redis 源码简洁剖析 13 - RDB 文件. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2013%20-%20RDB%20%E6%96%87%E4%BB%B6.md)
- [Redis 源码简洁剖析 14 - Redis 持久化. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2014%20-%20Redis%20%E6%8C%81%E4%B9%85%E5%8C%96.md)
- [Redis 源码简洁剖析 15 - AOF.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2015%20-%20AOF.md)
- [Redis 源码简洁剖析 16 - 客户端. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2016%20-%20%E5%AE%A2%E6%88%B7%E7%AB%AF.md)
- [Redis 源码简洁剖析 17 - 服务器. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2017%20-%20%E6%9C%8D%E5%8A%A1%E5%99%A8.md)
- [Redis 源码简洁剖析 18 - 复制、哨兵 Sentinel.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2018%20-%20%E5%A4%8D%E5%88%B6%E3%80%81%E5%93%A8%E5%85%B5%20Sentinel.md)

[Java 编程思想 - 最全思维导图 - GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注 `^_^`

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)