---
date: 2022-02-20
---


- [整体概述](#%E6%95%B4%E4%BD%93%E6%A6%82%E8%BF%B0)
- [客户端属性](#%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%B1%9E%E6%80%A7)
    - [套接字描述符](#%E5%A5%97%E6%8E%A5%E5%AD%97%E6%8F%8F%E8%BF%B0%E7%AC%A6)
    - [标志](#%E6%A0%87%E5%BF%97)
    - [输入缓冲区](#%E8%BE%93%E5%85%A5%E7%BC%93%E5%86%B2%E5%8C%BA)
    - [命名及命令参数](#%E5%91%BD%E5%90%8D%E5%8F%8A%E5%91%BD%E4%BB%A4%E5%8F%82%E6%95%B0)
    - [命令的实现函数](#%E5%91%BD%E4%BB%A4%E7%9A%84%E5%AE%9E%E7%8E%B0%E5%87%BD%E6%95%B0)
    - [输出缓冲区](#%E8%BE%93%E5%87%BA%E7%BC%93%E5%86%B2%E5%8C%BA)
- [客户端的创建与关闭](#%E5%AE%A2%E6%88%B7%E7%AB%AF%E7%9A%84%E5%88%9B%E5%BB%BA%E4%B8%8E%E5%85%B3%E9%97%AD)
    - [创建普通客户端](#%E5%88%9B%E5%BB%BA%E6%99%AE%E9%80%9A%E5%AE%A2%E6%88%B7%E7%AB%AF)
    - [关闭普通客户端](#%E5%85%B3%E9%97%AD%E6%99%AE%E9%80%9A%E5%AE%A2%E6%88%B7%E7%AB%AF)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)
- [我的公众号](#%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7)

# 整体概述

Redis 一个服务器可以和多个客户端建立网络连接，每个客户端都可以向服务器发送命令请求，服务器接收客户端的命令，处理后将结果返回给客户端。

Redis 的文件事件处理器使用 `I/O 多路复用`，Redis 使用`单线程单进程`处理命令请求，与多个客户端进行网络通信。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220101513.png?x-oss-process=style/yano)

每个连接了 Redis 服务器的客户端，服务器都建立了一个 `redisClient` 结构的`客户端状态`，保存了客户端当前的状态信息，以及执行相关功能时用到的数据结构。

Redis 服务器状态结构的 clients 属性是一个链表，保存了所有与服务器连接的客户端状态。

```c
struct redisServer {
    ……
    // 保存了所有客户端状态的链表
    list *clients;
    ……
};
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221084841.png?x-oss-process=style/yano)

# 客户端属性

先贴一下 client 完整的数据结构：

```c
typedef struct client {
    uint64_t id;            /* Client incremental unique ID. */
    connection *conn;
    int resp;               /* RESP protocol version. Can be 2 or 3. */
    redisDb *db;            /* Pointer to currently SELECTed DB. */
    robj *name;             /* As set by CLIENT SETNAME. */
    sds querybuf;           /* Buffer we use to accumulate client queries. */
    size_t qb_pos;          /* The position we have read in querybuf. */
    sds pending_querybuf;   /* If this client is flagged as master, this buffer
                               represents the yet not applied portion of the
                               replication stream that we are receiving from
                               the master. */
    size_t querybuf_peak;   /* Recent (100ms or more) peak of querybuf size. */
    int argc;               /* Num of arguments of current command. */
    robj **argv;            /* Arguments of current command. */
    int original_argc;      /* Num of arguments of original command if arguments were rewritten. */
    robj **original_argv;   /* Arguments of original command if arguments were rewritten. */
    size_t argv_len_sum;    /* Sum of lengths of objects in argv list. */
    struct redisCommand *cmd, *lastcmd;  /* Last command executed. */
    user *user;             /* User associated with this connection. If the
                               user is set to NULL the connection can do
                               anything (admin). */
    int reqtype;            /* Request protocol type: PROTO_REQ_* */
    int multibulklen;       /* Number of multi bulk arguments left to read. */
    long bulklen;           /* Length of bulk argument in multi bulk request. */
    list *reply;            /* List of reply objects to send to the client. */
    unsigned long long reply_bytes; /* Tot bytes of objects in reply list. */
    size_t sentlen;         /* Amount of bytes already sent in the current
                               buffer or object being sent. */
    time_t ctime;           /* Client creation time. */
    long duration;          /* Current command duration. Used for measuring latency of blocking/non-blocking cmds */
    time_t lastinteraction; /* Time of the last interaction, used for timeout */
    time_t obuf_soft_limit_reached_time;
    uint64_t flags;         /* Client flags: CLIENT_* macros. */
    int authenticated;      /* Needed when the default user requires auth. */
    int replstate;          /* Replication state if this is a slave. */
    int repl_put_online_on_ack; /* Install slave write handler on first ACK. */
    int repldbfd;           /* Replication DB file descriptor. */
    off_t repldboff;        /* Replication DB file offset. */
    off_t repldbsize;       /* Replication DB file size. */
    sds replpreamble;       /* Replication DB preamble. */
    long long read_reploff; /* Read replication offset if this is a master. */
    long long reploff;      /* Applied replication offset if this is a master. */
    long long repl_ack_off; /* Replication ack offset, if this is a slave. */
    long long repl_ack_time;/* Replication ack time, if this is a slave. */
    long long repl_last_partial_write; /* The last time the server did a partial write from the RDB child pipe to this replica  */
    long long psync_initial_offset; /* FULLRESYNC reply offset other slaves
                                       copying this slave output buffer
                                       should use. */
    char replid[CONFIG_RUN_ID_SIZE+1]; /* Master replication ID (if master). */
    int slave_listening_port; /* As configured with: REPLCONF listening-port */
    char *slave_addr;       /* Optionally given by REPLCONF ip-address */
    int slave_capa;         /* Slave capabilities: SLAVE_CAPA_* bitwise OR. */
    multiState mstate;      /* MULTI/EXEC state */
    int btype;              /* Type of blocking op if CLIENT_BLOCKED. */
    blockingState bpop;     /* blocking state */
    long long woff;         /* Last write global replication offset. */
    list *watched_keys;     /* Keys WATCHED for MULTI/EXEC CAS */
    dict *pubsub_channels;  /* channels a client is interested in (SUBSCRIBE) */
    list *pubsub_patterns;  /* patterns a client is interested in (SUBSCRIBE) */
    sds peerid;             /* Cached peer ID. */
    sds sockname;           /* Cached connection target address. */
    listNode *client_list_node; /* list node in client list */
    listNode *paused_list_node; /* list node within the pause list */
    RedisModuleUserChangedFunc auth_callback; /* Module callback to execute
                                               * when the authenticated user
                                               * changes. */
    void *auth_callback_privdata; /* Private data that is passed when the auth
                                   * changed callback is executed. Opaque for
                                   * Redis Core. */
    void *auth_module;      /* The module that owns the callback, which is used
                             * to disconnect the client if the module is
                             * unloaded for cleanup. Opaque for Redis Core.*/

    /* If this client is in tracking mode and this field is non zero,
     * invalidation messages for keys fetched by this client will be send to
     * the specified client ID. */
    uint64_t client_tracking_redirection;
    rax *client_tracking_prefixes; /* A dictionary of prefixes we are already
                                      subscribed to in BCAST mode, in the
                                      context of client side caching. */
    /* In clientsCronTrackClientsMemUsage() we track the memory usage of
     * each client and add it to the sum of all the clients of a given type,
     * however we need to remember what was the old contribution of each
     * client, and in which categoty the client was, in order to remove it
     * before adding it the new value. */
    uint64_t client_cron_last_memory_usage;
    int      client_cron_last_memory_type;
    /* Response buffer */
    int bufpos;
    char buf[PROTO_REPLY_CHUNK_BYTES];
} client;
```

## 套接字描述符

```c
typedef struct client {
    ……
    // 记录客户端正在使用的套接字描述符
    int fd;
    ……
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220104015.png?x-oss-process=style/yano)

## 标志

客户端的标志属性 flags 记录了`客户端的角色`（role），以及客户端目前所处的状态：

```c
typedef struct redisClient {
    // ...
    int flags;
    // ...
} redisClient;
```

具体值可参考：[《Redis 设计与实现-客户端属性》](http://redisbook.com/preview/client/redis_client_property.html)，flag 例子：

```c
# 客户端是一个主服务器
REDIS_MASTER

# 客户端正在被列表命令阻塞
REDIS_BLOCKED

# 客户端正在执行事务，但事务的安全性已被破坏
REDIS_MULTI | REDIS_DIRTY_CAS

# 客户端是一个从服务器，并且版本低于 Redis 2.8
REDIS_SLAVE | REDIS_PRE_PSYNC

# 这是专门用于执行 Lua 脚本包含的 Redis 命令的伪客户端
# 它强制服务器将当前执行的命令写入 AOF 文件，并复制给从服务器
REDIS_LUA_CLIENT | REDIS_FORCE_AOF | REDIS_FORCE_REPL
```

## 输入缓冲区

客户端状态的输入缓冲区用于保存`客户端发送的命令请求`：

```c
typedef struct redisClient {
    // ...
    sds querybuf;
    // ...
} redisClient;
```

如果客户端向服务器发送了以下命令请求：

```c
SET key value
```

客户端状态的 querybuf 属性将是一个包含以下内容的 SDS 值：

```c
*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n
```

展示了这个 SDS 值以及 querybuf 属性的样子：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221082404.png)

## 命名及命令参数

在服务器将客户端发送的命令请求保存到客户端状态的 `querybuf` 后，服务器会分析该命令，将得到的命令参数、命令参数的个数分别保存到客户端状态的 `argv` 属性和 `argc` 属性中：

```c
typedef struct redisClient {
    // ...
    robj **argv;
    int argc;
    // ...
} redisClient;
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221083136.png?x-oss-process=style/yano)

## 命令的实现函数

当服务器从协议内容中分析并得出 argv 属性和 argc 属性的值之后， 服务器将根据项 argv[0] 的值，在命令表中查找命令所对应的命令实现函数。

当程序在命令表中成功找到 argv[0] 所对应的 `redisCommand` 结构时， 它会将客户端状态的 `cmd 指针`指向这个结构：

```c
typedef struct redisClient {
    // ...
    struct redisCommand *cmd;
    // ...
} redisClient;
```

```c
struct redisCommand {
    char *name;
    redisCommandProc *proc;
    int arity;
    char *sflags;   /* Flags as string representation, one char per flag. */
    uint64_t flags; /* The actual flags, obtained from the 'sflags' field. */
    /* Use a function to determine keys arguments in a command line.
     * Used for Redis Cluster redirect. */
    redisGetKeysProc *getkeys_proc;
    /* What keys should be loaded in background when calling this command? */
    int firstkey; /* The first argument that's a key (0 = no keys) */
    int lastkey;  /* The last argument that's a key */
    int keystep;  /* The step between first and last key */
    long long microseconds, calls, rejected_calls, failed_calls;
    int id;     /* Command ID. This is a progressive ID starting from 0 that
                   is assigned at runtime, and is used in order to check
                   ACLs. A connection is able to execute a given command if
                   the user associated to the connection has this command
                   bit set in the bitmap of allowed commands. */
};
```

每个命令所对应的处理函数在是下面的 table：

```c
struct redisCommand redisCommandTable[] = {
    {"module",moduleCommand,-2,
     "admin no-script",
     0,NULL,0,0,0,0,0,0},

    {"get",getCommand,2,
     "read-only fast @string",
     0,NULL,1,1,1,0,0,0},

    {"getex",getexCommand,-2,
     "write fast @string",
     0,NULL,1,1,1,0,0,0},

     ……
}
```

## 输出缓冲区

保存执行命令所得的`命令回复`。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221084219.png?x-oss-process=style/yano)

客户端的`固定大小缓冲区`由 `buf` 和 `bufpos` 两个属性组成：

```c
typedef struct redisClient {
    // ...
    char buf[REDIS_REPLY_CHUNK_BYTES];
    // 记录了 buf 数组目前已使用的字节数量
    int bufpos;
    // ...
} redisClient;
```

`可变大小缓冲区`由 `reply 链表`和一个或多个字符串对象组成：

```c
typedef struct redisClient {
    // ...

    list *reply;
    // ...
} redisClient;
```

通过使用链表来连接多个字符串对象， 服务器可以为客户端保存一个非常长的命令回复， 而不必受到固定大小缓冲区 16 KB 大小的限制。展示了一个包含三个字符串对象的 reply 链表。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221084752.png?x-oss-process=style/yano)

# 客户端的创建与关闭

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221085412.png?x-oss-process=style/yano)

## 创建普通客户端

使用 connect 函数连接到服务器，服务器调用连接事件处理器，为客户端创建对应的客户端状态，并将其添加到服务器状态结构 clients 链表的末尾。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220221202740.png?x-oss-process=style/yano)

## 关闭普通客户端

关闭普通客户端的原因：
- 客户端进程退出或被杀死，客户端与服务端的网络连接被关闭
- 客户端向服务端发送了不符合协议格式的命令请求
- 客户端成为了 CLIENT KILL 命令的目标
- 客户端的空转时间超过 timeout 配置选项的值
- 客户端发送的命令请求大小，超过了深入缓冲区的限制大小（默认为 1GB）
- 服务端返回给客户端的数据超过了输出缓冲区的限制大小

# 参考链接

- [《Redis 设计与实现-客户端属性》](http://redisbook.com/preview/client/redis_client_property.html)

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