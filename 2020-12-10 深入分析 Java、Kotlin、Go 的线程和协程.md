![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-10-070550.jpg)

- [前言](#前言)
  - [协程是什么](#协程是什么)
  - [协程的好处](#协程的好处)
- [进程](#进程)
  - [进程是什么](#进程是什么)
  - [进程组成](#进程组成)
  - [进程特征](#进程特征)
- [线程](#线程)
  - [线程是什么](#线程是什么)
  - [线程组成](#线程组成)
  - [任务调度](#任务调度)
  - [进程与线程的区别](#进程与线程的区别)
  - [线程的实现模型](#线程的实现模型)
    - [一对一模型](#一对一模型)
    - [多对一模型](#多对一模型)
    - [多对多模型](#多对多模型)
  - [线程的“并发”](#线程的并发)
- [协程](#协程)
  - [协程的目的](#协程的目的)
  - [协程的特点](#协程的特点)
  - [协程的原理](#协程的原理)
- [Java、Kotlin、Go 的线程与协程](#javakotlingo-的线程与协程)
  - [Kotlin 的协程](#kotlin-的协程)
    - [使用「线程」的代码](#使用线程的代码)
    - [使用「协程」的代码](#使用协程的代码)
  - [Go 的协程](#go-的协程)
  - [Java 的 Kilim 协程框架](#java-的-kilim-协程框架)
  - [Java 的 Project Loom](#java-的-project-loom)
    - [使用 Fiber](#使用-fiber)
- [总结](#总结)
- [参考资料](#参考资料)

# 前言

Go 语言比 Java 语言性能优越的一个原因，就是轻量级线程`Goroutines`（协程Coroutine）。本篇文章深入分析下 Java 的线程和 Go 的协程。

## 协程是什么

协程并不是 Go 提出来的新概念，其他的一些编程语言，例如：Go、Python 等都可以在语言层面上实现协程，甚至是 Java，也可以通过使用扩展库来间接地支持协程。

当在网上搜索协程时，我们会看到：

- Kotlin 官方文档说「本质上，协程是轻量级的线程」。
- 很多博客提到「不需要从用户态切换到内核态」、「是协作式的」等等。

「协程 Coroutines」源自 Simula 和 Modula-2 语言，这个术语早在 1958 年就被 Melvin Edward Conway 发明并用于构建汇编程序，说明协程是一种编程思想，并不局限于特定的语言。

## 协程的好处

性能比 Java 好很多，甚至代码实现都比 Java 要简洁很多。

那这究竟又是为什么呢？下面一一分析。

说明：下面关于进程和线程的部分，几乎完全参考自：https://www.cnblogs.com/Survivalist/p/11527949.html，这篇文章写得太好了~~~

# 进程

## 进程是什么

计算机的核心是 CPU，执行所有的计算任务；操作系统负责任务的调度、资源的分配和管理；应用程序是具有某种功能的程序，程序是运行在操作系统上的。

进程是一个具有一定独立功能的程序在一个数据集上的一次动态执行的过程，是操作系统进行资源分配和调度的一个独立单位，是应用程序运行的载体。

## 进程组成

进程由三部分组成：

- `程序`：描述进程要完成的功能，是控制进程执行的指令集。
- `数据集合`：程序在执行时所需要的数据和工作区。
- `进程控制块`：(Program Control Block，简称PCB)，包含进程的描述信息和控制信息，是进程存在的唯一标志。

## 进程特征

- 动态性：进程是程序的一次执行过程，是临时的，有生命期的，是动态产生，动态消亡的。
- 并发性：任何进程都可以同其他进程一起并发执行。
- 独立性：进程是系统进行资源分配和调度的一个独立单位。
- 结构性：进程由程序、数据和进程控制块三部分组成。

# 线程

## 线程是什么

线程是程序执行中一个单一的`顺序控制流程`，是`程序执行流的最小单元`，是`处理器调度和分派的基本单位`。一个进程可以有一个或多个线程，各个线程之间`共享程序的内存空间`(也就是所在进程的内存空间)。

## 线程组成

- 线程ID、当前指令指针(PC)
- 寄存器
- 堆栈

## 任务调度

大部分操作系统(如Windows、Linux)的任务调度是采用`时间片轮转的抢占式调度方式`。

在一个进程中，当一个线程任务执行几毫秒后，会由操作系统的内核（负责管理各个任务）进行调度，通过硬件的计数器中断处理器，让该线程强制暂停并将该线程的寄存器放入内存中，通过查看线程列表决定接下来执行哪一个线程，并从内存中恢复该线程的寄存器，最后恢复该线程的执行，从而去执行下一个任务。

## 进程与线程的区别

- 线程是程序执行的最小单位，而进程是操作系统分配资源的最小单位；
- 一个进程由一个或多个线程组成，`线程是一个进程中代码的不同执行路线`；
- 进程之间相互独立，但同一进程下的各个线程之间共享程序的内存空间(包括代码段、数据集、堆等)及一些进程级的资源(如打开文件和信号)，某进程内的线程在其它进程不可见；
- 调度和切换：`线程上下文切换`比`进程上下文切换`要`快`得多。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-10-120038.jpg)

## 线程的实现模型

程序一般不会直接去使用内核线程，而是去使用内核线程的一种高级接口——`轻量级进程（Lightweight Process，LWP）`，轻量级进程就是我们通常意义上所讲的线程，也被叫做用户线程。

### 一对一模型

一个用户线程对应一个内核线程，如果是多核的 CPU，那么线程之间是真正的并发。

缺点：
  
  - 内核线程的数量有限，一对一模型使用的用户线程数量有限制。
  - 内核线程的调度，上下文切换的开销较大（虽然没有进程上下文切换的开销大），导致用户线程的执行效率下降。

### 多对一模型

`多个用户线程`映射到`一个内核线程`上，线程间的切换由`用户态`的代码来进行。用户线程的建立、同步、销毁都是在用户态中完成，不需要内核的介入。因此多对一的上下文切换速度快很多，且用户线程的数量几乎没有限制。

缺点：

- 若一个用户线程阻塞，其他所有线程都无法执行，此时内核线程处于阻塞状态。
- 处理器数量的增加，不会对多对一模型的线程性能造成影响，因为所有的用户线程都映射到了一个处理器上。

### 多对多模型

结合了`一对一模型`和`多对一`模型的优点，多个用户线程映射到多个内核线程上，由`线程库`负责在可用的可调度实体上调度用户线程。这样线程间的上下文切换很快，因为它避免了系统调用。但是增加了系统的复杂性。

优点：

- 一个用户线程的阻塞不会导致所有线程的阻塞，因为此时还有别的内核线程被调度来执行；
- 多对多模型对用户线程的数量没有限制；
- 在多处理器的操作系统中，多对多模型的线程也能得到一定的性能提升，但提升的幅度不如一对一模型的高。

## 线程的“并发”

只有在线程的数量 < 处理器的数量时，线程的并发才是真正的并发，这时不同的线程运行在不同的处理器上。但是当线程的数量 > 处理器的数量时，会出现一个处理器运行多个线程的情况。

在单个处理器运行多个线程时，并发是一种模拟出来的状态。操作系统采用时间片轮转的方式轮流执行每一个线程。现在，几乎所有的现代操作系统采用的都是时间片轮转的抢占式调度方式。

# 协程

当在网上搜索协程时，我们会看到：

- 本质上，协程是轻量级的线程。
- 很多博客提到「不需要从用户态切换到内核态」、「是协作式的」。

协程也并不是 Go 提出来的，协程是一种编程思想，并不局限于特定的语言。Go、Python、Kotlin 都可以在语言层面上实现协程，Java 也可以通过扩展库的方式间接支持协程。

协程比线程更加轻量级，可以由程序员自己管理的轻量级线程，对内核不可见。

## 协程的目的

在传统的 J2EE 系统中都是基于每个请求占用一个线程去完成完整的业务逻辑（包括事务）。所以系统的吞吐能力取决于每个线程的操作耗时。如果遇到很耗时的 I/O 行为，则整个系统的吞吐立刻下降，因为这个时候线程一直处于阻塞状态，如果线程很多的时候，会存在很多线程处于空闲状态（等待该线程执行完才能执行），造成了资源应用不彻底。

最常见的例子就是 JDBC（它是同步阻塞的），这也是为什么很多人都说数据库是瓶颈的原因。这里的耗时其实是让 CPU 一直在等待 I/O 返回，说白了线程根本没有利用 CPU 去做运算，而是处于空转状态。而另外过多的线程，也会带来更多的 ContextSwitch 开销。

对于上述问题，现阶段行业里的比较流行的解决方案之一就是单线程加上异步回调。其代表派是 node.js 以及 Java 里的新秀 Vert.x。

而协程的目的就是当出现长时间的 I/O 操作时，通过让出目前的协程调度，执行下一个任务的方式，来消除 ContextSwitch 上的开销。

## 协程的特点

- 线程的切换由操作系统负责调度，协程由用户自己进行调度，减少了上下文切换，提高了效率
- 线程的默认 Stack 是1M，协程更加轻量，是 1K，在相同内存中可以开启更多的协程。
- 由于在同一个线程上，因此可以`避免竞争关系`而使用锁。
- 适用于`被阻塞的`，且需要大量并发的场景。但不适用于大量计算的多线程，遇到此种情况，更好用线程去解决。

## 协程的原理

当出现IO阻塞的时候，由协程的调度器进行调度，通过将数据流立刻yield掉（主动让出），并且记录当前栈上的数据，阻塞完后立刻再通过线程恢复栈，并把阻塞的结果放到这个线程上去跑，这样看上去好像跟写同步代码没有任何差别，这整个流程可以称为`coroutine`，而跑在由coroutine负责调度的线程称为`Fiber`。比如Golang里的 go关键字其实就是负责开启一个`Fiber`，让func逻辑跑在上面。

由于协程的暂停完全由程序控制，发生在用户态上；而线程的阻塞状态是由操作系统内核来进行切换，发生在内核态上。
因此，协程的开销远远小于线程的开销，也就没有了 ContextSwitch 上的开销。

假设程序中默认创建两个线程为协程使用，在主线程中创建协程ABCD…，分别存储在就绪队列中，调度器首先会分配一个工作线程A执行协程A，另外一个工作线程B执行协程B，其它创建的协程将会放在队列中进行排队等待。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-10-144133.jpg)

当协程A调用暂停方法或被阻塞时，协程A会进入到挂起队列，调度器会调用等待队列中的其它协程抢占线程A执行。当协程A被唤醒时，它需要重新进入到就绪队列中，通过调度器抢占线程，如果抢占成功，就继续执行协程A，失败则继续等待抢占线程。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-10-144157.jpg)

# Java、Kotlin、Go 的线程与协程

Java 在 Linux 操作系统下使用的是用户线程+轻量级线程，`一个用户线程映射到一个内核线程`，线程之间的切换就涉及到了上下文切换。所以在 Java 中并不适合创建大量的线程，否则效率会很低。可以先看下 Kotlin 和 Go 的协程：

## Kotlin 的协程

Kotlin 在诞生之初，目标就是完全兼容 Java，却是一门非常务实的语言，其中一个特性，就是支持协程。

但是 Kotlin 最终还是运行在 JVM 中的，目前的 JVM 并不支持协程，Kotlin 作为一门编程语言，也只是能在语言层面支持协程。Kotlin 的协程是用于异步编程等场景的，在语言级提供协程支持，而将大部分功能委托给库。

### 使用「线程」的代码

```java
@Test
fun testThread() {
    // 执行时间 1min+
    val c = AtomicLong()
    for (i in 1..1_000_000L)
        thread(start = true) {
            c.addAndGet(i)
        }
    println(c.get())
}
```

上述代码创建了 `100 万个线程`，在每个线程里仅仅调用了 add 操作，但是由于创建线程太多，这个测试用例在我的机器上要跑 1 分钟左右。

### 使用「协程」的代码

```java
@Test
fun testLaunch() {
    val c = AtomicLong()
    runBlocking {
        for (i in 1..1_000_000L)
            launch {
                c.addAndGet(workload(i))
            }
    }
    print(c.get())
}

suspend fun workload(n: Long): Long {
    delay(1000)
    return n
}
```

这段代码是创建了 `100 万个协程`，测试用例在我的机器上执行时间大概是 10 秒钟。而且这段代码的每个协程都 delay 了 1 秒钟，执行效率仍然远远高于线程。

详细的语法可以查看 Kotlin 的官方网站：https://www.kotlincn.net/docs/reference/coroutines/basics.html

其中关键字 `launch` 是开启了一个协程，关键字 `suspend` 是挂起一个协程，而不会阻塞。现在在看这个流程，应该就懂了~

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-11-082219.jpg)

## Go 的协程

官方例程：https://gobyexample-cn.github.io/goroutines

go语言层面并`不支持多进程或多线程`，但是协程更好用，协程被称为用户态线程，不存在CPU上下文切换问题，效率非常高。下面是一个简单的协程演示代码：

```go
package main

func main() {
    go say("Hello World")
}

func say(s string) {
    println(s)
}
```

## Java 的 Kilim 协程框架

目前 Java 原生语言暂时不支持协程，可以使用 [kilim](https://github.com/kilim/kilim)，具体原理可以看官方文档，暂时还没有研究~


## Java 的 Project Loom

Java 也在逐步支持协程，其项目就是 `Project Loom`(https://openjdk.java.net/projects/loom/)。这个项目在18年底的时候已经达到可初步演示的原型阶段。不同于之前的方案，Project Loom 是从 JVM 层面对多线程技术进行彻底的改变。

官方介绍：
http://cr.openjdk.java.net/~rpressler/loom/Loom-Proposal.html

其中一段介绍了为什么引入这个项目：

    One of Java's most important contributions when it was first released, over twenty years ago, was the easy access to threads and synchronization primitives. Java threads (either used directly, or indirectly through, for example, Java servlets processing HTTP requests) provided a relatively simple abstraction for writing concurrent applications. These days, however, one of the main difficulties in writing concurrent programs that meet today's requirements is that the software unit of concurrency offered by the runtime — the thread — cannot match the scale of the domain's unit of concurrency, be it a user, a transaction or even a single operation. Even if the unit of application concurrency is coarse — say, a session, represented by single socket connection — a server can handle upward of a million concurrent open sockets, yet the Java runtime, which uses the operating system's threads for its implementation of Java threads, cannot efficiently handle more than a few thousand. A mismatch in several orders of magnitude has a big impact.

文章大意就是本文上面所说的，Java 的用户线程与内核线程是一对一的关系，一个 Java 进程很难创建上千个线程，如果是对于 I/O 阻塞的程序（例如数据库读取/Web服务），性能会很低下，所以要采用类似于协程的机制。

### 使用 Fiber

在引入 Project Loom 之后，JDK 将引入一个新类：java.lang.Fiber。此类与 java.lang.Thread 一起，都成为了 java.lang.Strand 的子类。即线程变成了一个虚拟的概念，有两种实现方法：Fiber 所表示的轻量线程和 Thread 所表示的传统的重量级线程。

```java
Fiber f = Fiber.schedule(() -> {
  println("Hello 1");
  lock.lock(); // 等待锁不会挂起线程
  try {
      println("Hello 2");
  } finally {
      lock.unlock();
  }
  println("Hello 3");
})
```

只需执行 `Fiber.schedule(Runnable task)` 就能在 `Fiber` 中执行任务。最重要的是，上面例子中的 lock.lock() 操作将不再挂起底层线程。除了 `Lock 不再挂起线程`以外，像 `Socket BIO 操作也不再挂起线程`。 但 synchronized，以及 Native 方法中线程挂起操作无法避免。

# 总结

协程大法好，比线程更轻量级，但是仅针对 I/O 阻塞才有效；对于 CPU 密集型的应用，因为 CPU 一直都在计算并没有什么空闲，所以没有什么作用。

Kotlin 兼容 Java，在编译器、语言层面实现了协程，JVM 底层并不支持协程；Go 天生就是支持协程的，不支持多进程和多线程。Java 的 `Project Loom` 项目支持协程，

# 参考资料

- 极客时间-Java性能调优实战/19.如何用协程来优化多线程业务？
- https://www.cnblogs.com/Survivalist/p/11527949.html
- https://www.jianshu.com/p/5db701a764cb