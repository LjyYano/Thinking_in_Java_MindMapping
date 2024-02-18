---
date: 2022-01-29
---

- [Sorted set 是什么](#sorted-set-是什么)
- [Sorted set 数据结构](#sorted-set-数据结构)
- [跳表（skiplist）](#跳表skiplist)
  - [结构定义](#结构定义)
  - [跳表节点查询](#跳表节点查询)
  - [层数设置](#层数设置)
  - [插入节点 zslInsert](#插入节点-zslinsert)
  - [删除节点 zslDelete](#删除节点-zsldelete)
- [Sorted set 基本操作](#sorted-set-基本操作)
  - [zsetAdd](#zsetadd)
    - [ziplist 编码](#ziplist-编码)
    - [skiplist 编码](#skiplist-编码)
    - [zsetAdd 整体代码](#zsetadd-整体代码)
  - [zsetDel](#zsetdel)
- [参考链接](#参考链接)
- [Redis 源码简洁剖析系列](#redis-源码简洁剖析系列)
- [我的公众号](#我的公众号)


# Sorted set 是什么

` 有序集合（Sorted set）` 是 Redis 中一种重要的数据类型，是一种 ` 概率平衡 ` 的数据结构，它允许快速的搜索、插入和删除操作，同时保持元素有序。

👉 [Sorted set 命令集合](https://redis.io/commands/?group=sorted-set)

- `ZRANGEBYSCORE`：按照元素权重返回一个范围内的元素
- `ZSCORE`：返回某个元素的权重值

# Sorted set 数据结构

代码实现：

- 结构定义：`server.h`
- 实现：`t_zset.c`

结构定义：

```c
typedef struct zset {
    dict *dict;
    zskiplist *zsl;
} zset;
```

结构定义是 `zset`，里面包含：
- ` 哈希表 dict` ：高效单点查询特性（ZSCORE）
- ` 跳表 zsl`：高效范围查询（ZRANGEBYSCORE）

# 跳表（skiplist）

` 多层 ` 的 ` 有序链表 `。下面展示的是 3 层的跳表，头节点是一个 level 数组，作为 level0~level2 的头指针。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220129140348.png)

## 结构定义

zskiplist 结构定义：

```c
typedef struct zskiplist {
    // 头节点和尾节点
    struct zskiplistNode *header, *tail;
    unsigned long length;
    int level;
} zskiplist;
```

zskiplistNode 结构定义：

```c
typedef struct zskiplistNode {
    // sorted set 中的元素
    sds ele;
    // 元素权重
    double score;
    // 后向指针（为了便于从跳表的尾节点倒序查找）
    struct zskiplistNode *backward;
    // 节点的 level 数组
    struct zskiplistLevel {
        // 每层上的前向指针
        struct zskiplistNode *forward;
        // 跨度，记录节点在某一层 *forward 指针和该节点，跨越了 level0 上的几个节点
        unsigned long span;
    } level[];
} zskiplistNode;
```

zskiplistNode 是 Redis 中用于实现有序集合（zset）的跳跃表（skiplist）节点的数据结构。

让我们逐一解释 zskiplistNode 结构体的组成部分：

- `sds ele;`：这是一个 SDS（Simple Dynamic String）类型的字段，用于存储有序集合中的元素（成员）。SDS 是 Redis 的字符串表示形式，它在传统的 C 字符串 (char*) 基础上提供了更多的功能和安全性，例如动态大小和二进制安全。
- `double score;`：这是一个 double 类型的字段，用于存储与元素关联的分数值。在 Redis 的有序集合中，每个元素都有一个分数，用于对元素进行排序。这个分数值可以是任意的双精度浮点数。
- `struct zskiplistNode *backward;`：这是一个指向前一个节点的指针。在跳跃表中，节点通常有多个指向其他节点的指针，这里的 backward 指针用于反向迭代跳跃表。
- `struct zskiplistLevel {...} level[];`：这是一个嵌套的结构体，它定义了跳跃表节点在每一层的连接信息。由于它是一个柔性数组（flexible array member），它不占用结构体大小计算的空间，并且允许动态地为每个节点分配不同数量的层级。嵌套结构体 zskiplistLevel 包含以下字段：
  - `struct zskiplistNode *forward;`：这是一个指向下一个节点的指针。在每一层中，forward 指针用于前向迭代跳跃表。
  - `unsigned long span;`：这是一个无符号长整型字段，用于存储当前节点到 forward 指针指向的下一个节点之间的跨度（间隔）。这个值在跳跃表操作中用于快速计算排名或者位置。

zskiplistNode 结构体的设计使得跳跃表节点可以有多个层级，每个层级都有自己的前向指针和跨度值。这使得跳跃表能够通过对节点层级的随机化处理，平衡搜索路径的长度，从而在平均情况下实现对数级的时间复杂度。跳跃表的这种结构特别适合于实现有序集合，因为它可以在保持元素排序的同时，快速地进行搜索和更新操作。


![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220129141259.png)

## 跳表节点查询

在查询某个节点时，跳表会从头节点的最高层开始，查找下一个节点：
- 访问下一个节点
  - 当前节点的元素权重 < 要查找的权重
  - 当前节点的元素权重 = 要查找的权重，且节点数据 < 要查找的数据
- 访问当前节点 level 数组的下一层指针
  - 当前节点的元素权重 > 要查找的权重

```c
// 获取跳表的表头
x = zsl->header;
// 从最大层数开始逐一遍历
for (i = zsl->level-1; i >= 0; i--) {
   ...
   while (x->level[i].forward && (x->level[i].forward->score < score || (x->level[i].forward->score == score
    && sdscmp(x->level[i].forward->ele,ele) < 0))) {
      ...
      x = x->level[i].forward;
    }
    ...
}
```

## 层数设置

几种方法：
1. 每层的节点数约是下一层节点数的一半。
   - 好处：查找时类似于二分查找，查找复杂度可以减低到 O(logN)
   - 坏处：每次插入 / 删除节点，都要 ` 调整后续节点层数 `，带来额外开销
2. ✅ ` 随机生成每个节点的层数 `。Redis 跳表采用了这种方法。

Redis 中，跳表节点层数是由 `zslRandomLevel` 函数决定。

```c
int zslRandomLevel(void) {
    int level = 1;
    while ((random()&0xFFFF) < (ZSKIPLIST_P * 0xFFFF))
        level += 1;
    return (level<ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
}
```

其中每层增加的概率是 `0.25`，最大层数是 32。

```c
#define ZSKIPLIST_MAXLEVEL 32 /* Should be enough for 2^64 elements */
#define ZSKIPLIST_P 0.25      /* Skiplist P = 1/4 */
```

## 插入节点 zslInsert

```c
zskiplistNode *zslInsert(zskiplist *zsl, double score, sds ele) {
    zskiplistNode *update[ZSKIPLIST_MAXLEVEL], *x;
    unsigned int rank[ZSKIPLIST_MAXLEVEL];
    int i, level;

    serverAssert(!isnan(score));
    x = zsl->header;
    // 从最高层的 level 开始找
    for (i = zsl->level-1; i >= 0; i--) {
        // 每层待插入的位置
        rank[i] = i == (zsl->level-1) ? 0 : rank[i+1];
        // forward.score <待插入 score || (forward.score < 待插入 score && forward.ele < ele)
        while (x->level[i].forward &&
               (x->level[i].forward->score < score ||
                (x->level[i].forward->score == score &&
                 sdscmp(x->level[i].forward->ele, ele) < 0))) {
            // 在同一层 level 找下一个节点
            rank[i] += x->level[i].span;
            x = x->level[i].forward;
        }
        update[i] = x;
    }

    // 随机层数
    level = zslRandomLevel();

    // 如果待插入节点的随机层数 > 跳表当前的层数
    if (level> zsl->level) {
        // 增加对应的层数
        for (i = zsl->level; i < level; i++) {
            rank[i] = 0;
            update[i] = zsl->header;
            update[i]->level[i].span = zsl->length;
        }
        zsl->level = level;
    }
    // 新建节点
    x = zslCreateNode(level, score, ele);
    // 设置新建节点的 level 数组
    for (i = 0; i < level; i++) {
        x->level[i].forward = update[i]->level[i].forward;
        update[i]->level[i].forward = x;

        /* update span covered by update[i] as x is inserted here */
        x->level[i].span = update[i]->level[i].span - (rank[0] - rank[i]);
        update[i]->level[i].span = (rank[0] - rank[i]) + 1;
    }

    for (i = level; i < zsl->level; i++) {
        update[i]->level[i].span++;
    }

    x->backward = (update[0] == zsl->header) ? NULL : update[0];
    if (x->level[0].forward)
        x->level[0].forward->backward = x;
    else
        zsl->tail = x;
    zsl->length++;
    return x;
}
```

流程简述：

1. 初始化：分配 `update` 和 `rank` 数组，用于记录插入路径和跨度。
2. 参数校验：校验待插入的分数值 `score`。
3. 查找插入位置：
   - 从跳跃表的顶层开始向下查找每一层级的插入点。
   - 更新 `update` 和 `rank` 记录，为之后插入新节点做准备。
4. 生成层高：通过 `zslRandomLevel` 函数生成新节点的随机层高 `level`。
5. 调整跳跃表层高：
   - 如果新节点的层高超过跳跃表的当前层高，更新跳跃表的层高，并调整 `update` 和 `rank`。
6. 创建新节点：调用 `zslCreateNode` 根据随机层高 `level`、分数 `score` 和元素 `ele` 创建新节点 `x`。
7. 连接新节点：
   - 将新节点 `x` 插入到跳跃表的各个层级中。
   - 更新 `forward` 指针和 `span` 记录。
8. 更新跨度和后继节点：
   - 新节点以上层级的 `span` 加一。
   - 配置新节点的 `backward` 指针和尾节点。
9. 更新跳跃表信息：递增跳跃表的 `length` 记录长度增加。
10. 返回新节点：返回新创建的节点 `x`。

## 删除节点 zslDelete

`zslDeleteNode` 函数用于从 Redis 的跳跃表（skiplist）中删除一个节点，同时更新相关的节点指针和跨度（span）信息。

```c
int zslDelete(zskiplist *zsl, double score, sds ele, zskiplistNode **node) {
    zskiplistNode *update[ZSKIPLIST_MAXLEVEL], *x;
    int i;

    x = zsl->header;
    // 找到待删除的节点
    for (i = zsl->level-1; i >= 0; i--) {
        while (x->level[i].forward &&
                (x->level[i].forward->score < score ||
                    (x->level[i].forward->score == score &&
                     sdscmp(x->level[i].forward->ele,ele) < 0)))
        {
            x = x->level[i].forward;
        }
        update[i] = x;
    }
    x = x->level[0].forward;
    // 判断节点的 score 和 ele 是否符合条件
    if (x && score == x->score && sdscmp(x->ele,ele) == 0) {
        // 删除该节点
        zslDeleteNode(zsl, x, update);
        if (!node)
            // 释放内存
            zslFreeNode(x);
        else
            *node = x;
        return 1;
    }
    return 0; /* not found */
}
```
流程简述：

1. 初始化：遍历跳跃表的所有层级。
2. 遍历更新：对于每个层级，检查当前层级的前向指针是否指向待删除节点 `x`：
   - 是，更新前向指针和跨度（span）。
   - 否，减少对应层级的跨度（span）。
3. 更新后向指针：如果待删除的节点 `x` 有后继节点，将后继节点的后向指针指向 `x` 的前驱节点。
4. 更新跳跃表尾部：如果待删除的节点 `x` 是跳跃表的尾节点，将跳跃表尾部指针更新为 `x` 的前驱节点。
5. 修剪跳跃表层级：如果跳跃表的最高层级无节点，则减少跳跃表的层级。
6. 更新跳跃表长度：减少跳跃表的节点计数。

# Sorted set 基本操作

首先看下如何创建跳表，代码在 object.c 中，可以看到会调用 dictCreate 函数创建哈希表，之后调用 zslCreate 函数创建跳表。

```c
robj *createZsetObject(void) {
    zset *zs = zmalloc(sizeof(*zs));
    robj *o;

    zs->dict = dictCreate(&zsetDictType,NULL);
    zs->zsl = zslCreate();
    o = createObject(OBJ_ZSET,zs);
    o->encoding = OBJ_ENCODING_SKIPLIST;
    return o;
}
```

哈希表和跳表的数据必须保持一致。我们通过 zsetAdd 函数研究一下。

## zsetAdd

啥都不说了，都在流程图里。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220129154144.png)

首先判断编码是 ziplist，还是 skiplist。

### ziplist 编码

里面需要判断是否要转换编码，如果转换编码，则需要调用 zsetConvert 转换成 ziplist 编码，这里就不叙述了。

```c
// ziplist 编码时的处理逻辑
if (zobj->encoding == OBJ_ENCODING_ZIPLIST) {
    unsigned char *eptr;

    // zset 存在要插入的元素
    if ((eptr = zzlFind(zobj->ptr, ele, &curscore)) != NULL) {
        // 存储要插入的元素时，在 not exist 时更新
        if (nx) {
            *out_flags |= ZADD_OUT_NOP;
            return 1;
        }

        ……
        if (newscore) *newscore = score;

        // 原来的 score 和待插入 score 不同
        if (score != curscore) {
            // 先删除原来的元素
            zobj->ptr = zzlDelete(zobj->ptr, eptr);
            // 插入新元素
            zobj->ptr = zzlInsert(zobj->ptr, ele, score);
            *out_flags |= ZADD_OUT_UPDATED;
        }
        return 1;
    }
    // zset 中不存在要插入的元素
    else if (!xx) {

        // 检测 ele 是否过大 || ziplist 过大
        if (zzlLength(zobj->ptr) + 1 > server.zset_max_ziplist_entries ||
            sdslen(ele) > server.zset_max_ziplist_value ||
            !ziplistSafeToAdd(zobj->ptr, sdslen(ele))) {
            // 转换成 skiplist 编码
            zsetConvert(zobj, OBJ_ENCODING_SKIPLIST);
        } else {
            // 在 ziplist 中插入 (element,score) pair
            zobj->ptr = zzlInsert(zobj->ptr, ele, score);
            if (newscore) *newscore = score;
            *out_flags |= ZADD_OUT_ADDED;
            return 1;
        }
    } else {
        *out_flags |= ZADD_OUT_NOP;
        return 1;
    }
}
```

### skiplist 编码

```c
// skiplist 编码时的处理逻辑
if (zobj->encoding == OBJ_ENCODING_SKIPLIST) {
    zset *zs = zobj->ptr;
    zskiplistNode *znode;
    dictEntry *de;

    // 从哈希表中查询新增元素
    de = dictFind(zs->dict, ele);

    // 查询到该元素
    if (de != NULL) {
        /* NX? Return, same element already exists. */
        if (nx) {
            *out_flags |= ZADD_OUT_NOP;
            return 1;
        }

        ……
        if (newscore) *newscore = score;

        // 权重发生变化
        if (score != curscore) {
            // 更新跳表节点
            znode = zslUpdateScore(zs->zsl, curscore, ele, score);
            // 让哈希表的元素的值指向跳表节点的权重
            dictGetVal(de) = &znode->score; /* Update score ptr. */
            *out_flags |= ZADD_OUT_UPDATED;
        }
        return 1;
    }
        // 如果新元素不存在
    else if (!xx) {
        ele = sdsdup(ele);
        // 在跳表中插入新元素
        znode = zslInsert(zs->zsl, score, ele);
        // 在哈希表中插入新元素
        serverAssert(dictAdd(zs->dict, ele, &znode->score) == DICT_OK);
        *out_flags |= ZADD_OUT_ADDED;
        if (newscore) *newscore = score;
        return 1;
    } else {
        *out_flags |= ZADD_OUT_NOP;
        return 1;
    }
}
```

### zsetAdd 整体代码

```c
int zsetAdd(robj *zobj, double score, sds ele, int in_flags, int *out_flags, double *newscore) {
    /* Turn options into simple to check vars. */
    int incr = (in_flags & ZADD_IN_INCR) != 0;
    int nx = (in_flags & ZADD_IN_NX) != 0;
    int xx = (in_flags & ZADD_IN_XX) != 0;
    int gt = (in_flags & ZADD_IN_GT) != 0;
    int lt = (in_flags & ZADD_IN_LT) != 0;
    *out_flags = 0; /* We'll return our response flags. */
    double curscore;

    /* NaN as input is an error regardless of all the other parameters. */
    // 判断 score 是否合法，不合法直接 return
    if (isnan(score)) {
        *out_flags = ZADD_OUT_NAN;
        return 0;
    }

    /* Update the sorted set according to its encoding. */

    // ziplist 编码时的处理逻辑
    if (zobj->encoding == OBJ_ENCODING_ZIPLIST) {
        unsigned char *eptr;

        // zset 存在要插入的元素
        if ((eptr = zzlFind(zobj->ptr, ele, &curscore)) != NULL) {
            // 存储要插入的元素时，在 not exist 时更新
            if (nx) {
                *out_flags |= ZADD_OUT_NOP;
                return 1;
            }

            /* Prepare the score for the increment if needed. */
            if (incr) {
                score += curscore;
                if (isnan(score)) {
                    *out_flags |= ZADD_OUT_NAN;
                    return 0;
                }
            }

            /* GT/LT? Only update if score is greater/less than current. */
            if ((lt && score>= curscore) || (gt && score <= curscore)) {
                *out_flags |= ZADD_OUT_NOP;
                return 1;
            }

            if (newscore) *newscore = score;

            // 原来的 score 和待插入 score 不同
            if (score != curscore) {
                // 先删除原来的元素
                zobj->ptr = zzlDelete(zobj->ptr, eptr);
                // 插入新元素
                zobj->ptr = zzlInsert(zobj->ptr, ele, score);
                *out_flags |= ZADD_OUT_UPDATED;
            }
            return 1;
        }
            // zset 中不存在要插入的元素
        else if (!xx) {

            // 检测 ele 是否过大 || ziplist 过大
            if (zzlLength(zobj->ptr) + 1 > server.zset_max_ziplist_entries ||
                sdslen(ele) > server.zset_max_ziplist_value ||
                !ziplistSafeToAdd(zobj->ptr, sdslen(ele))) {
                // 转换成 skiplist 编码
                zsetConvert(zobj, OBJ_ENCODING_SKIPLIST);
            } else {
                // 在 ziplist 中插入 (element,score) pair
                zobj->ptr = zzlInsert(zobj->ptr, ele, score);
                if (newscore) *newscore = score;
                *out_flags |= ZADD_OUT_ADDED;
                return 1;
            }
        } else {
            *out_flags |= ZADD_OUT_NOP;
            return 1;
        }
    }

    /* Note that the above block handling ziplist would have either returned or
     * converted the key to skiplist. */

    // skiplist 编码时的处理逻辑
    if (zobj->encoding == OBJ_ENCODING_SKIPLIST) {
        zset *zs = zobj->ptr;
        zskiplistNode *znode;
        dictEntry *de;

        // 从哈希表中查询新增元素
        de = dictFind(zs->dict, ele);

        // 查询到该元素
        if (de != NULL) {
            /* NX? Return, same element already exists. */
            if (nx) {
                *out_flags |= ZADD_OUT_NOP;
                return 1;
            }

            // 从哈希表中查询元素的权重
            curscore = *(double *) dictGetVal(de);

            // 如果要更新元素权重值
            if (incr) {
                score += curscore;
                if (isnan(score)) {
                    *out_flags |= ZADD_OUT_NAN;
                    return 0;
                }
            }

            /* GT/LT? Only update if score is greater/less than current. */
            if ((lt && score>= curscore) || (gt && score <= curscore)) {
                *out_flags |= ZADD_OUT_NOP;
                return 1;
            }

            if (newscore) *newscore = score;

            // 权重发生变化
            if (score != curscore) {
                // 更新跳表节点
                znode = zslUpdateScore(zs->zsl, curscore, ele, score);
                // 让哈希表的元素的值指向跳表节点的权重
                dictGetVal(de) = &znode->score; /* Update score ptr. */
                *out_flags |= ZADD_OUT_UPDATED;
            }
            return 1;
        }
            // 如果新元素不存在
        else if (!xx) {
            ele = sdsdup(ele);
            // 在跳表中插入新元素
            znode = zslInsert(zs->zsl, score, ele);
            // 在哈希表中插入新元素
            serverAssert(dictAdd(zs->dict, ele, &znode->score) == DICT_OK);
            *out_flags |= ZADD_OUT_ADDED;
            if (newscore) *newscore = score;
            return 1;
        } else {
            *out_flags |= ZADD_OUT_NOP;
            return 1;
        }
    } else {
        serverPanic("Unknown sorted set encoding");
    }
    return 0; /* Never reached. */
}
```

## zsetDel

```c
int zsetDel(robj *zobj, sds ele) {
    // ziplist 编码
    if (zobj->encoding == OBJ_ENCODING_ZIPLIST) {
        unsigned char *eptr;

        // 找到对应的节点
        if ((eptr = zzlFind(zobj->ptr, ele, NULL)) != NULL) {
            // 从 ziplist 中删除
            zobj->ptr = zzlDelete(zobj->ptr, eptr);
            return 1;
        }
    }
    // skiplist 编码
    else if (zobj->encoding == OBJ_ENCODING_SKIPLIST) {
        zset *zs = zobj->ptr;
        // 从 skiplist 中删除
        if (zsetRemoveFromSkiplist(zs, ele)) {
            if (htNeedsResize(zs->dict)) dictResize(zs->dict);
            return 1;
        }
    } else {
        serverPanic("Unknown sorted set encoding");
    }
    return 0; /* No such element found. */
}
```

zsetRemoveFromSkiplist 函数如下：

```c
static int zsetRemoveFromSkiplist(zset *zs, sds ele) {
    dictEntry *de;
    double score;

    de = dictUnlink(zs->dict,ele);
    if (de != NULL) {
        score = *(double*)dictGetVal(de);

        // 从哈希表 unlink 该元素
        dictFreeUnlinkedEntry(zs->dict,de);

        // 从跳表中删除该元素，并释放内存空间
        int retval = zslDelete(zs->zsl,score,ele,NULL);
        serverAssert(retval);

        return 1;
    }

    return 0;
}
```

代码中的 zslDelete 函数在跳表中分析过（文章中的跳表章节）。

# 参考链接

- [《Redis 设计与实现》- 有序集合对象](http://redisbook.com/preview/object/sorted_set.html)
- [极客时间《Redis 源码剖析与实战》- 05 | 有序集合为何能同时支持点查询和范围查询？](https://time.geekbang.org/column/article/404391)

# Redis 源码简洁剖析系列

- [Redis 7.0.md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%207.0.md)
- [Redis 源码简洁剖析 01 - 环境配置. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2001%20-%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)
- [Redis 源码简洁剖析 02 - SDS 字符串. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2002%20-%20SDS%20%E5%AD%97%E7%AC%A6%E4%B8%B2.md)
- [Redis 源码简洁剖析 03 - Dict Hash 基础. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2003%20-%20Dict%20Hash%20%E5%9F%BA%E7%A1%80.md)
- [Redis 源码简洁剖析 04 - Sorted set 有序集合. md](https://github.com/LjyYano/Thinking_in_Java_MindMapping/tree/master/%E7%BC%96%E7%A8%8B/Redis%20%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90%E7%B3%BB%E5%88%97/Redis%20%E6%BA%90%E7%A0%81%E7%AE%80%E6%B4%81%E5%89%96%E6%9E%90%2004%20-%20Sorted%20Set%20%E6%9C%89%E5%BA%8F%E9%9B%86%E5%90%88.md)
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