
# 是什么

维基百科：[Log-structured merge-tree
](https://en.wikipedia.org/wiki/Log-structured_merge-tree)

## 特点

Log-Structured-Merge-Tree，是一种存储结构。是顺序写入磁盘，在写多读少的场景下，性能比较好。（提高写性能，牺牲一点读性能）

## 应用

很多 NoSQL 数据库都使用了 LSM Tree，例如：

- HBase
- LevelDB
- RocksDB

> 为什么 MySQL 使用 B + 树，没有使用 LSM Tree？B + 树的数据更新直接在原数据处更改，但是 LSM 树的数据更新是日志式的。

# 核心思想

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-24-14-24-23.png)

## MemTable

存储在内存中，最近更新的数据，key 有序（HBase 使用跳跃表）。使用 WAL 技术，保证数据不丢失。

## Immutable MemTable

MemTable 达到一定大小后，会转换为 Immutable MemTable。Immutable MemTable 会被写入磁盘，成为一个 SSTable。

## SSTable(Sorted String Table)

有序键值对集合，是 LSM 数组在磁盘的数据结构。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-24-14-27-20.png)

# Compact 策略

> 待补充

# 参考链接

- 维基百科：[Log-structured merge-tree
](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
- [LSM Tree
](https://hujianxin.github.io/blog/posts/lsm/)
- [LSM 树详解
](https://zhuanlan.zhihu.com/p/181498475)