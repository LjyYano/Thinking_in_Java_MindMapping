---
date: 2020-07-10
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

# 前言

2018年4月，Oracle Labs新公开了一项黑科技：[Graal VM](https://www.graalvm.org/)。

这是一个在HotSpot虚拟机基础上增强而成的跨语言全栈虚拟机，可以作为“任何语言”的运行平台使用。

现在网络上关于 Graal VM 的相关资料并不多，还是要看官方文档。本文旨在简要介绍：

- 什么是 Graal VM？
- Graal VM 有什么好处？
- Graal VM 有什么缺点？
- Graal VM 的工作原理是什么？
- 在 macOS 上安装 Graal VM
- 将基于 Spring Boot 的 Java 应用程序编译成`本地应用程序`


# 思维导图

下面是一张 Graal VM 的简要`思维导图`。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-07-10-011227.png)

一篇通俗易懂的文章：[GraalVM：微服务时代的Java](https://zhuanlan.zhihu.com/p/137836206)。

# 什么是 Graal VM

Graal VM 被官方称为“Universal VM”和“Polyglot VM”，是一个在HotSpot虚拟机基础上增强而成的跨语言全栈虚拟机，口号是“Run Programs Faster Anywhere”。可以在 Graal VM 上运行“任何语言”，这些语言包括：

- 基于 Java 虚拟机的语言：Java、Scala、Groovy、Kotlin 等；
- 基于 LLVM 的语言：C、C++、Rust；
- 其他语言：JavaScript、Ruby、Python和R语言等。

Graal VM可以无额外开销地混合使用这些编程语言，支持不同语言中混用对方的接口和对象，也能够支持这些语言使用已经编写好的本地库文件。

# Graal VM 的好处

具体可参考官方文档：[Why GraalVM？](https://www.graalvm.org/docs/why-graal/)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-07-10-014113.png)

我认为最重要的特性是 `Ahead-of-Time Compilation`。Substrate VM 是一个在 Graal VM 0.20 版本里的极小型的运行时环境，包括了独立的异常处理、同步调度、线程管理、内存管理（垃圾收集）和JNI访问等组件。Substrate VM 还包含了一个`本地镜像的构造器`（Native Image Generator），用户可以通过本地镜像构造器构建基于构建机器的可执行文件。

构造器采用指针分析（Points-To Analysis）技术，从用户提供的程序入口出发，搜索所有可达的代码。在搜索的同时，它还将执行初始化代码，并在最终生成可执行文件时，将已初始化的堆保存至一个堆快照之中。

Substrate VM就可以直接从目标程序开始运行，而无须重复进行Java虚拟机的初始化过程。但相应地，原理上也决定了Substrate VM必须要求目标程序是完全封闭的，即不能动态加载其他编译期不可知的代码和类库。基于这个假设，Substrate VM才能探索整个编译空间，并通过静态分析推算出所有虚方法调用的目标方法。

## 使 Java 适应原生

以往单个服务需要 7*24 小时不间断运行，需要单机高可用，此时 Java 服务就很适合。但是 Java 应用程序都需要运行在上百兆的 JRE 上，在微服务上就并不合适。

同时在微服务中，应用可以随时拆分，每个应用并不需要很大的内存，而是需要快速启动、随时更新，也可能不需要长时间运行。Java 应用程序本来启动就很慢，同时需要充分预热才能够获取高性能。

GraalVM 提前编译就提供了一种解决方案，官方给出使用了 GraalVm 后启动时间能够提高 50 倍，内存有 5 倍的下降。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-07-10-015941.png)

# Graal VM 的缺点

Java 语言在微服务天生就有劣势，这是因为 Java 诞生之初的口号就是“一次编写，到处运行”。这个口号已经植入 Java 的基因中。如果想改变这些（真的要拿Java的劣势去和别的语言的优势相比），会有很多困难：

- Java 语言的反射机制，使得在编译期生成可执行文件很困难。因为通过反射机制可以在运行期间动态调用API接口，这些在编译期是无法感知的。除非放弃反射机制，或者在编译时提供配置文件供反射调用。
- ASM、CGLIB、Javassist字节码库会在运行时生成、修改字节码，这些也没法通过 AOT 编译成原生代码。比如 Spring 的依赖注入就使用了 CGLIB 增强。Spring 已经在新版本中适配了 GraalVM，可以关闭 CGLIB。
- 放弃 HotSpot 虚拟机本身的内部借款，因为在本地镜像中，连 HotSpot 本身都被消灭了。
- 启动时间、内存使用确实有大幅度优化，但是对于长时间运行的大型应用，未必有 HotSpot 的 Java 应用程序速度快。

# Graal VM 的工作原理

Graal VM的基本工作原理是将这些语言的源代码（例如JavaScript）或源代码编译后的中间格式（例如LLVM字节码）通过解释器转换为能被Graal VM接受的中间表示（Intermediate Representation，IR），譬如设计一个解释器专门对LLVM输出的字节码进行转换来支持C和C++语言，这个过程称为“程序特化”（Specialized，也常称为Partial Evaluation）。

Graal VM提供了Truffle工具集来快速构建面向一种新语言的解释器，并用它构建了一个称为Sulong的高性能LLVM字节码解释器。

# 在 macOS 上安装 Graal VM

Linux、Windows 等其他平台可以参考 [Install GraalVM](https://www.graalvm.org/getting-started/#install-graalvm)。由于我使用 macOS，本篇文章介绍如何在 macOS 上安装 Graal VM，基于 OpenJDK 11 的 GraalVM Community Edition。

## 安装 Graal VM

macOS 上的 GraalVM 社区版是 tar.gz 文件，JDK 的安装目录是：

```
/Library/Java/JavaVirtualMachines/<graalvm>/Contents/Home
```

x86 64位的 macOS 安装步骤如下：

1. 在 [GraalVM Releases repository on GitHub](https://github.com/graalvm/graalvm-ce-builds/releases) 上找到 `graalvm-ce-java11-darwin-amd64-20.1.0.tar.gz
` 下载。
2. 解压缩
```
tar -xvf graalvm-ce-java11-darwin-amd64-20.1.0.tar.gz
```
3. 将文件夹移动到 `/Library/Java/JavaVirtualMachines` 目录下（需要使用 sudo）。
```
sudo mv graalvm-ce-java11-20.1.0 /Library/Java/JavaVirtualMachines
```

检测是否安装成功，可以运行命令：

```
/usr/libexec/java_home -V
```

运行结果为：

```
Matching Java Virtual Machines (2):
    11.0.7, x86_64:	"GraalVM CE 20.1.0"	/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.1.0/Contents/Home
    1.8.0_201, x86_64:	"Java SE 8"	/Library/Java/JavaVirtualMachines/jdk1.8.0_201.jdk/Contents/Home

/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.1.0/Contents/Home
```

4. 由于机器上可能存在多个 JDK，需要配置运行环境。

将 GraalVM `bin` 目录加入 `PATH` 环境变量。

```
export PATH=/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.1.0/Contents/Home/bin:$PATH
```

设置 `JAVA_HOME` 环境变量。

```
export JAVA_HOME=/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.1.0/Contents/Home
```

注意：可能需要修改 bashc 配置文件。

## 安装 GraalVM 组件

通过上述步骤，已经安装好了 GraalVM 的基础组件，如果需要额外支持 Python、R 等语言，需要使用 `gu` 组件。

```
gu install ruby
gu install r
gu install python
gu install wasm
```

安装 `GraalVM Native Image`，运行命令：

```
gu install native-image
```

安装 `LLVM toolchain` 组件，运行命令：

```
gu install llvm-toolchain
```

# 将基于 Spring Boot 的 Java 应用程序编译成本地应用程序

可以参考 GitHub 的 [spring-boot-graalvm](https://github.com/jonashackt/spring-boot-graalvm#relocate-annotation-classpath-scanning-from-runtime-to-build-time) 项目，这个项目里详细列出了 GraalVM 编译 Spring Boot Java 应用程序可能出现的所有问题，并对比了 Java 应用启动与编译成本地可执行的 Java 程序。

Spring与Graal VM共同维护的在Spring Graal Native项目已经提供了大多数Spring Boot组件的配置信息（以及一些需要在代码层面处理的Patch），我们只需要简单依赖该工程即可。这样 Graal VM 就能获取编译期的反射、动态代理等配置。我们只需要简单依赖工程即可。

需要在 pom.xml 中增加依赖：

```
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-context-indexer</artifactId>
    <optional>true</optional>
</dependency>
<dependency>
    <groupId>org.springframework.experimental</groupId>
    <artifactId>spring-graalvm-native</artifactId>
    <version>0.7.1</version>
</dependency>
```

指定启动类的路径：

```
<properties>
    <start-class>com.yano.workflow.WorkflowApplication</start-class>
</properties>
```

配置一个独立的 profile，在编译时通过 `native-image-maven-plugin` 插件将其编译成本地可执行文件。

```
<profiles>
    <profile>
        <id>native</id>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.graalvm.nativeimage</groupId>
                    <artifactId>native-image-maven-plugin</artifactId>
                    <version>20.1.0</version>
                    <configuration>
                        <buildArgs>-J-Xmx4G -H:+TraceClassInitialization
                            -H:+ReportExceptionStackTraces
                            -Dspring.graal.remove-unused-autoconfig=true
                            -Dspring.graal.remove-yaml-support=true
                        </buildArgs>
                        <imageName>${project.artifactId}</imageName>
                    </configuration>
                    <executions>
                        <execution>
                            <goals>
                                <goal>native-image</goal>
                            </goals>
                            <phase>package</phase>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

该插件在 Maven 中央仓库不存在，需要指定 pluginRepositories 和 repositories：

```
<repositories>
    <repository>
        <id>spring-milestones</id>
        <name>Spring Milestones</name>
        <url>https://repo.spring.io/milestone</url>
    </repository>
</repositories>
<pluginRepositories>
    <pluginRepository>
        <id>spring-milestones</id>
        <name>Spring Milestones</name>
        <url>https://repo.spring.io/milestone</url>
    </pluginRepository>
</pluginRepositories>
```

Graal VM不支持CGLIB，只能使用JDK动态代理，所以应当把Spring对普通类的Bean增强给关闭掉。Spring Boot 的版本要大于等于 2.2，`SpringBootApplication` 注解上将 proxyBeanMethods 参数设置为 false。

```java
@SpringBootApplication(proxyBeanMethods = false)
public class SpringBootHelloApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringBootHelloApplication.class, args);
	}

}
```

在命令行通过 maven 打包项目：

```
mvn -Pnative clean package
```

最终在 target 目录能够看到可执行文件，大概在 50M 左右，相比 fat jar 为 17M。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-07-10-063311.png)

```
java -jar target/spring-boot-graal-0.0.1-SNAPSHOT.jar

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::             (v2.3.0.M4)

2020-04-30 15:40:21.187  INFO 40149 --- [           main] i.j.s.SpringBootHelloApplication         : Starting SpringBootHelloApplication v0.0.1-SNAPSHOT on PikeBook.fritz.box with PID 40149 (/Users/jonashecht/dev/spring-boot/spring-boot-graalvm/target/spring-boot-graal-0.0.1-SNAPSHOT.jar started by jonashecht in /Users/jonashecht/dev/spring-boot/spring-boot-graalvm)
2020-04-30 15:40:21.190  INFO 40149 --- [           main] i.j.s.SpringBootHelloApplication         : No active profile set, falling back to default profiles: default
2020-04-30 15:40:22.280  INFO 40149 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-04-30 15:40:22.288  INFO 40149 --- [           main] i.j.s.SpringBootHelloApplication         : Started SpringBootHelloApplication in 1.47 seconds (JVM running for 1.924)
```

能够通过命令行直接运行程序，启动速度贼快。对比 Hello World web 普通应用程序，启动时间是 `1.47s`，占用内存 `491 MB`。

而编译成本地代码的 Spring Boot 程序，启动速度是 `0.078s`，占用内存 `30 MB`。

```
./spring-boot-graal

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::

2020-05-01 10:25:31.200  INFO 42231 --- [           main] i.j.s.SpringBootHelloApplication         : Starting SpringBootHelloApplication on PikeBook.fritz.box with PID 42231 (/Users/jonashecht/dev/spring-boot/spring-boot-graalvm/target/native-image/spring-boot-graal started by jonashecht in /Users/jonashecht/dev/spring-boot/spring-boot-graalvm/target/native-image)
2020-05-01 10:25:31.200  INFO 42231 --- [           main] i.j.s.SpringBootHelloApplication         : No active profile set, falling back to default profiles: default
2020-05-01 10:25:31.241  WARN 42231 --- [           main] io.netty.channel.DefaultChannelId        : Failed to find the current process ID from ''; using a random value: 635087100
2020-05-01 10:25:31.245  INFO 42231 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-05-01 10:25:31.245  INFO 42231 --- [           main] i.j.s.SpringBootHelloApplication         : Started SpringBootHelloApplication in 0.078 seconds (JVM running for 0.08)
```

# 总结

- 本篇文章主要讨论 GraalVM 和 Java 的关系，GraalVM 上能够运行很多语言，可参考[Why GraalVM](https://www.graalvm.org/docs/why-graal/)。
- 注意 Graal 的环境变量配置，配置错误的话，是没法编译的，同时 JDK 11 需要高版本的 maven 版本。
- Graal VM 和 GraalVM 是一个东东，官网是叫 GraalVM，但是其他地方都是 Graal VM……
- 为了适应原生，JDK 自身也在演进。
- GraalVM 编译的 Java 本地应用仅适用于一次性运行、短时间运行的场景，长时间运行还是传统 Java 程序效率高。
- 本篇文章的 GitHub 地址：[LjyYano/Thinking_in_Java_MindMapping](https://github.com/LjyYano/Thinking_in_Java_MindMapping)

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)
