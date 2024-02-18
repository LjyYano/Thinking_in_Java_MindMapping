---
date: 2021-11-18
---

- [C 语言的字符串函数](#c-语言的字符串函数)
- [SDS 定义](#sds-定义)
- [SDS 内部结构](#sds-内部结构)
  - [sds struct](#sds-struct)
  - [sds 宏](#sds-宏)
- [SDS 的主要操作 API](#sds-的主要操作-api)
  - [字符串初始化](#字符串初始化)
- [Redis 源码简洁剖析系列](#redis-源码简洁剖析系列)
- [我的公众号](#我的公众号)

# C 语言的字符串函数

[C 语言 string 函数](https://devdocs.io/c-strings/)，在 C 语言中可以使用 `char*` 字符数组实现字符串，C 语言标准库 `string.h` 中也定义了多种字符串操作函数。

字符串使用广泛，需要满足：
- 高效的字符串操作，比如追加、拷贝、比较、获取长度
- 能保存任意的二进制数据，比如图片
- 尽可能省内存

> 💡 为什么 Redis 不直接使用 C 语言的字符串？

- C 语言 char* 以 `'\0'` 标识字符串的结束，则中间含有 `'\0'` 的字符串无法被正确表示；也正因为此，` 没有办法保存图像等二进制数据 `。
- C 语言 char* 效率问题：
  - 获取 ` 字符串长度 ` 的时间复杂度是 `O(n)`
  - 追加字符串的时间复杂度也是 `O(n)`
  - 可能由于可用空间不足，无法追加

下面代码展示了 C 语言中 '\0' 结束字符对字符串的影响。

```c
#include "stdio.h"
#include "string.h"

int main(void) {
    char *a = "red\0is";
    char *b = "redis\0";
    printf("%lu\n", strlen(a));
    printf("%lu\n", strlen(b));
}
```

输出结果是 3 和 5。


# SDS 定义

[SDS（简单动态字符串）](https://redis.io/docs/reference/internals/internals-sds/) 是 `simple dynamic string` 的简称，Redis 使用 SDS 作为字符串的数据结构。Redis 中所有的键（key）底层都是 SDS 实现的。

比如：

```
redis> SET msg "hello world"
OK
```

```
redis> RPUSH fruits "apple" "banana" "cherry"
(integer) 3
```

Redis SDS 源码主要在 sds.h 和 sds.c 中。其中可以发现 Redis 给 char* 起了别名：

```c
typedef char *sds;
```

# SDS 内部结构

SDS 结构中有一个元数据 flags，表示的是 SDS 类型（最低 3 位）。事实上，SDS 一共设计了 5 种类型，分别是
- sdshdr5
- sdshdr8
- sdshdr16
- sdshdr32
- sdshdr64

> 💡 这几个的区别就在于字符数组现有长度 len 和分配空间长度 alloc 的类型，为了节省内存。

## sds struct

```c
/* Note: sdshdr5 is never used, we just access the flags byte directly.
 * However is here to document the layout of type 5 SDS strings. */
struct __attribute__ ((__packed__)) sdshdr5 {
    unsigned char flags; /* 3 lsb of type, and 5 msb of string length */
    // buf 是柔性数组，必须是结构体的最后一个成员，不制定大小就不计算空间
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len; /* used */
    uint8_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr16 {
    uint16_t len; /* used */
    uint16_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr32 {
    uint32_t len; /* used */
    uint32_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr64 {
    uint64_t len; /* used */
    uint64_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
```

## sds 宏

```c
#define SDS_TYPE_5  0
#define SDS_TYPE_8  1
#define SDS_TYPE_16 2
#define SDS_TYPE_32 3
#define SDS_TYPE_64 4
```

```c
// ## 是 C 预处理器的连接符，如果 T=8，则为 sdshdr8

// 找到 header 地址，sh 即为 header 地址
#define SDS_HDR_VAR(T,s) struct sdshdr##T *sh = (void*)((s)-(sizeof(struct sdshdr##T)));

// 返回 struct sdshdr##T 类型的指针（header 地址）
#define SDS_HDR(T,s) ((struct sdshdr##T *)((s)-(sizeof(struct sdshdr##T))))
```

# SDS 的主要操作 API

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211119113853.png?x-oss-process=style/yano)

## 字符串初始化

整体和 Java 的 StringBuilder 很像了 O_o

```c
/* Create a new sds string starting from a null terminated C string. */
sds sdsnew(const char *init) {
    size_t initlen = (init == NULL) ? 0 : strlen(init);
    return sdsnewlen(init, initlen);
}
```

首先是判断输入的 init 字符串的长度，接着调用 sdsnewlen 分配内存空间并赋值。

```c
sds sdsnewlen(const void *init, size_t initlen) {
    return _sdsnewlen(init, initlen, 0);
}
```

核心函数_sdsnewlen 如下，主要就是先确保空间是否足够、分配空间，然后再调用 memcpy 将 *init 复制到对应的内存空间。

```c
/* Create a new sds string with the content specified by the 'init' pointer
 * and 'initlen'.
 * If NULL is used for 'init' the string is initialized with zero bytes.
 * If SDS_NOINIT is used, the buffer is left uninitialized;
 *
 * The string is always null-termined (all the sds strings are, always) so
 * even if you create an sds string with:
 *
 * mystring = sdsnewlen("abc",3);
 *
 * You can print the string with printf() as there is an implicit \0 at the
 * end of the string. However the string is binary safe and can contain
 * \0 characters in the middle, as the length is stored in the sds header. */
sds _sdsnewlen(const void *init, size_t initlen, int trymalloc) {
    void *sh;
    sds s;
    char type = sdsReqType(initlen);
    /* Empty strings are usually created in order to append. Use type 8
     * since type 5 is not good at this. */
    if (type == SDS_TYPE_5 && initlen == 0) type = SDS_TYPE_8;
    int hdrlen = sdsHdrSize(type);
    unsigned char *fp; /* flags pointer. */
    size_t usable;

    assert(initlen + hdrlen + 1> initlen); /* Catch size_t overflow */
    sh = trymalloc?
        s_trymalloc_usable(hdrlen+initlen+1, &usable) :
        s_malloc_usable(hdrlen+initlen+1, &usable);
    if (sh == NULL) return NULL;
    if (init==SDS_NOINIT)
        init = NULL;
    else if (!init)
        memset(sh, 0, hdrlen+initlen+1);
    s = (char*)sh+hdrlen;
    fp = ((unsigned char*)s)-1;
    usable = usable-hdrlen-1;
    if (usable> sdsTypeMaxSize(type))
        usable = sdsTypeMaxSize(type);
    switch(type) {
        case SDS_TYPE_5: {
            *fp = type | (initlen << SDS_TYPE_BITS);
            break;
        }
        case SDS_TYPE_8: {
            SDS_HDR_VAR(8,s);
            sh->len = initlen;
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_16: {
            SDS_HDR_VAR(16,s);
            sh->len = initlen;
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_32: {
            SDS_HDR_VAR(32,s);
            sh->len = initlen;
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_64: {
            SDS_HDR_VAR(64,s);
            sh->len = initlen;
            sh->alloc = usable;
            *fp = type;
            break;
        }
    }
    if (initlen && init)
        memcpy(s, init, initlen);
    s[initlen] = '\0';
    return s;
}
```

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