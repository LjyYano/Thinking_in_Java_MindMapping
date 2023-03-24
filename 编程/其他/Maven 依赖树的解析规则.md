---
date: 2020-11-13
---

- [一、依赖树结构](#一依赖树结构)
- [二、依赖问题](#二依赖问题)
  - [2.1 依赖冲突](#21-依赖冲突)
  - [2.2 依赖循环](#22-依赖循环)
  - [2.3 依赖排除](#23-依赖排除)
- [三、依赖分析](#三依赖分析)
  - [3.1 Maven 命令行](#31-maven-命令行)
  - [3.2 IDEA 插件](#32-idea-插件)
- [四、参考链接](#四参考链接)

对于 Java 开发工程师来说，Maven 是依赖管理和代码构建的标准。遵循 <font color = red>「约定大于配置」</font> 理念。Maven 是 Java 开发工程师日常使用的工具，本篇文章简要介绍一下 Maven 的依赖树解析。

# 一、依赖树结构

在 pom.xml 的 dependencies 中声明依赖包后，Maven 将直接引入依赖，并通过解析直接依赖的 pom.xml 将传递性依赖导入到当前项目，最终形成一个树状的依赖结构。

<font color = red>原则：深度优先遍历依赖，并缓存节点剪枝。</font>

比如下图依赖：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-11-07-100845.png?x-oss-process=image/resize,h_300)

1. A→B→D→E/F
2. A→C→D

在第 2 步`A→C→D`时，由于节点 D 已经被缓存，所以会立即返回，不必再次遍历 E/F，避免重复搜索。

# 二、依赖问题

## 2.1 依赖冲突

但是假如 2 个包同时依赖了同一个 jar 包，但是这个 jar 包版本不同，规则是什么样的呢？

比如下图 A 通过 B 和 D 引入了 1.0 版本的 E，同时 A 通过 C 引入了 2.0 版本的 E。针对这种多个版本构建依赖时，Maven 采用 <font color = red>「短路径优先」</font> 原则，即 A 会依赖 2.0 版本的 E。如果想引入 1.0 版本的 E，需要直接在 A 的 pom 中声明 E 的版本。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-11-07-105552.png?x-oss-process=image/resize,h_350)

如果 Java 项目过于庞大，或者依赖传递过于复杂时，可以使用 <font color = red>dependencyManagement</font> 定义默认的版本号，一次定义全局生效，避免开发者自行管理依赖的版本。

## 2.2 依赖循环

比如：A 依赖了 B，同时 B 又依赖了 A。这种循环依赖可能不会直接显现，但是可能会在一个很长的调用关系显现出来，也可能是模块架构的设计不合理。

我们可以使用 `mvn dependency:tree -Dverbose | grep cycle` 来判断项目中是否存在「循环依赖」。

## 2.3 依赖排除

我们可以使用 `exclusion` 来解决依赖冲突，但是 `exclusion` 会降低 Maven 依赖解析的效率，因为对应的 pom 文件不能缓存，每次都要重新遍历子树。

对于依赖排除：

- `exclusion` 会造成依赖重复扫描和缓存。
- 在距离根节点越远的 `exclusion`，影响的范围越小。
- 依赖树高度越高，引入 `exclusion` 的代价越大。

#  三、依赖分析

## 3.1 Maven 命令行

`mvn dependency:tree -Dverbose`

IDEA 插件 [Maven Helper](https://plugins.jetbrains.com/plugin/7179-maven-helper/)，打开 POM 文件后在左下角点击 `Dependency Analyzer`。

## 3.2 IDEA 插件

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2023-02-14-11-56-11.png?x-oss-process=image/resize,h_600)

# 四、参考链接

- [Apache Maven Project](https://maven.apache.org/index.html), by Apache
- [阿里云云效 Maven](https://developer.aliyun.com/mvn/guide), by 阿里云