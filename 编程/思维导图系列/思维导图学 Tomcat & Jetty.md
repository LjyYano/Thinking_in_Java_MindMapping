---
date: 2020-02-20
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)


# 目录

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024008.png)

# 基础

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024110.png)

# Tomcat架构

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024155.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024217.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024252.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024404.png)

# Jetty架构

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024549.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-030504.png)

# 其他

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024726.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024817.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024930.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-024952.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-02-28-025019.png)

# 对Tomcat的一些看法

作为一个Servlet容器，Tomcat的核心功能就是维护网络请求，将客户端的请求分解处理，分发到对应的具体处理逻辑中，然后获取响应结果包装返回给客户端。

但是个人感觉Tomcat的设计还是太重了，它并没有Jetty的架构灵活简单。Tomcat的架构设计简洁明了，但是查看源码实现并不简洁。Tomcat虽然能够嵌入式自启动，但是支持多个Host虚拟主机、Engine这些特性在微服务成为趋势的今天显得冗余。

