# 序言

零散地读完《Effective Java》（中文版第二版），真心觉得这是一本经典书籍。现在想写一下读完这本书的整体收获，而不是涉及到书中某一个具体的知识点。

# 收获

## 在重点或疑问的地方，做出标记和注释

在读《Effective Java》时，对于前 10 条建议，我并没有理解得很深刻，因为我只是简单地拿笔在书上划下重点的句子而已。我也感觉到了问题，后来 ` 在重点或疑问的地方，做出标记和注释 `，对于问题的理解提升很大。

虽然这是一个很愚蠢的问题——连小学一年级的学生都知道，但是我却刚刚体会到这样做的好处。比如我在看到第 12 条 ` 考虑实现 Comparable 接口 ` 一节时，首先问了自己一个问题：如何使用 Comparable 接口？

后来发现 Comparable 接口采用了 ` 策略模式 ` 的设计模式，进一步分析了策略模式。看到 P54 中间的一句话：` 依赖于比较关系的类包括有序集合类 TreeSet 和 TreeMap，以及工具类 Collection 和 Arrays，它们内部包含有搜索和排序算法 `。我就问了自己几个问题：这些工具类比如 Arrays 的 sort，使用的是什么算法？Comparable 接口是如何与 Arrays 的 sort 方法结合在一起，进而通过传入不同的 Comparable 接口，来实现 Arrays 的不同 sort 排序的？

之后我发现 Arrays.sort 会根据不同的类型，采取不同的排序方法。对于 ` 基本类型 `，会采用 ` 调优的快速排序 `；对于 ` 对象类型 `，会采取 ` 改进的归并排序 `。然后我就会问自己：为什么对于基本类型和对象类型，要采取不同的排序方法呢？快速排序的调优，体现在哪里？归并排序的改进，又体现在哪里？在查看源代码的基础上，我又发现 JDK 7 采用了一种 `Dual-Pivot Quicksort` 的快排方法，就会思考这个算法好在哪里？

在查看源代码的过程中，我发现注释中有个 API 的设计者是 `Josh Bloch`，我就 Google 了一下。我才注意到他就是这本书的作者啊！我才知道 Java 的集合框架就是他设计的，才知道译者序里面的介绍，都是关于他的…… 我看书很少注意作者，这个习惯可不好。进一步 Google，我发现了他的 Twitter，我是不是应该关注他？那还有哪些 Java 领域和计算机领域的国外、国内牛人，我应该关注一下？如果在使用 Java 的过程中，连它的开发者及演变过程都不知道…… 通过问自己几个问题，我一下子就打开了一个全新的世界 +_+

## 深入思考

忘记从哪里看见过一句话，大意是：` 只有了解全部的真相，才能获得全部的自由 `——编程领域更是如此。就好比我读《Effective Java》，如果只是简单阅读第 12 条 ` 考虑实现 Comparable 接口 ` 一节，想必几分钟就草草略过了。但是我获得了什么？是能够和别人吹嘘说：我把《Effective Java》看了 3 遍，《Java 编程思想》看了 5 遍？即使看 10 遍又有什么意义呢？如果我不花费时间，问自己几个问题，亲自去研究一下 Comparable 接口，那么我不会知道 JDK 底层的实现细节，我并没有了解全部的真相，每次使用时都会有个疑问：咦，Arrays.sort 是怎么通过对象的 Comparable 接口，实现不同的排序的？如果不去解决自己的疑惑，那么问题只会越来越多、越来越严重。

套用 M· 斯科特 · 派克《少有人走的路——心智成熟的旅程》中的一句话（大意）：` 逃避问题所带来的痛苦，甚至比问题本身所带来的痛苦，更为严重；问题永远不会自动消失，直到我们去直面问题、解决问题 `。我可能是有些过于类比了，但是如果关于编程的疑问，我们不去自己解决并亲自弄明白，那么我们就是在 ` 逃避问题 `。

**深入思考具有许多好处**（自己浅显的总结，欢迎大家留言讨论）：
1. 不会每次遇到问题，就想一次：这个功能是怎么实现的？这次没时间，还是以后再研究吧！
2. 大脑的容量是有限的，这些问题只有在真正解决之后，才不会占用大脑的容量。《Head First》系列在引言部分，提出的第一条建议就是：` 慢一点，你理解的越多，需要记住的就越少 `。
3. 在我们完全理解一个问题后，下次再遇到同样的问题，只会更加深对于这个问题的思考，而不是那个老问题（这个功能是怎么实现的）。
4. 增加自信，获得自由。

深入思考并不会占用太多时间，我们离大部分真相都只有一步的距离。而且重要的是 ` 思考的深度 `，而且这样思考能够带来很大的 ` 满足感 `。至少我在读《Effective Java》时，就是这个感觉——一点也不觉得累，通过不断问自己问题，获得了很多很多知识，并且一直处于兴奋状态。

## 优秀的框架（习惯），是指在无意识中也不会犯错

在第 45 条 ` 将局部变量的作用域最小化 ` 一节中（中文第二版 P182），作者为了说明为什么将作用域最小化，for 循环比 while 循环好时，列举出了一个代码片段，包含一个 “剪切——粘贴” 错误：本来是要初始化一个新的循环变量 i2，却使用了旧的循环变量 i。代码仍然能够通过编译，运行的时候也不会抛出异常，但是实现的功能却是错误的。如果使用了 `for-each` 形式，就会从根本上避免这种无意识的错误。

作者是 Java API 的设计者，考虑得不仅仅是如何才能够使 Java API 实现效率更高，还包括如何让客户端更具灵活性、如何从架构的设计上，减少客户端犯错误的机会。这完完全全也适合每一个开发者。进一步思考，在现实中也是一样啊！我曾经看过一篇文章，讨论如何通过优秀的习惯，减少无意识中犯错误的机会。

## 最重要的是思想，而不是实现细节

细节很重要，但是书籍、框架乃至 Java 的设计思想，才是最重要的（所以 Bruce Eckel 的《Thinking in Java》才会翻译成《Java 编程 ` 思想 `》？）。在阅读源码时，不仅仅是语义上的理解，考虑一下为什么要这么实现这个功能？这样实现有什么好处？它的适用场景有哪些？是否还能够改进？哪些思想我能够借鉴到平时的工作和生活中？

李笑来老师的一篇文章中有这样两段话：

> 他们在读书的时候，不仅仅是文字以及文字所阐述的道理，更多注意到的是作者的思考方式。作者的 “思考方式” 与自己的 “思考方式” 有什么不同？如果作者的 “思考方式” 更好，自己应该如何调整？
>
> 一本概率论读完，大多数人就是考个试也不一定及格，而另外的极少数人却成了科学家——因为他们改良了自己的思考方式，从此可以 “像一个科学家一样思考”……

如果我要成为 `Java 专家 `，我就应该去阅读 JDK 源码，因为这是 Java 专家及天才思想的结晶。我更应该去思考：他们为什么这样设计？他们的 ` 设计思想 ` 是什么？要 ` 像一个 Java 专家一样思考 `~

抓住思想的好处：
1. 提纲挈领，能够忽略不重要的细节，将注意力集中在重要的地方（所谓的 ` 二八法则 `）。
2. 阅读速度的提升。可以快速略过不重要的细节，我的阅读效率大大提升。
3. 能够 ` 看清全局 `，对整体有清晰的把握。
4. 可以改良自己的思考方式，使得我们 ` 像一个科学家一样思考 `、` 像一个 Java 专家一样思考 `。

# 总结

我在读完《Effective Java》后，发觉《Java 编程思想》这本书需要重新读一遍了，因为以前只是简单地划了一下重点句子而已。当然，除了一个人潜心研读之外，还需要多和他人讨论和总结。


