
- [为什么需要 MCP？](#为什么需要-mcp)
- [基本概念](#基本概念)
  - [关键术语](#关键术语)
  - [分层架构](#分层架构)
  - [传输机制](#传输机制)
- [Java Spring AI 集成实践](#java-spring-ai-集成实践)
  - [POM 依赖](#pom-依赖)
  - [配置示例 `application.properties`](#配置示例-applicationproperties)
  - [暴露 Tool](#暴露-tool)
  - [启动服务](#启动服务)
  - [在 MCP client 中配置 mcp.setting](#在-mcp-client-中配置-mcpsetting)
  - [使用 MCP！](#使用-mcp)
  - [说明](#说明)
- [典型应用场景](#典型应用场景)
- [MCP 生态与未来趋势](#mcp-生态与未来趋势)
- [参考链接](#参考链接)

---

> **目的**：帮助 Java / Spring Boot 开发者快速理解 MCP 的设计动机、协议细节、以及 如何在 Spring AI 中落地。

## 为什么需要 MCP？

MCP 助力开发者在 LLM 之上构建智能体和复杂工作流。由于 LLM 需要频繁与外部数据和工具集成，MCP 提供了以下核心价值：

* **开箱即用的集成能力**：提供丰富的预置集成方案，LLM 可直接接入使用
* **灵活的供应商切换**：支持在不同 LLM 服务商之间无缝迁移
* **安全最佳实践**：内置数据安全防护机制，确保基础设施安全可控

MCP 用 **JSON‑RPC 2.0 + 能力发现** 的模式，把「模型 ↔ 应用 ↔ 工具」之间的交互标准化，实现 *一次接入，多处复用*。

> MCP 协议就好比 USB 接口，USB 设备可以通过 USB Hub 连接到不同的计算机上，而不需要重新设计接口。
> - 我们在电脑上可以同时使用多个 USB 设备（鼠标、键盘、硬盘、游戏手柄），这些 USB 设备有不同的功能，只要实现了标准的 USB 接口协议即可。
> - 电脑可以类比成 LLM，USB Hub 可以类比成 MCP Server，USB 设备可以类比成 Tool、Resource、Prompt 等。
> - 通过 MCP 协议，LLM 可以通过 USB Hub 访问不同的 USB 设备，从而扩展出各种各样的能力（发邮件、打电话、地图旅行规划、订票）。

从某种程度上说，MCP 就像是设计模式中的命令（Command）模式 + 外观（Facade）模式。

## 基本概念

### 关键术语

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-04-22-13-43-40.png)

* **MCP 主机**：需要通过 MCP 访问数据的程序，如 Claude Desktop、IDE 或 AI 工具
* **MCP 客户端**：与服务器保持 1:1 连接的协议客户端
* **MCP 服务器**：通过标准化的模型上下文协议暴露特定能力的轻量级程序
* **本地数据源**：MCP 服务器可以安全访问的计算机文件、数据库和服务
* **远程服务**：MCP 服务器可以通过互联网连接的外部系统（例如通过 API）


### 分层架构

```
┌────────────────────────────┐

│  Client / Server API 层    │ ← McpClient / McpServer

├────────────────────────────┤

│  Session 会话层            │ ← 会话 & 状态管理

├────────────────────────────┤

│  Transport 传输层          │ ← Stdio / SSE / WebSocket / gRPC

└────────────────────────────┘
```

MCP 采用分层架构设计，每一层都有其特定的职责：

1. **Client / Server API 层**
   - 提供 McpClient 和 McpServer 接口
   - 处理高层业务逻辑和协议交互
   - 负责能力发现和工具调用

2. **Session 会话层**
   - 管理客户端和服务器之间的会话状态
   - 处理会话的生命周期（初始化、运行、关闭）
   - 维护会话上下文和状态信息

3. **Transport 传输层**
   - 提供多种传输机制支持：
     - Stdio：标准输入输出，适合本地进程间通信
     - SSE (Server-Sent Events)：单向服务器推送
     - WebSocket：全双工通信
     - gRPC：高性能 RPC 框架
   - 处理底层通信细节和协议转换

这种分层设计使得 MCP 具有：
- 良好的可扩展性：可以轻松添加新的传输机制
- 清晰的职责分离：各层专注于自己的功能
- 灵活的部署方式：支持多种通信场景

### 传输机制

| 传输 | 场景 | 特点 |
|------|------|------|
| **Stdio** | 本地 CLI / 子进程 | 零网络开销，启动快 |
| **HTTP + SSE** | 微服务 / Web 应用 | POST 请求 + SSE 推流，部署友好 |
| **自定义** | WebSocket / gRPC | 只需实现 Transport 接口即可 |


## Java Spring AI 集成实践

使用 [Spring AI](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html) 开发，详细说明可以参考官网文档。

> MCP 分为 Stdio 和 SSE 两种传输方式，下面的例子使用 SSE 方式，最简化开发一个发票助手 MCP，并展示如何通过模型自动调用这个 MCP。

### POM 依赖

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webflux</artifactId>
</dependency>
```

### 配置示例 `application.properties`

```
spring.main.banner-mode=off
# logging.pattern.console=
spring.ai.mcp.server.name=my-invoice-server
spring.ai.mcp.server.version=0.0.1
```

详细的配置参数及默认值可以参考官方文档：[Spring AI / Model Context Protocol (MCP) / MCP Server Boot Starters]([https://](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-server-boot-starter-docs.html#_configuration_properties))。

### 暴露 Tool

这里就模拟一个非常简单的功能，仅拼装对应参数，返回发票链接。

```java
@Service
public class InvoiceService {

    @Tool(description = "获取发票链接")
    public String getInvoiceUrl(@ToolParam(required = true, description = "发票 id") String invoiceId) {
        return "https://www.example.com/invoice/" + invoiceId;
    }
}
```

```JAVA
@SpringBootApplication
public class McpServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpServerApplication.class, args);
    }

    @Bean
    public ToolCallbackProvider invoiceTools(InvoiceService invoiceService) {
        return MethodToolCallbackProvider.builder().toolObjects(invoiceService).build();
    }
}
```

### 启动服务

执行 `java -jar mcp-server.jar` 启动服务，默认监听 8080 端口。

### 在 MCP client 中配置 mcp.setting

> cursor、VS code 中的 cline 插件都算是 MCP client。本文展示 cline 插件如何配置。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-04-22-14-24-29.png)

cline_mcp_setting.json 增加如下配置：

```json
{
  "mcpServers": {
    "invoice-local": {
      "url": "http://localhost:8080/sse",
      "autoApprove": [
        "getInvoiceUrl"
      ]
    }
  }
}
```

我们可以看到对应的 getInvoiceUrl 方法已经被自动注册到 MCP Server 中。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-04-22-14-25-28.png)

### 使用 MCP！

在 cline 中输入问题：“我有一个发票 id 是 123456，发票链接是多少？”，可以看到模型会自动判断是否需要调用 MCP Server 中的 getInvoiceUrl 方法，并拼装参数，获取结果。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-04-22-14-27-02.png)

### 说明

1. JDK 版本必须 >= 17
2. Spring Boot 版本必须 >= 3.2
3. Spring AI 底层使用 [modelcontextprotocol / java-sdk]([https://](https://github.com/modelcontextprotocol/java-sdk))
4. MCP 协议等都在快速发展中，上面的代码示例仅供参考，具体实现可能会有所不同

## 典型应用场景

1. **IDE 智能助手**：Server 暴露 Git / 构建 / 测试工具，LLM 可自动修改代码并提交。  
2. **企业数据问答**：Tool 封装 SQL / 向量检索，模型自然语言 → 结构化查询。  
3. **Agent Orchestration**：多个 MCP Server 负责 CRM、邮件、ERP 等，Client 统一调度。  
4. **本地脚本自动化**：Stdio Server 暴露文件系统 & shell，安全隔离下自动执行脚本。


##  MCP 生态与未来趋势

* **更细粒度权限模型**：计划支持基于 Tool / Resource 的访问控制列表 (ACL)。  
* **多模态采样**：后续版本或将支持音频、图像等跨模态上下文。  
* **社区采纳**：Cursor、Replit、Sourcegraph、Claude Desktop 等已在内部试用或上线。

## 参考链接

* [Model Context Protocol](https://github.com/modelcontextprotocol)
* [Spring AI MCP 示例仓库](https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol)
* [Spring AI 文档 (MCP 章节)](https://docs.spring.io/spring-ai/reference/)
* [JSON‑RPC 2.0 规范](https://www.jsonrpc.org/specification)
* [MCP.so](https://mcp.so/servers)