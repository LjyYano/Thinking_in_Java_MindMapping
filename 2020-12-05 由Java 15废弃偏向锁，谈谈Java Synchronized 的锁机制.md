![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-062310.jpg)

# Java 15 废弃偏向锁

JDK 15已经在2020年9月15日发布,详情见 [JDK 15 官方计划](https://openjdk.java.net/projects/jdk/15/)。其中有一项更新是`废弃偏向锁`，官方的详细说明在：[JEP 374: Disable and Deprecate Biased Locking](https://openjdk.java.net/jeps/374)。

具体的说明见：[JDK 15已发布，你所要知道的都在这里！](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-09-19%20JDK%2015%E5%B7%B2%E5%8F%91%E5%B8%83%EF%BC%8C%E4%BD%A0%E6%89%80%E8%A6%81%E7%9F%A5%E9%81%93%E7%9A%84%E9%83%BD%E5%9C%A8%E8%BF%99%E9%87%8C%EF%BC%81.md)

## 当时为什么要引入偏向锁？

偏向锁是 HotSpot 虚拟机使用的一项优化技术，能够减少无竞争锁定时的开销。偏向锁的目的是假定 monitor 一直由某个特定线程持有，直到另一个线程尝试获取它，这样就可以避免获取 monitor 时执行 cas 的原子操作。monitor 首次锁定时偏向该线程，这样就可以避免同一对象的后续同步操作步骤需要原子指令。从历史上看，偏向锁使得 JVM 的性能得到了显著改善。

## 现在为什么又要废弃偏向锁？

但是过去看到的性能提升，在现在看来已经不那么明显了。受益于偏向锁的应用程序，往往是使用了早期 Java 集合 API的程序（JDK 1.1），这些 API（Hasttable 和 Vector） 每次访问时都进行同步。JDK 1.2 引入了针对单线程场景的非同步集合（HashMap 和 ArrayList），JDK 1.5 针对多线程场景推出了性能更高的并发数据结构。这意味着如果代码更新为使用较新的类，由于不必要同步而受益于偏向锁的应用程序，可能会看到很大的性能提高。此外，围绕线程池队列和工作线程构建的应用程序，性能通常在禁用偏向锁的情况下变得更好。

偏向锁为同步系统引入了许多`复杂的代码`，并且对 HotSpot 的其他组件产生了影响。这种复杂性已经成为理解代码的障碍，也阻碍了对同步系统进行重构。因此，我们希望禁用、废弃并最终删除偏向锁。

## 思考

现在很多面试题都是讲述 CMS、G1 这些垃圾回收的原理，但是实际上官方在 Java 11 就已经推出了 ZGC，号称 GC 方向的未来。对于锁的原理，其实 Java 8 的知识也需要更新了，毕竟技术一直在迭代，还是要不断更新自己的知识……学无止境……

话说回来偏向锁产生的原因，很大程度上是 Java 一直在兼容以前的程序，即使到了 Java 15，以前的 Hasttable 和 Vector 这种老古董性能差的类库也不会删除。这样做的好处很明显，但是坏处也很明显，Java 要一直兼容这些代码，甚至影响 JVM 的实现。

本篇文章系统整理下 Java 的锁机制以及演进过程。

# 锁的发展过程

在 JDK 1.5 之前，Java 是依靠 `Synchronized` 关键字实现锁功能来做到这点的。Synchronized 是 JVM 实现的一种内置锁，锁的获取和释放是由 JVM 隐式实现。

到了 JDK 1.5 版本，并发包中新增了 `Lock` 接口来实现锁功能，它提供了与Synchronized 关键字类似的同步功能，只是在使用时需要显示获取和释放锁。

Lock 同步锁是`基于 Java 实现`的，而 Synchronized 是基于`底层操作系统`的 Mutex Lock 实现的，每次获取和释放锁操作都会带来`用户态和内核态的切换`，从而增加系统性能开销。因此，在锁竞争激烈的情况下，Synchronized同步锁在性能上就表现得非常糟糕，它也常被大家称为重量级锁。

特别是在单个线程重复申请锁的情况下，JDK1.5 版本的 Synchronized 锁性能要比 Lock 的性能差很多。

到了 JDK 1.6 版本之后，Java 对 Synchronized 同步锁做了充分的优化，甚至在某些场景下，它的性能已经超越了 Lock 同步锁。

# Synchronized

说明：部分参考自 https://juejin.cn/post/6844903918653145102

Synchronized 的基础使用就不列举了，它可以修饰方法，也可以修饰代码块。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-080835.jpg)

## 修饰方法

```java
public synchronized void syncMethod() {
    System.out.println("syncMethod");
}
```

反编译的结果如下图所示，可以看到 syncMethod 方法的 flag 包含 `ACC_SYNCHRONIZED` 标志位。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-094705.png)

## 修饰代码块

```java
public void syncCode() {
    synchronized (SynchronizedTest.class) {
        System.out.println("syncCode");
    }
}
```

反编译的结果如下图所示，可以看到 syncCode 方法中包含 `monitorenter` 和 `monitorexit` 两个 JVM 指令。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-094947.png)

# JVM 同步指令分析

## monitorenter

直接看官方的定义：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-095233.png)

主要的意思是说：

每个对象都与一个 monitor 相关联。当且仅当 monitor 对象有一个所有者时才会被锁定。执行 monitorenter 的线程试图获得与 objectref 关联的 monitor 的所有权，如下所示:
- 若与 objectref 相关联的 monitor 计数为 0，线程进入 monitor 并设置 monitor 计数为 1，这个线程成为这个 monitor 的拥有者。
- 如果该线程已经拥有与 objectref 关联的 monitor，则该线程重新进入 monitor，并增加 monitor 的计数。
- 如果另一个线程已经拥有与 objectref 关联的 monitor，则该线程将阻塞，直到 monitor 的计数为零，该线程才会再次尝试获得 monitor 的所有权。

## monitorexit

直接看官方的定义：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-105943.png)

主要的意思是说：

- 执行 monitorexit 的线程必须是与 objectref 引用的实例相关联的 monitor 的所有者。
- 线程将与 objectref 关联的 monitor 计数减一。如果计数为 0，则线程退出并释放这个 monitor。其他因为该 monitor 阻塞的线程可以尝试获取该 monitor。

## ACC_SYNCHRONIZED

[官方的定义](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-2.html#jvms-2.11.10)

JVM 对于方法级别的同步是隐式的，是方法调用和返回值的一部分。同步方法在运行时常量池的 method_info 结构中由 `ACC_SYNCHRONIZED` 标志来区分，它由方法调用指令来检查。当调用设置了 ACC_SYNCHRONIZED 标志位的方法时，调用线程会获取 monitor，调用方法本身，再退出 monitor。

# 操作系统的管程（Monitor）

管程是一种在信号量机制上进行改进的`并发编程模型`。

## 管程模型

管程的组成如下：

- `共享变量`
- `入口等待队列`
- `一个锁`：控制整个管程代码的互斥访问
- `0 个或多个条件变量`：每个条件变量都包含一个自己的等待队列，以及相应的出/入队操作

## ObjectMonitor

JVM 中的同步就是基于进入和退出管程（Monitor）对象实现的。每个对象实例都会有一个 Monitor，Monitor 可以和对象一起创建、销毁。Monitor 是由 ObjectMonitor 实现，而 ObjectMonitor 是由 C++ 的 ObjectMonitor.hpp 文件实现，如下所示：

```
ObjectMonitor() {
   _header = NULL;
   _count = 0; //记录个数
   _waiters = 0,
   _recursions = 0;
   _object = NULL;
   _owner = NULL;
   _WaitSet = NULL; //处于wait状态的线程，会被加入到_WaitSet
   _WaitSetLock = 0 ;
   _Responsible = NULL ;
   _succ = NULL ;
   _cxq = NULL ;
   FreeNext = NULL ;
   _EntryList = NULL ; //处于等待锁block状态的线程，会被加入到该列表
   _SpinFreq = 0 ;
   _SpinClock = 0 ;
   OwnerIsThread = 0 ;
}
```

本文使用的是 Java 11，其中有 sun.jvm.hotspot.runtime.ObjectMonitor 类，这个类有如下的初始化方法：

```java
private static synchronized void initialize(TypeDataBase db) throws WrongTypeException {
    heap = VM.getVM().getObjectHeap();
    Type type  = db.lookupType("ObjectMonitor");
    sun.jvm.hotspot.types.Field f = type.getField("_header");
    headerFieldOffset = f.getOffset();
    f = type.getField("_object");
    objectFieldOffset = f.getOffset();
    f = type.getField("_owner");
    ownerFieldOffset = f.getOffset();
    f = type.getField("FreeNext");
    FreeNextFieldOffset = f.getOffset();
    countField  = type.getJIntField("_count");
    waitersField = type.getJIntField("_waiters");
    recursionsField = type.getCIntegerField("_recursions");
}
```

可以和 C++ 的 ObjectMonitor.hpp 的结构对应上，如果查看 initialize 方法的调用链，能够发现很多 JVM 的内部原理，本篇文章限于篇幅和内容原因，不去详细叙述了。

## 工作原理

Java Monitor 的工作原理如图：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-06-084018.jpg)

当多个线程同时访问一段同步代码时，多个线程会先被存放在 `EntryList` 集合中，处于 block 状态的线程，都会被加入到该 列表。接下来当线程获取到对象的 Monitor时，Monitor 是依靠底层操作系统的 `Mutex Lock` 来实现互斥的，线程申请 Mutex 成功，则持有该 Mutex，其它线程将无法获取到该 Mutex。

如果线程调用 `wait()` 方法，就会释放当前持有的 Mutex，并且该线程会进入 `WaitSet` 集合中，等待下一次被唤醒。如果当前线程顺利执行完方法，也将释放 Mutex。



Monitor 依赖于底层操作系统的实现，存在`用户态`和`内核态`的转换，所以增加了性能开销。但是程序中使用了 Synchronized 关键字，程序也不全会使用 Monitor，因为 JVM 对 Synchronized 的实现也有 3 种：偏向锁、轻量级锁、重量级锁。

# 锁升级

为了提升性能，JDK 1.6 引入了`偏向锁`（就是这个已经被 JDK 15 废弃了）、`轻量级锁`、`重量级锁概念`，来减少锁竞争带来的上下文切换，而正是新增的 Java 对象头实现了锁升级功能。

## Java 对象头

那么 Java 对象头又是什么？在 JDK 1.6 中，对象实例分为：

- 对象头
  - Mark Word
  - 指向类的指针
  - 数组长度
- 实例数据
- 对齐填充

其中 Mark Word 记录了对象和锁有关的信息，在 64 位 JVM 中的长度是 64 位，具体信息如下图所示：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-06-085132.jpg)

## 偏向锁

为什么要有偏向锁呢？偏向锁主要用来优化`同一线程多次申请同一个锁`的竞争。可能大部分时间一个锁都是被一个线程持有和竞争。假如一个锁被线程 A 持有，后释放；接下来又被线程 A 持有、释放……如果使用 monitor，则每次都会发生用户态和内核态的切换，性能低下。

作用：当一个线程再次访问这个同步代码或方法时，该线程只需去对象头的 Mark Word 判断是否有偏向锁指向它的 ID，无需再进入 Monitor 去竞争对象了。当对象被当做同步锁并有一个线程抢到了锁时，锁标志位还是 01，“是否偏向锁”标志位设置为 1，并且记录抢到锁的线程 ID，表示进入偏向锁状态。

一旦出现其它线程竞争锁资源，偏向锁就会被撤销。撤销时机是在`全局安全点`，暂停持有该锁的线程，同时坚持该线程是否还在执行该方法。是则升级锁；不是则被其它线程抢占。

在`高并发`场景下，大量线程同时竞争同一个锁资源，偏向锁会被撤销，发生 `stop the world`后，开启偏向锁会带来更大的性能开销（这就是 Java 15 取消和禁用偏向锁的原因），可以通过添加 JVM 参数关闭偏向锁：

```
-XX:-UseBiasedLocking //关闭偏向锁（默认打开）
```

或

```
-XX:+UseHeavyMonitors  //设置重量级锁
```

## 轻量级锁

如果另一线程竞争锁，由于这个锁已经是偏向锁，则判断对象头的 Mark Word 的线程 ID 不是自己的线程 ID，就会进行 CAS 操作获取锁：
- 成功，直接替换 Mark Word 中的线程 ID 为当前线程 ID，该锁会保持偏向锁。
- 失败，标识锁有竞争，偏向锁会升级为轻量级锁。

轻量级锁的适用范围：`线程交替执行同步块，大部分锁在整个同步周期内部存在场馆时间的竞争`。

## 自旋锁与重量级锁

轻量级锁的 CAS 抢锁失败，线程会挂起阻塞。若正在持有锁的线程在很短的时间内释放锁，那么刚刚进入阻塞状态的线程又要重新申请锁资源。

如果线程持有锁的时间不长，则未获取到锁的线程可以不断尝试获取锁，避免线程被挂起阻塞。JDK 1.7 开始，自旋锁默认开启，自旋次数又 JVM 配置决定。

自旋锁重试之后如果抢锁依然失败，同步锁就会升级至重量级锁，锁标志位改为 10。在这个状态下，未抢到锁的线程都会进入 Monitor，之后会被阻塞在 `_WaitSet` 队列中。

在高负载、高并发的场景下，可以通过设置 JVM 参数来关闭自旋锁，优化性能：

```
-XX:-UseSpinning //参数关闭自旋锁优化(默认打开) 
-XX:PreBlockSpin //参数修改默认的自旋次数。JDK1.7后，去掉此参数，由jvm控制
```

# 再深入分析

锁究竟锁的是什么呢？又是谁锁的呢？

当多个线程都要执行某个同步方法时，只有一个线程可以获取到锁，然后其余线程都在阻塞等待。所谓的“锁”动作，就是让其余的线程阻塞等待；那 Monitor 是何时生成的呢？我个人觉得应该是在多个线程同时请求的时候，生成重量级锁，一个对象才会跟一个 Monitor 相关联。

那其余的被阻塞的线程是在哪里记录的呢？就是在这个 Monitor 对象中，而这个 Monitor 对象就在对象头中。（如果不对，欢迎大家留言讨论~）

# 锁优化

Synchronized 只在 JDK 1.6 以前性能才很差，因为这之前的 JVM 实现都是重量级锁，直接调用 ObjectMonitor 的 enter 和 exit。从 JDK 1.6 开始，HotSpot 虚拟机就增加了上述所说的几种优化：

- 偏向锁
- 轻量级锁
- 自旋锁

其余还有：

- 适应性自旋
- 锁消除
- 锁粗化

## 锁消除

这属于`编译器`对锁的优化，JIT 编译器在动态编译同步块时，会使用`逃逸分析`技术，判断同步块的锁对象是否只能被一个对象访问，没有发布到其它线程。

如果确认没有“逃逸”，JIT 编译器就不会生成 Synchronized 对应的锁申请和释放的机器码，就消除了锁的使用。

## 锁粗化

JIT 编译器动态编译时，如果发现几个相邻的同步块使用的是同一个锁实例，那么 JIT 编译器将会把这`几个同步块合并为一个大的同步块`，从而避免一个线程“反复申请、释放同一个锁“所带来的性能开销。

## 减小锁粒度

我们在代码实现时，尽量减少锁粒度，也能够优化锁竞争。

# 总结

- 其实现在 Synchronized 的性能并不差，偏向锁、轻量级锁并不会从用户态到内核态的切换；只有在竞争十分激烈的时候，才会升级到重量级锁。
- Synchronized 的锁是由 JVM 实现的。
- 偏向锁已经被废弃了。

# 参考

1. https://juejin.cn/post/6844903918653145102#heading-13
2. 极客时间：多线程之锁优化（上）：深入了解Synchronized同步锁的优化方法