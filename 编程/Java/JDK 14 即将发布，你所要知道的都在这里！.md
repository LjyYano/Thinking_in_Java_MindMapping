---
date: 2020-01-07
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

[toc]

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-01-07-103612.jpg)

JDK 14预计在2020年3月17日发布，详情见 [JDK 14 官方计划](https://openjdk.java.net/projects/jdk/14/)。

# 官方计划

* 2019/12/12		Rampdown Phase One (fork from main line)
* 2020/01/16		Rampdown Phase Two
* 2020/02/06		Initial Release Candidate
* 2020/02/20		Final Release Candidate
* 2020/03/17		General Availability

# 特性预览

* 305:	instanceof 的模式匹配 (预览)
* 343:	打包工具 (Incubator)
* 345:	G1的NUMA内存分配优化
* 349:	JFR事件流
* 352:	非原子性的字节缓冲区映射
* 358:	友好的空指针异常
* 359:	Records (预览)
* 361:	Switch表达式 (标准)
* 362:	弃用Solaris和SPARC端口
* 363:	移除CMS（Concurrent Mark Sweep）垃圾收集器
* 364:	macOS系统上的ZGC
* 365:	Windows系统上的ZGC
* 366:	弃用ParallelScavenge + SerialOld GC组合
* 367:	移除Pack200 Tools 和 API
* 368:	文本块 (第二个预览版)
* 370:	外部存储器API (Incubator)

# 深入理解新特性

## 305:	instanceof的模式匹配 (预览)

[JEP 305: Pattern Matching for instanceof \(Preview\)](https://openjdk.java.net/jeps/305)

使instanceof运算符具有模式匹配的能力。模式匹配能够使程序的通用逻辑更加简洁，同时也更加安全。

### 动机

几乎每个程序都包含判断表达式是否具有某种类型的逻辑，程序会对不同类型进行不同的处理。所有Java程序员都熟悉下面的`instanceof-and-cast`用法：

```java
if (obj instanceof String) {
    String s = (String) obj;
    // use s
}
```

这段程序做了3件事：

1. 一个判断（obj是一个String？）
2. 一个类型转换（将对象obj强制类型转换为String）
3. 声明一个新的本地变量s，指向上面的obj String

这种模式很简单，并且几乎所有Java程序员都可以理解。但是出于以下原因，上述做法并不是最理想的：

1. 语法乏味
2. 同时执行类型检测和类型转换并不是必要的
3. String类型在程序中出现了3次，这混淆了后面更重要的逻辑
4. 重复的代码容易滋生错误

与其把上述方式作为临时解决方案，不如去使用模式匹配。我们可以通过模式匹配简洁地表达对象，并允许各种语句和表达式对其进行测试。许多语言——从Haskell到C#，都因为简洁性和安全性选择了模式匹配。

### 具体描述

示例代码：

```java
if (obj instanceof String s) {
    // can use s here
} else {
    // can't use s here
}
```

`instanceof`运算符“匹配”规则如下：

- 如果obj是String类型，则将obj类型转换为String，并将其赋值给变量`s`。绑定的变量作用域为if语句内部，并不在false语句块内。

## 343:	打包工具 (Incubator)

[JEP 343: Packaging Tool \(Incubator\)](https://openjdk.java.net/jeps/343)

创建用于打包能独立运行的Java应用程序的工具。

### 动机

许多Java程序需要以“first-class”方式安装在本机平台，而不是简单地将其放置在类路径或模块路径上。对于应用开发人员来说，仅仅是交付简单的JAR文件是不够的。他们必须提供适合本机平台的软件安装包：需要以用户熟悉的方式分发、安装和卸载Java程序。比如在Windows上，用户希望双击一个软件包就能安装，然后可以在控制面板上卸下该软件；在MacOS上，用户希望双击DMG文件，将其应用程序拖放到Application文件夹中。

### 描述

`jpackage`打包工具可以将Java应用程序打包为针对特定平台的安装包，这个安装包包含所有必需的依赖项。该应用程序可以以普通JAR文件集合或模块集合的方式提供。软件包格式可以分为：

1. Linux：deb 和 rpm
2. macOS：pkg 和 dmg
3. Windows：msi 和 exe

#### 基本用法：非模块化应用

假设你有一个由JAR文件组成的应用程序，所有应用程序都位于lib目录下，并且主类在lib/main.jar中。下列命令

```java
$ jpackage --name myapp --input lib --main-jar main.jar
```

将以本地系统的默认格式打包应用程序，并将生成的打包文件保留在当前目录中。如果main.jar中的MANIFEST.MF文件没有Main-Class属性，我们必须显式地指定主类：

```java
$ jpackage --name myapp --input lib --main-jar main.jar --main-class myapp.Main
```

打包的名称是myapp。要启动该应用程序，启动器将从输入目录复制的每个JAR文件都放在JVM的类路径上。

如果希望生成默认格式以外的软件安装包，可以使用`--type`选项。例如要在macOS上生成pkg文件（而不是dmg文件），我们可以使用下面的命令：

```java
$ jpackage --name myapp --input lib --main-jar main.jar --type pkg
```

#### 基本用法：模块化应用

如果你有一个模块化应用程序，该应用程序由lib目录中的模块化JAR文件和/或JMOD文件组成，并且主类位于myapp模块中，则下面的命令

```java
$ jpackage --name myapp --module-path lib -m myapp
```

能够将其打包。如果myapp模块无法识别主类，则必须明确指定：

```java
$ jpackage --name myapp --module-path lib -m myapp/myapp.Main
```

## G1的NUMA内存分配优化

[JEP 345: NUMA-Aware Memory Allocation for G1](https://openjdk.java.net/jeps/345)

通过实现可识别NUMA的内存分配，提高大型计算机上的G1性能。

### 动机

现代的多插槽计算机越来越多地具有非统一的内存访问（NUMA，non-uniform memory access），即内存与每个插槽或内核之间的距离并不相等。 套接字之间的内存访问具有不同的性能特征，访问距离更远的套接字通常具有更多的延迟。

通过`-XX:+UseParallelGC`启用的并行垃圾收集器，已经`NUMA-aware`很长时间了，这提高了运行在单个JVM里多个套接字的性能。其他HotSpot收集器没有利用此功能，这意味着他们无法利用这种垂直多路NUMA缩放功能。大型企业应用程序尤其倾向于在多个套接字上以大型堆配置运行，但是他们希望在单个JVM中运行具有可管理性优势。 使用G1收集器的用户越来越多地遇到这种扩展瓶颈。

### 描述

G1的堆内存是固定大小的`region`的集合。一个region通常是一组物理页面，尽管在使用大页面（通过-XX:+UseLargePages设定）时，一个物理页面由多个region组成。

如果指定了`+XX:+UseNUMA`选项，JVM在初始化时，会将region平均分配在可用的NUMA节点上。

在开始时就为每个NUM节点分配固定的region有点不灵活，但是可以通过以下机制来缓解：为了给mutator线程分配新的对象，G1可能需要一个新的region。JVM会从NUMA节点中优先选择与当前线程绑定的空闲区域来执行此操作，这样新的对象就可以在同一个NUMA的新生代中。如果同一NUMA节点上没有空闲的region，G1将触发垃圾回收操作。另一种方法是，从距离最近的NUMA节点开始，按照距离顺序在其他NUMA节点中搜索可用region。

在老年代中，不会尝试将对象保存在同一个NUMA节点中。`humongous region`也并不适用这项分配策略。

## 349:	JFR事件流

[JEP 349: JFR Event Streaming](https://openjdk.java.net/jeps/349)

暴露JDK Flight Recorder数据，方便使用者持续监控。

### 动机

HotSpot VM通过JFR产生的数据点超过500个，但是使用者只能通过解析日志文件的方法使用它们。

用户要想消费这些数据，必须开始一个记录并停止，将内容转储到磁盘上，然后解析记录文件。这对于应用程序分析非常有效，但是监控数据却十分不方便（例如显示动态更新数据的仪表盘）。

与创建记录相关的开销包括：

- 发出在创建新记录时必须发生的事件
- 写入事件元数据（例如字段布局）
- 写入检查点数据（例如堆栈跟踪）
- 将数据从磁盘存储复制到单独的记录文件

如果有一种方法，可以在不创建新记录文件的情况下，从磁盘存储库中读取正在记录的数据，就可以避免上述开销。

### 描述

jdk.jfr模块里的`jdk.jfr.consumer`包，提供了异步订阅事件的功能。用户可以直接从磁盘存储库读取记录数据，也可以直接从磁盘存储流中读取数据，而无需转储记录文件。可以通过注册处理器（例如lambda函数）与流交互，从而对事件的到达进行响应。

下面的例子打印CPU的总体使用率，并持有锁10毫秒。

```java
try (var rs = new RecordingStream()) {
  rs.enable("jdk.CPULoad").withPeriod(Duration.ofSeconds(1));
  rs.enable("jdk.JavaMonitorEnter").withThreshold(Duration.ofMillis(10));
  rs.onEvent("jdk.CPULoad", event -> {
    System.out.println(event.getFloat("machineTotal"));
  });
  rs.onEvent("jdk.JavaMonitorEnter", event -> {
    System.out.println(event.getClass("monitorClass"));
  });
  rs.start();
}
```

`RecordingStream` 类实现了接口`jdk.jfr.consumer.EventStream`，该接口提供了一种统一的方式来过滤和使用事件，无论源是实时流还是磁盘上的文件。

```java
public interface EventStream extends AutoCloseable {
  public static EventStream openRepository();
  public static EventStream openRepository(Path directory);
  public static EventStream openFile(Path file);

  void setStartTime(Instant startTime);
  void setEndTime(Instant endTime);
  void setOrdered(boolean ordered);
  void setReuse(boolean reuse);

  void onEvent(Consumer<RecordedEvent> handler);
  void onEvent(String eventName, Consumer<RecordedEvent handler);
  void onFlush(Runnable handler);
  void onClose(Runnable handler);
  void onError(Runnable handler);
  void remove(Object handler);

  void start();
  void startAsync();

  void awaitTermination();
  void awaitTermination(Duration duration);
  void close();
}
```

创建流的方法有3种:

1. EventStream::openRepository(Path) 从磁盘存储库中构造一个流。这是一种可以直接通过文件系统监视其他进程的方法。磁盘存储库的位置存储在系统属性`jdk.jfr.repository`中，可以使用API读取到。
2. EventStream::openRepository()方法执行进程内监控。与RecordingStream不同，它不会开始录制。相反，仅当通过外部方式（例如，使用JCMD或JMX）启动记录时，流才接收事件。
3. EventStream::openFile(Path)从记录文件中创建流，扩充了已经存在的`RecordingFile`类。

该接口还可用于设置缓冲的数据量，以及是否应按时间顺序对事件进行排序。为了最大程度地降低分配压力，还可以选择控制是否应为每个事件分配新的事件对象，或者是否可以重用以前的对象。我们可以在当前线程中启动流，也可以异步启动流。

Java虚拟机（JVM）每秒一次将线程本地缓冲区中存储的事件定期刷新到磁盘存储库。一个单独的线程解析最近的文件，直到写入数据为止，然后将事件推送给订阅者。为了保持较低的开销，仅从文件中读取活动订阅的事件。要在刷新完成后收到通知，可以使用EventStream :: onFlush（Runnable）方法注册处理程序。这是在JVM准备下一组事件时将数据聚合或推送到外部系统的机会。


Java虚拟机（JVM）每隔一秒钟就会将线程的本地缓冲区存储的事件刷新到磁盘存储库中。解析文件使用的是一个独立的线程，这个线程解析后将事件推送给订阅者。为了保持较低的开销，仅从文件中读取活跃的订阅事件。若想在一次刷新完成后收到通知，可以使用EventStream::onFlush(Runnable)方法注册处理程序。

## 352:	非原子性的字节缓冲区映射

[JEP 352: Non-Volatile Mapped Byte Buffers](https://openjdk.java.net/jeps/352)

添加新的特定于JDK的文件映射模式，以便可以使用`FileChannel API`创建引用非易失性存储器的`MappedByteBuffer`实例。

### 动机

非易失性存储器 (non-volatile memory,NVM)可以使程序在运行过程中创建和更新程序状态，而减少持久性介质的大量复制/翻译成本。这对于事务程序非常重要，事务程序需要定期保持不确定状态的持久性，以便在崩溃后恢复程序状态。

现有的C库（例如Intel的libpmem）为C程序提供了对NVM的高效访问。现在在Java中调用基本库代价也是非常大的，因为这需要频繁进行系统调用或JNI调用，同时C语言中提供的持久数据类型分配在无法从Java直接访问的内存中。Java应用程序和中间件（例如Java事务管理器）与C或可以低成本链接到C库的语言相比，处于严重的劣势。

该特性试图通过允许映射到ByteBuffer的NVM的有效回写解决第一个问题。由于Java可以直接访问ByteBuffer映射的内存，因此这可以通过实现与C语言中提供的客户端库等效的客户端库来解决第二个问题，以管理不同持久数据类型的存储。

### 描述

#### 初步变更

该JEP使用了Java SE API的两个增强功能：

1. 支持implementation-defined的映射模式
2. MppedByteBuffer::force方法以指定范围

#### 特定于JDK的API更改

1. 通过新模块中的公共API公开新的MapMode枚举值

一个公共扩展枚举ExtendedMapMode将添加到`jdk.nio.mapmode`程序包：

```java
package jdk.nio.mapmode;
. . .
public class ExtendedMapMode {
    private ExtendedMapMode() { }

    public static final MapMode READ_ONLY_SYNC = . . .
    public static final MapMode READ_WRITE_SYNC = . . .
}
```

在调用FileChannel::map方法创建映射到NVM设备文件上的只读或读写MappedByteBuffer时，可以使用上述的枚举值。如果这些标志在不支持NVM设备文件的平台上传递，程序会抛出`UnsupportedOperationException`异常。在受支持的平台上，仅当目标FileChannel实例是从通过NVM设备打开的派生文件时，才能传递这些参数。在任何其他情况下，都会抛出IOException异常。

2. 发布`BufferPoolMXBean`，用于跟踪MappedByteBuffer统计信息

#### 初步商定的内部JDK API更改

1. 向类`jdk.internal.misc.Unsafe`中添加新的`writebackMemory`方法

## 358:	友好的空指针异常

[JEP 358: Helpful NullPointerExceptions](https://openjdk.java.net/jeps/358)

精确描述哪个变量为null，提高JVM生成的NullPointerExceptions的可用性。

### 动机

每个Java开发人员都遇到过NullPointerExceptions (NPEs)问题。NPE几乎可以出现在程序的任意位置，因此尝试捕获和修复它们是不可能的。下面的代码：

```java
a.i = 99;
```

JVM会打印出方法名、文件名和NPE异常的行数：

```java
Exception in thread "main" java.lang.NullPointerException
    at Prog.main(Prog.java:5)
```

使用这个错误报告，开发人员可以定位到 `a.i = 99;` 并推断对象a是null。但是对于更复杂的代码，不使用调试器就无法确定哪个变量为空。假设下面的代码中出现了一个NPE：

```java
a.b.c.i = 99;
```

仅仅使用文件名和行数，并不能精确定位到哪个变量为null，是a、b还是c？

访问数组也会发生类似的问题。假设此代码中出现一个NPE：

```java
a[i][j][k] = 99;
```

文件名和行号不能精确指出哪个数组组件为空。是a还是a [i]或a [i] [j]？

一行代码可能包含多个访问路径，每个访问路径都可能是NPE的来源。假设此代码中出现一个NPE：

```java
a.i = b.j;
```

文件名和行号并不能确定哪个对象为空，是a还是b？

NPE也可能在方法调用中传递，看下面的代码：

```java
x().y().i = 99;
```

文件名和行号不能指出哪个方法调用返回null。是x()还是y()？

### 描述

JVM在程序调用空引用的位置抛出NPE异常，通过分析程序的字节码指令，JVM可以精确判断哪个变量为空，并在NPE中描述详细信息（根据源代码）。包含方法名、文件名和行号的null-detail消息将显示在JVM的消息中。

例如`a.i = 99;`的NPE异常可能是如下格式：

```java
Exception in thread "main" java.lang.NullPointerException: 
        Cannot assign field "i" because "a" is null
    at Prog.main(Prog.java:5)
```

在更复杂的`a.b.c.i = 99;`语句中，NPE消息会包含导致空值的完整访问路径：

```java
Exception in thread "main" java.lang.NullPointerException: 
        Cannot read field "c" because "a.b" is null
    at Prog.main(Prog.java:5)
```

同样，如果数组访问和赋值语句`a[i][j][k] = 99;`引发NPE：

```java
Exception in thread "main" java.lang.NullPointerException:
        Cannot load from object array because "a[i][j]" is null
    at Prog.main(Prog.java:5)
```

类似地，`a.i = b.j;`会引发NPE:

```java
Exception in thread "main" java.lang.NullPointerException:
        Cannot read field "j" because "b" is null
    at Prog.main(Prog.java:5)
```

## 359:	Records (预览)

[JEP 359: Records \(Preview\)](https://openjdk.java.net/jeps/359)

通过`Records`（不知道如何翻译，囧……）增强Java编程语言。Records提供了一种紧凑的语法来声明类，这些类是浅层不可变数据的透明持有者。

### 动机

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

## 361:	Switch表达式 (标准)

[JEP 361: Switch Expressions \(Standard\)](https://openjdk.java.net/jeps/361)

扩展switch可以使其应用于语句或表达式。

### 动机

当我们准备增强Java编程语言以支持模式匹配（JEP 305）时，现有switch语句的一些不规则性（长期以来一直困扰着用户）成为了障碍。下面的代码中，众多的break语句使代码变得冗长，这种“视觉噪声”通常掩盖了更多的错误。

```java
switch (day) {
    case MONDAY:
    case FRIDAY:
    case SUNDAY:
        System.out.println(6);
        break;
    case TUESDAY:
        System.out.println(7);
        break;
    case THURSDAY:
    case SATURDAY:
        System.out.println(8);
        break;
    case WEDNESDAY:
        System.out.println(9);
        break;
}
```

我们建议引入一种新形式的switch标签`case L->`，以表示如果匹配标签，则只执行标签右边的代码。switch标签允许在每种情况下使用逗号分隔多个常量。现在可以这样编写以前的代码：

```java
switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> System.out.println(6);
    case TUESDAY                -> System.out.println(7);
    case THURSDAY, SATURDAY     -> System.out.println(8);
    case WEDNESDAY              -> System.out.println(9);
}
```

switch标签`case L->`右侧的代码被限制为表达式、代码块或throw语句。这样局部变量的范围在本块之内，而传统的switch语句局部变量的作用域是整个模块！

```java
switch (day) {
    case MONDAY:
    case TUESDAY:
        int temp = ...     // The scope of 'temp' continues to the }
        break;
    case WEDNESDAY:
    case THURSDAY:
        int temp2 = ...    // Can't call this variable 'temp'
        break;
    default:
        int temp3 = ...    // Can't call this variable 'temp'
}
```

许多现有的switch语句实质上是对switch表达式的模拟，其中每个分支要么分配给一个公共目标变量，要么返回一个值：

```java
int numLetters;
switch (day) {
    case MONDAY:
    case FRIDAY:
    case SUNDAY:
        numLetters = 6;
        break;
    case TUESDAY:
        numLetters = 7;
        break;
    case THURSDAY:
    case SATURDAY:
        numLetters = 8;
        break;
    case WEDNESDAY:
        numLetters = 9;
        break;
    default:
        throw new IllegalStateException("Wat: " + day);
}
```

上面的表述是复杂、重复且容易出错的。代码设计者的意图是为每天计算`numLetters`。这段代码可以改写成下面这段形式，更加清晰和安全：

```java
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY                -> 7;
    case THURSDAY, SATURDAY     -> 8;
    case WEDNESDAY              -> 9;
};
```

### 描述

#### Arrow labels

除了传统的`case L :`标签外，还定义了一种更简洁的形式：`case L ->`标签。如果表达式匹配了某个标签，则仅执行箭头右侧的表达式或语句；否则将不执行任何操作。

```java
static void howMany(int k) {
    switch (k) {
        case 1  -> System.out.println("one");
        case 2  -> System.out.println("two");
        default -> System.out.println("many");
    }
}
```

下面的代码：

```java
howMany(1);
howMany(2);
howMany(3);
```

将会打印：

```java
one
two
many
```

#### Switch expressions

JDK 14扩展了switch语句，使其可以应用于表达式中。例如上述的howMany方法可以重写为如下形式：

```java
static void howMany(int k) {
    System.out.println(
        switch (k) {
            case  1 -> "one";
            case  2 -> "two";
            default -> "many";
        }
    );
}
```

在通常情况下，switch表达式如下所示：

```java
T result = switch (arg) {
    case L1 -> e1;
    case L2 -> e2;
    default -> e3;
};
```

#### Yielding a value

大多数switch表达式在`case L->`标签的右侧都有一个表达式。如果需要一个完整的块，JDK 14引入了一个新的`yield`语句来产生一个值，该值成为封闭的switch表达式的值。

```java
int j = switch (day) {
    case MONDAY  -> 0;
    case TUESDAY -> 1;
    default      -> {
        int k = day.toString().length();
        int result = f(k);
        yield result;
    }
};
```

## 363:	移除CMS（Concurrent Mark Sweep）垃圾收集器

[JEP 363: Remove the Concurrent Mark Sweep \(CMS\) Garbage Collector](https://openjdk.java.net/jeps/363)

### 动机

在两年多以前的JEP 291中，我们就已经弃用了CMS收集器，并说明会在以后的发行版中删除，以加快其他垃圾收集器的发展。在这段时间里，我们看到了2个新的垃圾收集器`ZGC`和`Shenandoah`的诞生，同时对G1的进一步改进。G1自JDK 6开始便成为CMS的继任者。我们希望以后现有的收集器进一步减少对CMS的需求。

### 描述

此更改将禁用CMS的编译，删除源代码中gc/cms目录的内容，并删除仅与CMS有关的选项。尝试使用命令`-XX:+UseConcMarkSweepGC`开启CMS会收到以下警告：

```java
Java HotSpot(TM) 64-Bit Server VM warning: Ignoring option UseConcMarkSweepGC; \
support was removed in <version>
```

VM将使用默认收集器继续执行。

## 364:	macOS系统上的ZGC

[JEP 364: ZGC on macOS](https://openjdk.java.net/jeps/364)

将ZGC垃圾收集器移植到macOS。

### 动机

尽管我们希望需要ZGC可伸缩性的用户使用基于Linux的环境，但是在部署应用程序之前，开发人员通常会使用Mac进行本地开发和测试。 还有一些用户希望运行桌面应用程序，例如带有ZGC的IDE。

尽管我们希望需要ZGC可伸缩性的用户都是基于Linux环境的，但是在部署应用程序之前，开发人员通常会使用Mac进行本地开发和测试。 还有一些用户希望运行桌面应用程序，例如带有ZGC的IDE。

### 描述

ZGC的macOS实现由两部分组成（下面是机翻，写不动了……）：

1. 支持macOS上的多映射内存。 ZGC设计大量使用彩色指针，因此在macOS上我们需要一种将多个虚拟地址（在算法中包含不同颜色）映射到同一物理内存的方法。我们将为此使用mach microkernel mach_vm_remap API。堆的物理内存在单独的地址视图中维护，在概念上类似于文件描述符，但位于（主要是）连续的虚拟地址中。该内存被重新映射到内存的各种ZGC视图中，代表了算法的不同指针颜色。
2. ZGC支持不连续的内存保留。在Linux上，我们在初始化期间保留16TB的虚拟地址空间。我们假设没有共享库将映射到所需的地址空间。在默认的Linux配置上，这是一个安全的假设。但是在macOS上，ASLR机制会侵入我们的地址空间，因此ZGC必须允许堆保留不连续。假设VM实现使用单个连续的内存预留，则共享的VM代码也必须停止。如此一来，is_in_reserved（），reserved_region（）和base（）之类的GC API将从CollectedHeap中删除。

## 弃用ParallelScavenge + SerialOld GC组合

[JEP 366: Deprecate the ParallelScavenge + SerialOld GC Combination](https://openjdk.java.net/jeps/366)

### 动机

有一组GC算法的组合很少使用，但是维护起来却需要巨大的工作量：并行年轻代GC（ParallelScavenge）和串行老年代GC（SerialOld）的组合。用户必须使用`-XX:+UseParallelGC -XX:-UseParallelOldGC`来启用此组合。

这种组合是畸形的，因为它将并行的年轻代GC算法和串行的老年代GC算法组合在一起使用。我们认为这种组合仅在年轻代很多、老年代很少时才有效果。在这种情况下，由于老年代的体积较小，因此完整的收集暂停时间是可以接受的。但是在生产环境中，这种方式是非常冒险的：年轻代的对象容易导致OutOfMemoryException。此组合的唯一优势是总内存使用量略低。我们认为，这种较小的内存占用优势（最多是Java堆大小的约3％）不足以超过维护此GC组合的成本。

### 描述

除了弃用选项组合`-XX:+UseParallelGC -XX:-UseParallelOldGC `外，我们还将弃用选项`-XX:UseParallelOldGC`，因为它唯一的用途是取消选择并行的旧版GC，从而启用串行旧版GC。

因此，任何对UseParallelOldGC选项的明确使用都会显示弃用警告。

## 368:	文本块 (第二个预览版)

[JEP 368: Text Blocks \(Second Preview\)](https://openjdk.java.net/jeps/368)

Java语言增加文本块功能。文本块是多行字符串文字，能避免大多数转义。

### 动机

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

### 描述

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

## 370:	外部存储器API (Incubator)

[JEP 370: Foreign-Memory Access API \(Incubator\)](https://openjdk.java.net/jeps/370)

引入一个API，以允许Java程序安全有效地访问Java堆之外的外部内存。

### 动机

许多Java的库都能访问外部存储，例如Ignite, mapDB, memcached, and Netty's ByteBuf API。这样可以：

- 避免垃圾回收相关成本和不可预测性
- 跨多个进程共享内存
- 通过将文件映射到内存中来序列化、反序列化内存内容。

但是Java API却没有提供一个令人满意的访问外部内存的解决方案。

Java 1.4中引入的ByteBuffer API允许创建直接字节缓冲区，这些缓冲区是按堆外分配的，并允许用户直接从Java操作堆外内存。但是，直接缓冲区是有限的。

开发人员可以从Java代码访问外部内存的另一种常见途径是使用sun.misc.Unsafe API。Unsafe有许多公开的内存访问操作（例如Unsafe::getInt和putInt）。使用Unsafe访问内存非常高效：所有内存访问操作都定义为JVM内在函数，因此JIT会定期优化内存访问操作。然而根据定义，Unsafe API是不安全的——它允许访问任何内存位置（例如，Unsafe::getInt需要很长的地址）。如果Java程序了访问某些已释放的内存位置，可能会使JVM崩溃。最重要的是，Unsafe API不是受支持的Java API，并且强烈建议不要使用它。

虽然也可以使用JNI访问内存，但是与该解决方案相关的固有成本使其在实践中很少适用。整个开发流程很复杂，因为JNI要求开发人员编写和维护C代码段。 JNI本质上也很慢，因为每次访问都需要Java到native的转换。

在访问外部内存时，开发人员面临一个难题：应该使用安全但受限（可能效率较低）的方法（例如ByteBuffer），还是应该放弃安全保证并接受不受支持和危险的Unsafe API？

该JEP引入了受支持的，安全且有效的外部内存访问API。并且设计时就充分考虑了JIT优化。

### 描述

外部存储器访问API引入了三个主要的抽象：MemorySegment，MemoryAddress和MemoryLayout。

MemorySegment用于对具有给定空间和时间范围的连续内存区域进行建模。可以将MemoryAddress视为段内的偏移量，MemoryLayout是内存段内容的程序描述。

可以从多种来源创建内存段，例如本机内存缓冲区，Java数组和字节缓冲区（直接或基于堆）。例如，可以如下创建本机内存段：

```java
try (MemorySegment segment = MemorySegment.allocateNative(100)) {
   ...
}
```

上述代码将创建大小为100字节的，与本机内存缓冲区关联的内存段。

内存段在空间上受限制；任何试图使用该段来访问这些界限之外的内存的尝试都会导致异常。正如使用try-with-resource构造所证明的那样，片段在时间上也是有界的。也就是说，它们已创建，使用并在不再使用时关闭。关闭段始终是一个显式操作，并且可能导致其他副作用，例如与该段关联的内存的重新分配。任何访问已关闭的内存段的尝试都将导致异常。空间和时间安全性检查对于确保内存访问API的安全性至关重要。

通过获取内存访问var句柄可以取消引用与段关联的内存。这些特殊的var句柄具有至少一个强制访问坐标，类型为MemoryAddress，即发生取消引用的地址。它们是使用MemoryHandles类中的工厂方法获得的。要设置本机段的元素，我们可以使用如下所示的内存访问var句柄：

```java
VarHandle intHandle = MemoryHandles.varHandle(int.class);

try (MemorySegment segment = MemorySegment.allocateNative(100)) {
   MemoryAddress base = segment.baseAddress();
   for (int i = 0 ; i < 25 ; i++) {
        intHandle.set(base.offset(i * 4), i);
   }
}
```

# 总结

对普通Java开发人员来说，最重要的无疑是Record类、switch语句、文本块。新兴语言（例如Kotlin）早就实现了这些特性——语法更加简洁、特性更加丰富，在这些语言面前，曾经新兴的Java也变成了“老古董”。

实际开发过程中，Lombok插件和Spring Boot能大大提高Java的开发效率。Java近些年的版本迭代也是有目共睹的，虽然新版本特性更多、稳定性和安全性更高，但是目前企业开发仍以Java 8居多，中小企业的JDK升级意愿并不强烈。










































