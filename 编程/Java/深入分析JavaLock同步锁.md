![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-05-062310.jpg)

# 前言

Java 的锁实现，有 Synchronized 和 Lock。上一篇文章深入分析了 Synchronized 的实现原理：[由Java 15废弃偏向锁，谈谈Java Synchronized 的锁机制](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-12-05%20%E7%94%B1Java%2015%E5%BA%9F%E5%BC%83%E5%81%8F%E5%90%91%E9%94%81%EF%BC%8C%E8%B0%88%E8%B0%88Java%20Synchronized%20%E7%9A%84%E9%94%81%E6%9C%BA%E5%88%B6.md)。

本篇文章深入分析 Lock 的实现，以及对比其与 Synchronized 的不同。

# Synchronized 与 Lock 的对比

- 实现方式：Synchronized 由 JVM 实现；Lock 由 Java 底层代码实现
- 锁获取：Synchronized 是 JVM 隐式获取，不用 Java 代码；Lock 由 Java 代码实现，有多种获取方式
- 锁的释放：Synchronized 是 JVM 隐式释放，不用 Java 代码；Lock 可通过 `Lock.unlock()`，在 finally 中释放
- 锁的类型：`Synchronized 是非公平、可重入的`，`Lock 是非公平性、公平性、可重入的`
- 锁的中断：Synchronized 不支持中断，Lock 支持中断

# 实现原理

Lock 是一个接口类，其接口方法定义：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-07-114730.png)

- `lock()`：获取锁
- `lockInterruptibly()`：如果当前线程未被中断，则获取锁，可以响应中断
- `tryLock()`：仅在调用时锁为空闲状态才获取该锁，可以响应中断
- `tryLock(long time, TimeUnit unit)`：如果锁在给定的等待时间内空闲，并且当前线程未被中断，则获取锁
- `unlock()`：释放锁
- `newCondition()`：返回绑定到此 Lock 实例的新 Condition 实例

基础原理就不赘述了，Lock 接口的常用类：

- ReentrantLock（重入锁）
- ReentrantReadWriteLock（可重入的读写锁）

其都是依赖 `AQS` 实现的。AQS 类结构中包含一个`基于链表实现的等待队列`（CLH 队列），用于存储所有阻塞的线程，AQS 中还有一个 state 变量，表示加锁状态。

# ReentrantLock

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-07-115340.png)

# ReentrantReadWriteLock

ReentrantLock 是独占锁，对于同一份数据，如果一个线程读数据，另一个线程在写数据，那么读到的数据与最终的数据可能不一致。

在实际的业务场景中，读操作远远大于写操作。在多线程编程中，读操作不会修改共享资源的数据。针对读多写少的场景，我们可以使用 ReentrantReadWriteLock 来优化，ReentrantReadWriteLock 内部维护了 2 个锁：读锁 `ReadLock`，写锁 `WriteLock`。

规则简单概括为：
- 如果写锁没有被占用，就可以获取读锁
- 如果读锁没有被占用，才可以获取写锁

下面的测试代码，因为读锁和写锁是同时 lock 的，所以会死锁。

```java
@Test
public void testReadWriteLock() {
    ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    lock.readLock().lock();
    lock.writeLock().lock();
    System.out.println("Hello");
    lock.readLock().unlock();
    lock.writeLock().unlock();
}
```

# StampedLock

上述 ReentrantReadWriteLock 会有一个问题：在读很多，写很少的情况下，线程会因一直无法获取到锁而处于等待状态。

在 JDK 1.8 中，Java 提供了 `StampedLock`，有三种模式: 
- 写
- 悲观读
- 乐观读

一个写线程获取写锁，通过 WriteLock 获取票据 stamp，WriteLock 是一个独占锁，unlockWrite 需要传递参数 stamp。

不一样的地方在于读过程。线程会先通过乐观锁 `tryOptimisticRead` 获取票据 stamp，如果当前没有线程持有写锁，则会返回一非 0 的 stamp 信息。线程获取该 stamp 后，会拷贝一份共享资源到房发展。

之后方法还需要调用 validate，验证之前调用 tryOptimisticRead 返回的 stamp 在当前是否有其它线程持有了写锁，如果是，那么 validate 会返回 0，升级为悲观锁；否则就可以使用该 stamp 版本的锁对数据进行操作。

# 总结

相比于 Synchronized 同步锁，Lock 实现的锁更加灵活：
- 可以分为读写锁，优化读大于写的场景
- 可以中断
- 可以超时
- 可以区分公平性