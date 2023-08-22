---
date: 2022-02-10
---


- [RDB 是什么](#rdb-是什么)
- [RDB 文件格式](#rdb-文件格式)
  - [Header](#header)
  - [Body](#body)
    - [DB Selector](#db-selector)
    - [AUX Fields](#aux-fields)
    - [Key-Value](#key-value)
  - [Footer](#footer)
- [编码算法说明](#编码算法说明)
  - [Length 编码](#length-编码)
  - [String 编码](#string-编码)
  - [Score 编码](#score-编码)
  - [Value 编码](#value-编码)
    - [List](#list)
    - [Set](#set)
    - [Sorted Set](#sorted-set)
    - [Hash](#hash)
    - [Zipmap](#zipmap)
    - [Ziplist](#ziplist)
    - [Intset](#intset)
      - [Sorted Set in Ziplist Encoding](#sorted-set-in-ziplist-encoding)
      - [Hashmap in Ziplist Encoding](#hashmap-in-ziplist-encoding)
- [实际例子](#实际例子)
  - [安装、启动 Redis](#安装启动-redis)
  - [保存字符串](#保存字符串)
  - [保存 RDB 文件](#保存-rdb-文件)
  - [分析 RDB 文件](#分析-rdb-文件)
- [参考链接](#参考链接)
- [Redis 源码简洁剖析系列](#redis-源码简洁剖析系列)
- [我的公众号](#我的公众号)

# RDB 是什么

Redis `*.rdb` 是内存的`二进制文件`，通过 *.rdb 能够完全回复 Redis 的运行状态。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/
20220218175013.png?x-oss-process=style/yano)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220218174914.png)

# RDB 文件格式

详细信息可参考：[Redis RDB Dump File Format](https://github.com/sripathikrishnan/redis-rdb-tools/wiki/Redis-RDB-Dump-File-Format)。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220218174944.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220214194237.png?x-oss-process=style/yano)

## Header

RDB 文件的头部占用 9bytes，前 5bytes 为 `Magic String`, 后 4bytes 为`版本号`；

```c
52 45 44 49 53 #"REDIS", 就像 java 的 class 文件以 0xCAFEBABE 开头一样
30 30 30 36    #RDB 版本号，30 表示‘0’，版本号为 0006＝6
```

注意：版本号是字符串而不是整型：

```c
snprintf(magic,sizeof(magic),"REDIS%04d",RDB_VERSION);
```

RDB_VERSION 详细信息可参考：[Redis RDB Version History
](https://github.com/sripathikrishnan/redis-rdb-tools/blob/master/docs/RDB_Version_History.textile)

## Body

### DB Selector

FE 开头表示后跟表示 `DB Selector`，例如：

```bash
FE 00   #FE 表明数据库的哪个 db，此处为 db0
```

注意：DB Selector 长度不固定，具体的编码方式请参见后文的 Length 编码。

### AUX Fields

FA 开头表示后跟 AUX Fields, 记录生成 Dump 文件的 `Redis 相关信息`，例如 redis-ver、redis-bits、used-mem、aof-preamble 和 repl-id 等。这些信息采用 String 编码；

注意：redis3.0 版本的 RDB 版本号为 6，redis3.2 的版本号为 7；

### Key-Value

key-value 有三种格式：

1. expire 为 second
    
    ```bash
    FD $unsigned int    #失效时间（秒），4 个字节
    $value-type         #1 个字节，表明数据类型：set,map 等
    $string-encoded-key #key 值，字符串类型
    $encoded-value      #value, 编码方式和类型有关
    ```
    
2. expire 为 millisecond
    
    ```bash
    FC $unsigned long    #失效时间（毫秒），8 个字节
    $value-type          #数据类型，1 个字节
    $string-encoded-key  #key，字符串类型
    $encoded-value       #value, 编码方式和类型有关
    ```
    
3. 无 expire
    
    ```bash
    $value-type         #数据类型，1 个字节
    $string-encoded-key #key，字符串类型
    $encoded-value      #value, 编码方式和类型有关
    ```
    

## Footer

```bash
FF              #RDB 文件的结束
8byte checksum #循环冗余校验码，Redis 采用 crc-64-jones 算法，初始值为 0
```

# 编码算法说明

## Length 编码

> 长度采用 BigEndian 格式存储，为无符号整数

1. 如果以"00"开头，那么接下来的 6 个 bit 表示长度；
2. 如果以“01”开头，那么接下来的 14 个 bit 表示长度；
3. 如果以"10"开头，该 byte 的剩余 6bit 废弃，接着读入 4 个 bytes 表示长度 (BigEndian)；
4. 如果以"11"开头，那么接下来的 6 个 bit 表示特殊的编码格式，一般用来存储数字：

- 0 表示用接下来的 1byte 表示长度
- 1 表示用接下来的 2bytes 表示长度；
- 2 表示用接下来的 4bytes 表示长度；

## String 编码

该编码方式首先采用 Length 编码 进行解析：

1. 从上面的`Length 编码`知道，如果以"00","01","10"开头，首先读取长度；然后从接下来的内容中读取指定长度的字符；
2. 如果以"11"开头，而且接下来的 6 个字节为“0”、“1”和“2”, 那么直接读取接下来的 1，2，4bytes 做为字符串的内容（实际上存储的是数字，只不过按照字符串的格式存储）；
3. 如果以“11”开头，而且接下来的 6 个字节为"3", 表明采用 LZF 压缩字符串格式：

LZF 编码的解析步骤为：

1. 首先采用`Length 编码`读取压缩后字符串的长度 `clen`;
2. 接着采用`Length 编码`读取压缩前的字符串长度；
3. 读取 clen 长度的字节，并采用 lzf 算法解压得到原始的字符串

## Score 编码

1. 读取 1 个字节，如果为 255，则返回负无穷；
2. 如果为 254，返回正无穷；
3. 如果为 253，返回非数字；
4. 否则，将该字节的值做为长度，读取该长度的字节，将结果做为分值；

## Value 编码

Redis 中的 value 编码包括如下类型：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220214195122.png)

其中 String 编码在前面已经介绍过，接下来逐一介绍其他的 9 种编码方式；

### List

1. 首先用 Length 编码读取 List 的长度 lsize；
2. 采用 String 编码读取 lsize 个字符串

### Set

同 List

### Sorted Set

1. 首先用 Length 编码读取 Sorted Set 的长度 zsize；
2. 采用 String 编码读取字符串，采用 Score 编码读取分值；
3. 循环读取 zsize 次；

### Hash

1. 采用 Length 编码读取 Hash 的大小 hsize；
2. 采用 String 编码读取 2\*hsize 的字符串，按照 key,value 的方式组装成 Map

### Zipmap

用于存储 hashmap,Redis2.6 之后，该编码被废弃，转而采用 Ziplist 编码；

采用 String 编码读取整个 zipmap 字符串，hashmap 字符串的格式为：

```go
<zmlen><len>"foo"<len><free>"bar"<len>"hello"<len><free>"world"<zmend>
```

1. zmlen: 一个字节，Zipmap 的大小；如果>=254, 意味着 zipmap 的大小无法直接获取到，必须要遍历整个 zipmap 才能得到大小；
2. len: 字符串长度，1 或 5 个字节长度；如果第一个字节在 0~252 之间，那么长度为第一个字节；如果为 253, 那么接下来的 4 个字节表示长度；254 和 255 是无效值；
3. free:1 字节，表明 value 空闲的字节数；
4. zmend:0xff, 表示 Zipmap 的结尾；

### Ziplist

采用 String 编码读取整个 ziplist 字符串，字符串的格式为：

```xml
<zlbytes><zltail><zllen><entry><entry><zlend>
```

1. zlbytes:4 字节无符号整数，表示 ziplist 占用的总字节数；
2. zltail:4 字节无符号整数 (little endian), 表示尾元素的偏移量；
3. zllen:2 字节无符号整数 (little endian), 表示 ziplist 中的元素个数，当元素个数大于 65535 时，无法用 2 字节表示，需要遍历列表获取元素个数；
4. entry:ziplist 中的元素；
5. zlend: 常量 (0xff), 表示 ziplist 的结尾；

entry 的格式：

```xml
<length-prev-entry><encoding><content>
```

1. lenth-prev-entry: 如果第一个字节<254, 则用 1bytes 表示长度；否则则用接下来的 4bytes（无符号整数）表示长度；
2. encoding

- "00"开头：字符串，用接下来的 6bit 表示长度；
- "01"开头：字符串，用接下来的 14bit 表示长度；
- "10"开头：字符串，忽略本字节的 6bit, 用接下来的 32bit 表示长度；
- "11000000"开头：整数，内容为接下来的 16bit；
- "11010000"开头：整数，内容为接下来的 32bit；
- "11100000"开头：整数，内容为接下来的 64bit；
- "11110000"开头：整数，内容为接下来的 24bit；
- "11111110"开头：整数，内容为接下来的 8bit；
- "1111"开头 ：整数，内容为接下来的 4bit 的值减去 1；

3. content  
    entry 内容，它的长度通过前面的 encoding 确定；

注意：元素长度、内容长度等都是采用 Little Endian 编码；

### Intset

Intset 是一个整数组成的二叉树；当 set 的所有元素都是整形的时候，Redis 会采用该编码进行存储；Inset 最大可以支持 64bit 的整数，做为优化，如果整数可以用更少的字节数表示，Redis 可能会用 16~32bit 来表示；注意的是当插入一个长度不一样的整数时，有可能会引起整个存储结构的变化；

由于 Intset 是一个二叉树，因此它的元素都是排序过的；  
采用 String 编码读取整个 intset 字符串，字符串的格式为：

```xml
<encoding><length-of-contents><contents>
```

1. encoding:32bit 的无符号整数；可选值包括 2、4 和 8；表示 inset 中的每个整数占用的字节数；
2. length-of-contents:32bit 无符号整数，表示 Intset 中包含的整数个数；
3. contents: 整数数组，长度由 length-of-contents 决定；

#### Sorted Set in Ziplist Encoding

采用 Ziplist 编码，区别在于用两个 entry 分别表示元素和分值；

#### Hashmap in Ziplist Encoding

采用 Ziplist 编码，区别在于用两个 entry 分别表示 key 和 value;

# 实际例子

本篇文章在本地安装并启动 Redis 服务，保存一个 string 类型的字符串，save 之后查看保存的 rdb 文件的二进制。

## 安装、启动 Redis

下载见：[Redis Download](https://redis.io/download)

启动 Redis server：

```c
src/redis-server&
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220215104928.png?x-oss-process=style/yano)

启动一个 Redis client：

```c
src/redis-cli
```

## 保存字符串

```c
127.0.0.1:6379> set name yano
OK
```

## 保存 RDB 文件

```c
127.0.0.1:6379> save
80277:M 15 Feb 2022 10:51:07.308 * DB saved on disk
OK
```

在刚执行 redis-cli 的目录下，就生成了 rdb 文件，文件名是 dump.rdb。

## 分析 RDB 文件

使用 `hexedit` 命令分析 `dump.rdb` 文件：

```c
hexedit dump.rdb
```

dump.rdb 文件内容如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220214200607.png?x-oss-process=style/yano)

本篇文章只是分析 rdb 文件的基本结构和格式，只保存了一个最基础的 string。（图画了一个小时😁）RDB 这块的 Redis 源码就不分析了，基本上都是按照这个结构来的。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220214112526.png?x-oss-process=style/yano)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220214194952.png?x-oss-process=style/yano)

# 参考链接

- [18 | 如何生成和解读 RDB 文件？](https://time.geekbang.org/column/article/415563)
- [Redis RDB Dump File Format](https://github.com/sripathikrishnan/redis-rdb-tools/wiki/Redis-RDB-Dump-File-Format)
- [Redis RDB 格式](https://www.jianshu.com/p/b1b34f77a3ac)

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