---
date: 2021-12-06
---


- [Serving different use cases](#serving-different-use-cases)
- [The progress since JDK 8](#the-progress-since-jdk-8)
- [Throughput](#throughput)
- [Latency](#latency)
- [Footprint](#footprint)
- [Time to upgrade](#time-to-upgrade)
- [More details](#more-details)

文章原文链接：https://kstefanj.github.io/2021/11/24/gc-progress-8-17.html

JDK 17 has been out for a few months and it’s not just packed with new language features. The **performance boost** compared to older JDK versions is also really **significant**. It becomes especially clear when compared to the previous LTS releases, JDK 8 and JDK 11. Much of the improved performance comes from **new features and optimizations** in the [JVM](https://docs.oracle.com/en/java/javase/17/vm/java-virtual-machine-technology-overview.html) and in this post the focus will be on the **improvements done in the area of garbage collection**.

I recently gave a talk focusing on new features in **[G1 since JDK 8](https://inside.java/2021/10/11/p99-g1-to-infinity-and-beyond/)** and this post will expand this to also cover the progress made in **Parallel GC** and **ZGC**. We also have a fourth supported collector, **Serial GC**, but it is not included in this comparison. Serial is a stable collector that has low overhead, but the benchmark used below requires a high performing GC to work well.

## Serving different use cases

Deciding which garbage collector to use is not always obvious. It’s important to understand that to make the correct choice you first need to figure out what your **main goals** are. Often goals are to optimize for throughput, latency and/or footprint. The optimal solution would of course be to optimize for all of the above and get the best possible performance in every situation. The collectors strive to be as optimal as possible from every aspect, but they are designed to make **different tradeoffs** to support **different use-cases**.

A quick summary of what we mean by improving in the different areas:

- **Throughput** – lower the GC’s impact on the total number of transactions that can be completed in a set amount of time
- **Latency** – lower the GC’s impact on any single transaction
- **Footprint** – lower the additional resources used by the GC

Doing different tradeoffs doesn’t mean that the collectors can’t be improved from every aspect. When improving the collectors, one big part is to make sure that the tradeoffs are done as **efficiently** as possible. Another good approach to improve across the board is to **re-evaluate old design decisions** and come up with better solutions.

## The progress since JDK 8

Looking at the progress made since JDK 8 we see that all collectors have **improved** in more or less **every aspect**. To better show the progress the comparisons below are using normalized scores **comparing the collectors individually**, instead of looking at raw scores. I’ve been using [SPECjbb® 2015](https://www.spec.org/jbb2015/)[1](https://kstefanj.github.io/2021/11/24/gc-progress-8-17.html#fn:spec) with a 16 GB heap to compare the collectors. This is a well-known and stable benchmark that doesn’t only focus on GC performance, so the results will also show **progress for the whole Java platform**. The benchmark has a few different modes and it produces both a throughput metric and a latency metric. The latency metric is measuring throughput under response time constraints.

For pause time comparisons I’ve run the benchmark with a fixed load for an hour. This way all collectors are stressed at the same level regardless of their end score.

One last note before looking at the score charts. ZGC was introduced in JDK 11 ([production ready since JDK 15](https://openjdk.java.net/jeps/377)) so we only have two data points for ZGC compared to three for G1 and Parallel.

## Throughput

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211206140408.png?x-oss-process=style/yano)

Looking at the throughput metric we see that all collectors have **improved significantly** compared to older releases. ZGC is the one making the biggest improvement in this area. G1 and Parallel still have better raw throughput in this setup but scaling up the heap, ZGC closes this gap.

When it comes to this metric, we should also keep in mind that we are not only measuring GC performance. Other parts of the Java platform, for example the JIT compiler, also contribute to these improvements.

## Latency

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211206140507.png?x-oss-process=style/yano)

From a latency perspective the results have improved even more. Here we can see all the benefits of the work put into making **GC pauses shorter**. When it comes to this metric a lot of the improvements can really be attributed to what has been improved in the GCs.

G1 shows the best progress when considering this metric. ZGC has also improved a lot from a latency perspective. The most impressive part is not seen in this chart because the benchmark is measuring application latencies. ZGC does such a good job keeping the pauses short that we start to see other things affecting the latency score. If we instead look at how the **pause times have improved**, we can see that there has been some **extraordinary work going on in ZGC**.

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211206140430.png?x-oss-process=style/yano)

Here we look at raw numbers (because normalized pause-times are a bit strange) and as we can see ZGC in JDK 17 is way below its goal of **sub-millisecond pause times**. G1, with its goal of keeping a **balance between latency and throughput**, keeps well below its default pause time target of 200 ms. This chart also includes an extra bar to quickly show how the different collectors handle scalability. ZGC is designed to have pause times that do not scale with the heap size, and we clearly see that this is the case when the heap is enlarged to 128 GB. G1 handles the larger heap better than Parallel from a pause time perspective because it has the logic to keep the pause time target.

## Footprint

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211206140521.png?x-oss-process=style/yano)

This chart compares the **peak native memory overhead** of the three different collectors. Since both Parallel and ZGC have been pretty stable from this perspective, it makes more sense to look at raw numbers here as well. We can see that **G1 has really improved** in this area and the main reason for this is all features and enhancements to make **remembered set management more efficient**.

Even if the other collectors have not decreased their overhead, we should still remember that they have improved in the other areas without having to use additional memory.

## Time to upgrade

The **overall performance in JDK 17** compared to older versions is **significantly better** regardless of which collector you use. If you are still on JDK 8 and plan to upgrade, it might be a good time to **re-evaluate which GC to use**. In JDK 8 **Parallel was the default**, but this was **changed to G1 in JDK 9**. Since then G1 has improved at a higher rate than Parallel, but there are still use-cases where Parallel is the best choice. With the introduction of ZGC (production ready since JDK 15) there is also a third high performing alternative to put into the equation.

## More details

If you want more details around what’s been done to achieve those great results, I recommend reading [Per Liden’s blog](https://malloc.se/) focusing on ZGC and [Thomas Schatzl’s blog](https://tschatzl.github.io/) focusing on G1 (and a bit on Parallel).

For general news and insights from the Java team at Oracle make sure to check out [inside.java](https://inside.java/).