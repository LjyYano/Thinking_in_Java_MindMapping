---
date: 2019-06-06
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注 `^_^`

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

近期学习了下 Kotlin，不得不说 Kotlin 比 Java 简洁不少，个人感觉代码量能减少 50%。到现在已经使用 Java 语言做服务端开发两年半的时间了，对 Java 某些啰嗦的语法也是有很多想法。这篇文章谈谈我对 Kotlin 和 Java 的看法。

# 编程语言整体排名

[TIOBE Index for November 2018][1]

![][2]

从长远来看，排名前 10 的也基本上是 Java、C、C++、Python、C#、VB、PHP、JavaScript。至于 Kotlin 的排名，11 月份在编程语言仅排 41 名，Ratings 仅有 0.216%。

![][3]

曾看到一个理论是说，` 看一个事物还能存在多久，首先要看看它已经存在了多久。` 如果一门编程语言已经存在了 20 年，那么它在 20 年后也不会消失。像 C、VB 这样的语言，至今仍然能够在编程语言排行榜中占据非常重要的位置。

# Kotlin 的优点

[Kotlin 语言中文站][4] 官方网站已经有非常详细的说明，这里我只想说下我刚刚接触 Kotlin 两天的体会。

1. 能直接与 Java 相互调用，能与 Java 工程共存
2. 大大减少样板代码
3. 可以将 Kotlin 代码编译为无需虚拟机就可运行的原生二进制文件
4. 支持协程
5. 支持高阶函数
6. 语言层面解决空指针问题
7. 对字符串格式化的处理（$ 变量名）
8. 更像 Python 的语法
9. 对λ表达式支持更好
10. 中缀表达式

# Kotlin 的缺点

1. 尽管 Google 大力推崇 Kotlin，Kotlin 似乎并没有特别火热
2. Java 变量名和 Kotlin 关键字可能产生冲突
3. Kotlin 空安全和 Java 工程结合仍然存在问题

# 谈论下 Java 语言

## Java 语言的缺陷

1. 啰嗦的语法：很多 Java 类库的行数动不动就是 1000+
2. 伪泛型
3. 完全面向对象：这是 Java 最大的优点，但是也是很大的缺点。我想写个工具类，也要新建一个对象？
4. 沉重的历史包袱：因为要考虑向前兼容的问题，很多支持和改进并不彻底，最大的例子就是 JDK 1.5 引入的泛型。

## Java 11

`JDK 开始收费 `。我觉得 JDK 开始收费是个好事情，至少 Java 的版本发布周期变更为每六个月一次 —— 每半年发布一个大版本，每个季度发布一个中间特性版本，并且承诺不会跳票。Java 6 的发布时间是 2009 年，Java 7 的发布时间是 2011 年，Java 8 是 2014 年。新版本的 Java 确实有许多方便的特性和类库的升级。

`JDK 升级 `。由于工作原因，我使用了近 2 年的 Java 6。仅仅是升级到了 Java 8，就已经极大地提高了我的开发效率！——更不用说类库底层的优化。

# 使用何种编程语言

总的来说，`Java 号称是 C++ --，Kotlin 就像是 Java++。`Kotlin 没有像 Java 一样的历史包袱，设计之初就是为了解决 Java 的痛点。

但是世界上并没有完美的语言——像 Python 也存在版本分裂的问题。` 用再好的笔，也写不出更好的文章。` 如果单单是使用编程语言开发的话，充分利用好一门编程语言和 IDE 就足够了。

  [1]: https://www.tiobe.com/tiobe-index/
  [2]: http://static.zybuluo.com/Yano/k915xqyy14t54iepuqqwvzzj/image.png
  [3]: http://static.zybuluo.com/Yano/u56742co2xwpi7jw6z5tlkj6/image.png
  [4]: https://www.kotlincn.net/
