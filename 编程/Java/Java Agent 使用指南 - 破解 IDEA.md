---
date: 2021-07-31
---

- [Java Agent 是什么？](#java-agent-是什么)
  - [修改字节码的工具](#修改字节码的工具)
- [Instrumentation 原理](#instrumentation-原理)
    - [**启动时加载 instrument agent 过程**](#启动时加载-instrument-agent-过程)
    - [**运行时加载 instrument agent 过程**](#运行时加载-instrument-agent-过程)
  - [VirtualMachine#attach](#virtualmachineattach)
- [JVM 启动前静态 Instrument](#jvm-启动前静态-instrument)
  - [Premain 类](#premain-类)
  - [META-INF/MANIFEST.MF 设置](#meta-infmanifestmf-设置)
  - [测试类](#测试类)
  - [输出结果](#输出结果)
- [JVM 启动后动态 Instrument](#jvm-启动后动态-instrument)
  - [META-INF/MANIFEST.MF 设置](#meta-infmanifestmf-设置-1)
  - [AgentMain 类](#agentmain-类)
  - [测试类](#测试类-1)
  - [输出结果](#输出结果-1)
- [Java Agent 的应用](#java-agent-的应用)
  - [应用性能监控组件](#应用性能监控组件)
  - [Java 代码热更新工具](#java-代码热更新工具)
  - [IDEA 破解](#idea-破解)
  - [Arthas](#arthas)
  - [各种代码增强](#各种代码增强)
- [参考资料](#参考资料)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# Java Agent 是什么？

Java Agent 是一个特殊的 jar 文件，利用 JVM 的 Instrumentation API 来更改加载到 JVM 中的字节码。一共有 2 种方式：

- premain：使用 -javaagent 参数在 JVM 启动时静态加载代理
- agentmain：使用 Java Attach API 将代理动态加载到 JVM 中

需要说明的是，Oracle、OpenJDK 等 JVM 都提供了动态开启代理的机制，但是这个机制并不是强制的。本文首先介绍 Instrument 的原理，再从零到一介绍如何使用 premain 和 agentmain 更改字节码，最后再讲解通过 Java Agent 能够做什么（破解）。

## 修改字节码的工具

![](https://i.loli.net/2021/07/31/1wjALliFzh8J32B.png?x-oss-process=style/yano)

# Instrumentation 原理

具体可参考：[Package java.lang.instrument](https://docs.oracle.com/en/java/javase/11/docs/api/java.instrument/java/lang/instrument/package-summary.html)。

instrument 的底层实现依赖于 JVMTI(JVM Tool Interface)，它是 JVM 暴露出来的一些供用户扩展的接口集合，JVMTI 是基于事件驱动的，JVM 每执行到一定的逻辑就会调用一些事件的回调接口（如果有的话），这些接口可以供开发者去扩展自己的逻辑。JVMTIAgent 是一个利用 JVMTI 暴露出来的接口提供了代理启动时加载 (agent on load)、代理通过 attach 形式加载 (agent on attach) 和代理卸载 (agent on unload) 功能的动态库。而 instrument agent 可以理解为一类 JVMTIAgent 动态库，别名是 JPLISAgent(Java Programming Language Instrumentation Services Agent)，也就是专门为 java 语言编写的插桩服务提供支持的代理。

### **启动时加载 instrument agent 过程**

1. 创建并初始化 JPLISAgent；
2. 监听 `VMInit` 事件，在 JVM 初始化完成之后做下面的事情：
    1. 创建 InstrumentationImpl 对象 ；
    2. 监听 ClassFileLoadHook 事件 ；
    3. 调用 InstrumentationImpl 的`loadClassAndCallPremain`方法，在这个方法里会去调用 javaagent 中 MANIFEST.MF 里指定的 Premain-Class 类的 premain 方法 ；
3. 解析 javaagent 中 MANIFEST.MF 文件的参数，并根据这些参数来设置 JPLISAgent 里的一些内容。

### **运行时加载 instrument agent 过程**

通过 JVM 的 attach 机制来请求目标 JVM 加载对应的 agent，过程大致如下：

1. 创建并初始化 JPLISAgent；
2. 解析 javaagent 里 MANIFEST.MF 里的参数；
3. 创建 InstrumentationImpl 对象；
4. 监听 ClassFileLoadHook 事件；
5. 调用 InstrumentationImpl 的`loadClassAndCallAgentmain`方法，在这个方法里会去调用 javaagent 里 MANIFEST.MF 里指定的`Agent-Class`类的`agentmain`方法。

## VirtualMachine#attach

1. `VirtualMachine` 字面意义表示一个 Java 虚拟机，也就是程序需要监控的目标虚拟机，提供了获取系统信息（比如获取内存 dump、线程 dump，类信息统计（比如已加载的类以及实例个数等）， loadAgent，Attach 和 Detach （Attach 动作的相反行为，从 JVM 上面解除一个代理）等方法，可以实现的功能可以说非常之强大 。该类允许我们通过给 attach 方法传入一个 jvm 的 pid（进程 id)，远程连接到 jvm 上 。

    代理类注入操作只是它众多功能中的一个，通过`loadAgent`方法向 jvm 注册一个代理程序 agent，在该 agent 的代理程序中会得到一个 Instrumentation 实例，该实例可以 在 class 加载前改变 class 的字节码，也可以在 class 加载后重新加载。在调用 Instrumentation 实例的方法时，这些方法会使用 ClassFileTransformer 接口中提供的方法进行处理。

2. `VirtualMachineDescriptor` 则是一个描述虚拟机的容器类，配合 VirtualMachine 类完成各种功能。

attach 实现动态注入的原理如下：

通过 VirtualMachine 类的`attach(pid)`方法，便可以 attach 到一个运行中的 java 进程上，之后便可以通过`loadAgent(agentJarPath)`来将 agent 的 jar 包注入到对应的进程，然后对应的进程会调用 agentmain 方法。

![](https://i.loli.net/2021/07/31/iXGcfU4uDSCr3AL.png?x-oss-process=style/yano)

具体使用可参考：[Class VirtualMachine](https://docs.oracle.com/en/java/javase/11/docs/api/jdk.attach/com/sun/tools/attach/VirtualMachine.html)。基本使用方式如下：

```java
// attach to target VM
VirtualMachine vm = VirtualMachine.attach("2177");

// start management agent
Properties props = new Properties();
props.put("com.sun.management.jmxremote.port", "5000");
vm.startManagementAgent(props);

// detach
vm.detach();
```

attach 最终会调用到 com.sun.tools.attach.spi.AttachProvider#attachVirtualMachine(java.lang.String)，实现为：

```java
public VirtualMachine attachVirtualMachine(String vmid)
    throws AttachNotSupportedException, IOException
{
    checkAttachPermission();

    // AttachNotSupportedException will be thrown if the target VM can be determined
    // to be not attachable.
    testAttachable(vmid);

    return new VirtualMachineImpl(this, vmid);
}
```

VirtualMachineImpl 构造函数如下，核心是在两个进程之间建立一个 socket 连接进行通信，接收方 target VM 会针对不同的传入数据来做不同的处理。

```java
VirtualMachineImpl(AttachProvider provider, String vmid)
    throws AttachNotSupportedException, IOException
{
    super(provider, vmid);

    // This provider only understands pids
    int pid;
    try {
        pid = Integer.parseInt(vmid);
    } catch (NumberFormatException x) {
        throw new AttachNotSupportedException("Invalid process identifier");
    }

    // Find the socket file. If not found then we attempt to start the
    // attach mechanism in the target VM by sending it a QUIT signal.
    // Then we attempt to find the socket file again.
    File socket_file = new File(tmpdir, ".java_pid" + pid);
    socket_path = socket_file.getPath();
    if (!socket_file.exists()) {
        File f = createAttachFile(pid);
        try {
            sendQuitTo(pid);

            // give the target VM time to start the attach mechanism
            final int delay_step = 100;
            final long timeout = attachTimeout();
            long time_spend = 0;
            long delay = 0;

            // 省略……
        } finally {
            f.delete();
        }
    }

    // Check that the file owner/permission to avoid attaching to
    // bogus process
    checkPermissions(socket_path);

    // Check that we can connect to the process
    // - this ensures we throw the permission denied error now rather than
    // later when we attempt to enqueue a command.
    int s = socket();
    try {
        connect(s, socket_path);
    } finally {
        close(s);
    }
}
```

# JVM 启动前静态 Instrument

分为两步：

- 在某个类中实现 premain 静态方法
- 在 META-INF/MANIFEST.MF 中指定 Premain-Class

所谓 premain，就是运行在 main 函数之前的类。在 JVM 虚拟机启动之后，main 方法执行之前，JVM 会运行 -javaagent 所指定 jar 包内 Premain-Class 内的 premain 静态方法。

直接在命令行中输入 java，可以看到命令行提示中关于 javaagent 的使用说明：

```java
-javaagent:<jar 路径>[=<选项>]
                  加载 Java 编程语言代理，请参阅 java.lang.instrument
```

## Premain 类

编写 com.yano.Premain 类，其功能是在 test.jvm.AttachTest 类的 attachTest 方法前后分别打印一条语句。

```java
public class Premain {

    public static void premain(String agentArgs, Instrumentation inst) {
        inst.addTransformer(new SimpleTransformer(), true);
    }

    public static class SimpleTransformer implements ClassFileTransformer {

        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {

            if ("test/jvm/AttachTest".equals(className)) {
                try {
                    ClassPool pool = ClassPool.getDefault();
                    CtClass cc = pool.get("test.jvm.AttachTest");
                    CtMethod method = cc.getDeclaredMethod("attachTest");

                    // 在方法前后增加 2 行 print 语句
                    method.insertBefore("System.out.println(\"simple agent before\");");
                    method.insertAfter("System.out.println(\"simple agent after\");");

                    byte[] byteCode = cc.toBytecode();
                    // 将内存中曾经被 javassist 过的 className 对象移除
                    cc.detach();
                    return byteCode;
                } catch (NotFoundException | CannotCompileException | IOException e) {
                    e.printStackTrace();
                }
            }
            return null;
        }
    }
}
```

CtMethod 类中有各种对于方法的操作，比较常用的是 insertBefore 和 insertAfter，能够在方法体重前后增加语句（注意语句中使用到的类使用全路径名，因为我们并没有修改原类的 import）。

## META-INF/MANIFEST.MF 设置

本例直接在 maven 编译时生成 META-INF/MANIFEST.MF，同时本例的 javaagent 需要依赖 javassist。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.yano</groupId>
    <artifactId>simple-agent</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <maven-jar-plugin.version>3.1.1</maven-jar-plugin.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.javassist</groupId>
            <artifactId>javassist</artifactId>
            <version>3.27.0-GA</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>${maven-jar-plugin.version}</version>
                <configuration>
                    <archive>
                        <!--自动添加 META-INF/MANIFEST.MF -->
                        <manifest>
                            <addClasspath>true</addClasspath>
                        </manifest>
                        <manifestEntries>
                            <Premain-Class>com.yano.Premain</Premain-Class>
                            <Can-Redefine-Classes>true</Can-Redefine-Classes>
                            <Can-Retransform-Classes>true</Can-Retransform-Classes>
                        </manifestEntries>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

打包后 jar 包路径为：/Users/yano/code/simple-agent/target/simple-agent-1.0-SNAPSHOT.jar

## 测试类

启动一个 AttachTest 类，全路径为：test.jvm.AttachTest。上面编写的 SimpleTransformer 能够在 attachTest 方法前后增加两条打印语句。

```java
public class AttachTest {

    @Test
    public void attachTest() {
        System.out.println("attachTest start");
        try {
            TimeUnit.SECONDS.sleep(10);
        } catch (InterruptedException e) {
            // ignore
        }
        System.out.println("attachTest end");
    }
}
```

在 VM options 中加入 javaagent 参数

```java
-javaagent:/Users/yano/code/simple-agent/target/simple-agent-1.0-SNAPSHOT.jar
```

![](https://i.loli.net/2021/07/31/YtJlPBKTZOumqIM.png?x-oss-process=style/yano)

## 输出结果

运行单元测试后的输出结果如下，可以看到在方法前后增加了 simple agent before 和 simple agent after 两条日志。

```java
simple agent before
attachTest start
attachTest end
simple agent after
```

# JVM 启动后动态 Instrument

## META-INF/MANIFEST.MF 设置

pom 文件跟上面的设置唯一的区别在于：manifestEntries 里 Premain-Class 属性改成 Agent-Class。

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>${maven-jar-plugin.version}</version>
            <configuration>
                <archive>
                    <!--自动添加 META-INF/MANIFEST.MF -->
                    <manifest>
                        <addClasspath>true</addClasspath>
                    </manifest>
                    <manifestEntries>
		                    <!-- 改动在这里！ -->
                        <Agent-Class>com.yano.AgentMain</Agent-Class>
                        <Can-Redefine-Classes>true</Can-Redefine-Classes>
                        <Can-Retransform-Classes>true</Can-Retransform-Classes>
                    </manifestEntries>
                </archive>
            </configuration>
        </plugin>
    </plugins>
</build>
```

## AgentMain 类

agentmain 的实现和 premain 有所区别，因为此时 agentmain 是动态加载的，我们想改变 test.jvm.AttachTest 类的时候，test.jvm.AttachTest 类已经被 JVM 加载并运行了。

注意点：

- 采用 attach 机制，被代理的目标程序 VM 有可能很早之前已经启动，当然其所有类已经被加载完成，这个时候需要借助 Instrumentation#retransformClasses(Class<?>... classes) 让对应的类可以重新转换，从而激活重新转换的类执行 ClassFileTransformer 列表中的回调。
- 在 transform 方法中，需要增加 pool.appendClassPath(new LoaderClassPath(loader)); 否则会报 javassist.NotFoundException 异常。

```java
public class AgentMain {
    public static void agentmain(String agentArgs, Instrumentation instrumentation) {
        instrumentation.addTransformer(new DynamicTransformer(), true);
        try {
            instrumentation.retransformClasses(Class.forName("test.jvm.AttachTest"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static class DynamicTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            if (className.contains("test/jvm/AttachTest")) {
                try {
                    ClassPool pool = ClassPool.getDefault();
                    pool.appendClassPath(new LoaderClassPath(loader));
                    CtClass cc = pool.get("test.jvm.AttachTest");
                    CtMethod method = cc.getDeclaredMethod("simplePrint");

                    // 在方法前后增加 2 行 print 语句
                    method.insertBefore("System.out.println(\"simple agent before\");");
                    method.insertAfter("System.out.println(\"simple agent after\");");

                    return cc.toBytecode();
                } catch (NotFoundException | CannotCompileException | IOException  e) {
                    e.printStackTrace();
                }
            }
            return classfileBuffer;
        }
    }
}
```

## 测试类

启动一个程序，每间隔 5 秒打印一个数字，5 次后结束。

```java
@Test
public void attachDynamic() {
    System.out.println("attachDynamic start");
    int i = 0;
    while (i < 5) {
        simplePrint(i++);
        try {
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            // ignore
        }
    }
}

public void simplePrint(int i) {
    System.out.println(i);
}
```

在上面的 attachDynamic 单元测试启动后，启动下面的 agentMain 单元测试。列出系统所有正在运行的 VM，并过滤找到 attachDynamic 的 VM，并 attach 上去动态加载 agent jar 包；之后再 detach 释放连接。

```java
@Test
public void agentMain() {
    VirtualMachine.list().stream()
            .filter(vm -> vm.displayName().contains("test.jvm.AttachTest,attachDynamic"))
            .findFirst().ifPresent(vmd -> {
        try {
            VirtualMachine virtualMachine = VirtualMachine.attach(vmd.id());
            virtualMachine
                    .loadAgent("/Users/yano/code/simple-agent-main/target/simple-agent-main-1.0-SNAPSHOT.jar");
            virtualMachine.detach();
        } catch (Exception e) {
            e.printStackTrace();
        }
    });
}
```

## 输出结果

最终输出的结果（是在 attachDynamic 打印 0 之后，才启动的 agentMain），我们可以看到其动态更改了 simplePrint 函数。

```java
attachDynamic start
0
simple agent before
1
simple agent after
simple agent before
2
simple agent after
simple agent before
3
simple agent after
simple agent before
4
simple agent after
```

# Java Agent 的应用

说了这么多，Java Agent 有哪些应用呢？

1. 应用性能监控组件
2. Java 代码热更新工具
3. IDEA 破解
4. Arthas
5. 各种代码增强

## 应用性能监控组件

主要可以实现：

- 自动捕捉所有 error 级别异常，上报 Sentry
- 监控服务提供的所有 Http 接口、Redis 耗时操作（细化到每一种操作命令）、HBASE 操作耗时等

特点是业务代码无需关心上述逻辑，代码无侵入。

## Java 代码热更新工具

主要可以实现 Java 代码的热更新，避免 Java 工程在 debug 阶段提交代码、编译、部署等流程（往往需要 10 分钟的时间）。

## IDEA 破解

详情见 [源码分析 | 咋嘞？你的 IDEA 过期了吧！加个 Jar 包就破解了，为什么？](https://juejin.cn/post/6844904039516209160)。主要可以破解 IDEA，使用非社区版的功能。主要是代理 com/jetbrains/ls/newLicenses/DecodeCertificates 类，直接通过就对了。（IDEA 大版本都不一样，请支持正版）

在编写（下载）对应的 jetbrains-agent.jar 后，只需要在 IDEA 的 Help → Edit Custom VM Options 加入 java agent 代理即可。

![](https://i.loli.net/2021/07/31/GPmlQ4SOheEu8DU.png?x-oss-process=style/yano)

![](https://i.loli.net/2021/07/31/EUToZn54NasbR1y.png?x-oss-process=style/yano)

## Arthas

详情见 [Arthas 原理系列（四）：字节码插装让一切变得有可能](https://juejin.cn/post/6904280021632974856)。Java 程序员对 Arthas 肯定不会感到陌生，Arthas 底层当然也是 Java Agent、Instrumentation 这一套。强大之处已经有好多文章讲述了，略。

## 各种代码增强

水平有限，略。

# 参考资料

- [javaagent 使用指南](https://www.cnblogs.com/rickiyang/p/11368932.html)
- [源码分析 | 咋嘞？你的 IDEA 过期了吧！加个 Jar 包就破解了，为什么？](https://juejin.cn/post/6844904039516209160)
- [IDEA 通过 java-agent 实现永久破解](https://easyboot.xyz/posts/34402/)
- [Guide to Java Instrumentation](https://www.baeldung.com/java-instrumentation)
- [可配置、无侵入的应用性能监控组件设计](https://kstack.corp.kuaishou.com/tech/web/article/info/3429)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！

原创不易，希望大家转载时请先联系我，并标注原文链接。