---
date: 2025-11-11
updated: 2026-10-28
---

# JDK 24 新特性解析

> **维护说明（2026-10-28）：** 旧稿使用了多个 JDK 23 的 JEP 编号及不正确的特性状态，部分示例与 JDK 24 API 不符。本次依据 Oracle JDK 24 的正式发布资料进行勘误，保留这篇文章的原路径供历史链接继续访问。

JDK 24 已于 **2025 年 3 月 18 日** 发布，是非 LTS 版本。以下以实际纳入 JDK 24 的 JEP 为准，精选后端工程值得关注的变化。

## 1. 语言与 API

| JEP | 特性 | JDK 24 状态 |
| --- | --- | --- |
| [488](https://openjdk.org/jeps/488) | Primitive Types in Patterns、`instanceof` 和 `switch` | 第二次预览 |
| [492](https://openjdk.org/jeps/492) | Flexible Constructor Bodies | 第三次预览 |
| [494](https://openjdk.org/jeps/494) | Module Import Declarations | 第二次预览 |
| [495](https://openjdk.org/jeps/495) | Simple Source Files and Instance Main Methods | 第四次预览 |
| [484](https://openjdk.org/jeps/484) | Class-File API | 正式特性 |
| [485](https://openjdk.org/jeps/485) | Stream Gatherers | 正式特性 |

`Class-File API` 提供标准化的 class 文件解析、生成和转换能力；`Stream Gatherers` 扩展 Stream 的中间操作，适用于部分分组、窗口与状态化处理。

### 1.1 Stream Gatherers：固定窗口

这是 JDK 24 已正式发布的 API，无需 `--enable-preview`。下面的示例演示将 Stream 按每 2 个元素划分为一组：

```java
import java.util.stream.Gatherers;
import java.util.stream.Stream;

public class GathererDemo {
    public static void main(String[] args) {
        var windows = Stream.of(1, 2, 3, 4, 5)
            .gather(Gatherers.windowFixed(2))
            .toList();
        System.out.println(windows); // [[1, 2], [3, 4], [5]]
    }
}
```

运行方式：`javac GathererDemo.java && java GathererDemo`。与手工维护索引或可变容器相比，Gatherer 可以作为 Stream 管道中的中间操作进行组合；窗口大小很大时仍需评估内存使用。

参考：[JDK 24 Gatherers API](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/util/stream/Gatherers.html)。

## 2. 并发、GC 与性能

| JEP | 特性 | JDK 24 状态 |
| --- | --- | --- |
| [487](https://openjdk.org/jeps/487) | Scoped Values | 第四次预览 |
| [499](https://openjdk.org/jeps/499) | Structured Concurrency | 第四次预览 |
| [489](https://openjdk.org/jeps/489) | Vector API | 第九次孵化 |
| [490](https://openjdk.org/jeps/490) | ZGC: Remove the Non-Generational Mode | 正式变更 |
| [491](https://openjdk.org/jeps/491) | Synchronize Virtual Threads without Pinning | 正式特性 |
| [483](https://openjdk.org/jeps/483) | Ahead-of-Time Class Loading & Linking | 正式特性 |
| [450](https://openjdk.org/jeps/450) | Compact Object Headers | 实验性 |
| [475](https://openjdk.org/jeps/475) | Late Barrier Expansion for G1 | 正式变更 |

其中值得注意：

- **ZGC** 移除了非分代模式，不是简单的「把分代模式设为默认」；启用 ZGC 时应结合 GC 日志验证分代回收效果。
- **虚拟线程** 在 `synchronized` 场景下的载体线程 pinning 问题得到重要改善，但仍应结合实际阻塞场景进行测试。
- **AOT Class Loading & Linking** 关注类加载与链接的缓存，不等于将 Java 程序编译为 GraalVM Native Image。
- **Compact Object Headers** 在 JDK 24 仍属实验性特性，需要显式开启 `-XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders`，不应默认假设已经启用。
- **结构化并发** 在 JDK 24 仍是第四次预览；不同版本的预览 API 不可直接混用。

## 3. 安全相关与迁移提醒

| JEP | 内容 |
| --- | --- |
| [478](https://openjdk.org/jeps/478) | Key Derivation Function API（预览） |
| [472](https://openjdk.org/jeps/472) | Prepare to Restrict the Use of JNI |
| [486](https://openjdk.org/jeps/486) | Permanently Disable the Security Manager |
| [498](https://openjdk.org/jeps/498) | Warn upon Use of Memory-Access Methods in `sun.misc.Unsafe` |

这些变更可能影响老旧框架、JNI 依赖和使用不受支持内部 API 的系统。建议先在测试环境检查启动参数、警告日志与依赖兼容性。

## 4. 本次勘误

- **JEP 467（Markdown Documentation Comments）属于 JDK 23，不是 JDK 24 的新增正式特性。**
- JDK 24 的结构化并发应对应 **JEP 499**，不是 JEP 480。
- JDK 24 的 Scoped Values 应对应 **JEP 487**，不是 JEP 481。
- JDK 24 的模块导入声明应对应 **JEP 494**，不是 JEP 476。
- JDK 24 的 Flexible Constructor Bodies 应对应 **JEP 492**，不是 JEP 482。
- ZGC 移除非分代模式对应 **JEP 490**，不能误写为 JEP 474。

## 官方参考

- [Oracle JDK 24 Release Notes](https://www.oracle.com/java/technologies/javase/24-relnote-issues.html)
- [JDK 24 Significant Changes](https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html)
- [OpenJDK JDK 24 项目清单](https://openjdk.org/projects/jdk/24/)
