# 前言

String 是我们使用最频繁的对象，使用不当会对内存、程序的性能造成影响，本篇文章全面介绍一下 Java 的 String 是如何演进的，以及使用 String 的注意事项。

# 下面的输出结果是什么？

```java
@Test
public void testString() {
    String str1 = "abc";
    String str2 = new String("abc");
    String str3 = str2.intern();
    System.out.println(str1 == str2);
    System.out.println(str2 == str3);
    System.out.println(str1 == str3);
}
```

这段代码涉及了 Java 字符串的内存分配、新建对象和引用等方面的知识，输出结果是：

```
false
false
true
```

# String 对象的实现方式

String 对象的实现方式，在 Java 6、Java 7/8、Java 9 中都有很大的区别。下面是一张简要的对比图：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-11-29-062856.png)

## Java 6 的实现方式

String 对 char 数组进行了封装，主要有四个成员变量：
- char 数组
- 偏移量 offset
- 字符数量 count
- 哈希值 hash

String 对象可以通过 offset 和 count 在 char[] 数组中获取对应的字符串，这样做可以高效、快速地共享数组对象，节省内存空间，但是这种方法经常导致`内存泄漏`。

这是因为，假如有一个非常大的字符串数组对象 a，后来有一个小的字符串引用仅引用其中很少的字符 b，那么会新建大的数组 char[]，当 a 被释放后，char[] 的引用并不能被 GC，因为 b 还在引用。

## Java 7/8 的实现方式

String 类去掉了 offset 和 count，String.substring 方法也不再共享char[]，从而解决了内存泄漏问题。

## Java 9 的实现方式

`char[] → byte[]`，同时新增了`coder`属性，标识字符编码。这是因为 char 字符占 16 位（2个字节），如果仅存储单字节编码的字符就非常浪费空间。

coder 属性的作用是标识字符串是否为 Latin-1（单字节编码），0 标识是 Latin-1，1 代表是 UTF-16。

Java 11 中的 java.lang.String#substring(int, int) 方法如下：

```
public String substring(int beginIndex, int endIndex) {
    int length = length();
    checkBoundsBeginEnd(beginIndex, endIndex, length);
    int subLen = endIndex - beginIndex;
    if (beginIndex == 0 && endIndex == length) {
        return this;
    }
    return isLatin1() ? StringLatin1.newString(value, beginIndex, subLen)
                        : StringUTF16.newString(value, beginIndex, subLen);
}
```

# String 在 JVM 中是如何存储的？

这是一个很重要的问题，相信大部分人都不能描述清楚，因为 JVM 的实现改了很多版……

在 JDK 1.7 之前，运行时常量池逻辑包含`字符串常量池`，都存在方法区中，方法区在 HotSpot 虚拟机的实现为`永久代`。

在 JDK 1.7 中，`字符串常量池` → 堆，运行时常量池仍然在方法区中。

在 JDK 1.8 中，HotSpot 移除了永久代，使用元空间（Metaspace）代替。这时候`字符串常量池`在堆中，运行时常量池在元空间（Metaspace）。

## 永久代 VS 元空间（Metaspace）

元空间的本质和永久代类似，都是对 JVM 规范中`方法区的实现`。不过元空间与永久代之间最大的区别在于：元空间并不在虚拟机中，而是使用`本地内存`。

## 一句话总结

在新版 JDK 实现（毕竟 Java 8 都已经是老古董，Java 15 都发布了）中，字符串常量池是在堆中。

# 使用 String.intern 节省内存

虽然我还没有在项目中实际应用过，不过这个函数应该还挺有用的，能够复用 Java 中的字符串常量。文章开头的代码中，`System.out.println(str1 == str3);` 返回 true，就是因为 `java.lang.String#intern` 方法检测到字符串常量池有这个对象时，能够直接复用字符串常量池的对象，不会额外创建字符串常量。

```
String str1 = "abc";
String str2 = new String("abc");
```

注意上面的代码中，`new String("abc")` 里面的字符串 `abc` 与 str1 的 `abc` 不同，是在字符串常量池新创建的 `abc`。

String.intern 的代码注释如下。

```
/**
    * Returns a canonical representation for the string object.
    * <p>
    * A pool of strings, initially empty, is maintained privately by the
    * class {@code String}.
    * <p>
    * When the intern method is invoked, if the pool already contains a
    * string equal to this {@code String} object as determined by
    * the {@link #equals(Object)} method, then the string from the pool is
    * returned. Otherwise, this {@code String} object is added to the
    * pool and a reference to this {@code String} object is returned.
    * <p>
    * It follows that for any two strings {@code s} and {@code t},
    * {@code s.intern() == t.intern()} is {@code true}
    * if and only if {@code s.equals(t)} is {@code true}.
    * <p>
    * All literal strings and string-valued constant expressions are
    * interned. String literals are defined in section 3.10.5 of the
    * <cite>The Java&trade; Language Specification</cite>.
    *
    * @return  a string that has the same contents as this string, but is
    *          guaranteed to be from a pool of unique strings.
    * @jls 3.10.5 String Literals
    */
public native String intern();
```

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，希望大家关注^_^

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)