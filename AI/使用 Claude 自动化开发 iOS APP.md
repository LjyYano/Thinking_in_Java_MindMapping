# 使用 Claude 自动化开发 iOS APP

## 说明
作为 iOS 开发小白，本文记录了使用 Claude 自动化开发一个"深呼吸"功能 APP 的全过程。整个开发过程中无需手动编写任何代码，完全依靠与 Claude 的交互来完成。

## 前置条件
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- Claude 桌面版（配置好 MCP 协议）
- Xcode

## 开发过程

### 1. 项目目标

开发一个深呼吸引导 APP，帮助用户进行呼吸练习：

![APP 效果图](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-14-05.png?x-oss-process=image/resize,w_500)

### 2. 环境配置

#### Claude MCP 配置

![MCP 配置](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-15-10.png?x-oss-process=image/resize,w_500)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yano/code/ios_breath"
      ]
    }
  }
}
```

### 3. 功能开发流程

#### 基础功能实现
首先与 Claude 交互实现基本的计时器功能：

![初始开发对话](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-22-48.png?x-oss-process=image/resize,w_500)

Claude 生成了完整的代码:

![初始代码](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-00.png?x-oss-process=image/resize,w_500)

运行效果:

![运行效果1](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-25.png?x-oss-process=image/resize,w_300)
![运行效果2](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-24-32.png?x-oss-process=image/resize,w_300)

#### 功能增强

1. **自定义时间设置**

让 Claude 添加时间自定义功能：

![时间设置实现](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-28-38.png?x-oss-process=image/resize,w_300)

2. **声音提示功能**

添加语音提示和开关控制：

![声音功能实现](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-31-51.png?x-oss-process=image/resize,w_500)

遇到编译错误时，Claude 能快速定位并修复：

![错误修复](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-32-24.png?x-oss-process=image/resize,w_500)

3. **UI 优化**

逐步改进界面设计：

![UI优化1](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-35-52.png?x-oss-process=image/resize,w_500)
![UI优化2](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-36-01.png?x-oss-process=image/resize,w_300)
![UI优化3](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-13-36-13.png?x-oss-process=image/resize,w_300)

### 4. 最终效果

经过多轮优化后的界面：

![最终效果1](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-09.png?x-oss-process=image/resize,w_300)
![最终效果2](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-21.png?x-oss-process=image/resize,w_300)
![最终效果3](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-12-01-14-07-36.png?x-oss-process=image/resize,w_300)

### 5. 开发心得

1. Claude 能够准确理解需求并生成完整可用的代码
2. 遇到编译错误时，Claude 能够快速定位并修复问题
3. UI 优化过程中，Claude 能提供专业的设计建议并实现
4. 整个开发过程完全通过对话完成，无需手动编写代码

最终实现了一个功能完整的深呼吸引导 APP，包含：
- 可自定义的呼吸时间设置
- 语音提示功能（可开关）
- 优雅的 UI 界面和动画效果
- 流畅的用户交互体验

# 总结

Claude 很强大，多多探索。