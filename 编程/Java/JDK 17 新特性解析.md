---
date: 2021-10-04
---


- [前言](#前言)
- [新特性概览](#新特性概览)
- [JEP 406：switch 的模式匹配（预览）(JDK-8213076)](#jep-406switch-的模式匹配预览jdk-8213076)
- [JEP 409：密封类 (JDK-8260514)](#jep-409密封类-jdk-8260514)
  - [为什么需要此特性](#为什么需要此特性)
  - [特性描述](#特性描述)
- [JEP 382：新的 macOS 渲染管道 (JDK-8238361)](#jep-382新的-macos-渲染管道-jdk-8238361)
- [JEP 356：增强型伪随机数生成器 (JDK-8193209)](#jep-356增强型伪随机数生成器-jdk-8193209)
- [Ideal Graph Visualizer 的现代化 (JDK-8254145)](#ideal-graph-visualizer-的现代化-jdk-8254145)
- [“New API”的新页面和改进的“Deprecated”页 (JDK-8263468)](#new-api的新页面和改进的deprecated页-jdk-8263468)
- [错误消息中的源详细信息 (JDK-8267126)](#错误消息中的源详细信息-jdk-8267126)
- [JEP 412：外部函数和内存 API（孵化）(JDK-8265033)](#jep-412外部函数和内存-api孵化jdk-8265033)
- [控制台字符集 API(JDK-8264208)](#控制台字符集-apijdk-8264208)
- [用于反序列化的 JDK Flight Recorder 事件 (JDK-8261160)](#用于反序列化的-jdk-flight-recorder-事件-jdk-8261160)
- [JEP 415：实现特定于上下文的反序列化过滤器 (JDK-8264859)](#jep-415实现特定于上下文的反序列化过滤器-jdk-8264859)
- [本机字符编码名称的系统属性 (JDK-8265989)](#本机字符编码名称的系统属性-jdk-8265989)
- [添加 java.time.InstantSource (JDK-8266846)](#添加-javatimeinstantsource-jdk-8266846)
- [十六进制格式和解析实用程序 (JDK-8251989)](#十六进制格式和解析实用程序-jdk-8251989)
- [实验 Compiler Blackholes 支持 (JDK-8259316)](#实验-compiler-blackholes-支持-jdk-8259316)
- [HotSpot JVM 中的新类层次结构分析实现 (JDK-8266074)](#hotspot-jvm-中的新类层次结构分析实现-jdk-8266074)
- [JEP 391: macOS/AArch64 端口 (JDK-8251280)](#jep-391-macosaarch64-端口-jdk-8251280)
- [统一日志支持异步日志刷新 (JDK-8229517)](#统一日志支持异步日志刷新-jdk-8229517)
- [ARM 上的 macOS 早期访问可用 (JDK-8266858)](#arm-上的-macos-早期访问可用-jdk-8266858)
- [支持在 Keytool -genkeypair 命令中指定签名者 (JDK-8260693)](#支持在-keytool--genkeypair-命令中指定签名者-jdk-8260693)
- [SunJCE 提供程序通过 AES 密码支持 KW 和 KWP 模式 (JDK-8248268)](#sunjce-提供程序通过-aes-密码支持-kw-和-kwp-模式-jdk-8248268)
- [新 SunPKCS11 配置属性 (JDK-8240256)](#新-sunpkcs11-配置属性-jdk-8240256)
- [具有系统属性的可配置扩展 (JDK-8217633)](#具有系统属性的可配置扩展-jdk-8217633)
- [包摘要页面上的“Related Packages”(JDK-8260388)](#包摘要页面上的related-packagesjdk-8260388)
- [参考链接](#参考链接)
- [GitHub 项目](#github-项目)

# 前言

JDK 17 已经在 2021 年 9 月 14 日发布了，JDK 17 与 JDK 8、JDK 11 一样是一个 LTS 版本，意义非凡。JDK 13~16 的特性可以参考如下文章：

- [JDK 13 新特性简介](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2019-07-31%20JDK%2013%20%E6%96%B0%E7%89%B9%E6%80%A7%E7%AE%80%E4%BB%8B.md)
- [JDK 14 即将发布，你所要知道的都在这里！](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-01-07%20JDK%2014%E5%8D%B3%E5%B0%86%E5%8F%91%E5%B8%83%EF%BC%8C%E4%BD%A0%E6%89%80%E8%A6%81%E7%9F%A5%E9%81%93%E7%9A%84%E9%83%BD%E5%9C%A8%E8%BF%99%E9%87%8C%EF%BC%81.md)
- [JDK 15 已发布，你所要知道的都在这里！](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-09-19%20JDK%2015%E5%B7%B2%E5%8F%91%E5%B8%83%EF%BC%8C%E4%BD%A0%E6%89%80%E8%A6%81%E7%9F%A5%E9%81%93%E7%9A%84%E9%83%BD%E5%9C%A8%E8%BF%99%E9%87%8C%EF%BC%81.md)
- [Java 16 正式发布，新特性一一解析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-03-21%20Java%2016%20%E6%AD%A3%E5%BC%8F%E5%8F%91%E5%B8%83%EF%BC%8C%E6%96%B0%E7%89%B9%E6%80%A7%E4%B8%80%E4%B8%80%E8%A7%A3%E6%9E%90.md)

# 新特性概览

详情可参考 [JDK 17](https://openjdk.java.net/projects/jdk/17/)，所有特性包括：

306:	Restore Always-Strict Floating-Point Semantics
356:	Enhanced Pseudo-Random Number Generators
382:	New macOS Rendering Pipeline
391:	macOS/AArch64 Port
398:	Deprecate the Applet API for Removal
403:	Strongly Encapsulate JDK Internals
406:	Pattern Matching for switch (Preview)
407:	Remove RMI Activation
409:	Sealed Classes
410:	Remove the Experimental AOT and JIT Compiler
411:	Deprecate the Security Manager for Removal
412:	Foreign Function & Memory API (Incubator)
414:	Vector API (Second Incubator)
415:	Context-Specific Deserialization Filters

# JEP 406：switch 的模式匹配（预览）(JDK-8213076)

通过 switch 表达式和语句的模式匹配，以及模式语言的扩展，增强 Java 编程语言。将模式匹配扩展到 switch 允许对表达式进行测试，每个模式都有特定的操作，以便可以简洁而安全地表达复杂的面向数据的查询。

在新版 JDK 中，我们可以使用如下代码：

```java
static String formatter(Object o) {
    String formatted = "unknown";
    if (o instanceof Integer i) {
        formatted = String.format("int %d", i);
    } else if (o instanceof Long l) {
        formatted = String.format("long %d", l);
    } else if (o instanceof Double d) {
        formatted = String.format("double %f", d);
    } else if (o instanceof String s) {
        formatted = String.format("String %s", s);
    }
    return formatted;
}
```

```java
static String formatterPatternSwitch(Object o) {
    return switch (o) {
        case Integer i -> String.format("int %d", i);
        case Long l    -> String.format("long %d", l);
        case Double d  -> String.format("double %f", d);
        case String s  -> String.format("String %s", s);
        default        -> o.toString();
    };
}
```

```java
static void testFooBar(String s) {
    if (s == null) {
        System.out.println("oops!");
        return;
    }
    switch (s) {
        case "Foo", "Bar" -> System.out.println("Great");
        default           -> System.out.println("Ok");
    }
}
```

```java
static void testFooBar(String s) {
    switch (s) {
        case null         -> System.out.println("Oops");
        case "Foo", "Bar" -> System.out.println("Great");
        default           -> System.out.println("Ok");
    }
}
```

```java
static void testTriangle(Shape s) {
    switch (s) {
        case Triangle t && (t.calculateArea() > 100) ->
            System.out.println("Large triangle");
        case Triangle t ->
            System.out.println("Small triangle");
        default ->
            System.out.println("Non-triangle");
    }
}
```

详情可参考 [JEP 406: Pattern Matching for switch (Preview)](https://openjdk.java.net/jeps/406)

# JEP 409：密封类 (JDK-8260514)

密封类（Sealed Class）已添加到 Java 语言中。密封类和接口限制了哪些其他类或接口可以扩展或实现它们。

密封类由 JEP 360 并在 JDK 15 中作为预览功能交付。它们再次被提出，并进行了改进，由 JEP 397 并在 JDK 16 中作为预览功能提供。现在，在 JDK 17 中，密封类正在最终确定，与 JDK 16 没有任何更改。

## 为什么需要此特性
在 Java 语言中，代码的重用是通过类的继承实现的：多个子类可以继承同一个超类（并重用超类的方法）。但是重用代码并不是类层次结构的唯一目的，有时类层次结构仅仅是对某个领域的建模。以这种方式使用类层次结构时，限制子类集合可以简化建模。

比如在图形库中，Shape 类的开发者可能只希望有限个数的类扩展 Shape 类，开发者并不想为未知子类编写防御代码。以前的 Java 并不会限制 Shape 类的扩展属性，Shape 类可以拥有任意数量的子类。在封闭类（Sealed Classes）中，类层次结构是封闭的，但是代码仍然可以在有限范围内重用。

## 特性描述

通过 sealed 修饰符将一个类声明为密封类，permits 子句指定允许扩展密封类的类。例如下面的 Shape 类声明指定了三个可扩展的子类。

```java
package com.example.geometry;

public abstract sealed class Shape
    permits Circle, Rectangle, Square {...}
```

在子类数量很少时，在密封类的源文件中声明子类会很方便。当以这种方式声明子类时，密封类可以省略 allows 子句，同时 Java 编译器将从源文件中推断允许的子类。例如下面的例子：

```java
package com.example.geometry;

abstract sealed class Shape {...}
... class Circle    extends Shape {...}
... class Rectangle extends Shape {...}
... class Square    extends Shape {...}
```

密封类可以让代码更简洁，代码可以明确推断出所有允许的子类。比如传统的 if-else 和 instanceof 代码编译器分析起来很困难，无法确定子句是否覆盖了所有允许的子类。下面的方法会导致编译期错误：

```java
int getCenter(Shape shape) {
    if (shape instanceof Circle) {
        return ... ((Circle)shape).center() ...
    } else if (shape instanceof Rectangle) {
        return ... ((Rectangle)shape).length() ...
    } else if (shape instanceof Square) {
        return ... ((Square)shape).side() ...
    }
}
```

在之后支持模式匹配的版本中，编译器可以直接推断出 Shape 所有允许的子类，不需要 default 语句。此外，如果缺少子类的任意一个，编译器就会报错。

```java
int getCenter(Shape shape) {
    return switch (shape) {
        case Circle c    -> ... c.center() ...
        case Rectangle r -> ... r.length() ...
        case Square s    -> ... s.side() ...
    };
}
```

# JEP 382：新的 macOS 渲染管道 (JDK-8238361)

Swing API 用于渲染的 Java 2D API 现在可以使用新的 Apple Metal 加速渲染 API 给 macOS。

目前默认情况下，这是禁用的，因此渲染仍然使用 OpenGL API，这些 API 被 Apple 弃用，但仍然可用和支持。

# JEP 356：增强型伪随机数生成器 (JDK-8193209)

core-libs/java.util 为伪随机数生成器（PRNG）提供新的接口类型和实现，包括可跳转的 PRNG 和一类额外的可拆分 PRNG 算法（LXM）。

# Ideal Graph Visualizer 的现代化 (JDK-8254145)

Ideal Graph Visualizer（IGV）是一个可视化和交互式地探索 HotSpot VM C2 即时（JIT）编译器中使用的中间表示的工具，已经现代化。增强功能包括：

- 支持在最多 JDK 15 上运行 IGV（IGV 底层 NetBeans 平台支持的最新版本）
- 更快的、基于 Maven 的 IGV 构建系统
- 块形成、组删除和节点跟踪的稳定
- 默认过滤器中更直观的着色和节点分类
- 具有更自然默认行为的排名快速节点搜索

现代化的 IGV 部分兼容从早期 JDK 版本生成的图形。它支持基本功能，如图形加载和可视化，但辅助功能，如节点聚类和着色可能会受到影响。

# “New API”的新页面和改进的“Deprecated”页 (JDK-8263468)

JavaDoc 现在可以生成一个页面，总结 API 中最近的更改。要包括的最近版本的列表是使用 --since 命令行选项指定的。这些值用于查找具有匹配@since 的声明，因为要包含在新页面上的标记。--since-label 命令行选项提供了要在“New API”页面标题中使用的文本。

在总结已弃用项目的页面上，您可以查看按已弃用项目的版本分组的项目。

# 错误消息中的源详细信息 (JDK-8267126)

当 JavaDoc 报告输入源文件中的问题时，它将以类似编译器（javac）诊断消息的方式显示问题的源行，以及包含指向该行位置的插入符号（^）的行。

此外，日志记录和其他“信息”消息现在写入标准错误流，留下标准输出流用于命令行选项特别请求的输出，如命令行帮助。

# JEP 412：外部函数和内存 API（孵化）(JDK-8265033)

引入一个 API,Java 程序可以通过该 API 与 Java 运行时之外的代码和数据互操作。通过有效地调用外部函数（即 JVM 外部的代码），并通过安全地访问外部内存（即不由 JVM 管理的内存），该 API 使 Java 程序能够调用本机库并处理本机数据，而不会有 JNI 的脆弱性和危险。

有关更多详细信息，请参阅 JEP 412

# 控制台字符集 API(JDK-8264208)

java.io.Console 已更新，以定义一个新方法，该方法返回控制台的 Charset。返回的 Charset 可能与 Charset.defaultCharset() 方法返回的 Charset 不同。例如，它返回 IBM437，而 Charset.defaultCharset() 在 Windows (en-US) 上返回 windows-1252。

# 用于反序列化的 JDK Flight Recorder 事件 (JDK-8261160)

现在可以使用 JDK Flight Recorder (JFR) 监控对象的反序列化。当启用 JFR 且 JFR 配置包括反序列化事件时，每当运行程序尝试反序列化对象时，JFR 将发出事件。反序列化事件名为 jfr.Derialization，默认情况下禁用。反序列化事件包含序列化筛选器机制使用的信息；请参阅对象输入筛选器规范。此外，如果启用了过滤器，JFR 事件指示过滤器是接受还是拒绝对象的反序列化。有关如何使用 JFR 反序列化事件的更多信息，请参阅文章监控反序列化提高应用安全性。有关使用和配置 JFR 的参考信息，请参阅 JFR 运行时指南和 JFR 命令参考 JDK 任务控制文件的章节。

# JEP 415：实现特定于上下文的反序列化过滤器 (JDK-8264859)

JEP 415：特定于上下文的反序列化过滤器允许应用程序通过 JVM 范围的过滤器工厂配置特定于上下文的和动态选择的反序列化过滤器，该工厂被调用以为每个单独的反序列化操作选择过滤器。

用于序列化过滤的 Java 核心库开发人员指南介绍了用例，并提供了示例。

# 本机字符编码名称的系统属性 (JDK-8265989)

引入了一个新的系统属性本机。encode。此系统属性提供基础主机环境的字符编码名称。例如，它通常在 Linux 和 macOS 平台中具有 UTF-8，在 Windows (en-US) 中具有 Cp1252。请参阅 https://bugs.openjdk.java.net... 了解更多详细信息。

# 添加 java.time.InstantSource (JDK-8266846)

引入了一个新的接口 java.time.InstantSource。此接口是 java.time.Clock 的抽象，只关注当前时刻，不引用时区。

# 十六进制格式和解析实用程序 (JDK-8251989)

java.util.HexFormat 为基元类型和字节数组提供十六进制和十六进制之间的转换。分隔符、前缀、后缀和大写或小写的选项由返回 HexFormat 实例的工厂方法提供。

# 实验 Compiler Blackholes 支持 (JDK-8259316)

增加了对 Compiler Blackholes 的实验支持。这些对于低级基准测试非常有用，以避免关键路径上的死代码消除，而不影响基准性能。当前的支持以 CompileCommand 的形式实现，可访问为-XX:CompileCommand=blackhole,，并计划最终将其毕业到公共 API。

JMH 已经能够在指示/可用时自动检测和使用此设施。有关后续步骤，请查阅 JMH 文档。

# HotSpot JVM 中的新类层次结构分析实现 (JDK-8266074)

HotSpot JVM 中引入了一个新的类层次结构分析实现。它的特点是对抽象和默认方法的增强处理，从而改进了 JIT 编译器所做的内联决策。新实现将取代原始实现，并在默认情况下打开。

为了帮助诊断与新实现相关的可能问题，可以通过指定 -XX:+UnlockDiagnosticVMOptions -XX:-UseVtableBasedCHA 命令行标志来打开原始实现。

原始实现可能会在未来的版本中删除。

# JEP 391: macOS/AArch64 端口 (JDK-8251280)

macOS 11.0 现在支持 AArch64 体系结构。此 JEP 在 JDK 中实现了对 macos-aarch64 平台的支持。添加的功能之一是支持 W^X（write xor execute）内存。它仅对 macos-aarch64 启用，并可以在某些时候扩展到其他平台。JDK 可以在英特尔计算机上交叉编译，也可以在基于 Apple M1 的计算机上编译。

有关更多详细信息，请参见 JEP 391

# 统一日志支持异步日志刷新 (JDK-8229517)

为了避免使用统一日志记录的线程中出现不希望的延迟，用户现在可以请求统一日志记录系统在异步模式下运行。这可以通过传递命令行选项-Xlog:async 来完成。在异步日志记录模式下，日志站点将所有日志记录消息入队到缓冲区。独立线程负责将它们刷新到相应的输出。中间缓冲区是有界的。缓冲区耗尽时，入队消息将被丢弃。用户可以使用命令行选项-XX:AsyncLogBufferSize=. 来控制中间缓冲区的大小。

# ARM 上的 macOS 早期访问可用 (JDK-8266858)

新的 macOS 现在可用于 ARM 系统。ARM 端口的行为应与英特尔端口类似。没有已知的功能差异。在 macOS 上报告问题时，请指定是使用 ARM 还是 x64。

# 支持在 Keytool -genkeypair 命令中指定签名者 (JDK-8260693)

-signer 和-signerkeypass 选项已添加到 keytool 实用程序的-genkey 对命令中。-signer 选项指定签名者的私钥条目的密钥库别名，-signerkeypass 选项指定用于保护签名者私钥的密码。这些选项允许 keytool -genkey 对使用签名者的私钥对证书进行签名。这对于生成具有密钥协商算法作为公钥算法的证书特别有用。

# SunJCE 提供程序通过 AES 密码支持 KW 和 KWP 模式 (JDK-8248268)

SunJCE 提供程序已得到增强，以支持 AES 密钥换行算法（RFC 3394）和带填充算法的 AES 密钥换行算法（RFC 5649）。在早期版本中，SunJCE 提供程序在“AESWrap”密码算法下支持 RFC 3394，该算法只能用于包装和解包装密钥。通过此增强，增加了两种分组密码模式，KW 和 KWP，支持使用 AES 进行数据加密/解密和密钥包装/解包装。有关更多详细信息，请查看“JDK 提供程序文档”指南的“SunJCE 提供程序”部分。

# 新 SunPKCS11 配置属性 (JDK-8240256)

SunPKCS11 提供程序添加了新的提供程序配置属性，以更好地控制本机资源的使用。SunPKCS11 提供程序使用本机资源以便与本机 PKCS11 库一起工作。为了管理和更好地控制本机资源，添加了额外的配置属性，以控制清除本机引用的频率，以及是否在注销后销毁基础 PKCS11 令牌。

SunPKCS11 提供程序配置文件的 3 个新属性是：

destroyTokenAfterLogout （布尔值，默认值为 false）如果设置为 true，则在 SunPKCS11 提供程序实例上调用 java.security.AuthProvider.logout() 时，基础令牌对象将被销毁，资源将被释放。这基本上会在 logout() 调用后使 SunPKCS11 提供程序实例不可用。请注意，不应将此属性设置为 true 的 PKCS11 提供程序添加到系统提供程序列表中，因为提供程序对象在 logout() 方法调用后不可用。

cleaner.shortInterval（整数，默认值为 2000，以毫秒为单位）这定义了在繁忙期间清除本机引用的频率，即 cleaner 线程应多久处理队列中不再需要的本机引用以释放本机内存。请注意，cleaner 线程将在 200 次失败尝试后切换到“longInterval”频率，即在队列中找不到引用时。

cleaner.longInterval（整数，默认值为 60000，以毫秒为单位）这定义了在非繁忙期间检查本机引用的频率，即 cleaner 线程应检查队列中的本机引用的频率。请注意，如果检测到用于清理的本机 PKCS11 引用，cleaner 线程将切换回“短间隔”值。

# 具有系统属性的可配置扩展 (JDK-8217633)

已添加两个新的系统属性。系统属性 jdk.tls.client.disableExts 用于禁用客户端中使用的 TLS 扩展。系统属性 jdk.tls.server.disableExts 用于禁用服务器中使用的 TLS 扩展。如果禁用了扩展，则在握手消息中既不会生成也不会处理扩展。

属性字符串是在 IANA 文档中注册的逗号分隔的标准 TLS 扩展名称列表（例如，server_name、status_request 和签名_algorithms_cert）。请注意，扩展名区分大小写。未知、不支持、拼写错误和重复的 TLS 扩展名称令牌将被忽略。

请注意，阻止 TLS 扩展的影响是复杂的。例如，如果禁用了强制扩展，则可能无法建立 TLS 连接。请不要禁用强制扩展，除非您清楚地了解其影响，否则不要使用此功能。

# 包摘要页面上的“Related Packages”(JDK-8260388)

软件包的摘要页面现在包括一个列出任何“Related Packages”的部分。Related Packages（相关软件包）是根据常见命名约定启发式确定的，可能包括以下内容：

- “parent”包（即，包是子包的包）
- 同级包（即具有相同父包的其他包）
- 任何子包

相关软件包不一定都在同一个模块中。

# 参考链接

- [一文总结 Java\JDK 17 发布的新特性](https://segmentfault.com/a/1190000040701755)
- [https://openjdk.java.net/projects/jdk/17/](https://openjdk.java.net/projects/jdk/17/)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。
