---
date: 2022-02-06
---


- [aeEventLoop](#aeeventloop)
- [IO 事件处理](#io-%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86)
    - [IO 事件创建](#io-%E4%BA%8B%E4%BB%B6%E5%88%9B%E5%BB%BA)
    - [读事件处理](#%E8%AF%BB%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86)
    - [写事件处理](#%E5%86%99%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86)
- [时间事件处理](#%E6%97%B6%E9%97%B4%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86)
    - [时间事件定义](#%E6%97%B6%E9%97%B4%E4%BA%8B%E4%BB%B6%E5%AE%9A%E4%B9%89)
    - [时间事件创建](#%E6%97%B6%E9%97%B4%E4%BA%8B%E4%BB%B6%E5%88%9B%E5%BB%BA)
    - [时间事件回调函数](#%E6%97%B6%E9%97%B4%E4%BA%8B%E4%BB%B6%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0)
    - [时间事件的触发处理](#%E6%97%B6%E9%97%B4%E4%BA%8B%E4%BB%B6%E7%9A%84%E8%A7%A6%E5%8F%91%E5%A4%84%E7%90%86)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)
- [我的公众号](#%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7)

# aeEventLoop

Redis 事件驱动框架对应的数据结构，在 `ae.h` 中定义，记录了运行过程信息，有 2 个记录事件的变量：
- `IO 事件`：aeFileEvent 类型的指针 *events
- `时间事件`：aeTimeEvent 类型的指针 *timeEventHead，按照一定时间周期触发的事件

```c
/* State of an event based program */
typedef struct aeEventLoop {
    ……
    // IO 事件数组
    aeFileEvent *events;
    // 已触发事件数组
    aeFiredEvent *fired;
    // 时间事件的链表投
    aeTimeEvent *timeEventHead;
    // polling api 相关数据
    void *apidata;
    // 进入事件循环流程前执行的函数
    aeBeforeSleepProc *beforesleep;
    // 进入事件循环流程后执行的函数
    aeBeforeSleepProc *aftersleep;
} aeEventLoop;
```

在 `server.c` 的 initServer 函数中调用 `aeCreateEventLoop` 进行初始化。

```c
// 创建事件循环框架
server.el = aeCreateEventLoop(server.maxclients + CONFIG_FDSET_INCR);
```

```c
aeEventLoop *aeCreateEventLoop(int setsize) {
    aeEventLoop *eventLoop;
    int i;

    monotonicInit();    /* just in case the calling app didn't initialize */

    // 创建 eventLoop 并分配内存空间
    if ((eventLoop = zmalloc(sizeof(*eventLoop))) == NULL) goto err;
    eventLoop->events = zmalloc(sizeof(aeFileEvent) * setsize);
    eventLoop->fired = zmalloc(sizeof(aeFiredEvent) * setsize);
    if (eventLoop->events == NULL || eventLoop->fired == NULL) goto err;
    eventLoop->setsize = setsize;
    ……

    // 调用 aeApiCreate 函数
    if (aeApiCreate(eventLoop) == -1) goto err;
    // 把所有网络 IO 事件对应文件描述符的掩码，初始化为 AE_NONE，暂时不对任何事件进行监听
    for (i = 0; i < setsize; i++)
        eventLoop->events[i].mask = AE_NONE;
    return eventLoop;

    err:
    ……
    return NULL;
}
```

核心是调用 `aeApiCreate` 函数。aeApiCreate 函数封装了操作系统提供的 IO 多路复用函数，假设 Redis 运行在 Linux 操作系统上，并且 IO 多路复用机制是 epoll，此时会调用 `epoll_create` 创建 epoll 实例，同时会创建 epoll_event 结构的数组，数组大小等于参数 setsize。

```c
typedef struct aeApiState {
    // epoll 实例的描述符
    int epfd;
    // epoll_event 结构体数组，记录监听事件
    struct epoll_event *events;
} aeApiState;

static int aeApiCreate(aeEventLoop *eventLoop) {
    aeApiState *state = zmalloc(sizeof(aeApiState));

    if (!state) return -1;
    // 将 epoll_event 数组保存在 aeApiState 中
    state->events = zmalloc(sizeof(struct epoll_event)*eventLoop->setsize);
    ……
    // 将 epoll 实例描述符保存在 aeApiState 中
    state->epfd = epoll_create(1024); 
    ……
    // 将 aeApiState 变量赋值给 eventLoop 的 apidata
    eventLoop->apidata = state;
}
```

aeApiCreate 函数最后将创建好的 aeApiState 变量赋值给 eventLoop 的 apidata，之后 eventLoop 结构体中就有了 `epoll 实例` 和 `epoll_event 数组`信息，可以基于 epoll 创建和处理事件了。

```c
// 将 aeApiState 变量赋值给 eventLoop 的 apidata
eventLoop->apidata = state;
```

# IO 事件处理

Redis 的 IO 事件分 3 类：
1. `可读事件`
2. `可写事件`
3. `屏障事件`：反转事件的处理顺序。

IO 事件的数据结构是 `aeFileEvent` 结构体，IO 事件的创建是通过 `aeCreateFileEvent` 函数来完成的。

```c
typedef struct aeFileEvent {
    // 事件类型的掩码，AE_(READABLE|WRITABLE|BARRIER)
    int mask;
    // AE_READABLE 事件的处理函数
    aeFileProc *rfileProc;
    // AE_WRITABLE 事件的处理函数
    aeFileProc *wfileProc;
    // 指向客户端私有数据
    void *clientData;
} aeFileEvent;
```

## IO 事件创建

```c
int aeCreateFileEvent(aeEventLoop *eventLoop, int fd, int mask,
        aeFileProc *proc, void *clientData)
{
    // 错误处理
    if (fd >= eventLoop->setsize) {
        errno = ERANGE;
        return AE_ERR;
    }

    aeFileEvent *fe = &eventLoop->events[fd];

    // 核心
    if (aeApiAddEvent(eventLoop, fd, mask) == -1)
        return AE_ERR;
    fe->mask |= mask;
    if (mask & AE_READABLE) fe->rfileProc = proc;
    if (mask & AE_WRITABLE) fe->wfileProc = proc;
    fe->clientData = clientData;
    if (fd > eventLoop->maxfd)
        eventLoop->maxfd = fd;
    return AE_OK;
}
```

入参有 5 个：
- `*eventLoop`：循环流程结构体
- `fd`：IO 事件对应的文件描述符
- `mask`：事件类型掩码
- `*proc`：事件处理回调函数
- `*clientData`：事件私有数据

aeCreateFileEvent 函数会先根据传入的文件描述符 fd，在 eventLoop 的 IO 事件数组中，获取该描述符关联的 IO 事件指针变量* fe，如下所示：

```c
aeFileEvent *fe = &eventLoop->events[fd];
```

之后 aeCreateFileEvent 函数会调用 aeApiAddEvent 函数，添加要监听的事件：

```c
if (aeApiAddEvent(eventLoop, fd, mask) == -1)
    return AE_ERR;
```

aeApiAddEvent 函数实际上会调用操作系统提供的 `IO 多路复用`函数，来完成事件的添加。我们还是假设 Redis 实例运行在使用 epoll 机制的 Linux 上，那么 aeApiAddEvent 函数就会调用 `epoll_ctl` 函数，添加要监听的事件。aeApiAddEvent 函数源码如下：

```c
static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee = {0};
    /* If the fd was already monitored for some event, we need a MOD
     * operation. Otherwise we need an ADD operation. */
    int op = eventLoop->events[fd].mask == AE_NONE ?
             EPOLL_CTL_ADD : EPOLL_CTL_MOD;

    ee.events = 0;
    mask |= eventLoop->events[fd].mask;
    // 将可读或可写 IO 事件类型转换为 epoll 监听的类型 EPOLLIN 或 EPOLLOUT
    if (mask & AE_READABLE) ee.events |= EPOLLIN;
    if (mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    // 将要监听的文件描述符赋值给 epoll_event
    ee.data.fd = fd;
    // 增加新的观察事件
    if (epoll_ctl(state->epfd, op, fd, &ee) == -1) return -1;
    return 0;
}
```

至此事件驱动框架已经基于 epoll，封装了 IO 事件的创建。

## 读事件处理

Redis server 接收到客户端的连接请求时，会使用注册好的 `acceptTcpHandler` 函数进行处理。acceptTcpHandler 函数是在 `networking.c` 文件中，接受客户端连接并`创建已连接套接字 cfd`。

最终会调用 `acceptCommonHandler` 函数，其会调用 createClient 函数，最终会调用到 `aeCreateFileEvent` 函数，创建 `AE_READABLE` 的监听事件，回调函数是 `readQueryFromClient`。

至此事件驱动框架就增加了一个对客户端已连接套接字的监听。之后客户端有请求发送到 Redis server，框架就会回调 readQueryFromClient 函数处理请求。

```c
void acceptTcpHandler(aeEventLoop *el, int fd, void *privdata, int mask) {
    ……

    // 每次处理 1000 个
    while(max--) {
        cfd = anetTcpAccept(server.neterr, fd, cip, sizeof(cip), &cport);
        ……
        acceptCommonHandler(connCreateAcceptedSocket(cfd),0,cip);
    }
}
```

acceptCommonHandler 函数会调用到 createClient：

```c
static void acceptCommonHandler(connection *conn, int flags, char *ip) {
    ……
    /* Create connection and client */
    if ((c = createClient(conn)) == NULL) {
        ……
        connClose(conn); /* May be already closed, just ignore errors */
        return;
    }
}
```

createClient 函数会创建监听事件：

```c
client *createClient(connection *conn) {
    client *c = zmalloc(sizeof(client));

    /* passing NULL as conn it is possible to create a non connected client.
     * This is useful since all the commands needs to be executed
     * in the context of a client. When commands are executed in other
     * contexts (for instance a Lua script) we need a non connected client. */
    if (conn) {
        connNonBlock(conn);
        connEnableTcpNoDelay(conn);
        if (server.tcpkeepalive)
            connKeepAlive(conn,server.tcpkeepalive);
        connSetReadHandler(conn, readQueryFromClient);
        connSetPrivateData(conn, c);
    }
    ……
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220207103202.png?x-oss-process=style/yano)

## 写事件处理

readQueryFromClient 函数在 `networking.c` 中，收到客户端请求后，处理客户端命令，并将返回的数据写入客户端输出缓冲区。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220207171803.png?x-oss-process=style/yano&x-oss-process=style/yano)

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

在 aeProcessEvents 函数中，有 IO 事件发生时，会先判断是否有 `beforesleep` 函数：

```c
int aeProcessEvents(aeEventLoop *eventLoop, int flags)
{
    ……
    if (eventLoop->beforesleep != NULL && flags & AE_CALL_BEFORE_SLEEP)
        eventLoop->beforesleep(eventLoop);
    ……
```

beforeSleep 函数调用的 `handleClientsWithPendingWrites` 函数，会遍历每一个待写回数据的客户端，然后调用 `writeToClient` 函数，将客户端输出缓冲区中的数据写回。

从 aeProcessEvents 函数的代码中，我们可以看到该函数会调用 aeApiPoll 函数，查询监听的文件描述符中，有哪些已经就绪。一旦有描述符就绪，aeProcessEvents 函数就会根据事件的可读或可写类型，调用相应的回调函数进行处理。

```c
int aeProcessEvents(aeEventLoop *eventLoop, int flags)
{
    ……
    // 有 IO 事件发生 || 紧急时间事件发生
    if (eventLoop->maxfd != -1 ||
        ((flags & AE_TIME_EVENTS) && !(flags & AE_DONT_WAIT))) {
        ……
        // 调用 aeApiPoll 获取就绪的描述符
        numevents = aeApiPoll(eventLoop, tvp);

        /* After sleep callback. */
        if (eventLoop->aftersleep != NULL && flags & AE_CALL_AFTER_SLEEP)
            eventLoop->aftersleep(eventLoop);

        for (j = 0; j < numevents; j++) {
            aeFileEvent *fe = &eventLoop->events[eventLoop->fired[j].fd];
            ……

            // 如果触发的是可读事件，调用事件注册时设置的读事件回调处理函数
            if (!invert && fe->mask & mask & AE_READABLE) {
                fe->rfileProc(eventLoop, fd, fe->clientData, mask);
                fired++;
                fe = &eventLoop->events[fd]; /* Refresh in case of resize. */
            }

            // 如果触发的是可写事件，调用事件注册时设置的写事件回调处理函数
            if (fe->mask & mask & AE_WRITABLE) {
                if (!fired || fe->wfileProc != fe->rfileProc) {
                    fe->wfileProc(eventLoop, fd, fe->clientData, mask);
                    fired++;
                }
            }
```

整个流程就完成了。

# 时间事件处理

## 时间事件定义

```c
/* Time event structure */
typedef struct aeTimeEvent {
    // 时间事件 ID
    long long id;
    // 事件到达的时间戳
    monotime when;
    // 事件到达后的处理函数
    aeTimeProc *timeProc;
    // 事件结束后的处理函数
    aeEventFinalizerProc *finalizerProc;
    // 事件相关的私有数据
    void *clientData;
    // 链表前向指针
    struct aeTimeEvent *prev;
    // 链表后向指针
    struct aeTimeEvent *next;
    int refcount;
} aeTimeEvent;
```

```c
typedef int aeTimeProc(struct aeEventLoop *eventLoop, long long id, void *clientData);
typedef void aeEventFinalizerProc(struct aeEventLoop *eventLoop, void *clientData);
```

## 时间事件创建

```c
long long aeCreateTimeEvent(aeEventLoop *eventLoop, long long milliseconds,
        aeTimeProc *proc, void *clientData,
        aeEventFinalizerProc *finalizerProc)
{
    long long id = eventLoop->timeEventNextId++;
    aeTimeEvent *te;

    te = zmalloc(sizeof(*te));
    if (te == NULL) return AE_ERR;
    te->id = id;
    te->when = getMonotonicUs() + milliseconds * 1000;
    te->timeProc = proc;
    te->finalizerProc = finalizerProc;
    te->clientData = clientData;
    te->prev = NULL;
    te->next = eventLoop->timeEventHead;
    te->refcount = 0;
    if (te->next)
        te->next->prev = te;
    eventLoop->timeEventHead = te;
    return id;
}
```

核心就是创建 aeTimeEvent 指针 te，并将 te 放入 eventLoop 的时间事件的链表头：

```c
eventLoop->timeEventHead = te;
```

`aeCreateTimeEvent` 函数是在 `server.c` 文件中的 `initServer` 函数中调用的：

```c
// 为 server 后台任务创建定时事件
if (aeCreateTimeEvent(server.el, 1, serverCron, NULL, NULL) == AE_ERR) {
    serverPanic("Can't create event loop timers.");
    exit(1);
}
```

## 时间事件回调函数

`serverCron` 在 `server.c` 中：
- 调用`后台任务函数`
- 调用 `databaseCron 函数`，处理过期 key 或 rehash

```c
/* We need to do a few operations on clients asynchronously. */
// 执行客户端的异步操作
clientsCron();

/* Handle background operations on Redis databases. */
// 执行数据库的后台操作
databasesCron();
```

## 时间事件的触发处理

事件驱动框架的 aeMain 函数会循环调用 aeProcessEvents 函数，来处理各种事件。aeProcessEvents 函数的最后，会调用 `processTimeEvents` 函数处理时间任务。

```c
// 检查是否有时间事件
if (flags & AE_TIME_EVENTS)
    processed += processTimeEvents(eventLoop);
```

processTimeEvents 函数的主体逻辑，就是从 eventLoop 的时间事件的链表逐一取出每个事件，根据当前时间判断该事件的时间是否满足触发条件。如果满足就处理。

```c
static int processTimeEvents(aeEventLoop *eventLoop) {
    ……
    // 从时间事件链表中，取出事件
    te = eventLoop->timeEventHead;
    ……
    while(te) {
        ……

        // 当前时间已经满足事件的触发时间戳
        if (te->when <= now) {
            ……
            // 调用回调函数
            retval = te->timeProc(eventLoop, id, te->clientData);
            ……
            now = getMonotonicUs();
            if (retval != AE_NOMORE) {
                // 处理后，再次更新时间
                te->when = now + retval * 1000;
            }
            ……
        }
        // 获取下一个事件
        te = te->next;
    }
    return processed;
}
```

# 参考链接

- [极客时间：11 | Redis 事件驱动框架（下）：Redis 有哪些事件？](https://time.geekbang.org/column/article/408857)

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