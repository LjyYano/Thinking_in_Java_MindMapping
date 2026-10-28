---
date: 2025-11-11
updated: 2026-10-28
---

# JDK 25 新特性解析

> **维护说明（2026-10-28）：** 原稿将部分 JDK 23 / 24 的 JEP 编号、状态误写为 JDK 25 特性，并包含 Java 不支持的 `public lazy class` 示例。本次根据 Oracle JDK 25 发布说明重新校对。**本文展示主要特性，不替代完整的官方 JEP 清单。**

JDK 25 已于 **2025 年 9 月 16 日** 正式发布，是 Oracle 提供长期支持（LTS）的版本之一。对于正在运行 Java 17 / 21 的后端项目，值得优先关注并发、启动性能、JFR 和安全 API 的变化。

## 1. 语言特性

| JEP | 特性 | JDK 25 状态 | 重点 |
| --- | --- | --- | --- |
| [507](https://openjdk.org/jeps/507) | Primitive Types in Patterns、`instanceof` 和 `switch` | 第三次预览 | 原始类型参与模式匹配 |
| [511](https://openjdk.org/jeps/511) | Module Import Declarations | 正式特性 | `import module java.sql;` 一次导入模块导出的包 |
| [512](https://openjdk.org/jeps/512) | Compact Source Files and Instance Main Methods | 正式特性 | 简化小程序入口 |
| [513](https://openjdk.org/jeps/513) | Flexible Constructor Bodies | 正式特性 | 允许在 `super(...)` 前执行符合约束的语句 |

其中，模块导入声明适合减少示例程序中的导入样板代码。它不会自动加载任意模块，也不会绕过 Java 模块系统的导出限制。

## 2. 并发与运行时

| JEP | 特性 | JDK 25 状态 | 重点 |
| --- | --- | --- | --- |
| [505](https://openjdk.org/jeps/505) | Structured Concurrency | 第五次预览 | 将相关子任务视作一个有生命周期的工作单元 |
| [506](https://openjdk.org/jeps/506) | Scoped Values | 正式特性 | 在线程及子任务间共享有作用域的不可变数据 |
| [502](https://openjdk.org/jeps/502) | Stable Values | 预览 | 为延迟构造且只初始化一次的数据提供 API |
| [519](https://openjdk.org/jeps/519) | Compact Object Headers | 正式特性（默认关闭） | 可选择性减少对象头占用 |
| [514](https://openjdk.org/jeps/514) | AOT Command-Line Ergonomics | 正式特性 | 简化 AOT 缓存使用 |
| [515](https://openjdk.org/jeps/515) | AOT Method Profiling | 正式特性 | 利用历史方法画像改善预热 |

**注意：** 结构化并发在 JDK 25 **仍是预览 API**，不能称为「正式发布」。同时，其 API 与前几轮预览存在差异；旧的 `StructuredTaskScope.ShutdownOnFailure` 示例不应直接视为 JDK 25 的可编译示例。应以 [JDK 25 结构化并发文档](https://docs.oracle.com/en/java/javase/25/core/structured-concurrency.html) 为准。

## 3. 安全、监控与其他特性

| JEP | 特性 | JDK 25 状态 |
| --- | --- | --- |
| [470](https://openjdk.org/jeps/470) | PEM Encodings of Cryptographic Objects | 预览 |
| [510](https://openjdk.org/jeps/510) | Key Derivation Function API | 正式特性 |
| [508](https://openjdk.org/jeps/508) | Vector API | 第十次孵化 |
| [509](https://openjdk.org/jeps/509) | JFR CPU-Time Profiling | 实验性 |
| [518](https://openjdk.org/jeps/518) | JFR Cooperative Sampling | 正式特性 |
| [520](https://openjdk.org/jeps/520) | JFR Method Timing & Tracing | 正式特性 |

GC 方面还有 [JEP 521：Generational Shenandoah](https://openjdk.org/jeps/521)，需按 JDK 实现与实际业务负载评估。其他平台变更请查阅 [官方 JDK 25 项目清单](https://openjdk.org/projects/jdk/25/)。

## 4. 典型示例（Java 25）

以下选取已转为正式特性的 API / 语法。每个示例独立存为对应类名的 `.java` 文件；无需 `--enable-preview`。

### 4.1 模块导入声明（JEP 511）

```java
import module java.base;

public class ModuleImportDemo {
    public static void main(String[] args) {
        List<String> words = List.of("Java", "Agent");
        System.out.println(words.stream().map(String::toLowerCase).toList());
    }
}
```

`import module java.base;` 可导入 `java.base` 模块导出包内的公共类型。大型项目若同时导入多个模块，仍应注意重名类型带来的歧义。

### 4.2 紧凑源文件及实例 main 方法（JEP 512）

```java
// Hello.java
void main() {
    IO.println("Hello, Java 25");
}
```

执行 `java Hello.java`。**注意：JDK 25 中应调用 `IO.println(...)`，不应将旧预览版本的裸 `println(...)` 示例当作正式 API 使用。**

### 4.3 灵活构造函数体（JEP 513）

```java
import java.math.BigInteger;

public class PositiveBigInteger extends BigInteger {
    public PositiveBigInteger(long value) {
        if (value <= 0) {
            throw new IllegalArgumentException("value must be positive");
        }
        super(Long.toString(value));
    }
}
```

`super(...)` 调用之前可验证参数，但前置代码不能任意访问尚未构造好的实例；具体约束参见 [Oracle JDK 25 文档](https://docs.oracle.com/en/java/javase/25/language/flexible-constructor-bodies.html)。

### 4.4 Scoped Values（JEP 506）

```java
public class ScopedDemo {
    private static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();

    public static void main(String[] args) {
        ScopedValue.where(TRACE_ID, "trace-001")
            .run(() -> printTrace());
    }

    private static void printTrace() {
        System.out.println(TRACE_ID.get()); // trace-001
    }
}
```

它适合传递一次请求范围内的只读上下文，不代表能无条件替换所有可变的 `ThreadLocal` 使用场景。

### 4.5 Compact Object Headers（JEP 519）

JDK 25 将紧凑对象头转为产品特性，但**默认仍未开启**。可在压测环境通过以下 JVM 参数开启并比较内存使用及性能：

```bash
java -XX:+UseCompactObjectHeaders -jar app.jar
```

不再需要 JDK 24 的 `-XX:+UnlockExperimentalVMOptions`。不要把这个优化当成所有工作负载都会获益的默认设置。

## 5. 升级与使用建议

1. 评估时先区分**正式特性、预览特性、实验性特性和孵化模块**。预览功能需要按官方文档显式启用，且未来版本可能调整 API。
2. 结构化并发和 Scoped Values 对多任务后端服务值得关注，但不要把 JDK 21、24 的预览代码未经修改地复制到 JDK 25。
3. 先进行依赖、JVM 参数、GC 与压测回归，再决定升级生产环境。LTS 不意味着旧依赖一定兼容。

## 6. 本次勘误

旧版文章中的以下描述不正确，已从正文移除：

- **JEP 475 不是「延迟初始化类」**：它是 JDK 24 的 G1 Late Barrier Expansion；Java 不存在 `public lazy class` 语法。
- **JEP 480 不是 JDK 25 正式结构化并发**：JDK 25 对应 JEP 505（第五次预览）。
- **JEP 481 不是 JDK 25 的正式 Scoped Values**：JDK 25 对应 JEP 506。
- **JEP 476、477、479 等旧编号不可直接当作 JDK 25 对应特性编号**：应以 JEP 511、512、513 等最终版本为准。

## 官方参考

- [Oracle JDK 25 Release Notes](https://www.oracle.com/java/technologies/javase/25-relnote-issues.html)
- [JDK 25 Significant Changes](https://docs.oracle.com/en/java/javase/25/migrate/significant-changes-jdk-25.html)
- [OpenJDK JDK 25 项目清单](https://openjdk.org/projects/jdk/25/)
