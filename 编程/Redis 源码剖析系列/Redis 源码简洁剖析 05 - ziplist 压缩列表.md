---
date: 2022-02-02
---


- [ziplist 是什么](#ziplist-是什么)
  - [Redis 哪些数据结构使用了 ziplist？](#redis-哪些数据结构使用了-ziplist)
- [ziplist 特点](#ziplist-特点)
  - [优点](#优点)
  - [缺点](#缺点)
- [ziplist 数据结构](#ziplist-数据结构)
- [ziplist 节点](#ziplist-节点)
  - [pre\_entry\_length](#pre_entry_length)
  - [encoding 和 length](#encoding-和-length)
  - [content](#content)
- [ziplist 基本操作](#ziplist-基本操作)
  - [创建新 ziplist](#创建新-ziplist)
  - [将节点添加到末端](#将节点添加到末端)
  - [将节点添加到某个/某些节点的前面](#将节点添加到某个某些节点的前面)
  - [删除节点](#删除节点)
- [参考链接](#参考链接)
- [Redis 源码简洁剖析系列](#redis-源码简洁剖析系列)
- [我的公众号](#我的公众号)

# ziplist 是什么

压缩列表，内存紧凑的数据结构，占用一块连续的内存空间。一个 ziplist 可以包含多个节点（entry）， 每个节点可以保存一个长度受限的字符数组（不以 `\0` 结尾的 `char` 数组）或者整数， 包括：

- 字符数组
    
    - 长度小于等于 `63` （2^6-1）字节的字符数组
    - 长度小于等于 `16383` （12^14-1） 字节的字符数组
    - 长度小于等于 `4294967295` （2^32-1）字节的字符数组
    
- 整数
    
    - `4` 位长，介于 `0` 至 `12` 之间的无符号整数
    - `1` 字节长，有符号整数
    - `3` 字节长，有符号整数
    - `int16_t` 类型整数
    - `int32_t` 类型整数
    - `int64_t` 类型整数

## Redis 哪些数据结构使用了 ziplist？

- 哈希键
- 列表键
- 有序集合键

# ziplist 特点

## 优点

- 节省内存

## 缺点

- 不能保存过多的元素，否则访问性能会下降
- 不能保存过大的元素，否则容易导致内存重新分配，甚至引起连锁更新

# ziplist 数据结构

啥都不说了，都在注释里。

```c
// ziplist 中的元素，是 string 或者 integer
typedef struct {
    // 如果元素是 string，slen 就表示长度
    unsigned char *sval;
    unsigned int slen;
    // 如果是 integer，sval 是 NULL，lval 就是 integer 的值
    long long lval;
} ziplistEntry;
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220203102540.png?x-oss-process=style/yano)

为了方便地取出 ziplist 的各个域以及一些指针地址， ziplist 模块定义了以下宏：

```c
// 取出 zlbytes 的值
#define ZIPLIST_BYTES(zl)       (*((uint32_t*)(zl)))

// 取出 zltail 的值
#define ZIPLIST_TAIL_OFFSET(zl) (*((uint32_t*)((zl)+sizeof(uint32_t))))

// 取出 zllen 的值
#define ZIPLIST_LENGTH(zl)      (*((uint16_t*)((zl)+sizeof(uint32_t)*2)))

// 返回 ziplist header 部分的长度，总是固定的 10 字节
#define ZIPLIST_HEADER_SIZE     (sizeof(uint32_t)*2+sizeof(uint16_t))

// 返回 ziplist end 部分的长度，总是固定的 1 字节
#define ZIPLIST_END_SIZE        (sizeof(uint8_t))

// 返回到达 ziplist 第一个节点（表头）的地址
#define ZIPLIST_ENTRY_HEAD(zl)  ((zl)+ZIPLIST_HEADER_SIZE)

// 返回到达 ziplist 最后一个节点（表尾）的地址
#define ZIPLIST_ENTRY_TAIL(zl)  ((zl)+intrev32ifbe(ZIPLIST_TAIL_OFFSET(zl)))

// 返回 ziplist 的末端，也即是 zlend 之前的地址
#define ZIPLIST_ENTRY_END(zl)   ((zl)+intrev32ifbe(ZIPLIST_BYTES(zl))-1)
```

# ziplist 节点

```c
typedef struct zlentry {
    // 前一个节点的长度，通过这个值，可以进行指针计算，从而跳转到上一个节点
    unsigned int prevrawlen;
    unsigned int prevrawlensize;
    // entry 的编码方式
    // 1. entry 是 string，可能是 1 2 5 个字节的 header
    // 2. entry 是 integer，固定为 1 字节
    unsigned int lensize;
    // 实际 entry 的字节数
    // 1. entry 是 string，则表示 string 的长度
    // 2. entry 是 integer，则根据数值范围，可能是 1, 2, 3, 4, 8
    unsigned int len;
    // prevrawlensize + lensize
    unsigned int headersize;
    // ZIP_STR_* 或者 ZIP_INT_*
    unsigned char encoding;
    unsigned char *p;            /* Pointer to the very start of the entry, that
                                    is, this points to prev-entry-len field. */
} zlentry;
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220204085123.png?x-oss-process=style/yano)

## pre_entry_length

记录`前一个节点的长度`。通过这个值，可以进行指针计算，从而`跳转到上一个节点`。

```c
area        |<---- previous entry --->|<--------------- current entry ---------------->|

size          5 bytes                   1 byte             ?          ?        ?
            +-------------------------+-----------------------------+--------+---------+
component   | ...                     | pre_entry_length | encoding | length | content |
            |                         |                  |          |        |         |
value       |                         | 0000 0101        |    ?     |   ?    |    ?    |
            +-------------------------+-----------------------------+--------+---------+
            ^                         ^
address     |                         |
            p = e - 5                 e
```

以上图为例，从当前节点的指针 e，减去 pre_entry_length 的值（0000 0101 的十进制值，5），就可以得到指向前一个节点的地址 p。

## encoding 和 length

`encoding` 和 `length` 两部分一起决定了 `content` 部分所保存的数据的类型（以及长度）。

其中， `encoding` 域的长度为两个 bit ， 它的值可以是 `00` 、 `01` 、 `10` 和 `11` ：

- `00` 、 `01` 和 `10` 表示 `content` 部分保存着字符数组。
- `11` 表示 `content` 部分保存着整数。

以 `00` 、 `01` 和 `10` 开头的字符数组的编码方式如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220204085734.png)

表格中的下划线 _ 表示留空，而变量 b 、 x 等则代表实际的二进制数据。为了方便阅读，多个字节之间用空格隔开。

11 开头的整数编码如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220204085805.png)

## content

`content` 部分保存着节点的内容，类型和长度由 `encoding` 和 `length` 决定。

以下是一个保存着字符数组 `hello world` 的节点的例子：

```c
area      |<---------------------- entry ----------------------->|

size        ?                  2 bit      6 bit    11 byte
          +------------------+----------+--------+---------------+
component | pre_entry_length | encoding | length | content       |
          |                  |          |        |               |
value     | ?                |    00    | 001011 | hello world   |
          +------------------+----------+--------+---------------+
```

`encoding` 域的值 `00` 表示节点保存着一个长度小于等于 63 字节的字符数组， `length` 域给出了这个字符数组的准确长度 —— `11` 字节（的二进制 `001011`）， `content` 则保存着字符数组值 `hello world` 本身（为了方便表示， `content` 部分使用字符而不是二进制表示）。

以下是另一个节点，它保存着整数 `10086` ：

```c
area      |<---------------------- entry ----------------------->|

size        ?                  2 bit      6 bit    2 bytes
          +------------------+----------+--------+---------------+
component | pre_entry_length | encoding | length | content       |
          |                  |          |        |               |
value     | ?                |    11    | 000000 | 10086         |
          +------------------+----------+--------+---------------+
```

`encoding` 域的值 `11` 表示节点保存的是一个整数； 而 `length` 域的值 `000000` 表示这个节点的值的类型为 `int16_t` ； 最后， `content` 保存着整数值 `10086` 本身（为了方便表示， `content` 部分用十进制而不是二进制表示）。
# ziplist 基本操作

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220203104757.png)

## 创建新 ziplist

创建一个新的 ziplist，时间复杂度是 O(1)。

```c
/* Create a new empty ziplist. */
unsigned char *ziplistNew(void) {
    // header 和 end 需要的字节数
    unsigned int bytes = ZIPLIST_HEADER_SIZE+ZIPLIST_END_SIZE;
    // 分配 bytes 长度的内存
    unsigned char *zl = zmalloc(bytes);
    // 赋值 zlbytes
    ZIPLIST_BYTES(zl) = intrev32ifbe(bytes);
    // 赋值 zltail
    ZIPLIST_TAIL_OFFSET(zl) = intrev32ifbe(ZIPLIST_HEADER_SIZE);
    // 赋值 zllen
    ZIPLIST_LENGTH(zl) = 0;
    // 赋值 zlend
    zl[bytes-1] = ZIP_END;
    return zl;
}
```

```c
area        |<---- ziplist header ---->|<-- end -->|

size          4 bytes   4 bytes 2 bytes  1 byte
            +---------+--------+-------+-----------+
component   | zlbytes | zltail | zllen | zlend     |
            |         |        |       |           |
value       |  1011   |  1010  |   0   | 1111 1111 |
            +---------+--------+-------+-----------+
                                       ^
                                       |
                               ZIPLIST_ENTRY_HEAD
                                       &
address                        ZIPLIST_ENTRY_TAIL
                                       &
                               ZIPLIST_ENTRY_END
```

空白 ziplist 的表头、表尾和末端处于同一地址。

创建了 ziplist 之后， 就可以往里面添加新节点了， 根据新节点添加位置的不同， 这个工作可以分为两类来进行：

1. 将节点添加到 ziplist 末端：在这种情况下，新节点的后面没有任何节点。
2. 将节点添加到某个/某些节点的前面：在这种情况下，新节点的后面有至少一个节点。

以下两个小节分别讨论这两种情况。

## 将节点添加到末端

将新节点添加到 ziplist 的末端需要执行以下三个步骤：

1. 记录到达 ziplist 末端所需的偏移量（因为之后的内存重分配可能会改变 ziplist 的地址，因此记录偏移量而不是保存指针）
2. 根据新节点要保存的值，计算出编码这个值所需的空间大小，以及编码它前一个节点的长度所需的空间大小，然后对 ziplist 进行内存重分配。
3. 设置新节点的各项属性： `pre_entry_length` 、 `encoding` 、 `length` 和 `content` 。
4. 更新 ziplist 的各项属性，比如记录空间占用的 `zlbytes` ，到达表尾节点的偏移量 `zltail` ，以及记录节点数量的 `zllen` 。

举个例子，假设现在要将一个新节点添加到只含有一个节点的 ziplist 上，程序首先要执行步骤 1 ，定位 ziplist 的末端：

```c
area        |<---- ziplist header ---->|<--- entries -->|<-- end -->|

size          4 bytes  4 bytes  2 bytes  5 bytes          1 bytes
            +---------+--------+-------+----------------+-----------+
component   | zlbytes | zltail | zllen | entry 1        | zlend     |
            |         |        |       |                |           |
value       |  10000  |  1010  |   1   | ?              | 1111 1111 |
            +---------+--------+-------+----------------+-----------+
                                       ^                ^
                                       |                |
address                         ZIPLIST_ENTRY_HEAD   ZIPLIST_ENTRY_END
                                       &
                                ZIPLIST_ENTRY_TAIL
```

然后执行步骤 2 ，程序需要计算新节点所需的空间：

假设我们要添加到节点里的值为字符数组 `hello world` ， 那么保存这个值共需要 12 字节的空间：

- 11 字节用于保存字符数组本身；
- 另外 1 字节中的 2 bit 用于保存类型编码 `00` ， 而其余 6 bit 则保存字符数组长度 `11` 的二进制 `001011` 。

另外，节点还需要 1 字节， 用于保存前一个节点的长度 `5` （二进制 `101` ）。

合算起来，为了添加新节点， ziplist 总共需要多分配 13 字节空间。 以下是分配完成之后， ziplist 的样子：

```c
area        |<---- ziplist header ---->|<------------ entries ------------>|<-- end -->|

size          4 bytes  4 bytes  2 bytes  5 bytes          13 bytes           1 bytes
            +---------+--------+-------+----------------+------------------+-----------+
component   | zlbytes | zltail | zllen | entry 1        | entry 2          | zlend     |
            |         |        |       |                |                  |           |
value       |  10000  |  1010  |   1   | ?              | pre_entry_length | 1111 1111 |
            |         |        |       |                | ?                |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | encoding         |           |
            |         |        |       |                | ?                |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | length           |           |
            |         |        |       |                | ?                |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | content          |           |
            |         |        |       |                | ?                |           |
            |         |        |       |                |                  |           |
            +---------+--------+-------+----------------+------------------+-----------+
                                       ^                ^
                                       |                |
address                       ZIPLIST_ENTRY_HEAD   ZIPLIST_ENTRY_END
                                       &
                              ZIPLIST_ENTRY_TAIL
```

步骤三，更新新节点的各项属性（为了方便表示， content 的内容使用字符而不是二进制来表示）：

```c
area        |<---- ziplist header ---->|<------------ entries ------------>|<-- end -->|

size          4 bytes  4 bytes  2 bytes  5 bytes          13 bytes           1 bytes
            +---------+--------+-------+----------------+------------------+-----------+
component   | zlbytes | zltail | zllen | entry 1        | entry 2          | zlend     |
            |         |        |       |                |                  |           |
value       |  10000  |  1010  |   1   | ?              | pre_entry_length | 1111 1111 |
            |         |        |       |                | 101              |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | encoding         |           |
            |         |        |       |                | 00               |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | length           |           |
            |         |        |       |                | 001011           |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | content          |           |
            |         |        |       |                | hello world      |           |
            |         |        |       |                |                  |           |
            +---------+--------+-------+----------------+------------------+-----------+
                                       ^                ^
                                       |                |
address                       ZIPLIST_ENTRY_HEAD   ZIPLIST_ENTRY_END
                                       &
                              ZIPLIST_ENTRY_TAIL
```

最后一步，更新 ziplist 的 zlbytes 、 zltail 和 zllen 属性：

```c
area        |<---- ziplist header ---->|<------------ entries ------------>|<-- end -->|

size          4 bytes  4 bytes  2 bytes  5 bytes          13 bytes           1 bytes
            +---------+--------+-------+----------------+------------------+-----------+
component   | zlbytes | zltail | zllen | entry 1        | entry 2          | zlend     |
            |         |        |       |                |                  |           |
value       |  11101  |  1111  |  10   | ?              | pre_entry_length | 1111 1111 |
            |         |        |       |                | 101              |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | encoding         |           |
            |         |        |       |                | 00               |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | length           |           |
            |         |        |       |                | 001011           |           |
            |         |        |       |                |                  |           |
            |         |        |       |                | content          |           |
            |         |        |       |                | hello world      |           |
            |         |        |       |                |                  |           |
            +---------+--------+-------+----------------+------------------+-----------+
                                       ^                ^                  ^
                                       |                |                  |
address                                |          ZIPLIST_ENTRY_TAIL   ZIPLIST_ENTRY_END
                                       |
                               ZIPLIST_ENTRY_HEAD
```

## 将节点添加到某个/某些节点的前面

比起将新节点添加到 ziplist 的末端， 将一个新节点添加到某个/某些节点的前面要复杂得多， 因为这种操作除了将新节点添加到 ziplist 以外， 还可能引起后续一系列节点的改变。

举个例子，假设我们要将一个新节点 `new` 添加到节点 `prev` 和 `next` 之间：

```c
   add new entry here
           |
           V
+----------+----------+----------+----------+----------+
|          |          |          |          |          |
|   prev   |   next   | next + 1 | next + 2 |   ...    |
|          |          |          |          |          |
+----------+----------+----------+----------+----------+
```

程序首先为新节点扩大 ziplist 的空间：

```c
+----------+----------+----------+----------+----------+----------+
|          |          |          |          |          |          |
|   prev   |   ???    |   next   | next + 1 | next + 2 |   ...    |
|          |          |          |          |          |          |
+----------+----------+----------+----------+----------+----------+

           |<-------->|
              expand
              space

```

然后设置 new 节点的各项值 —— 到目前为止，一切都和前面介绍的添加操作一样：

```c
             set value,
             property,
             length,
             etc.
                |
                v
+----------+----------+----------+----------+----------+----------+
|          |          |          |          |          |          |
|   prev   |   new    |   next   | next + 1 | next + 2 |   ...    |
|          |          |          |          |          |          |
+----------+----------+----------+----------+----------+----------+
```

现在，新的 `new` 节点取代原来的 `prev` 节点， 成为了 `next` 节点的新前驱节点， 不过， 因为这时 `next` 节点的 `pre_entry_length` 域编码的仍然是 `prev` 节点的长度， 所以程序需要将 `new` 节点的长度编码进 `next` 节点的 `pre_entry_length` 域里， 这里会出现三种可能：

1. `next` 的 `pre_entry_length` 域的长度正好能够编码 `new` 的长度（都是 1 字节或者都是 5 字节）
2. `next` 的 `pre_entry_length` 只有 1 字节长，但编码 `new` 的长度需要 5 字节
3. `next` 的 `pre_entry_length` 有 5 字节长，但编码 `new` 的长度只需要 1 字节

对于情况 1 和 3 ， 程序直接更新 `next` 的 `pre_entry_length` 域。

如果是第二种情况， 那么程序必须对 ziplist 进行内存重分配， 从而扩展 `next` 的空间。 然而，因为 `next` 的空间长度改变了， 所以程序又必须检查 `next` 的后继节点 —— `next+1` ， 看它的 `pre_entry_length` 能否编码 `next` 的新长度， 如果不能的话，程序又需要继续对 `next+1` 进行扩容。

这就是说， 在某个/某些节点的前面添加新节点之后， 程序必须沿着路径挨个检查后续的节点，是否满足新长度的编码要求， 直到遇到一个能满足要求的节点（如果有一个能满足，则这个节点之后的其他节点也满足）， 或者到达 ziplist 的末端 `zlend` 为止。

## 删除节点

删除节点和添加操作的步骤类似。

1) 定位目标节点，并计算节点的空间长度 `target-size` ：

```c
   target start here
           |
           V
+----------+----------+----------+----------+----------+----------+
|          |          |          |          |          |          |
|   prev   |  target  |   next   | next + 1 | next + 2 |   ...    |
|          |          |          |          |          |          |
+----------+----------+----------+----------+----------+----------+

           |<-------->|
            target-size
```

2) 进行内存移位，覆盖 `target` 原本的数据，然后通过内存重分配，收缩多余空间：

```c
   target start here
           |
           V
+----------+----------+----------+----------+----------+
|          |          |          |          |          |
|   prev   |   next   | next + 1 | next + 2 |   ...    |
|          |          |          |          |          |
+----------+----------+----------+----------+----------+

           | <------------------------------------------ memmove
```

3) 检查 `next` 、 `next+1` 等后续节点能否满足新前驱节点的编码。和添加操作一样，删除操作也可能会引起连锁更新。

# 参考链接

- [《Redis 设计与实现》- 压缩列表](https://redisbook.readthedocs.io/en/latest/compress-datastruct/ziplist.html)

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