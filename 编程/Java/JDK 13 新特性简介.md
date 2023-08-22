---
date: 2019-07-31
---

# 公众号

最近写的文章也会同步到公众号中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

# JDK 13 发布日期

[OpenJDK 13主页](https://openjdk.java.net/projects/jdk/13/)可以看到 JDK 13预计在今年的`9月17日`发布。排期如下：


- 2019/06/13		Rampdown Phase One (fork from main line)
- 2019/07/18		Rampdown Phase Two
- 2019/08/08		Initial Release Candidate
- 2019/08/22		Final Release Candidate
- 2019/09/17		General Availability

# 功能

- 350:	Dynamic CDS Archives
- 351:	ZGC: Uncommit Unused Memory
- 353:	Reimplement the Legacy Socket API
- 354:	Switch Expressions (Preview)
- 355:	Text Blocks (Preview)

## 350 Dynamic CDS Archives

扩展应用程序类-数据共享，以允许在 Java 应用程序执行结束时动态归档类。归档类将包括默认的基础层 CDS（class data-sharing）存档中不存在的所有已加载的应用程序类和库类。

## 351 ZGC: Uncommit Unused Memory

增强ZGC以将未使用的堆内存返回给操作系统。

目前ZGC并没有将未使用的内存返回给操作系统，即使这些内存已经空闲了很长时间。在需要关注内存占用的应用程序的情况下，效果很不理想。比如：

- 应用程序长时间处于空闲状态、或与其他应用程序共享或竞争资源
- 应用程序在不同的执行期间，有不同的堆空间需求。

HotSpot中的其他垃圾收集器，如G1和Shenandoah，已经提供了这种功能，这个功能在某些情况下非常有用。将这个功能添加到ZGC是大势所趋。

## 353 Reimplement the Legacy Socket API

用更简单、现代的方法实现 java.net.Socket 和 java.net.ServerSocket API。新实现会使线程编程变得很方便。

java.net.Socket 和 java.net.ServerSocket API 最初的实现版本可以追溯到 JDK 1.0，当时是Java和C代码混合编写，调试和维护都非常痛苦。

## 354 Switch Expressions (Preview)

扩展 Switch 语句，能够用在变量或表达式上，同时也支持λ表达式。`... -> labels`这种形式类似于直接 break，能够简化日常编码。该功能包含在 JDK 13预览版中。

Java以前的Switch预发：

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

JDK 13引入了一种新的Switch语法：`case L ->`。如果匹配到label，仅仅右边的代码会被执行，同时这里也支持多个label。代码的格式如下：

```java
switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> System.out.println(6);
    case TUESDAY                -> System.out.println(7);
    case THURSDAY, SATURDAY     -> System.out.println(8);
    case WEDNESDAY              -> System.out.println(9);
}
```

传统Switch语句都是为了计算某个变量的值，以前都是这么写的：

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

上述写法非常容易出错，同时有大量重复代码。我们可以使用下面的Switch表达式，这样更安全简洁：

```java
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY                -> 7;
    case THURSDAY, SATURDAY     -> 8;
    case WEDNESDAY              -> 9;
};
```

## 355 Text Blocks (Preview)

Java 语法中同时会增加`文本块`的功能。文本块是一个多行的字符串文字，避免对大多数对字符串的转移，同时以可预测的方式自动格式化字符串，同时给了开发人员控制权。该项功能包含在 JDK 13 的预览版中。

在Java中，HTML,XML,SQL或JSON字符串都需要大量转义，可读性很差并且难以维护。本质上`Text Blocks`是一个二维的文本块，而不是一维的字符序列。

### HTML example

使用Java原来的“一维”字符序列：

```java
String html = "<html>\n" +
              "    <body>\n" +
              "        <p>Hello, world</p>\n" +
              "    </body>\n" +
              "</html>\n";
```

使用“二维”的文本块：

```java
String html = """
              <html>
                  <body>
                      <p>Hello, world</p>
                  </body>
              </html>
              """;
```

### SQL example

使用Java原来的“一维”字符序列：

```java
String query = "SELECT `EMP_ID`, `LAST_NAME` FROM `EMPLOYEE_TB`\n" +
               "WHERE `CITY` = 'INDIANAPOLIS'\n" +
               "ORDER BY `EMP_ID`, `LAST_NAME`;\n";
```

使用“二维”的文本块：

```java
String query = """
               SELECT `EMP_ID`, `LAST_NAME` FROM `EMPLOYEE_TB`
               WHERE `CITY` = 'INDIANAPOLIS'
               ORDER BY `EMP_ID`, `LAST_NAME`;
               """;
```

### Polyglot language example

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
Object obj = engine.eval("function hello() {\n" +
                         "    print('\"Hello, world\"');\n" +
                         "}\n" +
                         "\n" +
                         "hello();\n");
```

使用“二维”的文本块：

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
Object obj = engine.eval("""
                         function hello() {
                             print('"Hello, world"');
                         }
                         
                         hello();
                         """);

```
