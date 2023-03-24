---
date: 2021-12-07
---


- [传统的垃圾回收](#传统的垃圾回收)
  - [CMS 与 G1 停顿时间瓶颈](#cms-与-g1-停顿时间瓶颈)
- [ZGC 概览](#zgc-概览)
- [深入 ZGC 原理](#深入-zgc-原理)
  - [标记 Marking](#标记-marking)
  - [着色指针 Reference Coloring](#着色指针-reference-coloring)
  - [Relocation](#relocation)
  - [重映射和读屏障 Remapping and Load Barriers](#重映射和读屏障-remapping-and-load-barriers)
  - [ZGC 并发处理演示](#zgc-并发处理演示)
- [支持平台](#支持平台)
- [ZGC 性能对比](#zgc-性能对比)
  - [吞吐量对比](#吞吐量对比)
  - [停顿时间对比](#停顿时间对比)
- [快速开始](#快速开始)
- [变更记录](#变更记录)
  - [JDK 17](#jdk-17)
  - [JDK 16](#jdk-16)
  - [JDK 15](#jdk-15)
  - [JDK 14](#jdk-14)
  - [JDK 13](#jdk-13)
  - [JDK 12](#jdk-12)
  - [JDK 11](#jdk-11)
- [FAQ](#faq)
  - [ZGC 中的“Z”表示什么？](#zgc-中的z表示什么)
  - [发音是 "zed gee see" 还是 "zee gee see"?](#发音是-zed-gee-see-还是-zee-gee-see)
- [带着问题思考](#带着问题思考)
  - [为什么说 ZGC 的停顿时间不会随着堆的大小而变化？](#为什么说-zgc-的停顿时间不会随着堆的大小而变化)
  - [对象的存活状态，记录在哪里？与 CMS 和 G1 有什么不同？](#对象的存活状态记录在哪里与-cms-和-g1-有什么不同)
  - [为什么 ZGC 的停顿时间会这么短？](#为什么-zgc-的停顿时间会这么短)
  - [会出现多个指针指向老对象，remap 时一个指针修改新地址里的数据，其他指针仍读取老数据的情况？](#会出现多个指针指向老对象remap-时一个指针修改新地址里的数据其他指针仍读取老数据的情况)
- [GitHub 项目](#github-项目)
- [参考资料](#参考资料)
- [官方 PPT](#官方-ppt)

# 传统的垃圾回收

我们在开发 Java 程序时，并不需要显示释放内存，Java 的垃圾回收器会自动帮我们回收。GC 会自动监测对象引用，并释放不可达的对象。GC 需要监测堆内存中对象的状态，如果一个对象不可达，GC 就可以考虑回收这个对象。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211160320.png)

## CMS 与 G1 停顿时间瓶颈

在介绍 ZGC 之前，首先回顾一下 CMS 和 G1 的 GC 过程以及停顿时间的瓶颈。CMS 新生代的 Young GC、G1 和 ZGC 都基于标记-复制算法，但算法具体实现的不同就导致了巨大的性能差异。

标记-复制算法应用在 CMS 新生代（ParNew 是 CMS 默认的新生代垃圾回收器）和 G1 垃圾回收器中。标记-复制算法可以分为三个阶段：

- 标记阶段，即从 GC Roots 集合开始，标记活跃对象；
- 转移阶段，即把活跃对象复制到新的内存地址上；
- 重定位阶段，因为转移导致对象的地址发生了变化，在重定位阶段，所有指向对象旧地址的指针都要调整到对象新的地址上。

CMS 在 JDK11 已经被 G1 所取代，G1 GC 的详细算法可以参考文章：[JVM G1GC 的算法与实现](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-03-16%20JVM%20G1GC%E7%9A%84%E7%AE%97%E6%B3%95%E4%B8%8E%E5%AE%9E%E7%8E%B0.md)。

# ZGC 概览

**The Z Garbage Collector**, also known as **ZGC**, is a scalable low latency garbage collector designed to meet the following goals:

- **Sub-millisecond** max pause times
- Pause times **do not** increase with the heap, live-set or root-set size
- Handle heaps ranging from a **8MB** to **16TB** in size

总结下来就是：

- 停顿时间不超过 10ms；
- 停顿时间不会随着堆的大小，或者活跃对象的大小而增加；
- 支持 8MB~4TB 级别的堆，未来支持 16TB。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211172428.png?x-oss-process=style/yano)

ZGC was initially introduced as an experimental feature in JDK 11, and was declared **Production Ready** in JDK 15.

ZGC 的主要特点：

- Concurrent
- Region-based
- Compacting
- NUMA-aware
- Using colored pointers
- Using load barriers

At its core, ZGC is a **concurrent** garbage collector, meaning all heavy lifting work is done while **Java threads continue to execute**. This greatly limits the impact garbage collection will have on your application's response time.

This [OpenJDK](http://openjdk.java.net/) project is sponsored by the [HotSpot Group](http://openjdk.java.net/groups/hotspot/).

ZGC 有一个“marking”的阶段，可以找到可达对象。GC 可以使用多种方法来存储对象的状态信息：比如创建一个 Map，key 是内存地址，value 是该地址上对象的状态信息。这种方法虽然简单，但是需要使用额外的内存来存储这些状态；同时维护这样的 Map 也是一个挑战。

ZGC 使用了一种完全不同的叫 **着色指针（reference coloring）** 方法：使用对象引用中的特定比特位来存储对象的状态。但是这种方法也有一个挑战，使用引用位来存储对象的元信息意味着多个引用可以指向同一个对象，因为对象位并不保存有关对象位置的任何信息。我们可以使用多重映射来解决此问题。

我们还希望解决内存碎片的问题。ZGC 使用 **relocation** 来解决这个问题。但是对于一个很大的堆来说，relocation 过程会非常慢。因为 ZGC 并不希望有很长的延时，ZGC 会将大多数的 relocation 过程与应用程序并行执行。但是这又引入了另一个问题。

比方说我们有了一个对象的引用，ZGC relocation 了这个对象，紧接着发生了线程的上下文切换，用户线程正在试图获取这个对象的旧内存地址。ZGC 使用 **读屏障（load barriers）** 来解决这个问题。load barrier 是线程从堆中获取一个对象引用时加入的一小段代码——比如我们需要访问一个对象的非原始类型的字段。

在 ZGC 中，load barrier 会检查引用元信息中的特定位，根据这些位的信息，ZGC 可能会在我们得到引用之前做一些处理，可能产生一个完全不同的引用，我们称这个过程为“重映射 remapping”。

# 深入 ZGC 原理

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211173008.png?x-oss-process=style/yano)

## 标记 Marking

ZGC 将标记分为 3 个阶段：

- stop-the-world 阶段。在这个阶段，我们寻找并标记根引用（root references）。根引用是堆中可达对象的起点，可以是局部变量或静态字段。这个阶段通常时间非常短，因为根引用的数量一般都非常小；
- concurrent 阶段。在这个阶段，我们从根引用开始遍历对象图，并标记每个到达的对象；
- stop-the-world 阶段。处理一些如弱引用的边缘情况。

此时我们就知道哪些对象是可达的。ZGC 使用 marked0 和 marked1 元数据位进行标记。

## 着色指针 Reference Coloring

一个引用就代表虚拟内存中一个字节的位置。我们并不需要使用引用的所有位来标识位置。在 32 位系统中，我们只能寻址 4GB 内存。由于现代计算机基本都有比这更多的内存，我们显然不能占用着 32 位中的任意一位。因此 ZGC 需要使用 64 位引用，这也就意味着 ZGC 仅适用于 64 位平台。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211172137.png)

ZGC 引用使用 42 位来表示地址，引用可以寻址 4TB 的内存空间。最重要的是，我们有 4 位来存储引用的状态：

- finalizable 位：该对象只能通过终结器（finalizer）访问
- remap 位：引用是最新的，并指向对象的当前位置
- marked0 和 marked11 位：标记可达对象

我们称这些位为元数据位，ZGC 中这些位有且仅有一个位是 1。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211215212142.png)

其中，[0~4TB) 对应 Java 堆，[4TB ~ 8TB) 称为 M0 地址空间，[8TB ~ 12TB) 称为 M1 地址空间，[12TB ~ 16TB) 预留未使用，[16TB ~ 20TB) 称为 Remapped 空间。

当应用程序创建对象时，首先在堆空间申请一个虚拟地址，但该虚拟地址并不会映射到真正的物理地址。ZGC 同时会为该对象在 M0、M1 和 Remapped 地址空间分别申请一个虚拟地址，且这三个虚拟地址对应同一个物理地址，但这三个空间在同一时间有且只有一个空间有效。ZGC 之所以设置三个虚拟地址空间，是因为它使用“空间换时间”思想，去降低 GC 停顿时间。“空间换时间”中的空间是虚拟空间，而不是真正的物理空间。后续章节将详细介绍这三个空间的切换过程。

## Relocation

在 ZGC 中，Relocation 包括以下几个阶段：

- 并发阶段。查找需要重新定位的块，将它们加入 Relocation 候选集合。
- stop-the-world 阶段。重定位重定位集中的所有根引用并更新它们的引用。
- 并发节点。将重定位集中的所有剩余对象重定位，并将旧地址和新地址之间的映射存储在转发表中。
- 剩余引用的重写发生在下一个标记阶段。我们不需要两次遍历对象树。

## 重映射和读屏障 Remapping and Load Barriers

读屏障是 JVM 向应用代码插入一小段代码的技术。当应用线程从堆中读取对象引用时，就会执行这段代码。需要注意的是，仅“从堆中读取对象引用”才会触发这段代码。

读屏障示例：

```java
Object o = obj.FieldA   // 从堆中读取引用，需要加入屏障
<Load barrier>
Object p = o  // 无需加入屏障，因为不是从堆中读取引用
o.dosomething() // 无需加入屏障，因为不是从堆中读取引用
int i =  obj.FieldB  //无需加入屏障，因为不是对象引用
```

ZGC 中读屏障的代码作用：在对象标记和转移过程中，用于确定对象的引用地址是否满足条件，并作出相应动作。

## ZGC 并发处理演示

接下来详细介绍 ZGC 一次垃圾回收周期中地址视图的切换过程：

- **初始化**：ZGC 初始化之后，整个内存空间的地址视图被设置为 Remapped。程序正常运行，在内存中分配对象，满足一定条件后垃圾回收启动，此时进入标记阶段。
- **并发标记阶段**：第一次进入标记阶段时视图为 M0，如果对象被 GC 标记线程或者应用线程访问过，那么就将对象的地址视图从 Remapped 调整为 M0。所以，在标记阶段结束之后，对象的地址要么是 M0 视图，要么是 Remapped。如果对象的地址是 M0 视图，那么说明对象是活跃的；如果对象的地址是 Remapped 视图，说明对象是不活跃的。
- **并发转移阶段**：标记结束后就进入转移阶段，此时地址视图再次被设置为 Remapped。如果对象被 GC 转移线程或者应用线程访问过，那么就将对象的地址视图从 M0 调整为 Remapped。

其实，在标记阶段存在两个地址视图 M0 和 M1，上面的过程显示只用了一个地址视图。之所以设计成两个，是为了区别前一次标记和当前标记。也即，第二次进入并发标记阶段后，地址视图调整为 M1，而非 M0。

着色指针和读屏障技术不仅应用在并发转移阶段，还应用在并发标记阶段：将对象设置为已标记，传统的垃圾回收器需要进行一次内存访问，并将对象存活信息放在对象头中；而在 ZGC 中，只需要设置指针地址的第 42~45 位即可，并且因为是寄存器访问，所以速度比访问内存更快。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211172102.png)

# 支持平台

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211207193738.png)

# ZGC 性能对比

## 吞吐量对比

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211172619.png?x-oss-process=style/yano)

## 停顿时间对比

嗯，对比还是很明显的……

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211211172634.png?x-oss-process=style/yano)

# 快速开始

通过下面的参数，能够启用 ZGC。

```
-XX:+UseZGC -Xmx<size> -Xlog:gc
```

如果想获取更多详细 log，可以使用下面的参数：

```
-XX:+UseZGC -Xmx<size> -Xlog:gc*
```

# 变更记录

##  JDK 17

- Dynamic Number of GC threads
- Reduced mark stack memory usage
- macOS/aarch64 support
- GarbageCollectorMXBeans for both pauses and cycles
- Fast JVM termination

##  JDK 16

- Concurrent Thread Stack Scanning ([JEP 376](http://openjdk.java.net/jeps/376))
- Support for in-place relocation
- Performance improvements (allocation/initialization of forwarding tables, etc)

##  JDK 15

- Production ready ([JEP 377](http://openjdk.java.net/jeps/377))
- Improved NUMA awareness
- Improved allocation concurrency
- Support for Class Data Sharing (CDS)
- Support for placing the heap on NVRAM
- Support for compressed class pointers
- Support for incremental uncommit
- Fixed support for transparent huge pages
- Additional JFR events

##  JDK 14

- macOS support ([JEP 364](http://openjdk.java.net/jeps/364))
- Windows support ([JEP 365](http://openjdk.java.net/jeps/365))
- Support for tiny/small heaps (down to 8M)
- Support for JFR leak profiler
- Support for limited and discontiguous address space
- Parallel pre-touch (when using -XX:+AlwaysPreTouch)
- Performance improvements (clone intrinsic, etc)
- Stability improvements

##  JDK 13

- Increased max heap size from 4TB to 16TB
- Support for uncommitting unused memory ([JEP 351](http://openjdk.java.net/jeps/351))
- Support for -XX:SoftMaxHeapSIze
- Support for the Linux/AArch64 platform
- Reduced Time-To-Safepoint

##  JDK 12

- Support for concurrent class unloading
- Further pause time reductions

## JDK 11

- Initial version of ZGC
- Does not support class unloading (using -XX:+ClassUnloading has no effect)

# FAQ

##  ZGC 中的“Z”表示什么？

ZGC 只是一个名字，Z 没有什么特殊含义。

##  发音是 "zed gee see" 还是 "zee gee see"?

没有规定，两者都可以。

# 带着问题思考

## 为什么说 ZGC 的停顿时间不会随着堆的大小而变化？

ZGC 几乎所有的阶段都是并发（应用线程与 GC 线程同时运行）。之所以说 ZGC 的停顿时间不会随着堆的大小而变化，是因为开始的 Pause Mark Start 阶段，要做根集合（root set）扫描，包括全局变量、线程栈里面的对象指针，但不包括 GC 堆里的对象指针（只会根据线程的多少、线程栈大小变化）。因为全局变量、线程栈里的对象指针是可控的，不会随着堆的大小变化。

## 对象的存活状态，记录在哪里？与 CMS 和 G1 有什么不同？

- CMS：记录在对象头里
- G1：记录在独立的数据结构里
- ZGC：记录在指针上

## 为什么 ZGC 的停顿时间会这么短？

R 大的总结：

与标记对象的传统算法相比，ZGC 在指针上做标记，在访问指针时加入 Load Barrier（读屏障），比如当对象正被 GC 移动，指针上的颜色就会不对，这个屏障就会先把指针更新为有效地址再返回，也就是，永远只有单个对象读取时有概率被减速，而不存在为了保持应用与 GC 一致而粗暴整体的 Stop The World。

## 会出现多个指针指向老对象，remap 时一个指针修改新地址里的数据，其他指针仍读取老数据的情况？

不会，就是因为「读屏障」。在读每个指针时，都执行一段额外的逻辑，这段逻辑就是 remap——根据 Relocaton Set 找到新的地址，将老地址改为新地址。

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 参考资料

- [https://www.baeldung.com/jvm-zgc-garbage-collector](https://www.baeldung.com/jvm-zgc-garbage-collector)
- [https://wiki.openjdk.java.net/display/zgc/Main#Main-JDK17](https://wiki.openjdk.java.net/display/zgc/Main#Main-JDK17)
- [新一代垃圾回收器 ZGC 的探索与实践](https://tech.meituan.com/2020/08/06/new-zgc-practice-in-meituan.html)
- [ZGC-FOSDEM-2018.pdf](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/ZGC-FOSDEM-2018.pdf)
- [JVM G1GC 的算法与实现](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-03-16%20JVM%20G1GC%E7%9A%84%E7%AE%97%E6%B3%95%E4%B8%8E%E5%AE%9E%E7%8E%B0.md)
- [Java 程序员的荣光，听 R 大论 JDK11 的 ZGC](https://juejin.cn/post/6844903666902630414)

# 官方 PPT

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211215214124.png)