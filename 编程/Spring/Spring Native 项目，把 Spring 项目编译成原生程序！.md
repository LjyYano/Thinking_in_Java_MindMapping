---
date: 2021-06-20
---


- [Spring Native 是什么](#spring-native-是什么)
  - [优点](#优点)
  - [缺点](#缺点)
  - [原生镜像（native image）和常规 JVM 程序的区别](#原生镜像native-image和常规-jvm-程序的区别)
- [前置条件：GraalVM](#前置条件graalvm)
  - [支持的语言](#支持的语言)
  - [关键特性](#关键特性)
  - [GraalVM 下的 Java 微服务](#graalvm-下的-java-微服务)
- [Spring Native 的 Hello World](#spring-native-的-hello-world)
  - [系统要求](#系统要求)
  - [示例代码](#示例代码)
    - [配置 Spring Boot 版本](#配置-spring-boot-版本)
    - [添加 Spring Native 依赖](#添加-spring-native-依赖)
    - [添加 Spring AOT 插件](#添加-spring-aot-插件)
    - [开启 native image 支持](#开启-native-image-支持)
    - [Maven Repository](#maven-repository)
  - [构建本地应用程序](#构建本地应用程序)
  - [运行本地应用](#运行本地应用)
  - [可能遇到的问题](#可能遇到的问题)
    - [权限问题](#权限问题)
    - [内存问题](#内存问题)
- [Spring Native 所遇到的问题](#spring-native-所遇到的问题)
- [参考链接](#参考链接)

Spring 发布了 Spring Native 的 beta 版本，该功能已经在 start.spring.io 上可用了。

# Spring Native 是什么

Spring Native 可以通过 GraalVM 将 Spring 应用程序编译成原生镜像，提供了一种新的方式来部署 Spring 应用。Spring Native 支持 Java 和 Kotlin。

这个项目的目标是寻找 Spring JVM 的替代方案，提供一个能将应用程序打包，并运行在轻量级容器的方案。期望能够在 Spring Native 中支持所有的 Spring 应用程序（几乎不用修改代码）。

## 优点

- 编译出来的原生 Spring 应用可以作为一个独立的可执行文件进行部署（不需要安装 JVM）
- 几乎瞬时的启动（一般小于 100 毫秒）
- 瞬时的峰值性能
- 更低的资源消耗

## 缺点

- 比 JVM 更长的构建时间
- 相比于传统的 Java 运行方式，运行时优化不足

## 原生镜像（native image）和常规 JVM 程序的区别

- 在构建时会从主入口点，静态分析应用程序
- 在构建时会移除未使用的代码
- 需要配置反射、动态代理等
- classpath 在构建时就已经确定
- 没有类延迟加载：可执行文件中所有的内容都会在启动时加载到内存中
- 在构建时就运行了一些代码
- 构建原生镜像还存在一些 [局限性](https://github.com/oracle/graal/blob/master/substratevm/Limitations.md)

# 前置条件：GraalVM

GraalVM 介绍起来篇幅比较长，这里仅简要介绍。官网：https://www.graalvm.org/

GraalVM 是一个高性能的多语言运行时环境。设计目的是能够提高用 Java 和其他 JVM 语言编写的应用程序的执行速度，同时还为 JavaScript、Ruby、Python 和许多其他流行语言提供运行时。GraalVM 的多语言能力使得在一个应用程序中混合使用多种编程语言成为可能，同时消除了不同语言间互相调用的成本。详细内容可参考：[Get Started with GraalVM](https://www.graalvm.org/docs/getting-started/)

## 支持的语言

![Specific Languages 1](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325144139.png?x-oss-process=style/yano)

![Specific Languages 2](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325144402.png?x-oss-process=style/yano)

## 关键特性

![关键特性](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325144431.png?x-oss-process=style/yano)

## GraalVM 下的 Java 微服务

具体内容可参考：[Lightweight cloud-native Java applications](https://medium.com/graalvm/lightweight-cloud-native-java-applications-35d56bc45673)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325144533.png?x-oss-process=style/yano)

# Spring Native 的 Hello World

构建 Spring Boot native 应用程序有 2 种方式：
- 使用 [Spring Boot Buildpacks support](https://docs.spring.io/spring-native/docs/current/reference/htmlsingle/#getting-started-buildpacks) 构建一个包含本地可执行文件的轻量级容器。
- 使用 [ the GraalVM native image Maven plugin support](https://docs.spring.io/spring-native/docs/current/reference/htmlsingle/#getting-started-native-image) 构建一个本地可执行文件。

本文只介绍第一种。

## 系统要求

在待构建的机器上，必须安装了 Docker，可以参考 [Get Docker](https://docs.docker.com/get-docker/)，同时注意要能够以非 root 用户启动和运行。

可以通过使用 `docker run hello-world` （不包含`sudo`）命令检查 Docker daemon 是否可用。

## 示例代码

一个简单的 Spring Boot Web 程序：

```java
git clone https://github.com/spring-guides/gs-rest-service
cd gs-rest-service/complete
```

### 配置 Spring Boot 版本

```java
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.4.4</version>
    <relativePath/>
</parent>
```

### 添加 Spring Native 依赖

`org.springframework.experimental:spring-native` 提供了 native 配置的 API，例如 `@NativeHint` 这些 Spring 运行成 native image 的注解类。

```java
<dependencies>
    <!-- ... -->
    <dependency>
        <groupId>org.springframework.experimental</groupId>
        <artifactId>spring-native</artifactId>
        <version>0.9.1</version>
    </dependency>
</dependencies>
```

### 添加 Spring AOT 插件

Spring AOT 插件执行代码的提前转换，用以修复 native image 的兼容性。

```java
<build>
    <plugins>
        <!-- ... -->
        <plugin>
            <groupId>org.springframework.experimental</groupId>
            <artifactId>spring-aot-maven-plugin</artifactId>
            <version>0.9.1</version>
            <executions>
                <execution>
                    <id>test-generate</id>
                    <goals>
                        <goal>test-generate</goal>
                    </goals>
                </execution>
                <execution>
                    <id>generate</id>
                    <goals>
                        <goal>generate</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### 开启 native image 支持

Spring Boot 的 [Spring Boot Buildpacks support](https://docs.spring.io/spring-native/docs/current/reference/htmlsingle/#getting-started-buildpacks) 可以将 Spring Boot 应用程序打包成一个容器。[native image buildpack](https://github.com/paketo-buildpacks/native-image) 可以通过 `BP_NATIVE_IMAGE` 环境变量开启。

```java
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <image>
            <builder>paketobuildpacks/builder:tiny</builder>
            <env>
                <BP_NATIVE_IMAGE>true</BP_NATIVE_IMAGE>
            </env>
        </image>
    </configuration>
</plugin>
```

### Maven Repository

```java
<repositories>
    <!-- ... -->
    <repository>
        <id>spring-release</id>
        <name>Spring release</name>
        <url>https://repo.spring.io/release</url>
    </repository>
</repositories>
```

```java
<pluginRepositories>
    <!-- ... -->
    <pluginRepository>
        <id>spring-release</id>
        <name>Spring release</name>
        <url>https://repo.spring.io/release</url>
    </pluginRepository>
</pluginRepositories>
```

## 构建本地应用程序

```java
mvn spring-boot:build-image
```

通过此命令，可以创建一个使用 GraalVM native image compiler 构建的 Linux 容器，默认情况下，这个镜像是在本地。

## 运行本地应用

可以使用 docker images 命令，查看镜像：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325154902.png?x-oss-process=style/yano)

使用 docker 启动这个镜像：

```java
docker run --rm -p 8080:8080 rest-service:0.0.1-SNAPSHOT
```

本次启动时间是`47ms`，而 JVM 的程序启动一般都是`1500ms`左右。

![启动时间](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325155102.png?x-oss-process=style/yano)

现在服务已经启动了，可以通过 [localhost:8080/greeting](localhost:8080/greeting) 访问服务。在浏览器中可以看到：

```java
{"id":1,"content":"Hello, World!"}
```

## 可能遇到的问题

### 权限问题

若编译时遇到下面的情况，则表明构建时没有 docker 权限，如果配置一直不成功，可以直接在 `mvn spring-boot:build-image` 命令前加个 `sudo`。

![报错 1](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325152452.png?x-oss-process=style/yano)

### 内存问题

若编译时遇到下面的情况，是 OOM 问题，需要把 Docker 的内存改大（8G）。

![报错 2](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210325152601.png?x-oss-process=style/yano)

以 Mac 的 Docker Client 设置为例：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/B241FBEC-2B1B-4F18-A1EE-891C921272A1.png?x-oss-process=style/yano)

# Spring Native 所遇到的问题

这部分参考自：[云原生时代，Java 的危与机](https://www.infoq.cn/article/rqfww2r2zpyqiolc1wbe)

JVM 的程序运行时间长，是因为存在虚拟机的初始化和类加载过程，如果将字节码直接编译成原生代码，则可以彻底解决这些问题。同时因为没有即时编译器在运行时编译，所有代码都在编译期编译和优化。因为少了 Java 虚拟机、即时编译器这些额外组件，原生程序也能够省去它们原本消耗的内存资源和镜像体积。

Java 支持提前编译最大的困难，在于 Java 是一门动态链接的语言，它假设程序的代码空间是开发的，允许在程序的任何时候通过类加载器去加载新的类，作为程序的一部分。要进行提前编译，就必须放弃这部分动态性，所有要运行的代码必须在编译期全部可知。这样动态加载、反射（通过反射可以调用在编译期不可知的方法）、动态代理、字节码生成库（如 CGLib）等一切会运行时产生新代码的功能都不再可用。

- 对于反射，需要用户在编译期，通过配置文件或编译器参数的形式，明确告知编译器程序代码中哪些方法只通过反射来访问的。
- 用户往往不知道动态生成字节码的具体信息，这些只能由程序去做妥协。默认情况下，每一个 Spring 管理的 Bean 都要用到 CGLib。从 Spring Framework 5.2 开始增加了@proxyBeanMethods 注解来排除对 CGLib 的依赖，仅使用标准的动态代理去增强类。

当然 Spring Native 遇到的问题有很多，且仍然处于试验阶段。以原生方式运行后，启动时间是能够缩短很多，但是程序的运行效率还是若于传统基于 JVM 的方式，且编译成原生程序代码的时间更长。

# 参考链接

- [Spring Native documentation](https://docs.spring.io/spring-native/docs/current/reference/htmlsingle/#overview)
- [GitHub spring-projects-experimental/spring-native](https://github.com/spring-projects-experimental/spring-native/tree/master/samples)
- [Get Started with GraalVM](https://www.graalvm.org/docs/getting-started/)