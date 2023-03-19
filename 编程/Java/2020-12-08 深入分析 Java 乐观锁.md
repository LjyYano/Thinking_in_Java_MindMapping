![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-08-095930.jpg)

# 前言

激烈的锁竞争，会造成`线程阻塞挂起`，导致`系统的上下文切换`，增加系统的性能开销。那有没有不阻塞线程，且保证线程安全的机制呢？——`乐观锁`。

# 乐观锁是什么？

操作共享资源时，总是很乐观，认为自己可以成功。在操作失败时（资源被其他线程占用），并不会挂起阻塞，而仅仅是返回，并且失败的线程可以重试。

优点：
- 不会死锁
- 不会饥饿
- 不会因竞争造成系统开销

# 乐观锁的实现

## CAS 原子操作

CAS。在 `java.util.concurrent.atomic` 中的类都是基于 CAS 实现的。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-08-100536.png)

以 AtomicLong 为例，一段测试代码：

```java
@Test
public void testCAS() {
    AtomicLong atomicLong = new AtomicLong();
    atomicLong.incrementAndGet();
}
```

java.util.concurrent.atomic.AtomicLong#incrementAndGet 的实现方法是：

```java
public final long incrementAndGet() {
    return U.getAndAddLong(this, VALUE, 1L) + 1L;
}
```

其中 U 是一个 Unsafe 实例。

```java
private static final jdk.internal.misc.Unsafe U = jdk.internal.misc.Unsafe.getUnsafe();
```

本文使用的源码是 JDK 11，其 getAndAddLong 源码为：

```java
@HotSpotIntrinsicCandidate
public final long getAndAddLong(Object o, long offset, long delta) {
    long v;
    do {
        v = getLongVolatile(o, offset);
    } while (!weakCompareAndSetLong(o, offset, v, v + delta));
    return v;
}
```

可以看到里面是一个 while 循环，如果不成功就一直循环，是一个乐观锁，坚信自己能成功，一直 CAS 直到成功。最终调用了 native 方法：

```java
@HotSpotIntrinsicCandidate
public final native boolean compareAndSetLong(Object o, long offset,
                                                long expected,
                                                long x);
```

## 处理器实现原子操作

从上面可以看到，CAS 是调用处理器底层的指令来实现原子操作，那么处理器底层是如何实现原子操作的呢？

处理器的处理速度>>处理器与物理内存的通信速度，所以在处理器内部有 L1、L2 和 L3 的高速缓存，可以加快读取的速度。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-12-09-054558.jpg)

`单核处理器`能够保存内存操作是原子性的，当一个线程读取一个字节，所以进程和线程看到的都是同一个缓存里的字节。但是`多核处理器`里，每个处理器都维护了一块字节的内存，每个内核都维护了一个字节的缓存，多线程并发会存在`缓存不一致`的问题。

那处理器如何保证内存操作的原子性呢？
- 总线锁定：当处理器要操作共享变量时，会在总线上发出 Lock 信号，其他处理器就不能操作这个共享变量了。
- 缓存锁定：某个处理器对缓存中的共享变量操作后，就通知其他处理器重新读取该共享资源。

# LongAdder vs AtomicLong

本文分析的 AtomicLong 源码，其实是在循环不断尝试 CAS 操作，如果长时间不成功，就会给 CPU 带来很大开销。JDK 1.8 中新增了原子类 `LongAdder`，能够更好应用于高并发场景。

LongAdder 的原理就是降低操作共享变量的并发数，也就是将对单一共享变量的操作压力分散到多个变量值上，将竞争的每个写线程的 value 值分散到一个数组中，不同线程会命中到数组的不同槽中，各个线程只对自己槽中的 value 值进行 CAS 操作，最后在读取值的时候会将原子操作的共享变量与各个分散在数组的 value 值相加，返回一个近似准确的数值。

LongAdder 内部由一个base变量和一个 cell[] 数组组成。当只有一个写线程，没有竞争的情况下，LongAdder 会直接使用 base 变量作为原子操作变量，通过 CAS 操作修改变量；当有多个写线程竞争的情况下，除了占用 base 变量的一个写线程之外，其它各个线程会将修改的变量写入到自己的槽 cell[] 数组中。

一个测试用例：

```java
@Test
public void testLongAdder() {
    LongAdder longAdder = new LongAdder();
    longAdder.add(1);
    System.out.println(longAdder.longValue());
}
```

先看里面的 `longAdder.longValue()` 代码：

```java
public long longValue() {
    return sum();
}
```

最终是调用了 sum() 方法，是对里面的 cells 数组每项加起来求和。这个值在读取的时候并不准，因为这期间可能有其他线程在并发修改 cells 中某个项的值：

```java
public long sum() {
    Cell[] cs = cells;
    long sum = base;
    if (cs != null) {
        for (Cell c : cs)
            if (c != null)
                sum += c.value;
    }
    return sum;
}
```

add() 方法源码：

```java
public void add(long x) {
    Cell[] cs; long b, v; int m; Cell c;
    if ((cs = cells) != null || !casBase(b = base, b + x)) {
        boolean uncontended = true;
        if (cs == null || (m = cs.length - 1) < 0 ||
            (c = cs[getProbe() & m]) == null ||
            !(uncontended = c.cas(v = c.value, v + x)))
            longAccumulate(x, null, uncontended);
    }
}
```

add 具体的代码本篇文章就不详细叙述了~