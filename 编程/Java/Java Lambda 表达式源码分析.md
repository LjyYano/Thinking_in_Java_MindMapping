---
date: 2021-08-18
---


- [基本概念](#基本概念)
  - [Lambda 表达式](#lambda-表达式)
  - [函数式接口](#函数式接口)
  - [方法引用](#方法引用)
- [深入实现原理](#深入实现原理)
  - [字节码](#字节码)
  - [为什么不使用匿名内部类？](#为什么不使用匿名内部类)
  - [invokedynamic](#invokedynamic)
- [总结](#总结)
- [参考链接](#参考链接)
- [GitHub 项目](#github-项目)

Lambda 表达式是什么？JVM 内部究竟是如何实现 Lambda 表达式的？为什么要这样实现？

# 基本概念

## Lambda 表达式

下面的例子中，`() -> System.out.println("1")` 就是一个 Lambda 表达式。Java 8 中每一个 Lambda 表达式必须有一个函数式接口与之对应。Lambda 表达式就是函数式接口的一个实现。

```java
@Test
public void test0() {
    Runnable runnable = () -> System.out.println("1");
    runnable.run();

    ToIntBiFunction<Integer, Integer> function = (n1, n2) -> n1 + n2;
    System.out.println(function.applyAsInt(1, 2));

    ToIntBiFunction<Integer, Integer> function2 = Integer::sum;
    System.out.println(function2.applyAsInt(1, 2));
}
```

大致形式就是 `(param1, param2, param3, param4…) -> { doing…… };`

## 函数式接口

首先要从 FunctionalInterface 注解讲起，详情见 [Annotation Type FunctionalInterface](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/FunctionalInterface.html)。

> An informative annotation type used to indicate that an interface type declaration is intended to be a functional interface as defined by the Java Language Specification. Conceptually, a functional interface has exactly one abstract method. Since default methods have an implementation, they are not abstract. If an interface declares an abstract method overriding one of the public methods of java.lang.Object, that also does not count toward the interface's abstract method count since any implementation of the interface will have an implementation from java.lang.Object or elsewhere.

简单总结一下函数式接口的特征：

- FunctionalInterface 注解标注一个函数式接口，不能标注类，方法，枚举，属性这些。
- 如果接口被标注了 @FunctionalInterface，这个类就必须符合函数式接口的规范。
- 即使一个接口没有标注 @FunctionalInterface，如果这个接口满足函数式接口规则，依旧可以被当作函数式接口。

注意：interface 中重写 Object 类中的抽象方法，不会增加接口的方法数，因为接口的实现类都是 Object 的子类。

我们可以看到 Runnable 接口，里面只有一个抽象方法 `run()`，则这个接口就是一个函数式接口。

```java
@FunctionalInterface
public interface Runnable {
    public abstract void run();
}
```

## 方法引用

所谓方法引用，是指如果某个方法签名和接口恰好一致，就可以直接传入方法引用。文章开头的示例中，下面这块代码就是方法引用。

```java
ToIntBiFunction<Integer, Integer> function2 = Integer::sum;
```

java.lang.Integer#sum 的实现如下：

```java
public static int sum(int a, int b) {
    return a + b;
}
```

比如我们计算一个 Stream 的和，可以直接传入 `Integer::sum` 这个方法引用。

```java
@Test
public void test1() {
    Integer sum = IntStream.range(0, 10).boxed().reduce(Integer::sum).get();
    System.out.println(sum);
}
```

上面的代码中，为什么可以直接在 reduce 方法中传入 `Integer::sum` 这个方法引用呢？这是因为 reduce 方法的入参就是 `BinaryOperator` 的函数式接口。

```java
Optional<T> reduce(BinaryOperator<T> accumulator);
```

`BinaryOperator` 是继承自 `BiFunction`，定义如下：

```java
@FunctionalInterface
public interface BiFunction<T, U, R> {

    R apply(T t, U u);

    default <V> BiFunction<T, U, V> andThen(Function<? super R, ? extends V> after) {
        Objects.requireNonNull(after);
        return (T t, U u) -> after.apply(apply(t, u));
    }
}
```

可以看到，只要是符合 `R apply(T t, U u);` 的方法引用，都可以传入 reduce 中。可以是上面代码中的 `Integer::sum`，也可以是 `Integer::max`。

# 深入实现原理

## 字节码

首先写 2 个 Lambda 方法：

```java
public class LambdaMain {

    public static void main(String[] args) {
        new Thread(() -> System.out.println("1")).start();
        IntStream.range(0, 5).boxed().filter(i -> i < 3).map(i -> i + "").collect(Collectors.toList());
    }
}
```

之后 `javac LambdaMain.java` 编译成字节码文件，再通过 `javap -p LambdaMain` 输出 class 文件的所有类和成员，得到输出结果：

```java
Compiled from "LambdaMain.java"
public class test.jdk.LambdaMain {
  public test.jdk.LambdaMain();
  public static void main(java.lang.String[]);
  private static java.lang.String lambda$main$2(java.lang.Integer);
  private static boolean lambda$main$1(java.lang.Integer);
  private static void lambda$main$0();
}
```

- 输出的 `void lambda$main$0()` 对应的是 `() -> System.out.println("1")`
- 输出的 `boolean lambda$main$1(java.lang.Integer)` 对应的是 `i -> i < 3`
- 输出的 `java.lang.String lambda$main$2(java.lang.Integer)` 对应的是 `i -> i + ""`

我们可以看出 Lambda 表达式在 Java 8 中首先会生成一个`私有的静态函数`。

## 为什么不使用匿名内部类？

如果要在 Java 语言中实现 lambda 表达式，生成匿名内部类就可以轻松实现。但是 JDK 为什么没有这么实现呢？这是因为匿名内部类有一些缺点。

1. 每个匿名内部类都会在`编译时`创建一个对应的`class 文件`，在`运行时`不可避免的会有加载、验证、准备、解析、初始化等`类加载`过程。
2. 每次调用都会创建一个这个`匿名内部类 class 的实例对象`，无论是有状态的（使用到了外部的变量）还是无状态（没有使用外部变量）的内部类。

## invokedynamic

本来要写文字的，但是俺发现俺总结的思维导图还挺清晰的，直接提出来吧，囧。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210820085524.png?x-oss-process=style/yano)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210820085748.png?x-oss-process=style/yano)

详情见 [Class LambdaMetafactory 官方文档](https://docs.oracle.com/javase/8/docs/api/java/lang/invoke/LambdaMetafactory.html)，java.lang.invoke.LambdaMetafactory#metafactory 的实现。

```java
public static CallSite metafactory(MethodHandles.Lookup caller,
                                    String invokedName,
                                    MethodType invokedType,
                                    MethodType samMethodType,
                                    MethodHandle implMethod,
                                    MethodType instantiatedMethodType)
        throws LambdaConversionException {
    AbstractValidatingLambdaMetafactory mf;
    mf = new InnerClassLambdaMetafactory(caller, invokedType,
                                            invokedName, samMethodType,
                                            implMethod, instantiatedMethodType,
                                            false, EMPTY_CLASS_ARRAY, EMPTY_MT_ARRAY);
    mf.validateMetafactoryArgs();
    return mf.buildCallSite();
}
```

其主要的概念有如下几个：

- invokedynamic 字节码指令：运行时 JVM 第一次到某个地方的这个指令的时候会进行 linkage，会调用用户指定的 Bootstrap Method 来决定要执行什么方法，之后便不需要这个步骤。
- Bootstrap Method: 用户可以自己编写的方法，最终需要返回一个 CallSite 对象。
- CallSite: 保存 MethodHandle 的容器，里面有一个 target MethodHandle。
MethodHandle: 真正要执行的方法的指针。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210820090707.png?x-oss-process=style/yano)

测试一下 Lambda 函数生成的字节码，为了方便起见，java 代码改成如下：

```java
public class LambdaMain {

    public static void main(String[] args) {
        new Thread(() -> System.out.println("1")).start();
    }
}
```

先编译成 class 文件，之后再反汇编 `javap -c -p LambdaMain` 看下输出：

```java
Compiled from "LambdaMain.java"
public class test.jdk.LambdaMain {
  public test.jdk.LambdaMain();
    Code:
       0: aload_0
       1: invokespecial #1                  // Method java/lang/Object."<init>":()V
       4: return

  public static void main(java.lang.String[]);
    Code:
       0: new           #2                  // class java/lang/Thread
       3: dup
       4: invokedynamic #3,  0              // InvokeDynamic #0:run:()Ljava/lang/Runnable;
       9: invokespecial #4                  // Method java/lang/Thread."<init>":(Ljava/lang/Runnable;)V
      12: invokevirtual #5                  // Method java/lang/Thread.start:()V
      15: return

  private static void lambda$main$0();
    Code:
       0: getstatic     #6                  // Field java/lang/System.out:Ljava/io/PrintStream;
       3: ldc           #7                  // String 1
       5: invokevirtual #8                  // Method java/io/PrintStream.println:(Ljava/lang/String;)V
       8: return
}
```

可以看到 Thread 里的 Runnable 实现是通过 invokedynamic 调用的。详细情况 [JVM 虚拟机规范](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html#jvms-4.7.23)，等有时间再补充吧~~~

# 总结

- Lambda 表达式在 Java 中最终编译成`私有的静态函数`，JDK 最终使用 invokedynamic 字节码指令调用。

# 参考链接

- [Java--浅析函数式接口&Lambda 表达式&方法引用&Stream API
](https://juejin.cn/post/6931614095124725773)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。