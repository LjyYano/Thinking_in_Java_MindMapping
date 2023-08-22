---
date: 2022-02-15
---


- [AOF 是什么](#aof-%E6%98%AF%E4%BB%80%E4%B9%88)
- [AOF 持久化的实现](#aof-%E6%8C%81%E4%B9%85%E5%8C%96%E7%9A%84%E5%AE%9E%E7%8E%B0)
    - [命令追加](#%E5%91%BD%E4%BB%A4%E8%BF%BD%E5%8A%A0)
    - [AOF 文件的写入和同步](#aof-%E6%96%87%E4%BB%B6%E7%9A%84%E5%86%99%E5%85%A5%E5%92%8C%E5%90%8C%E6%AD%A5)
- [AOF 文件的载入和数据还原](#aof-%E6%96%87%E4%BB%B6%E7%9A%84%E8%BD%BD%E5%85%A5%E5%92%8C%E6%95%B0%E6%8D%AE%E8%BF%98%E5%8E%9F)
- [AOF 重写](#aof-%E9%87%8D%E5%86%99)
    - [为什么需要重写](#%E4%B8%BA%E4%BB%80%E4%B9%88%E9%9C%80%E8%A6%81%E9%87%8D%E5%86%99)
    - [什么是重写](#%E4%BB%80%E4%B9%88%E6%98%AF%E9%87%8D%E5%86%99)
    - [如何重写](#%E5%A6%82%E4%BD%95%E9%87%8D%E5%86%99)
    - [AOF 后台重写](#aof-%E5%90%8E%E5%8F%B0%E9%87%8D%E5%86%99)
        - [为什么需要后台重写](#%E4%B8%BA%E4%BB%80%E4%B9%88%E9%9C%80%E8%A6%81%E5%90%8E%E5%8F%B0%E9%87%8D%E5%86%99)
        - [带来的问题](#%E5%B8%A6%E6%9D%A5%E7%9A%84%E9%97%AE%E9%A2%98)
        - [AOF 重写缓冲区](#aof-%E9%87%8D%E5%86%99%E7%BC%93%E5%86%B2%E5%8C%BA)
    - [注意](#%E6%B3%A8%E6%84%8F)
- [实际例子](#%E5%AE%9E%E9%99%85%E4%BE%8B%E5%AD%90)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)
- [Redis 源码简洁剖析系列](#redis-%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97)
- [我的公众号](#%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7)

# AOF 是什么

`Append Only File`，通过保存 Redis 服务器所执行的命令来记录数据库状态。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220218175400.png)

# AOF 持久化的实现

## 命令追加

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220082532.png)

服务器在执行完一个写命令后，会以协议格式将被执行的`写命令`追加到服务器状态的 `aof_buf 缓冲区`的末尾：

```c
struct redisServer {
    ……
    // AOF 缓冲区
    sds aof_buf;
    ……
}
```

## AOF 文件的写入和同步

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220083354.png)

# AOF 文件的载入和数据还原

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220083719.png)

流程：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220083540.png?x-oss-process=style/yano)

# AOF 重写

## 为什么需要重写

AOF 持久化是通过保存被执行的写命令来记录数据库状态的，随着服务器运行时间的流逝，AOF 文件的内容会越来越多，`文件体积越来越大`。如果客户端执行了下面的命令：

```c
127.0.0.1:6379> set name yano
OK
127.0.0.1:6379> set name yano2
OK
127.0.0.1:6379> set name yano3
OK
```

那么 AOF 文件就需要保存 3 条命令，不仅使保存的 AOF 文件体积变大，还使得 Redis 启动时载入数据变慢。

## 什么是重写

AOF 文件重写（`rewrite`），创建新的 AOF 文件替代现有的 AOF 文件，新旧两个 AOF 文件所保存的数据库状态相同，但新 AOF 文件不会包含任何浪费空间的冗余命令，体积更小。

## 如何重写

不是读取和分析现有的 AOF 文件内容，而是直接从数据库读取值组成相应的命令 AOF 文件。

## AOF 后台重写

### 为什么需要后台重写

重写函数 aof_rewrite 会进行大量的写入操作，执行这个函数的线程会被长时间阻塞，但是 Redis 服务器使用单个线程来处理命令请求，如果直接在主线程直接更新，在重写期间，服务器将无法处理客户端发来的命令请求。所以将 AOF 重写程序放到子进程中执行。

### 带来的问题

子进程在进行 AOF 重写期间，服务器进程还需要继续处理命令请求，新的命令可能对现有的数据库状态进行修改，导致服务器当前数据库状态和重写后的 AOF 文件保存的数据状态不一致。

### AOF 重写缓冲区

为了解决这种`数据不一致`的问题，Redis 设置了一个 `AOF 重写缓冲区`，在服务器创建子进程之后开始使用，当 Redis 服务器执行完一个写命令后，同时将这个写命令发送给 `AOF 缓冲区`和 `AOF 重写缓冲区`：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220084719.png?x-oss-process=style/yano)

当子进程完成 AOF 重写工作后，它会向父进程发送一个信号，父进程在收到这个信号后，会调用一个信号处理函数：
1. 将 AOF 重写缓冲区的所有内容写入新的 AOF 文件，这样新 AOF 文件所保存的数据库状态就与服务器当前的数据库状态一致；
2. 对新 AOF 文件改名，原子覆盖现有的 AOF 文件，完成新旧 AOF 文件的替换。

下图左边是正常流程，右边是 AOF 重写期间的流程：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220220084745.png?x-oss-process=style/yano)

## 注意

在实际中，为了避免在执行命令时造成客户端输入缓冲区的溢出，重写程序在处理列表、哈希表、集合、有序集合可能带有多个元素的键时，会先检查键所包含的元素数量，如果元素数量超过了一个常量阈值，重写程序会使用多条命令来记录键的值。

# 实际例子

配置 `redis.conf` 文件，使用 AOF：

```c
appendonly yes
appendfsync always
appendfilename "appendonly.aof"
dir ./
```

启动 Redis server：

```c
src/redis-server redis.conf&
```

启动 Redis client：

```c
src/redis-cli
```

设置 key：

```c
127.0.0.1:6379> set name yano
OK
127.0.0.1:6379> set name yano2
OK
127.0.0.1:6379> set name yano3
OK
```

查看 appendonly.aof 文件：

```c
➜  redis-6.2.6 cat appendonly.aof
*2
$6
SELECT
$1
0
*3
$3
set
$4
name
$4
yano
*3
$3
set
$4
name
$5
yano2
*3
$3
set
$4
name
$5
yano3
```

# 参考链接

- [19 | AOF 重写（上）：触发时机与重写的影响](https://time.geekbang.org/column/article/416264)
- [《Redis 设计与实现》- 第 11 章 AOF 持久化](https://redisbook.readthedocs.io/en/latest/internal/aof.html)
- [Redis Persistence](https://redis.io/topics/persistence)

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