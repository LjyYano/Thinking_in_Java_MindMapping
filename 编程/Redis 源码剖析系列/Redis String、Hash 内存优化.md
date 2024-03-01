---
date: 2024-03-01
---

- [问题](#问题)
- [String 格式写入](#string-格式写入)
  - [String 底层实现](#string-底层实现)
- [Hash 格式写入](#hash-格式写入)
  - [Hash 底层实现](#hash-底层实现)
  - [如何存储](#如何存储)


# 问题

💡 如果存储上亿条数据，如何进行内存优化？是使用 String 存储还是 Hash 存储？

> 假设存储的数据是用户信息，即 userId 以及 userData。
> 假设两者的长度都是 8 字节

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-03-01-15-58-51.png)

# String 格式写入

1 条数据理论上应该占用 16 字节，即 8 字节 userId + 8 字节 userData。但是实际上内存占用比这个更大。

为了实现从键到值的快速访问，Redis 使用了一个全局哈希表来保存所有键值对。其中 Key 用 SDS 格式存储，Value 则用 RedisObject 存储，RedisObject 再指向具体的底层数据结构。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-03-01-15-58-29.png)

## String 底层实现

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-03-01-15-59-56.png)

Redis 没有使用 C 语言传统的字符串（以空字符为结尾的字符数组），而是自己创建了一种名为 SDS（简单动态字符串）的抽象类型，用作 Redis 默认的字符串。SDS 的定义如下：

```c
struct sdshdr {
    int len;         // 记录 buf 数组中已使用字节的数量
    int free;        // 记录 buf 数组中未使用字节的数量
    char buf[];      // 字节数组，用于保存实际字符串
}
```

一个简单的 set 命令最终会产生 4 个消耗内存的结构：
- 一个 dictEntry 结构，24 字节，负责保存具体的键值对
- 一个 redisObject 结构，16 字节，负责保存 value 对象
- 一个 SDS 结构，（sizeof(int) \* 2 + 1 个结束符 + key 长度），用作 key 字符串
- 一个 SDS 结构，（sizeof(int) \* 2 + 1 个结束符 + value 长度），用作 value 字符串

当 key 个数逐渐增多，redis 还会以 rehash 的方式扩展哈希表节点数组，即增大哈希表的 bucket 个数，每个 bucket 元素都是个指针（`dictEntry*`），占 8 字节，bucket 个数是超过 key 个数向上求整的 2 的 n 次方。

由此可见，在 String 格式中，Redis 自身的数据结构占了绝大部分的内存。通过查阅相关资料，我们可以使用 Hash 格式的压缩表来压缩存储。

# Hash 格式写入

## Hash 底层实现

Hash 底层是 ziplist 与 hashtable 结构之一。

当一个哈希对象可以满足以下两个条件中的任意一个，哈希对象会选择使用 ziplist 来进行存储：

1. 哈希对象中的所有键值对总长度 (包括键和值) 小于 64 字节（这个阈值可以通过参数 hash-max-ziplist-value 来进行控制）。
2. 哈希对象中的键值对数量小于 512 个（这个阈值可以通过参数 hash-max-ziplist-entries 来进行控制）。

一旦不满足这两个条件中的任意一个，哈希对象就会选择使用 hashtable 来存储。

压缩表实际上类似一个数组，数组中的每一个元素都对应保存一个数据。和数组不同的是，压缩列表在表头有三个字段 zlbytes、zltail 和 zllen，分别表示列表长度、列表尾的偏移量和列表中的 entry 个数；压缩列表在表尾还有一个 zlend，表示列表的结束。Entry 中保存了 field 和 Value 数据。


![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-03-01-16-09-34.png)

Hash 在使用压缩表的数据结构时只使用了少量 Redis 自身的对象，可以极大的节约内存。


## 如何存储

KV 结构的数据如何才能存入 key/field/value 格式呢？我们可以采用基数排序的思想，将数据均匀的分散在不同的桶中，将每个桶中的数据放入对应的 key 中。

为保持分桶均匀，我们使用 Crc64 算法对用户 ID 作 hash 计算。将计算后的 Long 值做拆分，取前 19 个比特位（524287 个分桶）计算 key，取后 45 个比特位作为 filed，用户数据作为 data。最终 6.5 亿数据拆分的分桶数为 524287，每个分桶中有 1240 个数据。

