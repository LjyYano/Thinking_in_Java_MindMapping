---
date: 2022-09-09
---

<!-- TOC -->

- [QPS 和并发](#qps-和并发)
- [经典限流算法](#经典限流算法)
  - [滑动时间窗口算法](#滑动时间窗口算法)
  - [漏桶算法 (Leaky Bucket)](#漏桶算法-leaky-bucket)
  - [令牌桶算法 (Token Bucket)](#令牌桶算法-token-bucket)
- [RateLimiter 基本使用](#ratelimiter-基本使用)
- [RateLimiter 源码分析](#ratelimiter-源码分析)
  - [UML](#uml)
  - [RateLimiter 基本参数](#ratelimiter-基本参数)
    - [创建](#创建)
    - [获取令牌](#获取令牌)
- [参考链接](#参考链接)
- [我的公众号](#我的公众号)

<!-- /TOC -->

# QPS 和并发

- QPS：每秒进入的请求（每秒钟都有进入，不管是否完成）
- 并发：正在处理的请求，QPS 进入的请求没有处理完，并发就会增加

# 经典限流算法

- 时间窗口
- 漏桶算法
- 令牌桶算法

## 滑动时间窗口算法

- 设定目标限流 maxQps
- 根据当前时间获取对应的时间窗口
- 根据统计数据计算出当前时间窗口内的请求量是否大于 maxQps
- 小于则处理本次请求，更新统计数据，否则按限流处理

![http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-05-25-19-19-56.png](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-05-25-19-19-56.png)

优缺点：

- 实现简单
- 时间分片，容易在时间片的临界点出现流量抖动
- 流量较大时，容易出现在一个时间片的开始就用完了限速额度，直到下一个窗口才有额度，导致实际处理的流量不均匀

## 漏桶算法 (Leaky Bucket)

漏桶算法的思想：

- 漏桶有一定的容量 P，水以不定的速率 V-in 流入漏桶中，漏桶以恒定的 V-out 速率漏出水
- 当$V_{in} > V_{out}$，水就会在桶中堆积
- 堆积的水超过同的容量 P 时，就溢出丢弃
- 当$V_{in} < V_{out}$时，会消耗桶中储存的水

优点：漏桶可以起到整流的效果，因为漏出速率恒定，短时高流量会在桶内堆积，低流量会消耗桶内累计的请求，对下游（有限的，取决于桶容量）屏蔽这种波动。

## 令牌桶算法 (Token Bucket)

令牌桶算法的核心思想是，请求需要拿到令牌才能被处理，通过控制令牌的产生速率，就能控制实际服务的 qps。

- 令牌桶有固定容量，并且以恒定速率 rate 产生令牌，即每 1/rate 秒产出一个令牌
- 新产生的令牌会放入令牌桶，桶满则丢弃
- 请求需要从桶中取走一个令牌才能被处理，若桶空则被限流

漏桶算法和令牌桶算法的异同：

- 流量 <= 处理速度： 两者速度相同，漏桶保持空，令牌桶保持满
- 流量 远大于 处理速度：两者速度相同，漏桶保持满，令牌桶保持空
- 流量 <= 处理速度，偶尔有突发流量时：
    - 漏桶的漏出速率是固定的，即使下游处理能力有富余，整个系统的处理速度也是固定的。
    - 令牌桶的可以在流量低峰期储存富余的令牌（<=桶容量），可以消耗桶里的令牌来处理掉一定的突发流量。

摘抄一段 [wikipedia](https://en.wikipedia.org/wiki/Leaky_bucket) 原话：

> The implementation of the leaky-bucket as a queue does not use available network resources efficiently. Because it transmits packets only at fixed intervals, there will be many instances when the traffic volume is very low and large portions of network resources (bandwidth in particular) are not being used. Therefore no mechanism exists in the leaky-bucket implementation as a queue to allow individual flows to burst up to port speed, effectively consuming network resources at times when there would not be resource contention in the network. Implementations of the token bucket and leaky bucket as a meter do, however, allow output traffic flows to have bursty characteristics.
漏桶的漏出速率是固定的参数，所以，即使网络中不存在资源冲突（没有发生拥塞），漏桶算法也不能使某一个单独的流突发到端口速率
> 
> This explains why, given equivalent parameters, the two algorithms will see exactly the same packets as conforming or nonconforming. The differences in the properties and performance of implementations of the leaky and token bucket algorithms thus result entirely from the differences in the implementations, i.e. they do not stem from differences in the underlying algorithms.
> 给定相同的参数，两个算法通过和不通过基本一样。功能和性能上的差异完全来自于他们的不同实现，两个算法思想并没有本质上的区别。

# RateLimiter 基本使用

RateLimiter 通过固定桶大小、令牌产出速率，动态维护桶内令牌数、下一次可用令牌产出时间，实现了一种高效的基于令牌桶的限流。RateLimiter，顾名思义是对 Rate 的 Limiter，能够限制令牌产生的速率。

[Quick Guide to the Guava RateLimiter](https://www.baeldung.com/guava-rate-limiter)

[Class RateLimiter docs](https://guava.dev/releases/22.0/api/docs/index.html?com/google/common/util/concurrent/RateLimiter.html)

# RateLimiter 源码分析

## UML

整体 UML 图如下，其实主要只有 2 个类：抽象类 RateLimiter 和实现类 SmoothRateLimiter（也是 abstract 的）。整体实现非常简单、简洁。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-13-10-01-01.png)

SmoothBursty（适用于突发流量） 和 SmoothWarmingUp（自带预热机制） 的区别：
1. SmoothBursty 初始化的时候令牌池中的令牌数量为 0，而 SmoothWarmingUp 初始化的时候令牌数量为 maxPermits。
2. SmoothBursty 从令牌池中获取令牌不需要等待，而 SmoothWarmingUp 从令牌池中获取令牌需要等待一段时间，该时间长短和令牌池中的令牌数量有关系。

RareLimiter 中的令牌来源有两个：
1. 令牌池。SmoothBursty 从令牌池中获取令牌是不需要额外等待时间的，而 SmoothWarmingUp 从令牌池中获取令牌是需要额外等待时间的。
2. 透支未来令牌。这一点，SmoothBursty 和 SmoothWarmingUp 均相同。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-13-09-58-30.png)

## RateLimiter 基本参数

RateLimiter 主要的方法有下面这些，创建使用 create，获取使用 acquire 或 tryAcquire 方法。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-13-10-07-12.png)

RateLimiter 只有一个实现类 SmoothRateLimiter，SmoothRateLimiter 有 2 个内部类 SmoothWarmingUp 和 SmoothBursty。SmoothRateLimiter 的基本参数有：

```java
/** The currently stored permits. */
// 当前桶里缓存的令牌数，随着请求动态更新
double storedPermits;

/** The maximum number of stored permits. */
double maxPermits;

/**
* The interval between two unit requests, at our stable rate. E.g., a stable rate of 5 permits
* per second has a stable interval of 200ms.
*/
// 产生一个令牌的时间间隔/速率
double stableIntervalMicros;

/**
* The time when the next request (no matter its size) will be granted. After granting a request,
* this is pushed further in the future. Large requests push this further than small requests.
*/
// 下一个“可用”的令牌产出时间
private long nextFreeTicketMicros = 0L; // could be either in the past or future
```

### 创建

```java
public static RateLimiter create(double permitsPerSecond) {
/*
    * The default RateLimiter configuration can save the unused permits of up to one second. This
    * is to avoid unnecessary stalls in situations like this: A RateLimiter of 1qps, and 4 threads,
    * all calling acquire() at these moments:
    *
    * T0 at 0 seconds
    * T1 at 1.05 seconds
    * T2 at 2 seconds
    * T3 at 3 seconds
    *
    * Due to the slight delay of T1, T2 would have to sleep till 2.05 seconds, and T3 would also
    * have to sleep till 3.05 seconds.
    */
return create(permitsPerSecond, SleepingStopwatch.createFromSystemTimer());
}
```

从上面代码的注释中可以看出，

默认使用的是 SmoothBursty 实现：

```java
  @VisibleForTesting
  static RateLimiter create(double permitsPerSecond, SleepingStopwatch stopwatch) {
    RateLimiter rateLimiter = new SmoothBursty(stopwatch, 1.0 /* maxBurstSeconds */);
    rateLimiter.setRate(permitsPerSecond);
    return rateLimiter;
  }
```

会调用到 setRate 方法：

```java
public final void setRate(double permitsPerSecond) {
checkArgument(
    permitsPerSecond > 0.0 && !Double.isNaN(permitsPerSecond), "rate must be positive");
synchronized (mutex()) {
    doSetRate(permitsPerSecond, stopwatch.readMicros());
}
```

在 setRate 时需要对实例对象加锁，调用了 mutex() 方法。

```java
// Can't be initialized in the constructor because mocks don't call the constructor.
@MonotonicNonNull private volatile Object mutexDoNotUseDirectly;

private Object mutex() {
Object mutex = mutexDoNotUseDirectly;
if (mutex == null) {
    synchronized (this) {
    mutex = mutexDoNotUseDirectly;
    if (mutex == null) {
        mutexDoNotUseDirectly = mutex = new Object();
    }
}
return mutex;
}
```

SmoothBursty 类里的 doSetRate 具体实现源码：

```java
@Override
void doSetRate(double permitsPerSecond, double stableIntervalMicros) {
    double oldMaxPermits = this.maxPermits;
    maxPermits = maxBurstSeconds * permitsPerSecond;
    if (oldMaxPermits == Double.POSITIVE_INFINITY) {
    // if we don't special-case this, we would get storedPermits == NaN, below
    storedPermits = maxPermits;
    } else {
    storedPermits =
        (oldMaxPermits == 0.0)
            ? 0.0 // initial state
            : storedPermits * maxPermits / oldMaxPermits;
    }
}
```

### 获取令牌

RateLimiter 提供了两个方法用以获取令牌：acquire 和 tryAcquire，其中 acquire 的返回值是获取令牌成功需要等待的时间，tryAcquire 的返回值是获取令牌是否成功。acquire 方法和 tryAcquire 方法都可以传入需要获取的令牌数量，如果不传，默认需要获取的令牌数量为 1。

先来看看 acquire 方法的实现：

```java
public double acquire() {
    return acquire(1);
}

public double acquire(int permits) {
    // reserve 方法的返回值表示何时能获取令牌
    long microsToWait = reserve(permits);
    // sleep 一段时间，直到能够获取令牌，因此如果不能获取到令牌，acquire 方法会阻塞当前线程
    stopwatch.sleepMicrosUninterruptibly(microsToWait);
    return 1.0 * microsToWait / SECONDS.toMicros(1L);
}

final long reserve(int permits) {
    // permits 必须大于 0
    checkPermits(permits);
    // synchronized 同步锁，用于解决并发问题
    synchronized (mutex()) {
        return reserveAndGetWaitLength(permits, stopwatch.readMicros());
    } 
}

final long reserveAndGetWaitLength(int permits, long nowMicros) {
    long momentAvailable = reserveEarliestAvailable(permits, nowMicros);
    // 如果当前时间已经大于等于了能获取到令牌的时间，需要等待的时间为 0
    return max(momentAvailable - nowMicros, 0);
}

/**
 * 这是一个抽象方法，在 SmoothRateLimiter 中实现，返回能获得 permits 个令牌的时间戳。
 * 对于 SmoothBursty 而言，只需考虑前一个请求透支令牌的影响。
 * 对于 SmoothWarmingUp 而言，还需考虑获取令牌的等待时间。
 */
abstract long reserveEarliestAvailable(int permits, long nowMicros);
```

reserveEarliestAvailable 方法在抽象类 SmoothRateLimiter 中实现，

```java
  @Override
  final long reserveEarliestAvailable(int requiredPermits, long nowMicros) {
    resync(nowMicros);
    long returnValue = nextFreeTicketMicros;
    double storedPermitsToSpend = min(requiredPermits, this.storedPermits);
    double freshPermits = requiredPermits - storedPermitsToSpend;
    long waitMicros =
        storedPermitsToWaitTime(this.storedPermits, storedPermitsToSpend)
            + (long) (freshPermits * stableIntervalMicros);

    this.nextFreeTicketMicros = LongMath.saturatedAdd(nextFreeTicketMicros, waitMicros);
    this.storedPermits -= storedPermitsToSpend;
    return returnValue;
  }
```

tryAcquire 方法的实现：

```java
public boolean tryAcquire() {
    // 默认传入的超时时间是 0
    return tryAcquire(1, 0, MICROSECONDS);
}

public boolean tryAcquire(int permits, long timeout, TimeUnit unit) {
    long timeoutMicros = max(unit.toMicros(timeout), 0);
    checkPermits(permits);
    long microsToWait;
    synchronized (mutex()) {
        long nowMicros = stopwatch.readMicros();
        // 由于传入的超时时间 timeoutMicros 是 0，所以不会阻塞
        if (!canAcquire(nowMicros, timeoutMicros)) {
            return false;
        } else {
            // 和 acquire 共用的是同一个方法
            microsToWait = reserveAndGetWaitLength(permits, nowMicros);
        }
    }
    stopwatch.sleepMicrosUninterruptibly(microsToWait);
    return true;
}

private boolean canAcquire(long nowMicros, long timeoutMicros) {
    return queryEarliestAvailable(nowMicros) - timeoutMicros <= nowMicros;
}

/**
 * 这是一个抽象方法，在 SmoothRateLimiter 中实现，用于记录前一个请求由于透支令牌对当前请求的影响。
 * 即只有在当前时间戳大于该方法的返回值时，才能够消除前一个请求对当前请求的影响，才能正常获取令牌。
 */
abstract long queryEarliestAvailable(long nowMicros);
```

# 参考链接

- [谷歌 Guava 限流工具 RateLimiter](https://zhuanlan.zhihu.com/p/205266820)

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)