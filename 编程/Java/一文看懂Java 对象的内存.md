---
date: 2021-08-17
---


- [说明](#说明)
- [Java 对象模型](#java-对象模型)
- [基本类型占用存储空间和指针压缩](#基本类型占用存储空间和指针压缩)
  - [基础对象占用存储空间](#基础对象占用存储空间)
  - [Java 中基础数据类型是在栈上分配还是在堆上分配？](#java-中基础数据类型是在栈上分配还是在堆上分配)
  - [指针压缩](#指针压缩)
  - [CompressedOops 工作原理](#compressedoops-工作原理)
- [Java 对象到底占用多大内存](#java-对象到底占用多大内存)
  - [JDK 分析 JVM 对象布局工具](#jdk-分析-jvm-对象布局工具)
  - [测试空对象](#测试空对象)
    - [启用 oop](#启用-oop)
    - [禁用 oop](#禁用-oop)
  - [测试复杂对象](#测试复杂对象)
    - [启用 oop](#启用-oop-1)
    - [禁用 oop](#禁用-oop-1)
  - [包含对象引用的对象](#包含对象引用的对象)
    - [启用 oop](#启用-oop-2)
    - [禁用 oop](#禁用-oop-2)
- [总结](#总结)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 说明

本文绝大多数内容，都是直接摘自 [高端面试必备：一个 Java 对象占用多大内存](https://www.cnblogs.com/rickiyang/p/14206724.html#:~:text=%E5%AF%B9%E8%B1%A1%E5%A4%B4%E4%BF%A1%E6%81%AF%EF%BC%9A64%20%E4%BD%8D,%E5%8E%8B%E7%BC%A9%E5%90%8E16%20%E5%AD%97%E8%8A%82%E3%80%82)，因为这篇文章写得太好了，我觉得没有必要重新写一遍了 0_o

# Java 对象模型

HotSpot JVM 使用名为 `oops (Ordinary Object Pointers)` 的数据结构来表示对象。这些 oops 等同于本地 C 指针。 `instanceOops` 是一种特殊的 oop，表示 Java 中的`对象实例`。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210817110242.png?x-oss-process=style/yano)

在 Hotspot VM 中，对象在内存中的存储布局分为 3 块区域：

- 对象头（Header）
- 实例数据（Instance Data）
- 对齐填充（Padding）

对象头又包括三部分：MarkWord、元数据指针、数组长度。

- `MarkWord`：用于存储对象运行时的数据，好比 HashCode、锁状态标志、GC 分代年龄等。这部分在 64 位操作系统下占 8 字节，32 位操作系统下占 4 字节。
- `指针`：对象指向它的类元数据的指针，虚拟机通过这个指针来确定这个对象是哪一个类的实例。
这部分就涉及到指针压缩的概念，在开启指针压缩的状况下占 4 字节，未开启状况下占 8 字节。
- `数组长度`：这部分只有是数组对象才有，若是是非数组对象就没这部分。这部分占 4 字节。

实例数据就不用说了，用于存储对象中的各类类型的字段信息（包括从父类继承来的）。

关于`对齐填充`，Java 对象的大小默认是`按照 8 字节对齐`，也就是说 Java 对象的大小必须是 8 字节的倍数。若是算到最后不够 8 字节的话，那么就会进行对齐填充。

那么为何非要进行 8 字节对齐呢？这样岂不是浪费了空间资源？

其实不然，由于 `CPU 进行内存访问`时，`一次寻址`的指针大小是 8 字节，正好也是 L1 缓存行的大小。如果不进行内存对齐，则可能出现跨缓存行的情况，这叫做 `缓存行污染`。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210817111611.png?x-oss-process=style/yano)

由于当 obj1 对象的字段被修改后，那么 CPU 在访问 obj2 对象时，必须将其重新加载到缓存行，因此影响了程序执行效率。

也就说，8 字节对齐，是为了效率的提高，以`空间换时间`的一种方案。固然你还能够 16 字节对齐，可是 8 字节是最优选择。

正如我们之前看到的，JVM 为对象进行填充，使其大小变为 8 个字节的倍数。使用这些填充后，oops 中的`最后三位始终为零`。这是因为在二进制中 8 的倍数的数字总是以 000 结尾。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210817111736.png?x-oss-process=style/yano)

由于 JVM 已经知道最后三位始终为零，因此在堆中存储那些零是没有意义的。相反假设它们存在并存储 3 个其他更重要的位，以此来模拟 35 位的内存地址。现在我们有一个带有 3 个右移零的 32 位地址，所以我们将 35 位指针压缩成 32 位指针。这意味着我们可以在不使用 64 位引用的情况下使用最多 `32 GB`。

# 基本类型占用存储空间和指针压缩

## 基础对象占用存储空间

Java 基础对象在内存中占用的空间如下：

| 类型    | 占用空间 (byte) |
| ------- | --------------- |
| boolean | 1               |
| byte    | 1               |
| short   | 2               |
| char    | 2               |
| int     | 4               |
| float   | 4               |
| long    | 8               |
| double  | 8               |

另外，`引用类型`在 32 位系统上每个引用对象占用 4 byte，在 64 位系统上每个引用对象占用 8 byte。

## Java 中基础数据类型是在栈上分配还是在堆上分配？

我们继续深究一下，基本数据类占用内存大小是固定的，那具体是在哪分配的呢，是在堆还是栈还是方法区？大家不妨想想看！ 要解答这个问题，首先要看这个数据类型在哪里定义的，有以下三种情况。

- 如果在`方法体内`定义的，这时候就是在`栈`上分配的
- 如果是`类的成员变量`，这时候就是在`堆`上分配的
- 如果是`类的静态成员变量`，在`方法区`上分配的

## 指针压缩

引用类型在 64 位系统上占用 8 个字节，虽然一个并不大，但是耐不住多。

所以为了解决这个问题，JDK 1.6 开始 64 bit JVM 正式支持了 `-XX:+UseCompressedOops` （需要 jdk1.6.0_14) ，这个参数可以压缩指针。

启用 CompressOops 后，会压缩的对象包括：

- 对象的全局静态变量（即类属性）；
- 对象头信息：64 位系统下，原生对象头大小为 16 字节，压缩后为 12 字节；
- 对象的引用类型：64 位系统下，引用类型本身大小为 8 字节，压缩后为 4 字节；
- 对象数组类型：64 位平台下，数组类型本身大小为 24 字节，压缩后 16 字节。

当然压缩也不是万能的，针对一些特殊类型的指针 JVM 是不会优化的。 比如：

- 指向非 Heap 的对象指针
- 局部变量、传参、返回值、NULL 指针。

## CompressedOops 工作原理

32 位内最多可以表示 4GB，64 位地址为 堆的基地址 + 偏移量，当堆内存 < 32GB 时候，在压缩过程中，把 偏移量 / 8 后保存到 32 位地址。在解压再把 32 位地址放大 8 倍，所以启用 CompressedOops 的条件是堆内存要在 4GB * 8=32GB 以内。

# Java 对象到底占用多大内存

前面我们分析了 Java 对象到底都包含哪些东西，所以现在我们可以开始剖析一个 Java 对象到底占用多大内存。

由于现在基本都是 64 位的虚拟机，所以后面的讨论都是基于 64 位虚拟机。 首先记住公式，对象由 对象头 + 实例数据 + padding 填充字节组成，虚拟机规范要求对象所占内存必须是 8 的倍数，padding 就是干这个的。

上面说过对象头由 Markword + 类指针 kclass（该指针指向该类型在方法区的元类型） 组成。

## JDK 分析 JVM 对象布局工具

JDK 提供了一个工具，`JOL` 全称为 `Java Object Layout`，是分析 JVM 中对象布局的工具，该工具大量使用了 Unsafe、JVMTI 来解码布局情况。下面我们就使用这个工具来获取一个 Java 对象的大小。

```
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.16</version>
</dependency>
```

## 测试空对象

创建一个空的对象 A，里面什么都没有。

```java
static class A {
}
```

测试代码：

```java
@Test
public void testEmptyClass() {
    ClassLayout classLayout = ClassLayout.parseInstance(new A());
    System.out.println(classLayout.toPrintable());
}
```

### 启用 oop

首先看一下启用了 oop 的内存分布，我们在单元测试的启动参数中，加入`-XX:+UseCompressedOops`：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210817142450.png?x-oss-process=style/yano)

执行单元测试，输出结果如下：

```java
test.jdk.ClassSizeTest$A object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000005 (biasable; age: 0)
  8   4        (object header: class)    0x08014b4f
 12   4        (object alignment gap)    
Instance size: 16 bytes
Space losses: 0 bytes internal + 4 bytes external = 4 bytes total
```

可以看出 class A 的对象实例，object header: mark 是 8 个字节，object header: class 是 4 个字节，由于两个加起来是 12 个字节，并不是 8 的整数倍，所以填充了 4 个字节，最终对象实例占用了 16 个字节。

### 禁用 oop

接着看一下禁用 oop 的内存分布，单元测试的启动参数中，加入`-XX:-UseCompressedOops`（注意中间是减号，不是加号）：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210817142804.png?x-oss-process=style/yano)

执行单元测试，输出结果如下：

```java
test.jdk.ClassSizeTest$A object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x000000000000000d (biasable; age: 1)
  8   8        (object header: class)    0x0000000232b9b0e0
Instance size: 16 bytes
Space losses: 0 bytes internal + 0 bytes external = 0 bytes total
```

可以看出 class A 的对象实例，object header: mark 是 8 个字节，object header: class 也是 8 个字节，由于两个加起来是 16 个字节，是 8 的整数倍，所以没有填充，最终对象实例占用了 16 个字节，没有空间损失。

## 测试复杂对象

这次对象复杂一点，里面有 4 个变量：占 4 字节的 int 型，占 1 个字节的布尔型，占 8 个字节的 double 型，占 1 个字节的布尔型。

```java
static class B {
    int a;
    boolean b;
    double c;
    boolean d;
}
```

测试的单元方法如下：

```java
@Test
public void testClass() {
    ClassLayout classLayout = ClassLayout.parseInstance(new B());
    System.out.println(classLayout.toPrintable());
}
```

### 启用 oop

```java
test.jdk.ClassSizeTest$B object internals:
OFF  SZ      TYPE DESCRIPTION               VALUE
  0   8           (object header: mark)     0x0000000000000005 (biasable; age: 0)
  8   4           (object header: class)    0x08016f76
 12   4       int B.a                       0
 16   8    double B.c                       0.0
 24   1   boolean B.b                       false
 25   1   boolean B.d                       false
 26   6           (object alignment gap)    
Instance size: 32 bytes
Space losses: 0 bytes internal + 6 bytes external = 6 bytes total
```

首先可以看到，class B 对象实例内部并没有按照代码里的声明顺序，B 中有 2 个布尔值，每个都占 1 个字节，实例变量中这 2 个变量是分配在了对象的最后，这样能够节省空间。最终这个对象只浪费了 6 个字节作地址对齐。

### 禁用 oop

```java
test.jdk.ClassSizeTest$B object internals:
OFF  SZ      TYPE DESCRIPTION               VALUE
  0   8           (object header: mark)     0x0000000000000005 (biasable; age: 0)
  8   8           (object header: class)    0x000000023b87aac8
 16   8    double B.c                       0.0
 24   4       int B.a                       0
 28   1   boolean B.b                       false
 29   1   boolean B.d                       false
 30   2           (object alignment gap)    
Instance size: 32 bytes
Space losses: 0 bytes internal + 2 bytes external = 2 bytes total
```

写不动了，不分析了……

## 包含对象引用的对象

在上面 class B 的基础上，再加一个引用类型~

```java
static class C {
    int a;
    boolean b;
    double c;
    boolean d;
    Integer e;
}
```

单元测试代码：

```java
@Test
public void testClass2() {
    ClassLayout classLayout = ClassLayout.parseInstance(new C());
    System.out.println(classLayout.toPrintable());
}
```

### 启用 oop

```java
test.jdk.ClassSizeTest$C object internals:
OFF  SZ                TYPE DESCRIPTION               VALUE
  0   8                     (object header: mark)     0x0000000000000005 (biasable; age: 0)
  8   4                     (object header: class)    0x08014b91
 12   4                 int C.a                       0
 16   8              double C.c                       0.0
 24   1             boolean C.b                       false
 25   1             boolean C.d                       false
 26   2                     (alignment/padding gap)   
 28   4   java.lang.Integer C.e                       null
Instance size: 32 bytes
Space losses: 2 bytes internal + 0 bytes external = 2 bytes total
```

和上面示例的区别，主要在下面这 2 行：

```java
 26   2                     (alignment/padding gap)   
 28   4   java.lang.Integer C.e                       null
```

C 的实例对象总共占用了 32 个字节，其中内部因为对齐损失了 2 个字节，外部没有损失。Integer 对象的引用是占 4 个字节的。

### 禁用 oop

```java
test.jdk.ClassSizeTest$C object internals:
OFF  SZ                TYPE DESCRIPTION               VALUE
  0   8                     (object header: mark)     0x000000000000000d (biasable; age: 1)
  8   8                     (object header: class)    0x000000023537aae8
 16   8              double C.c                       0.0
 24   4                 int C.a                       0
 28   1             boolean C.b                       false
 29   1             boolean C.d                       false
 30   2                     (alignment/padding gap)   
 32   8   java.lang.Integer C.e                       null
Instance size: 40 bytes
Space losses: 2 bytes internal + 0 bytes external = 2 bytes total
```

C 的实例对象总共占用了 40 个字节，其中内部因为对齐损失了 2 个字节，外部没有损失。Integer 对象的引用是占 8 个字节的。

# 总结

- `引用类型大小`：在 64 位系统上占用 8 字节，开启指针压缩 oop 后占用 4 字节；在 32 位系统上占用 4 字节。
- `对象占用大小`：对象头+实例数据+padding 填充字节，对象所占字节必须是 8 的整数倍。
- `对象头大小`：在 64 位系统上占用 16 字节，开启指针压缩 oop 后占用 12 个字节。
- `指针压缩的对象（64 位系统）`：
  - 对象的全局静态变量
  - 对象头信息（由 16 字节→12 字节）
  - 对象的引用类型（由 8 字节→4 字节）
  - 对象数组类型（由 24 字节→16 字节）

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！

原创不易，希望大家转载时请先联系我，并标注原文链接。