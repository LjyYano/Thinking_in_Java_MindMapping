---
date: 2022-07-22
---


- [说明](#%E8%AF%B4%E6%98%8E)
- [目录](#%E7%9B%AE%E5%BD%95)
- [思维导图](#%E6%80%9D%E7%BB%B4%E5%AF%BC%E5%9B%BE)
    - [导读](#%E5%AF%BC%E8%AF%BB)
    - [第 1 章 什么是对象](#%E7%AC%AC-1-%E7%AB%A0-%E4%BB%80%E4%B9%88%E6%98%AF%E5%AF%B9%E8%B1%A1)
    - [第 3 章 一切都是对象](#%E7%AC%AC-3-%E7%AB%A0-%E4%B8%80%E5%88%87%E9%83%BD%E6%98%AF%E5%AF%B9%E8%B1%A1)
    - [第 6 章 初始化和清理](#%E7%AC%AC-6-%E7%AB%A0-%E5%88%9D%E5%A7%8B%E5%8C%96%E5%92%8C%E6%B8%85%E7%90%86)
    - [第 7 章 实现隐藏](#%E7%AC%AC-7-%E7%AB%A0-%E5%AE%9E%E7%8E%B0%E9%9A%90%E8%97%8F)
    - [第 8 章 复用](#%E7%AC%AC-8-%E7%AB%A0-%E5%A4%8D%E7%94%A8)
    - [第 9 章 多态](#%E7%AC%AC-9-%E7%AB%A0-%E5%A4%9A%E6%80%81)
    - [第 10 章 接口](#%E7%AC%AC-10-%E7%AB%A0-%E6%8E%A5%E5%8F%A3)
    - [第 11 章 内部类](#%E7%AC%AC-11-%E7%AB%A0-%E5%86%85%E9%83%A8%E7%B1%BB)
    - [第 13 章 函数式编程](#%E7%AC%AC-13-%E7%AB%A0-%E5%87%BD%E6%95%B0%E5%BC%8F%E7%BC%96%E7%A8%8B)
    - [第 14 章 流](#%E7%AC%AC-14-%E7%AB%A0-%E6%B5%81)
    - [第 15 章 异常](#%E7%AC%AC-15-%E7%AB%A0-%E5%BC%82%E5%B8%B8)
    - [第 17 章 文件](#%E7%AC%AC-17-%E7%AB%A0-%E6%96%87%E4%BB%B6)
    - [第 18 章 字符串](#%E7%AC%AC-18-%E7%AB%A0-%E5%AD%97%E7%AC%A6%E4%B8%B2)
    - [第 19 章 反射](#%E7%AC%AC-19-%E7%AB%A0-%E5%8F%8D%E5%B0%84)
    - [第 20 章 泛型](#%E7%AC%AC-20-%E7%AB%A0-%E6%B3%9B%E5%9E%8B)
    - [进阶卷 第 01 章 枚举](#%E8%BF%9B%E9%98%B6%E5%8D%B7-%E7%AC%AC-01-%E7%AB%A0-%E6%9E%9A%E4%B8%BE)
    - [进阶卷 第 05 章 并发编程](#%E8%BF%9B%E9%98%B6%E5%8D%B7-%E7%AC%AC-05-%E7%AB%A0-%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B)
    - [进阶卷 第 06 章 底层并发](#%E8%BF%9B%E9%98%B6%E5%8D%B7-%E7%AC%AC-06-%E7%AB%A0-%E5%BA%95%E5%B1%82%E5%B9%B6%E5%8F%91)
    - [结语](#%E7%BB%93%E8%AF%AD)
- [链接](#%E9%93%BE%E6%8E%A5)
- [我的公众号](#%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7)
- [写在最后](#%E5%86%99%E5%9C%A8%E6%9C%80%E5%90%8E)

# 说明

原来读过 [《Java 编程思想（第 4 版）》](https://book.douban.com/subject/2130190/)，但是这个版本还是基于 Java 5 讲解。由于 Java 8 做出了非常大的改进（是 Java 变化最大的版本），且截止到 2022-07-22，Java 版本都更新到 18 了……原来那本书确实需要更新了。

原作者 `Bruce Eckel` 又重新出版了新书：[《On Java 中文版 基础卷》](https://book.douban.com/subject/35751619/) 和 [《On Java 中文版 进阶卷》](https://book.douban.com/subject/35751623/)。本文是对基础卷和进阶卷的思维导图笔记总结，略过了部分较为基础的章节，并未完全详尽书中所有知识点。

本文地址发布在 https://github.com/LjyYano/Thinking_in_Java_MindMapping 上，GitHub 地址：[链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-07-22%20%E6%80%9D%E7%BB%B4%E5%AF%BC%E5%9B%BE%E5%AD%A6%E3%80%8AOn%20Java%E3%80%8B%E5%9F%BA%E7%A1%80%E5%8D%B7.md)，请在转载时标明原文链接~

# 目录

有几个章节过于基础，没有放在思维导图上：
- 02 安装 Java 和本书示例
- 04 操作符
- 05 控制流
- 12 集合
- 16 代码校验
- 21 数组

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-41-19.png?x-oss-process=style/yano)

# 思维导图

## 导读

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-19-07.png?x-oss-process=style/yano)

我的语言之局限，即我的世界之局限。这句话不仅适用于我们日常读写的语言，也适用于编程语言。很微妙的一件事是，`一门语言会悄然无息地引导你进入某种思维模式`，同时远离其他思维模式。Java 尤其如此。

如果你了解一门语言的不足之处和局限性，当你遇到某个语言特性不可用时，就不会被卡住，以致无法继续。同时，因为你已经知晓其局限性，所以就可以更好地进行程序设计。

Java 8 包含了许多基础和重要的改进，而由于 Java 一直严格遵守自己的向后兼容性承诺，做出这些改进无疑需要花费相当多的精力。

如果一开始就将你的项目“发展”成一个有机的、进化的生命体，而不是像建造玻璃墙的摩天大楼一样进行一次性施工，你将获得更大的成功和更直接的反馈。

相关链接：
- OpenJDK 官方版本计划及功能：[JDK Project](https://openjdk.org/projects/jdk/)
- [JDK 17 Features](https://openjdk.org/projects/jdk/17/)

## 第 1 章 什么是对象

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-21-53.png?x-oss-process=style/yano)

工具已经越来越不像机器，而是越来越像思维的一部分。

所有编程语言都是一种`抽象`。

如果我可以将问题从表象中抽取出来，那么什么样的对象可以马上解决我的问题呢？

## 第 3 章 一切都是对象

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-22-57.png?x-oss-process=style/yano)

## 第 6 章 初始化和清理

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-23-29.png?x-oss-process=style/yano)

## 第 7 章 实现隐藏

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-23-57.png?x-oss-process=style/yano)

## 第 8 章 复用

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-24-27.png?x-oss-process=style/yano)

## 第 9 章 多态

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-24-53.png?x-oss-process=style/yano)

相关链接：
- [一文看懂 Java 对象的内存](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-08-17%20%E4%B8%80%E6%96%87%E7%9C%8B%E6%87%82Java%20%E5%AF%B9%E8%B1%A1%E7%9A%84%E5%86%85%E5%AD%98.md)

## 第 10 章 接口

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-25-41.png?x-oss-process=style/yano)

任何抽象都应该由真正的需求来驱动。接口应该是在必要时用来重构的东西，而不是在任何地方都多加一个间接层级，进而带来额外的复杂性。这种额外的复杂性影响很大，如果你让某人在克服这种复杂性上花费时间，而他最终却发现你添加接口只不过是为了“以防万一”，而非出于什么令人信服的其他理由，他就会质疑你做过的其他所有设计。

相关链接：
- 新特性 [JEP 409: Sealed Classes](https://openjdk.org/jeps/409)

## 第 11 章 内部类

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-26-42.png?x-oss-process=style/yano)

## 第 13 章 函数式编程

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-27-15.png?x-oss-process=style/yano)

lambda 表达式和方法引用远非完美，`我们要永远承受 Java 设计者在语言诞生初期的草率决定所导致的代价`。lambda 在 Java 并非一等公民。这并不意味着 Java 8 没有大的改进，但确实意味着，像许多 Java 语法一样，最终会有一个让你感到不爽的临界点。

相关链接：
- [Java Lambda 表达式源码分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-08-18%20Java%20Lambda%20%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90.md)

## 第 14 章 流

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-28-17.png?x-oss-process=style/yano)

相关链接：
- [Java Stream 源码分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-12-03%20Java%20Stream%20%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90.md)

## 第 15 章 异常

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-30-28.png?x-oss-process=style/yano)

异常处理的优点之一，就是它使得你可以在某处集中精力处理你要解决的问题，而在另一处处理你编写代码产生的错误。

Java 坚定地强调将所有的错误都以异常形式报告的这一事实，正是它远超过诸如 C++ 这类语言的长处之一。

相关链接：
- 新特性 [JEP 358: Helpful NullPointerExceptions](https://openjdk.org/jeps/358)

## 第 17 章 文件

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-30-57.png?x-oss-process=style/yano)

在非常难用的文件 I/O 编程存在多年之后，Java 终于简化了读写文件的基本操作。

## 第 18 章 字符串

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-31-33.png?x-oss-process=style/yano)

相关链接：
- [Java String 演进全解析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-11-29%20Java%20String%20%E6%BC%94%E8%BF%9B%E5%85%A8%E8%A7%A3%E6%9E%90.md)
- [30 分钟玩转「正则表达式」](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-12-01%2030%E5%88%86%E9%92%9F%E7%8E%A9%E8%BD%AC%E3%80%8C%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E3%80%8D.md)
- 新特性 [JEP 378: Text Blocks](https://openjdk.org/jeps/378)

## 第 19 章 反射

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-34-45.png?x-oss-process=style/yano)

相关链接：
- [Java ClassLoader](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-09-13%20Java%20ClassLoader.md)
- 新特性 [JEP 394: Pattern Matching for instanceof](https://openjdk.org/jeps/394)

## 第 20 章 泛型

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-22-20-36-12.png?x-oss-process=style/yano)

在 Java 中，泛型是在这门语言发布了几乎 10 年后才引入的，所以向泛型的迁移问题是必须要考虑的，也对泛型的设计产生了很大冲击。结果就是，作为程序员的你，将因为 Java 设计者在创建 1.0 版本时缺乏远见而承受痛苦。

有些语言对参数化类型采用了更简洁、影响更小的实现方法。不难想象，这样一种语言有可能成为 Java 的接班人，因为它完全采用了 C++ 对待 C 的方式：站在巨人的肩膀上，并看得更远。

## 进阶卷 第 01 章 枚举

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-15-08-47-03.png?x-oss-process=style/yano)

## 进阶卷 第 05 章 并发编程

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-15-08-47-55.png?x-oss-process=style/yano)

## 进阶卷 第 06 章 底层并发

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-09-15-08-48-46.png?x-oss-process=style/yano)

## 结语

在不少讨论中能听到这样的声音：“C++ 是一门设计拙劣的语言。”我则认为理解 C++ 和 Java 做出的各种决策有助于站在更高的位置看待问题。

如同任何人类语言一样，`Java 提供了一种表达概念的方式`。如果使用得当，随着问题变得更庞大更复杂，这种表达工具将会比别的可供选择的语言更为简单、灵活。

曾几何时，C++ 是编程语言界的“皇冠”，人们认为会永远如此。很多人也这么看 Java，但由于 JVM 的缘故，Java 已经使自己可以被轻而易举地替换掉了。现在，任何人都可以创建一门新的语言，并在短时间内使其像 Java 一样高效运行。但在以前，对于一门新的语言来说，大部分开发时间往往花在实现正确、高效的编译器上。

在我写作本书时，Java 是世界上首屈一指的编程语言。然而 `Java 终将老去`，就像 C++ 那样，衰退到只会在某些特殊场合用到（甚至只用于支持遗留代码，因为 Java 不如 C++ 和硬件结合那么紧密）。但是 Java 无心插柳却已蔚然成荫的真正光辉之处是，它为自己的替代品创造了一条非常平坦的道路，即使 Java 本身已经到了无法再进化的地步。未来的所有语言都应该从中学习：要么创造一种可以不断重构的文化（如 Python 和 Ruby 做到的那样），要么让竞争者可以茁壮成长。

---

C 语言是低级语言，这会限制你的野心。这些限制使得扩展多线程库看起来合情合理。然而 Java 更宏大的雄心壮志，使得在将低级语言模型直接照搬到高级语言的过程中，很快就暴露出了根基上的问题。这些错配问题体现于 Thread 类中大量方法的弃用，在随后的为并发提供更好抽象的高级库的浪潮中也暴露了出来。

令人惊叹的是，尽管有这么多无法弥补的重大问题，Java 还是发展到了现在的程度。Java 的后续版本已经增加了库以提升并发的抽象水平。事实上，我之前绝没有想到 Java 8 会带来如此大的提升：并行流和 CompletableFuture——这是史诗般的魔法，我还将非常惊讶地看到更多魔法的诞生。

当面临多个可选方案时，先尝试需要最少假设的方案。

你很容易依赖一门语言，并且陷入一种想要用该语言解决一切问题的状态。

# 链接

由于思维导图中的链接没法截图，按照先后顺序贴在下面：

- OpenJDK 官方版本计划及功能：[JDK Project](https://openjdk.org/projects/jdk/)
- [JDK 17 Features](https://openjdk.org/projects/jdk/17/)
- [一文看懂 Java 对象的内存](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-08-17%20%E4%B8%80%E6%96%87%E7%9C%8B%E6%87%82Java%20%E5%AF%B9%E8%B1%A1%E7%9A%84%E5%86%85%E5%AD%98.md)
- 新特性 [JEP 409: Sealed Classes](https://openjdk.org/jeps/409)
- [Java Lambda 表达式源码分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-08-18%20Java%20Lambda%20%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90.md)
- [Java Stream 源码分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-12-03%20Java%20Stream%20%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90.md)
- 新特性 [JEP 358: Helpful NullPointerExceptions](https://openjdk.org/jeps/358)
- [Java String 演进全解析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-11-29%20Java%20String%20%E6%BC%94%E8%BF%9B%E5%85%A8%E8%A7%A3%E6%9E%90.md)
- [30 分钟玩转「正则表达式」](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2020-12-01%2030%E5%88%86%E9%92%9F%E7%8E%A9%E8%BD%AC%E3%80%8C%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E3%80%8D.md)
- 新特性 [JEP 378: Text Blocks](https://openjdk.org/jeps/378)
- [Java ClassLoader](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-09-13%20Java%20ClassLoader.md)
- 新特性 [JEP 394: Pattern Matching for instanceof](https://openjdk.org/jeps/394)

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

# 写在最后

思维导图是用`亿图脑图 MindMaster`制作的，之前重度使用了 Xmind 和 WPS，感觉还是亿图这个思维导图软件比较适合我。

本文 GitHub 地址：[链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2022-07-22%20%E6%80%9D%E7%BB%B4%E5%AF%BC%E5%9B%BE%E5%AD%A6%E3%80%8AOn%20Java%E3%80%8B%E5%9F%BA%E7%A1%80%E5%8D%B7.md)。如果需要思维导图原件，请在 GitHub 私信获取~