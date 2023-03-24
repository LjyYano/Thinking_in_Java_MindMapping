---
date: 2021-08-16
---


- [LockSupport 类有什么用？](#locksupport-类有什么用)
- [主要有哪些方法？](#主要有哪些方法)
- [举几个例子](#举几个例子)
  - [让线程阻塞](#让线程阻塞)
  - [让线程阻塞 2 秒后停止](#让线程阻塞-2-秒后停止)
- [看看官方文档](#看看官方文档)
- [核心函数分析](#核心函数分析)
  - [park 函数](#park-函数)
  - [unpark 函数](#unpark-函数)
- [Object.wait()、Thread.sleep()、LockSupport.park() 区别](#objectwaitthreadsleeplocksupportpark-区别)
- [其他说明](#其他说明)
- [参考链接](#参考链接)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# LockSupport 类有什么用？

线程阻塞工具类，能够让线程在任意位置`阻塞/唤醒`。LockSupport 用来创建锁和其他同步类的基本线程阻塞原语。简而言之，当调用 LockSupport.park 时，表示当前线程将会等待，直至获得许可，当调用 LockSupport.unpark 时，必须把等待获得许可的线程作为参数进行传递，好让此线程继续运行。 

# 主要有哪些方法？

```java
public static void park(Object blocker); // 暂停当前线程
public static void parkNanos(Object blocker, long nanos); // 暂停当前线程，不过有超时时间的限制
public static void parkUntil(Object blocker, long deadline); // 暂停当前线程，直到某个时间
public static void park(); // 无期限暂停当前线程
public static void parkNanos(long nanos); // 暂停当前线程，不过有超时时间的限制
public static void parkUntil(long deadline); // 暂停当前线程，直到某个时间
public static void unpark(Thread thread); // 恢复当前线程
public static Object getBlocker(Thread t);
```

park 的意思是“停车”，让线程“停车”就是让线程阻塞的意思；所以 unpark 就是恢复当前线程。

# 举几个例子

## 让线程阻塞

首先写一个让线程阻塞的测试用例，很简单，就是 `LockSupport.park()` 这一句话。

```java
@Test
public void testPark0() {
    LockSupport.park();
}
```
执行后我们发现，这个线程会一直阻塞在这里，单元测试永远也不会停止。

## 让线程阻塞 2 秒后停止

接下来就比上面难一点了，我们阻塞主线程，然后 2 秒后恢复当前线程，之后程序结束运行。

```java
@Test
public void testPark1() {
    Thread mainThread = Thread.currentThread();
    // 开启一个线程，10 秒后把主线程 unpark
    new Thread(() -> {
        try {
            TimeUnit.SECONDS.sleep(2);
        } catch (InterruptedException e) {
            // ignore
        }
        LockSupport.unpark(mainThread);
    }).start();

    // 阻塞主线程
    LockSupport.park();
}
```

更简单一点的方法：

```java
@Test
public void testPark3() {
    LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(2));
}
```

# 看看官方文档

https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/locks/LockSupport.html

> Basic thread blocking primitives for creating locks and other synchronization classes.

> This class associates, with each thread that uses it, a permit (in the sense of the Semaphore class). A call to park will return immediately if the permit is available, consuming it in the process; otherwise it may block. A call to unpark makes the permit available, if it was not already available. (Unlike with Semaphores though, permits do not accumulate. There is at most one.)

> Methods park and unpark provide efficient means of blocking and unblocking threads that do not encounter the problems that cause the deprecated methods Thread.suspend and Thread.resume to be unusable for such purposes: Races between one thread invoking park and another thread trying to unpark it will preserve liveness, due to the permit. Additionally, park will return if the caller's thread was interrupted, and timeout versions are supported. The park method may also return at any other time, for "no reason", so in general must be invoked within a loop that rechecks conditions upon return. In this sense park serves as an optimization of a "busy wait" that does not waste as much time spinning, but must be paired with an unpark to be effective.

> The three forms of park each also support a blocker object parameter. This object is recorded while the thread is blocked to permit monitoring and diagnostic tools to identify the reasons that threads are blocked. (Such tools may access blockers using method getBlocker(Thread).) The use of these forms rather than the original forms without this parameter is strongly encouraged. The normal argument to supply as a blocker within a lock implementation is this.

# 核心函数分析

先引入 `sun.misc.Unsafe` 类中的 park 和 unpark 函数，因为 LockSupport 的核心函数都是基于 Unsafe 类中定义的 park 和 unpark 函数，下面给出两个函数的定义：

```java
public native void park(boolean isAbsolute, long time);
public native void unpark(Thread thread);
```

## park 函数

阻塞线程，并且线程在`下列情况发生之前`都会被阻塞：
- 调用 unpark 函数，释放该线程的许可
- 该线程被中断
- 设置的时间到了

其中无参的重载版本：

```java
public static void park() {
    // 获取许可，设置时间为无限长，直到可以获取许可
    UNSAFE.park(false, 0L);
}
```

## unpark 函数

此函数表示如果给定线程的许可尚不可用，则使其可用。如果线程在 park 上受阻塞，则它将解除其阻塞状态。否则，保证下一次调用 park 不会受阻塞。如果给定线程尚未启动，则无法保证此操作有任何效果。

```java
public static void unpark(Thread thread) {
    if (thread != null) // 线程为不空
        UNSAFE.unpark(thread); // 释放该线程许可
}
```

# Object.wait()、Thread.sleep()、LockSupport.park() 区别

这 3 个方法都能够`阻塞当前线程`，但是还是有很多区别的！

|                      | Object.wait()     | Thread.sleep() | LockSupport.park()                   |
| -------------------- | ----------------- | -------------- | ------------------------------------ |
| `释放锁资源 monitor` | 释放              | 不释放         | 不负责（Condition.await() 负责释放） |
| 指定时间             | 必须指定          | 可选           | 可选                                 |
| 外部唤醒             | notify()          | 不可           | unpark()                             |
| 异常                 | 无                | 抛出异常       | 无                                   |
| 执行位置             | synchronized 块中 | 任意           | 任意                                 |
| 死锁                 | 使用不当会死锁    | 无             | 顺序反也不会死锁                     |

# 其他说明

LockSupport 类只负责阻塞线程，并不涉及锁相关的内容。Condition.await() 的功能和 Object.wait() 是类似的，不过 Condition.await() 底层是调用 LockSupport.park() 来实现线程阻塞的。

# 参考链接

- [JUC 锁：LockSupport 详解](https://www.pdai.tech/md/java/thread/java-thread-x-lock-LockSupport.html)
- [LockSupport 官方文档](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/locks/LockSupport.html)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！

原创不易，希望大家转载时请先联系我，并标注原文链接。