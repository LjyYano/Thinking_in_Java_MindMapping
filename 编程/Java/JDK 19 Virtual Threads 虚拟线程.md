---
date: 2022-11-01
---


- [前言](#前言)
- [Project Loom](#project-loom)
  - [Loom 是什么？](#loom-是什么)
  - [为什么要引入 Loom？](#为什么要引入-loom)
- [Virtual threads](#virtual-threads)
  - [Platform thread 是什么？](#platform-thread-是什么)
  - [Virtual thread 是什么？](#virtual-thread-是什么)
  - [Virtual thread 的好处？](#virtual-thread-的好处)
  - [使用 virtual thread](#使用-virtual-thread)
    - [使用 Thread.Builder 创建 virtual thread](#使用-threadbuilder-创建-virtual-thread)
    - [使用 Executors.newVirtualThreadPerTaskExecutor() 创建 virtual thread](#使用-executorsnewvirtualthreadpertaskexecutor-创建-virtual-thread)
    - [调度 virtual thread](#调度-virtual-thread)
- [补充说明](#补充说明)
  - [JDK 19 使用说明](#jdk-19-使用说明)
  - [JVM 源码分析](#jvm-源码分析)
- [参考链接](#参考链接)
- [GitHub 项目](#github-项目)
- [我的公众号](#我的公众号)

# 前言

JDK 19 支持了`virtual thread`（虚拟线程）：[JEP 425: Virtual Threads (Preview)](https://openjdk.org/jeps/425)，虚拟线程是 [Loom](https://cr.openjdk.java.net/~rpressler/loom/Loom-Proposal.html) 项目中的一个重要特性。

# Project Loom

## Loom 是什么？

`Loom` 项目的目标是提升 Java 的并发性能。Java 自诞生就提供了线程，它是一种很方便的并发结构（先不谈线程间的通信问题 0_o），但是这种线程是使用操作系统内核线程实现的，并不能满足当前的开发需求，浪费云计算中的宝贵资源。Loom 项目引入 `fiber` 作为轻量级、高效的线程，fiber 由 JVM 管理，开发者可以使用和之前线程相同的操作，且 fiber 具有更好的性能、占用的内存也更少。

## 为什么要引入 Loom？

在二十多年前 Java 首次发布时，Java 最重要的特性之一就是能方便地访问线程，提供同步原语。Java 线程为编写并发程序提供了相对简单的抽象。但是在现在使用 Java 编写并发程序的一个问题是：并发的规模。我们希望并发服务的并发量越大越好，一个服务器能处理上万个套接字。但是由于之前的 Java 线程是使用操作系统线程实现的，在单台服务器上创建几千个套接字都很勉强了……

开发者就必须做出选择：要么直接将一个并发单元建模成线程，要么在比线程更细力度的级别上实现并发，但是需要自己编写异步代码。

Java 生态引入了异步 API，包括 JDK 的异步 NIO、异步 servlet 和异步第三方库。这些新的 API 在使用中并不优雅，而且也不容易理解，出现的原因主要是 Java 的并发单元（线程）实现得不够。仅仅是因为 Java 线程的运行时性能不够，就需要放弃线程，使用各种第三方的实现。

Java 线程使用内核线程实现固然有一些优点，比如所有的 native code 都是由内核线程支持的，所以线程中的 Java 代码能够调用 native API。但是上面提到的缺点太大了，导致难以编写高性能的代码。Erlang 和 Go 等语言都提供了轻量级线程，轻量级线程越来越流行。

Loom 项目的主要目标是添加一个通过 Java 运行时管理的叫 fiber 的轻量级线程结构，fiber 可以跟现有的中建立、操作系统的线程实现一起使用。fiber 的内存占用非常小，比内核线程轻得多，fiber 之间的任务切换开销趋近于 0。在单个 JVM 实例上就可以生成数百万个 fiber，开发者可以直接写同步阻塞的调用。同时开发者并不需要为了性能/简单性的权衡同时提供同步和异步 API。

线程并不是一个原子结构，包括 `scheduler` 和 `continuation` 2 个模块。Java fiber 构建在这 2 个模块之上。

# Virtual threads

虚拟线程（virtual thread）就是轻量级线程，可以减少编写高吞吐高并发的应用程序的工作量。

## Platform thread 是什么？

Platform thread 是操作系统线程的包装，platform Thread 在底层的 OS 线程上运行 Java 代码，数量受限于操作系统线程的数量。Platform thread 通常有比较大的线程堆栈和操作系统维护的其他资源，platform thread 也支持线程的本地变量。

可以使用 platform thread 运行所有类型的任务，就是有点浪费资源，可能会资源耗尽。

## Virtual thread 是什么？

和 platform thread 一样，virtual thread 也是 `java.lang.Thread` 的实例。但是 virtual thread 并不与特定的操作系统线程绑定。Virtual thread 的代码仍然在操作系统的线程上运行，但是当 virtual thread 上运行的代码调用阻塞 I/O 时，Java 运行时将挂起这个 virtual thread 直到其恢复。与挂起的 virtual thread 相关联的操作系统线程可以对其他 virtual thread 执行操作。

Virtual thread 和实现方式和虚拟内存的实现方式类似。为了模拟大量内存，操作系统将一个大的虚拟地址空间映射到有限的 RAM。类似地，为了模拟大量线程，Java 运行时将大量 virtual thread 映射到少量操作系统线程上。

与 platform thread 不同，virtual thread 的调用堆栈较浅，例如只是一个 HTTP 调用或 JDBC 查询。尽管 virtual thread 支持线程局部变量，但是使用时要慎重，因为单个 JVM 可能支持数百万个 virtual thread。

Virtual thread 适合运行大部分时间被阻塞的任务（等待 I/O 操作），但并不适合 CPU 密集型操作。

## Virtual thread 的好处？

Virtual thread 适合使用在高吞吐量的并发应用程序中，尤其是并发任务需要大量等待的。例如在服务器应用程序中，就需要处理很多阻塞 I/O 操作的请求。在 virtual thread 上运行的代码并不会比 platform thread 上运行的代码更快，virtual thread 的好处在于更高的吞吐量，而不是速度。

## 使用 virtual thread

`Thread` 和 `Thread.Builder` API 都提供了创建 platform thread 和 virtual thread 的方法。`java.util.concurrent.Executors`也提供了创建使用 virtual thread 的任务的 `ExecutorService`。

下面的代码需要使用 JDK 19，可以直接在 IDEA 中下载：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-02-17-53-38.png?x-oss-process=image/resize,h_600)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-02-17-54-16.png?x-oss-process=image/resize,h_600)

### 使用 Thread.Builder 创建 virtual thread

```java
Thread thread = Thread.ofVirtual().start(() -> System.out.println("Hello"));
thread.join();
```

下面代码是使用 `Thread.Builder` 创建 2 个 virtual thread：

```java
try {
    Thread.Builder builder =
        Thread.ofVirtual().name("worker-", 0);

    Runnable task = () -> {
        System.out.println("Thread ID: " +
            Thread.currentThread().threadId());
    };            

    // name "worker-0"
    Thread t1 = builder.start(task);   
    t1.join();
    System.out.println(t1.getName() + " terminated");

    // name "worker-1"
    Thread t2 = builder.start(task);   
    t2.join();  
    System.out.println(t2.getName() + " terminated");
    
} catch (InterruptedException e) {
    e.printStackTrace();
}
```

输出大概是下面这个样子：

```java
Thread ID: 21
worker-0 terminated
Thread ID: 24
worker-1 terminated
```

### 使用 Executors.newVirtualThreadPerTaskExecutor() 创建 virtual thread

```java
try (ExecutorService myExecutor =
    Executors.newVirtualThreadPerTaskExecutor()) {
    Future<?> future =
        myExecutor.submit(() -> System.out.println("Running thread"));
    future.get();
    System.out.println("Task completed");
} catch (InterruptedException | ExecutionException e) {
    e.printStackTrace();
}   
```

### 调度 virtual thread

Java 运行时将 virtual thread 挂载到一个 platform thread 上，操作系统像往常一样调度 platform thread。Virtual thread 可以从对应的 platform thread 上卸载（通常发生在 virtual thread 执行阻塞 I/O 操作时）。当一个 virtual thread 被卸载后，Java 运行时调度器能挂载不同的 virtual thread。

Virtual thread 也能固定到 platform thread 上，此时在阻塞操作期间也无法卸载 virtual thread。固定的情况有：

- virtual thread 在同步块或同步方法中（synchronized）
- virtual thread 在运行本地方法或 [外部函数](https://docs.oracle.com/en/java/javase/19/core/foreign-function-and-memory-api.html#GUID-FBE990DA-C356-46E8-9109-C75567849BA8)

# 补充说明

## JDK 19 使用说明

要想运行上面的代码，需要几个条件：

- IDEA 需要升级到最新版（2022.2.3），因为最新版才包含 JDK 19 的语言特性
- 在 Project Structure 中将 Language Level 设置为 `19 (Preview)`

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-03-11-52-54.png?x-oss-process=image/resize,h_600)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-03-11-53-18.png?x-oss-process=image/resize,h_600)

## JVM 源码分析

通过查看 JDK 8 和 JDK 19 的 Thread 源码，可以发现里面的实现已经大不一样了。对于 Thread 这块又涉及大量的操作系统底层接口，最好能直接看 JDK 源码。其实有一个完全不用下载，不用配置环境查看底层源码的方法，那就是使用 `Github`~~~

JDK 源码在这里：[https://github.com/openjdk/jdk](https://github.com/openjdk/jdk)，里面有每个 JDK 版本的源码。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-03-11-58-27.png?x-oss-process=image/resize,h_600)

我们可以直接在里面搜索文件，响应速度还可以。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-03-11-59-08.png?x-oss-process=image/resize,h_600)

比如想查看 Thread.c 源码，直接在网页上就能查看（除了跳转功能）：

```c
static JNINativeMethod methods[] = {
    {"start0",           "()V",        (void *)&JVM_StartThread},
    {"isAlive0",         "()Z",        (void *)&JVM_IsThreadAlive},
    {"setPriority0",     "(I)V",       (void *)&JVM_SetThreadPriority},
    {"yield0",           "()V",        (void *)&JVM_Yield},
    {"sleep0",           "(J)V",       (void *)&JVM_Sleep},
    {"currentCarrierThread", "()" THD, (void *)&JVM_CurrentCarrierThread},
    {"currentThread",    "()" THD,     (void *)&JVM_CurrentThread},
    {"setCurrentThread", "(" THD ")V", (void *)&JVM_SetCurrentThread},
    {"interrupt0",       "()V",        (void *)&JVM_Interrupt},
    {"holdsLock",        "(" OBJ ")Z", (void *)&JVM_HoldsLock},
    {"getThreads",       "()[" THD,    (void *)&JVM_GetAllThreads},
    {"dumpThreads",      "([" THD ")[[" STE, (void *)&JVM_DumpThreads},
    {"getStackTrace0",   "()" OBJ,     (void *)&JVM_GetStackTrace},
    {"setNativeName",    "(" STR ")V", (void *)&JVM_SetNativeThreadName},
    {"extentLocalCache",  "()[" OBJ,    (void *)&JVM_ExtentLocalCache},
    {"setExtentLocalCache", "([" OBJ ")V",(void *)&JVM_SetExtentLocalCache},
    {"getNextThreadIdOffset", "()J",     (void *)&JVM_GetNextThreadIdOffset}
};
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-11-03-19-43-13.png?x-oss-process=image/resize,h_600)

扩展阅读：
- [如何阅读 JVM 源码](https://developer.aliyun.com/article/935147)
- [如何阅读 JDK、JVM 源代码？](http://xieli.leanote.com/post/%E5%A6%82%E4%BD%95%E9%98%85%E8%AF%BBJDK%E6%BA%90%E4%BB%A3%E7%A0%81%EF%BC%9F)
- [从零开始学 JVM 系列（五）：搭建 HotSpot 源码阅读环境](https://juejin.cn/post/6969389200416178213)

# 参考链接

- [Oracle Core Libraries 12 Virtual Threads](https://docs.oracle.com/en/java/javase/19/core/virtual-threads.html#GUID-DC4306FC-D6C1-4BCC-AECE-48C32C1A8DAA)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)