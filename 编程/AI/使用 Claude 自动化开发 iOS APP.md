
## 目录

- [说明](#说明)
- [前置条件](#前置条件)
- [过程记录](#过程记录)
  - [1. 明确目标](#1-明确目标)
  - [2. Claude 配置](#2-claude-配置)
  - [3. 初始化 Xcode 项目](#3-初始化-xcode-项目)
  - [4. 与 Claude 交互](#4-与-claude-交互)
    - [初始化项目](#初始化项目)
    - [自定义时间](#自定义时间)
    - [增加声音提示、声音开关](#增加声音提示声音开关)
    - [UI 初步优化](#ui-初步优化)
    - [bug 修复](#bug-修复)
    - [UI 优化](#ui-优化)

# 说明

iOS 开发小白，使用 Claude 自动化开发 iOS APP 的过程记录（全程没有自己写一行代码，甚至连一行复制粘贴都没有~）

# 前置条件

- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- Claude 桌面版（配置好 MCP 协议）
- Xcode

# 过程记录

## 1. 明确目标

通过 Claude 自动化开发一个“深呼吸”功能的 APP：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-14-05.png)

## 2. Claude 配置

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-15-10.png)

```json
{
  "globalShortcut": "",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yano/code/ios_breath",
        "/Users/yano/code/java-research",
        "/Users/yano/code/Thinking_in_Java_MindMapping"
      ]
    }
  }
}
```

## 3. 初始化 Xcode 项目

点击 `New Project`，选择 `App`，填写项目名称 `Breath`，点击 `Next`，选择存储路径，点击 `Create`。

## 4. 与 Claude 交互

### 初始化项目

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-22-48.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-23-08.png)

生成的代码如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-00.png)

运行效果：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-25.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-32.png)

### 自定义时间

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-25-48.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-28-38.png)

### 增加声音提示、声音开关

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-31-51.png)

但是代码编译不通过，又让 Claude 帮忙修改：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-32-24.png)

之后增加声音控制开关：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-32-37.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-31-32.png)

### UI 初步优化

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-35-03.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-35-15.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-35-52.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-36-01.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-36-13.png)

### bug 修复

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-37-26.png)

### UI 优化

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-37-53.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-38-20.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-09.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-21.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-36.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-08-18.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-48.png)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-08-04.png)