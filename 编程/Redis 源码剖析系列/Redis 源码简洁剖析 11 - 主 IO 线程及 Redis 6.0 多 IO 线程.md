---
date: 2022-02-08
---


- [Redis 到底是不是单线程的程序？](#redis-%E5%88%B0%E5%BA%95%E6%98%AF%E4%B8%8D%E6%98%AF%E5%8D%95%E7%BA%BF%E7%A8%8B%E7%9A%84%E7%A8%8B%E5%BA%8F)
- [多 IO 线程的初始化](#%E5%A4%9A-io-%E7%BA%BF%E7%A8%8B%E7%9A%84%E5%88%9D%E5%A7%8B%E5%8C%96)
- [IO 线程运行函数 IOThreadMain](#io-%E7%BA%BF%E7%A8%8B%E8%BF%90%E8%A1%8C%E5%87%BD%E6%95%B0-iothreadmain)
    - [如何推迟客户端「读」操作？](#%E5%A6%82%E4%BD%95%E6%8E%A8%E8%BF%9F%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%AF%BB%E6%93%8D%E4%BD%9C)
    - [如何推迟客户端「写」操作？](#%E5%A6%82%E4%BD%95%E6%8E%A8%E8%BF%9F%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%86%99%E6%93%8D%E4%BD%9C)
    - [如何把待「读」客户端分配给 IO 线程执行？](#%E5%A6%82%E4%BD%95%E6%8A%8A%E5%BE%85%E8%AF%BB%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%88%86%E9%85%8D%E7%BB%99-io-%E7%BA%BF%E7%A8%8B%E6%89%A7%E8%A1%8C)
    - [如何把待「写」客户端分配给 IO 线程执行？](#%E5%A6%82%E4%BD%95%E6%8A%8A%E5%BE%85%E5%86%99%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%88%86%E9%85%8D%E7%BB%99-io-%E7%BA%BF%E7%A8%8B%E6%89%A7%E8%A1%8C)
- [总结](#%E6%80%BB%E7%BB%93)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)


# Redis 到底是不是单线程的程序？

Redis 只有在处理「客户端请求」时，是单线程的；整个 Redis server 不是单线程的，还有后台线程在辅助处理任务。

Redis 选择单线程处理请求，是因为 Redis 操作的是`「内存」`，加上设计了「高效」的数据结构，所以`操作速度极快`，利用 `IO 多路复用机制`，单线程依旧可以有非常高的性能。

Redis 不让主线程执行一些耗时操作，比如同步写、删除等，而是交给后台线程异步完成，从而避免了对主线程的阻塞。

在 2020 年 5 月推出的 Redis 6.0 版本中，还会使用`多线程`来处理 IO 任务，能够充分利用服务器的`多核特性`，使用多核运行多线程，让多线程帮助加速`数据读取`、`命令解析`和`数据写回`的速度，提升 Redis 的整体性能。

# 多 IO 线程的初始化

在 main 函数中，会调用 InitServerLast 函数，Redis 6.0 源码：

```c
void InitServerLast() {
    bioInit();
    // 初始化 IO 线程
    initThreadedIO();
    set_jemalloc_bg_thread(server.jemalloc_bg_thread);
    server.initial_memory_usage = zmalloc_used_memory();
}
```

在调用了 bioInit 函数后，又调用了 initThreadedIO 函数初始化多 IO 线程。`initThreadedIO` 函数在 `networking.c` 文件中。

```c
void initThreadedIO(void) {
    // IO 线程激活标志：设置为「未激活」
    server.io_threads_active = 0;

    // 只有 1 个 io 线程，直接返回，直接在主线程处理 IO
    if (server.io_threads_num == 1) return;

    if (server.io_threads_num > IO_THREADS_MAX_NUM) {
        serverLog(LL_WARNING,"Fatal: too many I/O threads configured. "
                             "The maximum number is %d.", IO_THREADS_MAX_NUM);
        exit(1);
    }

    /* Spawn and initialize the I/O threads. */
    for (int i = 0; i < server.io_threads_num; i++) {
        io_threads_list[i] = listCreate();
        // Thread 0 是主线程
        if (i == 0) continue;

        /* Things we do only for the additional threads. */
        pthread_t tid;
        // 初始化 io_threads_mutex
        pthread_mutex_init(&io_threads_mutex[i],NULL);
        setIOPendingCount(i, 0);
        pthread_mutex_lock(&io_threads_mutex[i]); /* Thread will be stopped. */
        // pthread_create 创建 IO 线程，线程运行函数是 IOThreadMain
        if (pthread_create(&tid,NULL,IOThreadMain,(void*)(long)i) != 0) {
            serverLog(LL_WARNING,"Fatal: Can't initialize IO thread.");
            exit(1);
        }
        // 初始化 io_threads 数组，设置值为线程标识
        io_threads[i] = tid;
    }
}
```

代码中首先判断 io_threads_num：
- io_threads_num = 1，表示直接在主线程处理，直接返回
- io_threads_num > IO_THREADS_MAX_NUM，表示 IO 线程数量>宏定义的值（默认值 128），直接退出程序

initThreadedIO 函数就会给以下四个数组进行初始化操作：

- `io_threads_list` 数组：保存了每个 IO 线程要处理的客户端，将数组每个元素初始化为一个 List 类型的列表
- `io_threads_pending` 数组：保存等待每个 IO 线程处理的客户端个数
- `io_threads_mutex` 数组：保存线程互斥锁
- `io_threads` 数组：保存每个 IO 线程的描述符

这四个数组的定义都在 networking.c 文件中：

```c

pthread_t io_threads[IO_THREADS_MAX_NUM];   //记录线程描述符的数组
pthread_mutex_t io_threads_mutex[IO_THREADS_MAX_NUM];  //记录线程互斥锁的数组
_Atomic unsigned long io_threads_pending[IO_THREADS_MAX_NUM];  //记录线程待处理的客户端个数
list *io_threads_list[IO_THREADS_MAX_NUM];  //记录线程对应处理的客户端
```

initThreadedIO 函数在 for 循环中，调用 pthread_create 函数创建线程。pthread_create 详细语法见：[pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)。

创建的线程要运行的函数是 IOThreadMain，*arg 参数就是当前创建线程的编号（从 1 开始，0 是主 IO 线程）。

```c
/* Spawn and initialize the I/O threads. */
for (int i = 0; i < server.io_threads_num; i++) {
    io_threads_list[i] = listCreate();
    // Thread 0 是主线程
    if (i == 0) continue;

    /* Things we do only for the additional threads. */
    pthread_t tid;
    // 初始化 io_threads_mutex
    pthread_mutex_init(&io_threads_mutex[i],NULL);
    setIOPendingCount(i, 0);
    pthread_mutex_lock(&io_threads_mutex[i]);
    // pthread_create 创建 IO 线程，线程运行函数是 IOThreadMain
    if (pthread_create(&tid,NULL,IOThreadMain,(void*)(long)i) != 0) {
        serverLog(LL_WARNING,"Fatal: Can't initialize IO thread.");
        exit(1);
    }
    // 初始化 io_threads 数组，设置值为线程标识
    io_threads[i] = tid;
}
```

# IO 线程运行函数 IOThreadMain

主要逻辑是一个 while(1) 的循环，会把 `io_threads_list` 在这个线程对应的元素取出来，判断并处理。

```c
void *IOThreadMain(void *myid) {
    ……

    while(1) {
        /* Wait for start */
        for (int j = 0; j < 1000000; j++) {
            if (getIOPendingCount(id) != 0) break;
        }

        ……
        // 获取 IO 线程要处理的客户端列表
        listRewind(io_threads_list[id],&li);
        while((ln = listNext(&li))) {
            // 从客户端列表中获取一个客户端
            client *c = listNodeValue(ln);
            // 线程是「写操作」，调用 writeToClient 将数据写回客户端
            if (io_threads_op == IO_THREADS_OP_WRITE) {
                writeToClient(c,0);
            // 如果是『读操作』，调用 readQueryFromClient 从客户端读数据
            } else if (io_threads_op == IO_THREADS_OP_READ) {
                readQueryFromClient(c->conn);
            } 
            ……
        }
        // 处理完所有客户端，清空该线程的客户端列表
        listEmpty(io_threads_list[id]);
        // 将该线程的待处理任务数量设为 0
        setIOPendingCount(id, 0);
    }
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220208214321.png?x-oss-process=style/yano)

注：上面代码中 `io_threads_op` 变量是在 `handleClientsWithPendingWritesUsingThreads` 函数和 `handleClientsWithPendingReadsUsingThreads` 函数中设置的。

问题：IO 线程要处理的客户端是如何添加到 io_threads_list 数组中的呢？

是在 redisServer 全局变量里，有两个 List 类型的成员变量：
- `clients_pending_write`：待写回数据的客户端
- `clients_pending_read`：待读取数据的客户端

```c

struct redisServer {
    ...
    // 待写回数据的客户端
    list *clients_pending_write;  
    // 待读取数据的客户端
    list *clients_pending_read;  
    ...
}
```

Redis server 在接收到客户端请求、返回给客户端数据的过程中，会根据一定条件，`推迟客户端的读写操作`，并分别把待读写的客户端保存到这两个列表中。之后 Redis server 每次进入事件循环前，都会把列表中的客户端添加到 io_threads_list 数组中，交给 IO 线程处理。

## 如何推迟客户端「读」操作？

处理可读事件的回调函数是 readQueryFromClient。

```c
void readQueryFromClient(connection *conn) {
    // 从 connection 结构中获取客户端
    client *c = connGetPrivateData(conn);
    ……

    // 是否推迟从客户端读取数据（使用多线程 IO 时）
    if (postponeClientRead(c)) return;

    ……
}
```

主要看下 postponeClientRead 函数。

```c
int postponeClientRead(client *c) {
    if (server.io_threads_active &&
        server.io_threads_do_reads &&
        !ProcessingEventsWhileBlocked &&
        !(c->flags & (CLIENT_MASTER|CLIENT_SLAVE|CLIENT_PENDING_READ|CLIENT_BLOCKED))) 
    {
        // 客户端 flag 添加 CLIENT_PENDING_READ 标记，推迟客户端的读操作
        c->flags |= CLIENT_PENDING_READ;
        // 将客户端添加到 server 的 clients_pending_read 列表中
        listAddNodeHead(server.clients_pending_read,c);
        return 1;
    } else {
        return 0;
    }
}
```

if 的判断条件：是否可以推迟当前客户端的读操作；if 块里的执行逻辑：将客户端添加到 clients_pending_read 列表中。下面主要看下判断条件：

1. `server.io_threads_active = 1`：多 IO 线程已激活。
2. `server.io_threads_do_reads = 1`：多 IO 线程可用于处理延迟执行的客户端读操作，是在 Redis 配置文件 redis.conf 中，通过配置项 。io-threads-do-reads 设置的，默认值为 no。
3. `ProcessingEventsWhileBlocked = 0`：ProcessingEventsWhileBlocked 函数没有在执行，当 Redis 在读取 RDB 文件或 AOF 文件时，会调用这个函数，用来处理事件驱动框架捕获到的事件，避免因读取 RDB 或 AOF 文件造成 Redis 阻塞。
4. 客户端现有标识不能有 `CLIENT_MASTER`、`CLIENT_SLAVE` 和 `CLIENT_PENDING_READ`
   - CLIENT_MASTER：客户端用于主从复制 
   - CLIENT_SLAVE：客户端用于主从复制 
   - CLIENT_PENDING_READ：客户端本来就被设置为推迟读操作

## 如何推迟客户端「写」操作？

Redis 在执行了客户端命令，要给客户端返回结果时，会调用 `addReply` 函数将待返回的结果写入输出缓冲区。addReply 函数开始就会调用 prepareClientToWrite 函数。

```c
/* -----------------------------------------------------------------------------
 * Higher level functions to queue data on the client output buffer.
 * The following functions are the ones that commands implementations will call.
 * -------------------------------------------------------------------------- */

/* Add the object 'obj' string representation to the client output buffer. */
void addReply(client *c, robj *obj) {
    if (prepareClientToWrite(c) != C_OK) return;

    ……
}
```

`prepareClientToWrite` 函数的注释如下：

```c
/* This function is called every time we are going to transmit new data
 * to the client. The behavior is the following:
 *
 * If the client should receive new data (normal clients will) the function
 * returns C_OK, and make sure to install the write handler in our event
 * loop so that when the socket is writable new data gets written.
 *
 * If the client should not receive new data, because it is a fake client
 * (used to load AOF in memory), a master or because the setup of the write
 * handler failed, the function returns C_ERR.
 *
 * The function may return C_OK without actually installing the write
 * event handler in the following cases:
 *
 * 1) The event handler should already be installed since the output buffer
 *    already contains something.
 * 2) The client is a slave but not yet online, so we want to just accumulate
 *    writes in the buffer but not actually sending them yet.
 *
 * Typically gets called every time a reply is built, before adding more
 * data to the clients output buffers. If the function returns C_ERR no
 * data should be appended to the output buffers. */
```

```c
int prepareClientToWrite(client *c) {
    ……
    // 当前客户端没有待写回数据 && flag 不包含 CLIENT_PENDING_READ
    if (!clientHasPendingReplies(c) && !(c->flags & CLIENT_PENDING_READ))
            clientInstallWriteHandler(c);

    return C_OK;
}
```

clientInstallWriteHandler 如下，if 判断条件就不赘述了。

```c
void clientInstallWriteHandler(client *c) {

    if (!(c->flags & CLIENT_PENDING_WRITE) &&
        (c->replstate == REPL_STATE_NONE ||
         (c->replstate == SLAVE_STATE_ONLINE && !c->repl_put_online_on_ack)))
    {
        // 将客户端的标识设置为 CLIENT_PENDING_WRITE（待写回）
        c->flags |= CLIENT_PENDING_WRITE;
        // 将 client 加入 server 的 clients_pending_write 列表
        listAddNodeHead(server.clients_pending_write,c);
    }
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220209104325.png?x-oss-process=style/yano)

上面介绍如如何推迟客户端的读操作、写操作，那 Redis 是如何将推迟读写操作的客户端，分配给多 IO 线程执行的呢？是通过：
- `handleClientsWithPendingReadsUsingThreads 函数`：将 clients_pending_read 列表中的客户端分配给 IO 线程
- `handleClientsWithPendingWritesUsingThreads 函数`：将 clients_pending_write 列表中的客户端分配给 IO 线程

## 如何把待「读」客户端分配给 IO 线程执行？

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220209105654.png?x-oss-process=style/yano)

beforeSleep 函数中调用了 handleClientsWithPendingReadsUsingThreads 函数：

```c
/* We should handle pending reads clients ASAP after event loop. */
handleClientsWithPendingReadsUsingThreads();
```

`handleClientsWithPendingReadsUsingThreads` 函数如下，逻辑都在注释中：

```c
/* When threaded I/O is also enabled for the reading + parsing side, the
 * readable handler will just put normal clients into a queue of clients to
 * process (instead of serving them synchronously). This function runs
 * the queue using the I/O threads, and process them in order to accumulate
 * the reads in the buffers, and also parse the first command available
 * rendering it in the client structures. */
int handleClientsWithPendingReadsUsingThreads(void) {
    // 判断 io_threads_active 是否被激活，io_threads_do_reads 是否可以用 IO 线程处理待读客户端
    if (!server.io_threads_active || !server.io_threads_do_reads) return 0;

    // 判断 clients_pending_read 长度
    int processed = listLength(server.clients_pending_read);
    if (processed == 0) return 0;

    /* Distribute the clients across N different lists. */
    listIter li;
    listNode *ln;
    // 获取 clients_pending_read 的客户端列表
    listRewind(server.clients_pending_read,&li);
    // 轮询方式，将客户端分配给 IO 线程
    int item_id = 0;
    while((ln = listNext(&li))) {
        client *c = listNodeValue(ln);
        int target_id = item_id % server.io_threads_num;
        listAddNodeTail(io_threads_list[target_id],c);
        item_id++;
    }

    // 将 IO 线程的操作标识设置为「读操作」
    io_threads_op = IO_THREADS_OP_READ;
    for (int j = 1; j < server.io_threads_num; j++) {
        // 每个线程等待处理的客户端数量 → io_threads_pending 数组
        int count = listLength(io_threads_list[j]);
        setIOPendingCount(j, count);
    }

    // 处理 0 号线程（主线程）的待读客户端
    listRewind(io_threads_list[0],&li);
    while((ln = listNext(&li))) {
        client *c = listNodeValue(ln);
        readQueryFromClient(c->conn);
    }
    // 清空 0 号列表
    listEmpty(io_threads_list[0]);

    // 循环，等待其他所有 IO 线程的待读客户端都处理完
    while(1) {
        unsigned long pending = 0;
        for (int j = 1; j < server.io_threads_num; j++)
            pending += getIOPendingCount(j);
        if (pending == 0) break;
    }

    /* Run the list of clients again to process the new buffers. */
    // 取出 clients_pending_read 列表
    while(listLength(server.clients_pending_read)) {
        ln = listFirst(server.clients_pending_read);
        client *c = listNodeValue(ln);
        // 判断客户端标识符是否有 CLIENT_PENDING_READ，有则表示被 IO 线程解析过
        c->flags &= ~CLIENT_PENDING_READ;
        // 将客户端从 clients_pending_read 列表中删掉
        listDelNode(server.clients_pending_read,ln);

        serverAssert(!(c->flags & CLIENT_BLOCKED));
        if (processPendingCommandsAndResetClient(c) == C_ERR) {
            /* If the client is no longer valid, we avoid
             * processing the client later. So we just go
             * to the next. */
            continue;
        }

        // 解析并执行客户端的所有命令
        processInputBuffer(c);

        /* We may have pending replies if a thread readQueryFromClient() produced
         * replies and did not install a write handler (it can't).
         */
        if (!(c->flags & CLIENT_PENDING_WRITE) && clientHasPendingReplies(c))
            clientInstallWriteHandler(c);
    }

    /* Update processed count on server */
    server.stat_io_reads_processed += processed;

    return processed;
}
```

## 如何把待「写」客户端分配给 IO 线程执行？

待写客户端的分配处理是由 `handleClientsWithPendingWritesUsingThreads` 函数完成的，该函数也是在 `beforeSleep` 函数中调用的。逻辑和 handleClientsWithPendingReadsUsingThreads 函数很像。

```c
int handleClientsWithPendingWritesUsingThreads(void) {

    // 判断 clients_pending_write 列表的数量
    int processed = listLength(server.clients_pending_write);
    if (processed == 0) return 0;

    // 只有主 IO 线程 || 不使用 IO 线程
    if (server.io_threads_num == 1 || stopThreadedIOIfNeeded()) {
        return handleClientsWithPendingWrites();
    }

    /* Start threads if needed. */
    if (!server.io_threads_active) startThreadedIO();

    /* Distribute the clients across N different lists. */
    listIter li;
    listNode *ln;
    listRewind(server.clients_pending_write,&li);
    int item_id = 0;
    // 把待写客户端，按照轮询方式分配给 IO 线程
    while((ln = listNext(&li))) {
        client *c = listNodeValue(ln);
        c->flags &= ~CLIENT_PENDING_WRITE;

        if (c->flags & CLIENT_CLOSE_ASAP) {
            listDelNode(server.clients_pending_write, ln);
            continue;
        }

        int target_id = item_id % server.io_threads_num;
        listAddNodeTail(io_threads_list[target_id],c);
        item_id++;
    }

    // 将 IO 线程的操作标识设置为「写操作」
    io_threads_op = IO_THREADS_OP_WRITE;
    for (int j = 1; j < server.io_threads_num; j++) {
        // 每个线程等待处理的客户端数量 → io_threads_pending 数组
        int count = listLength(io_threads_list[j]);
        setIOPendingCount(j, count);
    }

    /* Also use the main thread to process a slice of clients. */
    listRewind(io_threads_list[0],&li);
    while((ln = listNext(&li))) {
        client *c = listNodeValue(ln);
        writeToClient(c,0);
    }
    listEmpty(io_threads_list[0]);

    // 循环，等待其他所有 IO 线程的待写客户端都处理完
    while(1) {
        unsigned long pending = 0;
        for (int j = 1; j < server.io_threads_num; j++)
            pending += getIOPendingCount(j);
        if (pending == 0) break;
    }

    /* Run the list of clients again to install the write handler where
     * needed. */
    listRewind(server.clients_pending_write,&li);
    while((ln = listNext(&li))) {
        client *c = listNodeValue(ln);

        // 再次检查是否有待写客户端
        if (clientHasPendingReplies(c) &&
                connSetWriteHandler(c->conn, sendReplyToClient) == AE_ERR)
        {
            freeClientAsync(c);
        }
    }
    listEmpty(server.clients_pending_write);

    /* Update processed count on server */
    server.stat_io_writes_processed += processed;

    return processed;
}
```

需要注意的是，`stopThreadedIOIfNeeded` 函数中会判断`待写入的客户端数量如果 < IO 线程数 * 2`，则也会直接返回，直接使用主 IO 线程处理待写客户端。这是因为待写客户端不多时，使用多线程效率反而会下降。

```c
int stopThreadedIOIfNeeded(void) {
    int pending = listLength(server.clients_pending_write);

    /* Return ASAP if IO threads are disabled (single threaded mode). */
    if (server.io_threads_num == 1) return 1;

    if (pending < (server.io_threads_num*2)) {
        if (server.io_threads_active) stopThreadedIO();
        return 1;
    } else {
        return 0;
    }
}
```

# 总结

Redis 6.0 实现的`多 IO 线程机制`，主要是使用多个 IO 线程，并发处理客户端`读取数据`、`解析命令`、`写回数据`，充分利用服务器的`多核`特性，提高 IO 效率。

Redis server 会根据 `readQueryFromClient` 函数调用 postponeClientRead 函数决定是否要推迟客户端操作；会根据 `addReply` 函数中的 prepareClientToWrite 函数，决定是否推迟客户端的写操作。待读客户端加入到 clients_pending_read 列表，待写客户端加入 clients_pending_write 列表。

IO 线程创建之后，会一直检测 `io_threads_list` 列表，如果有待读写的客户端，IO 线程就会调用 readQueryFromClient 或 writeToClient 函数进行处理。

但是多 IO 线程并不会执行命令，`执行命令`仍然在`主 IO 线程`。

# 参考链接

- [极客时间：12 | Redis 真的是单线程吗？](https://time.geekbang.org/column/article/409927)
- [极客时间：13 | Redis 6.0 多 IO 线程的效率提高了吗？](https://time.geekbang.org/column/article/410666)
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)。

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