---
date: 2022-07-09
---


- [说明](#%E8%AF%B4%E6%98%8E)
- [思维导图](#%E6%80%9D%E7%BB%B4%E5%AF%BC%E5%9B%BE)
    - [目录](#%E7%9B%AE%E5%BD%95)
    - [内核接收网络包](#%E5%86%85%E6%A0%B8%E6%8E%A5%E6%94%B6%E7%BD%91%E7%BB%9C%E5%8C%85)
    - [内核与用户进程协作](#%E5%86%85%E6%A0%B8%E4%B8%8E%E7%94%A8%E6%88%B7%E8%BF%9B%E7%A8%8B%E5%8D%8F%E4%BD%9C)
    - [内核发送网络包](#%E5%86%85%E6%A0%B8%E5%8F%91%E9%80%81%E7%BD%91%E7%BB%9C%E5%8C%85)
    - [TCP 连接](#tcp-%E8%BF%9E%E6%8E%A5)
    - [网络性能优化](#%E7%BD%91%E7%BB%9C%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96)
- [GitHub 项目](#github-%E9%A1%B9%E7%9B%AE)

# 说明

经朋友推荐发现一本好书：[《深入理解 Linux 网络》](https://book.douban.com/subject/35922722/)，本文以思维导图的形式，展示俺做的笔记，原书对 Linux 网络进行了详细的源码分析，非常推荐~本文就没有长篇文字了，图片都是自己画的，希望有人引用时，能够注明本文 GitHub 地址 ^_^

# 思维导图

## 目录

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-41-38.png?x-oss-process=style/yano)

## 内核接收网络包

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-42-06.png?x-oss-process=style/yano)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-42-12.png?x-oss-process=style/yano)

## 内核与用户进程协作

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-43-00.png?x-oss-process=style/yano)

同步阻塞流程（整体）：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-44-05.png?x-oss-process=style/yano)

同步阻塞流程（细节）：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-44-12.png?x-oss-process=style/yano)

epoll 原理：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-44-31.png?x-oss-process=style/yano)

## 内核发送网络包

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-10.png?x-oss-process=style/yano)

整体流程：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-18.png?x-oss-process=style/yano)

read + send 系统调用：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-24.png?x-oss-process=style/yano)

sendfile 系统调用：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-30.png?x-oss-process=style/yano)

## TCP 连接

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-54.png?x-oss-process=style/yano)

建立连接流程：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-45-59.png?x-oss-process=style/yano)

内核内存划分：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-46-06.png?x-oss-process=style/yano)

## 网络性能优化

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2022-07-09-20-46-33.png?x-oss-process=style/yano)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。

# 我的公众号

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)