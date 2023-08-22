---
date: 2020-09-19
---

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-09-19-095525.jpg)

JDK 15已经在2020年9月15日发布！详情见 [JDK 15 官方计划](https://openjdk.java.net/projects/jdk/15/)。下面是对 JDK 15 所有新特性的详细解析！

# 官方计划

* 2019/12/12		Rampdown Phase One (fork from main line)
* 2020/06/11		Rampdown Phase One (fork from main line)
* 2020/07/16		Rampdown Phase Two
* 2020/08/06		Initial Release Candidate
* 2020/08/20		Final Release Candidate
* 2020/09/15		General Availability

# 特性预览

- 339:	爱德华兹曲线数字签名算法（EdDSA）
- 360:	Sealed Classes (Preview)
- 371:	Hidden Classes
- 372:	移除 Nashorn JavaScript 引擎
- 373:	重新实现 DatagramSocket API
- 374:	禁用偏向锁
- 375:	instanceof的模式匹配（Second Preview）
- 377:	ZGC: 可扩展的低延迟垃圾收集器
- 378:	文本块
- 379:	Shenandoah: 低暂停时间的垃圾收集器
- 381:	删除 Solaris 和 SPARC Ports
- 383:	外部存储器访问API (Second Incubator)
- 384:	Records (Second Preview)
- 385:	废弃 RMI Activation

# 深入理解新特性

## 339:	爱德华兹曲线数字签名算法（EdDSA）

[JEP 339: Edwards-Curve Digital Signature Algorithm (EdDSA)](https://openjdk.java.net/jeps/339)

与其他签名方案相比，EdDSA 具有更高的安全性和性能，并且已有很多其他加密库（如 OpenSSL 和 BoringSSL）支持此签名方案。EdDSA 是 TLS 1.3的可选组件，且是 TLS 1.3 中仅有的三种签名方案之一。用户可以不必再使用第三方库了。

## 360:	Sealed Classes (Preview)

[JEP 360: Sealed Classes (Preview)](https://openjdk.java.net/jeps/360)

### 为什么需要此特性

在 Java 语言中，代码的重用是通过类的继承实现的：多个子类可以继承同一个超类（并重用超类的方法）。但是重用代码并不是类层次结构的唯一目的，有时类层次结构仅仅是对某个领域的建模。以这种方式使用类层次结构时，限制子类集合可以简化建模。

比如在图形库中，Shape 类的开发者可能只希望有限个数的类扩展 Shape 类，开发者并不想为未知子类编写防御代码。以前的 Java 并不会限制 Shape 类的扩展属性，Shape 类可以拥有任意数量的子类。在封闭类（Sealed Classes）中，类层次结构是封闭的，但是代码仍然可以在有限范围内重用。

### 特性描述

通过 `sealed` 修饰符将一个类声明为密封类，permits子句指定允许扩展密封类的类。例如下面的 Shape 类声明指定了三个可扩展的子类。

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

### JDK 中的密封类

```java
package java.lang.constant;

public sealed interface ConstantDesc
    permits String, Integer, Float, Long, Double,
            ClassDesc, MethodTypeDesc, DynamicConstantDesc {...}

// ClassDesc is designed for subclassing by JDK classes only
public sealed interface ClassDesc extends ConstantDesc
    permits PrimitiveClassDescImpl, ReferenceClassDescImpl {...}
final class PrimitiveClassDescImpl implements ClassDesc {...}
final class ReferenceClassDescImpl implements ClassDesc {...} 

// MethodTypeDesc is designed for subclassing by JDK classes only
public sealed interface MethodTypeDesc extends ConstantDesc
    permits MethodTypeDescImpl {...}
final class MethodTypeDescImpl implements MethodTypeDesc {...}

// DynamicConstantDesc is designed for subclassing by user code
public non-sealed abstract class DynamicConstantDesc implements ConstantDesc {...}
```

### JVM 支持

JVM 在运行时识别密封类和接口，并防止未经授权的子类和子接口扩展密封类。

尽管 sealed 关键字是类修饰符，但是 ClassFile 中并没有 ACC_SEALED 标志。相反，密封类的类文件具有 PermittedSubclasses属性，该属性隐式指示密封修饰符，并显式指定允许的子类：

```java
PermittedSubclasses_attribute {
    u2 attribute_name_index;
    u4 attribute_length;
    u2 number_of_classes;
    u2 classes[number_of_classes];
}
```

### Reflection API

`java.lang.Class` 将增加如下 public 方法：

- java.lang.constant.ClassDesc[] getPermittedSubclasses()
- boolean isSealed()

## 371: Hidden Classes

[JEP 371: Hidden Classes](https://openjdk.java.net/jeps/371)

### 为什么需要此特性

隐藏类不能被其他类的字节码直接使用，适合在运行时生成类、并通过反射间接使用隐藏类的框架。

### 特性描述

许多机遇 JVM 构建的语言都通过动态生成类，提高灵活性和效率。比如在 Java 语言中，javac 不会在编译时将 lambda 表达式转换成特殊的类文件，而是保存在字节码中，该字节码可以把 lambda 表达式动态生成为相应的对象。同样地，非 Java 语言经常通过运行时生成动态代理，来实现语言的高级特性。

语言的实现者通常希望将动态生成的类，在逻辑上成为静态生成类的实现的一部分：

- 不可发现。仅通过名字就发现该类是不必要且有害的，因为这破坏了`动态生成类仅是静态生成类的实现细节`这一目标。
- 访问控制。可能希望将静态生成类的访问控制扩展到动态生成类。
- 生命周期。动态生成类的生命周期可能很短，在静态生成类中保留它们会占用不必要的内存。针对这种情况的现有解决方案（类加载器）不仅麻烦，而且效率低下。

不幸的是，类定义的标准 API（ClassLoader::defineClass 和 Lookup::defineClass）并不在意该类的字节码是动态生成（在运行时）还是静态生成（在编译时）的。如果标准 API 可以定义无法被发现，且具有有限生命周期的隐藏类，则动态生成类的 JDK 内部和外部框架都可以定义隐藏类，这样做可以提高 JVM 语言实现的效率。比如：

- java.lang.reflect.Proxy 可以定义隐藏类作为实现代理接口的代理类；
- java.lang.invoke.StringConcatFactory 可以生成隐藏类来保存常量连接方法；
- java.lang.invoke.LambdaMetaFactory 可以生成隐藏的 nestmate 类，以容纳访问封闭变量的 lambda 主体。

## 372:	移除 Nashorn JavaScript 引擎

[JEP 372: Remove the Nashorn JavaScript Engine](https://openjdk.java.net/jeps/372)

### 特性描述

Java 11 中已经将该引擎标记为废弃，并明确表示要在将来的版本中删除它。Nashorn JavaScript 引擎最开始是 JDK 8 通过 JEP 174 继承的，用来代替 Rhino 脚本引擎，当时 Nashorn JavaScript 引擎是 ECMAScript-262 5.1 标准的完整实现。但是随着 ECMAScript 语言构造以及 API 的修改，我们发现 Nashorn 难以维护。

JDK 的两个模块会永久删除：

- jdk.scripting.nashorn
- jdk.scripting.nashorn.shell

## 373:	重新实现 DatagramSocket API

[JEP 373: Reimplement the Legacy DatagramSocket API](https://openjdk.java.net/jeps/373)

Java.net.DatagramSocket 和 java.net.MulticastSocket API 重构了基础实现，使得其更易于维护和调试。新的实现能更好地适应虚拟线程的工作。

## 374:	禁用偏向锁

[JEP 374: Disable and Deprecate Biased Locking](https://openjdk.java.net/jeps/374)

### 特性描述

默认情况下禁用偏向锁，并废弃所有相关的命令行。

### 为什么需要此特性

偏向锁是 HotSpot 虚拟机使用的一项优化技术，能够减少无竞争锁定时的开销。偏向锁的目的是假定 monitor 一直由某个特定线程持有，直到另一个线程尝试获取它，这样就可以避免获取 monitor 时执行 cas 的原子操作。monitor 首次锁定时偏向该线程，这样就可以避免同一对象的后续同步操作步骤需要原子指令。从历史上看，偏向锁使得 JVM 的性能得到了显著改善。

但是过去看到的性能提升，在现在看来已经不那么明显了。受益于偏向锁的应用程序，往往是使用了早期 Java 集合 API的程序（JDK 1.1），这些 API（Hasttable 和 Vector） 每次访问时都进行同步。JDK 1.2 引入了针对单线程场景的非同步集合（HashMap 和 ArrayList），JDK 1.5 针对多线程场景推出了性能更高的并发数据结构。这意味着如果代码更新为使用较新的类，由于不必要同步而受益于偏向锁的应用程序，可能会看到很大的性能提高。此外，围绕线程池队列和工作线程构建的应用程序，性能通常在禁用偏向锁的情况下变得更好。

偏向锁为同步系统引入了许多复杂的代码，并且对 HotSpot 的其他组件产生了影响。这种复杂性已经成为理解代码的障碍，也阻碍了对同步系统进行重构。因此，我们希望禁用、废弃并最终删除偏向锁。

## 375:	instanceof的模式匹配（Second Preview）

[JEP 375: Pattern Matching for instanceof (Second Preview)](https://openjdk.java.net/jeps/375)

### 为什么需要此特性

通过对 instanceof 运算符进行模式匹配，来增加 Java 语言。模式匹配可以使应用程序更简洁、安全地提取特定对象。

## 特性描述

很多程序都会判断一个表达式是否具有某种类型或结构，然后有条件地进一步处理，比如下面的 instanceof-and-cast 用法：

```java
if (obj instanceof String) {
    String s = (String) obj;
    // use s
}
```

上述代码做了 3 件事：

- 判断 obj 是否是 string 类型
- 将 obj 转换为 string 类型
- 声明了一个新的局部变量 s

这种模式很简单，但是这样的写法并不是最优的。第 2 步的类型转换是重复的，同时重复可能会带来错误。模式匹配允许简明地表达对象的所需“形状”（模式），并允许各种语句和表达式针对其输入来测试“形状”（匹配）。从 Haskell 到 C＃ 等很多语言都接受了模式匹配。

 在下面的代码中，短语 String s 是类型测试模式：
 
 ```java
if (obj instanceof String s) {
    // can use s here
} else {
    // can't use s here
}
```

下面的代码也是正确的：

```java
if (obj instanceof String s && s.length() > 5) {.. s.contains(..) ..}
```

## 377:	ZGC: 可扩展的低延迟垃圾收集器

[JEP 377: ZGC: A Scalable Low-Latency Garbage Collector (Production)](https://openjdk.java.net/jeps/377)

ZGC 已经在 JEP 333时集成到了 JDK 11 中，当时是作为实验特性引入的。在 JDK 11 发布以来，我们收到了很多积极的反馈，并修复了许多 bug，添加了很多新功能。更重要的是，ZGC 已经支持所有主流平台：

- Linux/x86_64 (JEP 333)
- Linux/aarch64 (8214527)
- Windows (JEP 365)
- macOS (JEP 364)

现在可以通过 `-XX：+UnlockExperimentalVMOptions -XX：+UseZGC` 命令选项启用 ZGC。

## 378:	文本块 

[JEP 378: Text Blocks](https://openjdk.java.net/jeps/378)

Java语言增加文本块功能。文本块是多行字符串文字，能避免大多数情况下的转义问题。

### 为什么需要此特性

在Java中，HTML, XML, SQL, JSON等字符串对象都很难阅读和维护。

#### HTML

使用`one-dimensional`的字符串语法：

```java
String html = "<html>\n" +
              "    <body>\n" +
              "        <p>Hello, world</p>\n" +
              "    </body>\n" +
              "</html>\n";
```

使用`two-dimensional`文本块语法：

```java
String html = """
              <html>
                  <body>
                      <p>Hello, world</p>
                  </body>
              </html>
              """;
```

#### SQL

使用`one-dimensional`的字符串语法：

```java
String query = "SELECT `EMP_ID`, `LAST_NAME` FROM `EMPLOYEE_TB`\n" +
               "WHERE `CITY` = 'INDIANAPOLIS'\n" +
               "ORDER BY `EMP_ID`, `LAST_NAME`;\n";
```

使用`two-dimensional`文本块语法：

```java
String query = """
               SELECT `EMP_ID`, `LAST_NAME` FROM `EMPLOYEE_TB`
               WHERE `CITY` = 'INDIANAPOLIS'
               ORDER BY `EMP_ID`, `LAST_NAME`;
               """;
```

#### 多语言示例

使用`one-dimensional`的字符串语法：

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
Object obj = engine.eval("function hello() {\n" +
                         "    print('\"Hello, world\"');\n" +
                         "}\n" +
                         "\n" +
                         "hello();\n");
```

使用`two-dimensional`文本块语法：

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
Object obj = engine.eval("""
                         function hello() {
                             print('"Hello, world"');
                         }
                         
                         hello();
                         """);
```

### 特性描述

文本块是Java语言的新语法，可以用来表示任何字符串，具有更高的表达能力和更少的复杂度。

文本块的开头定界符是由三个双引号字符（"""）组成的序列，后面跟0个或多个空格，最后跟一个行终止符。内容从开头定界符的行终止符之后的第一个字符开始。

结束定界符是三个双引号字符的序列。内容在结束定界符的第一个双引号之前的最后一个字符处结束。

与字符串文字中的字符不同，文本块的内容中可以直接包含双引号字符。允许在文本块中使用\“，但不是必需的或不建议使用。

与字符串文字中的字符不同，内容可以直接包含行终止符。允许在文本块中使用\n，但不是必需或不建议使用。例如，文本块：

```java
"""
line 1
line 2
line 3
"""
```

等效于字符串文字：

```java
"line 1\nline 2\nline 3\n"
```

或字符串文字的串联：

```java
"line 1\n" +
"line 2\n" +
"line 3\n"
```

## 379:	Shenandoah: 低暂停时间的垃圾收集器

[JEP 379: Shenandoah: A Low-Pause-Time Garbage Collector (Production)](https://openjdk.java.net/jeps/379)

### 特性描述

Shenandoah GC 由JEP 189 集成到 JDK 12 中。现在，Shenandoah GC 已经可以用于生产环境了！（Shenandoah GC 的具体特性以后会有专门的文章讲解，本篇文章略过）。

## 381:	删除 Solaris 和 SPARC Ports

[JEP 381: Remove the Solaris and SPARC Ports](https://openjdk.java.net/jeps/381)

删除了对 Solaris/SPARC、Solaris/x64和 Linux/SPARC 端口支持的源代码，并重新构建 JDK。这些代码在 JDK 14中已经被标记为废弃的，并明确表示在未来版本中会删除。

## 383:	外部存储器访问API (Second Incubator)

[JEP 383: Foreign-Memory Access API (Second Incubator)](https://openjdk.java.net/jeps/383)

引入新的能使 Java 程序安全高效访问 Java 堆内存之外的外部内存的 API。

## 384:	Records (Second Preview)

[JEP 384: Records (Second Preview)](https://openjdk.java.net/jeps/384)

通过 `Records`（不知道如何翻译，囧……）增强Java编程语言。Records提供了一种紧凑的语法来声明类，这些类是浅层不可变数据的透明持有者。

### 为什么需要此特性

我们经常听到这样的抱怨：“Java太冗长”、“Java规则过多”。首当其冲的就是充当简单集合的“数据载体”的类。为了写一个数据类，开发人员必须编写许多低价值、重复且容易出错的代码：构造函数、访问器、equals()、hashCode()和toString()等等。

尽管IDE可以帮助开发人员编写数据载体类的绝大多数编码，但是这些代码仍然冗长。

从表面上看，将Records是为了简化模板编码而生的，但是它还有“远大”的目标：`modeling data as data`。records应该更简单、简洁、数据不可变。

### 描述

records是Java的一种新的类型。同枚举一样，records也是对类的一种限制。records放弃了类通常享有的特性：将API和表示解耦。但是作为回报，records使数据类变得非常简洁。

一个record具有名称和状态描述。状态描述声明了record的组成部分。例如：

```java
record Point(int x, int y) { }
```

因为records在语义上是数据的简单透明持有者，所以记录会自动获取很多标准成员：

- 状态声明中的每个成员，都有一个 private final的字段；
- 状态声明中的每个组件的公共读取访问方法，该方法和组件具有相同的名字；
- 一个公共的构造函数，其签名与状态声明相同；
- equals和hashCode的实现；
- toString的实现。

### 限制

records不能扩展任何类，并且不能声明私有字段以外的实例字段。声明的任何其他字段都必须是静态的。

records类都是隐含的final类，并且不能是抽象类。这些限制使得records的API仅由其状态描述定义，并且以后不能被其他类实现或继承。

### 在record中额外声明变量

也可以显式声明从状态描述自动派生的任何成员。可以在没有正式参数列表的情况下声明构造函数（这种情况下，假定与状态描述相同），并且在正常构造函数主体正常完成时调用隐式初始化（this.x=x）。这样就可以在显式构造函数中仅执行其参数的验证等逻辑，并省略字段的初始化，例如：

```java
record Range(int lo, int hi) {
  public Range {
    if (lo > hi)  /* referring here to the implicit constructor parameters */
      throw new IllegalArgumentException(String.format("(%d,%d)", lo, hi));
  }
}
```

### 语法

```java
RecordDeclaration:
  {ClassModifier} record TypeIdentifier [TypeParameters] 
    (RecordComponents) [SuperInterfaces] [RecordBody]

RecordComponents:
  {RecordComponent {, RecordComponent}}

RecordComponent:
  {Annotation} UnannType Identifier

RecordBody:
  { {RecordBodyDeclaration} }

RecordBodyDeclaration:
  ClassBodyDeclaration
  RecordConstructorDeclaration

RecordConstructorDeclaration:
  {Annotation} {ConstructorModifier} [TypeParameters] SimpleTypeName
    [Throws] ConstructorBody
```

### 反射 API

下面的方法会被加到`java.lang.Class`中：

* RecordComponent[] getRecordComponents()
* boolean isRecord()

## 385:	废弃 RMI Activation

[JEP 385: Deprecate RMI Activation for Removal](https://openjdk.java.net/jeps/385)

将 `RMI Activation` 机制标记为废弃，以便在将来的某个版本删除掉。RMI Activation 是 RMI 的过时部分，但是这并不表示会弃用 RMI 的其他部分。

# 总结

以上就是 `JDK 15` 的全部新特性，我们可以看到 G1 GC 已经退出历史舞台，新的 `ZGC`、`Shenandoah GC` 已经登上历史舞台。同时也丢弃了像`自旋锁`这种历史包袱，增加了许多诸如`文本块`等简洁的语法特性。我们可以预见 Java 的性能会越来越好，同时也会越来越简洁。（当然简洁程度跟 Kotlin 这种新兴语言是比不了的，毕竟完全没有历史包袱）。欢迎大家关注我的公众号。

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)
