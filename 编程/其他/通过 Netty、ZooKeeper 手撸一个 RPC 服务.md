---
date: 2021-05-08
---


- [说明](#说明)
  - [项目链接](#项目链接)
  - [微服务框架都包括什么？](#微服务框架都包括什么)
  - [如何实现 RPC 远程调用？](#如何实现-rpc-远程调用)
  - [开源 RPC 框架](#开源-rpc-框架)
    - [限定语言](#限定语言)
    - [跨语言 RPC 框架](#跨语言-rpc-框架)
- [本地 Docker 搭建 ZooKeeper](#本地-docker-搭建-zookeeper)
  - [下载镜像](#下载镜像)
  - [启动容器](#启动容器)
  - [查看容器日志](#查看容器日志)
- [RPC 接口](#rpc-接口)
- [Netty RPC server](#netty-rpc-server)
  - [接口实现](#接口实现)
  - [服务启动](#服务启动)
  - [注册服务](#注册服务)
  - [ZooKeeper 实现](#zookeeper-实现)
- [Netty RPC Client](#netty-rpc-client)
  - [创建代理](#创建代理)
  - [远程调用](#远程调用)
- [编解码](#编解码)
  - [RpcDecoder](#rpcdecoder)
  - [RpcEncoder](#rpcencoder)
- [RpcServerInboundHandler](#rpcserverinboundhandler)
- [Server 在 ZooKeeper 的路径](#server-在-zookeeper-的路径)
- [说明](#说明-1)
- [参考链接](#参考链接)

# 说明

使用 Netty、ZooKeeper 和 Spring Boot 手撸一个微服务框架。

## 项目链接

[GitHub 源码地址](https://github.com/LjyYano/NettyRpc)

## 微服务框架都包括什么？

详细信息可参考：[RPC 实战与原理](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-01-24%20RPC%20%E5%AE%9E%E6%88%98%E4%B8%8E%E5%8E%9F%E7%90%86.md)

项目可以分为调用方（client）和提供方（server），client 端只需要调用接口即可，最终调用信息会通过网络传输到 server，server 通过解码后反射调用对应的方法，并将结果通过网络返回给 client。对于 client 端可以完全忽略网络的存在，就像调用本地方法一样调用 rpc 服务。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210508144620.png)

整个项目的 model 结构如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210508144139.png)

## 如何实现 RPC 远程调用？

- 客户端、服务端如何建立网络连接：HTTP、Socket
- 服务端如何处理请求：NIO（使用 Netty）
- 数据传输采用什么协议
- 数据如何序列化、反序列化：JSON，PB，Thrift

## 开源 RPC 框架

### 限定语言
* Dubbo：Java，阿里
* Motan：Java，微博
* Tars：C++，腾讯（已支持多语言）
* Spring Cloud：Java
    * 网关 Zuul
    * 注册中心 Eureka
    * 服务超时熔断 Hystrix
    * 调用链监控 Sleuth
    * 日志分析 ELK

### 跨语言 RPC 框架
* gRPC：HTTP/2
* Thrift：TCP

# 本地 Docker 搭建 ZooKeeper

## 下载镜像

启动 Docker，并下载 ZooKeeper 镜像。详见 [https://hub.docker.com/_/zookeeper](https://hub.docker.com/_/zookeeper)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210508152337.png?x-oss-process=style/yano)

## 启动容器

启动命令如下，容器的名称是`zookeeper-rpc-demo`，同时向本机暴露 8080、2181、2888 和 3888 端口：

```
docker run --name zookeeper-rpc-demo --restart always -p 8080:8080 -p 2181:2181 -p 2888:2888 -p 3888:3888  -d zookeeper
```

```
This image includes EXPOSE 2181 2888 3888 8080 (the zookeeper client port, follower port, election port, AdminServer port respectively), so standard container linking will make it automatically available to the linked containers. Since the Zookeeper "fails fast" it's better to always restart it.
```

## 查看容器日志

可以通过下面的命令进入容器，其中`fb6f95cde6ba`是我本机的 Docker ZooKeeper 容器 id。

```
docker exec -it fb6f95cde6ba /bin/bash
```

在容器中进入目录：/apache-zookeeper-3.7.0-bin/bin，执行命令 `zkCli.sh -server 0.0.0.0:2181` 链接 zk 服务。

# RPC 接口

本示例提供了两个接口：HelloService 和 HiService，里面分别有一个接口方法，客户端仅需引用 rpc-sample-api，只知道接口定义，并不知道里面的具体实现。

```java
public interface HelloService {
    String hello(String msg);
}
```

```java
public interface HiService {
    String hi(String msg);
}
```

# Netty RPC server

启动一个 Server 服务，实现上面的两个 RPC 接口，并向 ZooKeeper 进行服务注册。

## 接口实现

```java
/**
 * @author yano
 * GitHub 项目： https://github.com/LjyYano/Thinking_in_Java_MindMapping
 * @date 2021-05-07
 */
@RpcServer(cls = HelloService.class)
public class HelloServiceImpl implements HelloService {

    @Override
    public String hello(String msg) {
        return "hello echo: " + msg;
    }
}
```

```java
/**
 * @author yano
 * GitHub 项目： https://github.com/LjyYano/Thinking_in_Java_MindMapping
 * @date 2021-05-07
 */
@RpcServer(cls = HiService.class)
public class HiServiceImpl implements HiService {

    public String hi(String msg) {
        return "hi echo: " + msg;
    }
}
```

这里涉及到了两个问题：
1. Server 应该决定将哪些接口实现注册到 ZooKeeper 上？
2. HelloServiceImpl 和 HiService 在 ZooKeeper 的路径应该是什么样的？

## 服务启动

本示例 Server 使用 Spring Boot，但是我们并不需要启动一个 Web 服务，只需要保持后台运行就可以，所以将 web 设置成 `WebApplicationType.NONE`

```java
@SpringBootApplication
public class RpcServerApplication {

    public static void main(String[] args) {
        new SpringApplicationBuilder(RpcServerApplication.class)
                .web(WebApplicationType.NONE)
                .run(args);
    }
}
```

## 注册服务

NettyApplicationContextAware 是一个 ApplicationContextAware 的实现类，程序在启动时，将带有 RpcServer（下面会讲解）注解的实现类注册到 ZooKeeper 上。

```java
@Component
public class NettyApplicationContextAware implements ApplicationContextAware {

    private static final Logger logger = LoggerFactory.getLogger(NettyApplicationContextAware.class);

    @Value("${zk.address}")
    private String zookeeperAddress;

    @Value("${zk.port}")
    private int zookeeperPort;

    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        Map<String, Object> rpcBeanMap = new HashMap<>();
        for (Object object : applicationContext.getBeansWithAnnotation(RpcServer.class).values()) {
            rpcBeanMap.put("/" + object.getClass().getAnnotation(RpcServer.class).cls().getName(), object);
        }
        try {
            NettyServer.start(zookeeperAddress, zookeeperPort, rpcBeanMap);
        } catch (Exception e) {
            logger.error("register error !", e);
        }
    }
}
```

RpcServer 注解的定义如下：

```java
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Target(ElementType.TYPE)
@Component
public @interface RpcServer {

    /**
     * 接口类，用以接口注册
     */
    Class<?> cls();

}
```

`applicationContext.getBeansWithAnnotation(RpcServer.class).values()` 就是获取项目中带有 RpcServer 注解的类，并将其放入一个 rpcBeanMap 中，其中 key 就是待注册到 ZooKeeper 中的路径。注意路径使用接口的名字，而不是类的名字。

使用注解的好处是，Server A 可以仅提供 HelloService，Server B 仅提供 HiService，不会相互影响且更加灵活。

服务注册主要在 com.yano.server.NettyServer#start 中。

```java
public class NettyServer {

    private static final Logger logger = LoggerFactory.getLogger(NettyServer.class);

    public static void start(String ip, int port, Map<String, Object> params) throws Exception {
        EventLoopGroup bossGroup = new NioEventLoopGroup();
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap serverBootstrap = new ServerBootstrap();
            serverBootstrap.group(bossGroup, workerGroup)
                    .channel(NioServerSocketChannel.class)
                    .option(ChannelOption.SO_BACKLOG, 1024)
                    .option(ChannelOption.SO_KEEPALIVE, true)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        protected void initChannel(SocketChannel socketChannel) {
                            socketChannel.pipeline()
                                    .addLast(new RpcDecoder(Request.class))
                                    .addLast(new RpcEncoder(Response.class))
                                    .addLast(new RpcServerInboundHandler(params));
                        }
                    });

            ChannelFuture future = serverBootstrap.bind(ip, port).sync();
            if (future.isSuccess()) {
                params.keySet().forEach(key -> ZooKeeperOp.register(key, ip + ":" + port));
            }
            future.channel().closeFuture().sync();
        } finally {
            bossGroup.shutdownGracefully();
            workerGroup.shutdownGracefully();
        }
    }

}
```

这个类的作用是：
1. 通过 Netty 启动一个 Socket 服务，端口号通过参数传入
2. 将上面的接口实现注册到 ZooKeeper 中

```java
params.keySet().forEach(key -> ZooKeeperOp.register(key, ip + ":" + port));
```

## ZooKeeper 实现

主要就是维护 zk 连接，并将 Server 的 ip 和 port 注册到对应的 ZooKeeper 中。这里使用 Ephemeral node，这样 Server 在下线丢失连接之后，ZooKeeper 能够自动删除节点，这样 Client 就不会获取到下线的 Server 地址了。

```java
public class ZooKeeperOp {

    private static final String zkAddress = "localhost:2181";
    private static final ZkClient zkClient = new ZkClient(zkAddress);

    public static void register(String serviceName, String serviceAddress) {
        if (!zkClient.exists(serviceName)) {
            zkClient.createPersistent(serviceName);
        }
        zkClient.createEphemeral(serviceName + "/" + serviceAddress);
        System.out.printf("create node %s \n", serviceName + "/" + serviceAddress);
    }

    public static String discover(String serviceName) {
        List<String> children = zkClient.getChildren(serviceName);
        if (CollectionUtils.isEmpty(children)) {
            return "";
        }
        return children.get(ThreadLocalRandom.current().nextInt(children.size()));
    }
}
```

# Netty RPC Client

Netty RPC Client 主要是像调用本地方法一样调用上述的两个接口，验证能够正常返回即可。

```java
public class RpcClientApplication {

    public static void main(String[] args) {
        HiService hiService = RpcProxy.create(HiService.class);
        String msg = hiService.hi("msg");
        System.out.println(msg);

        HelloService helloService = RpcProxy.create(HelloService.class);
        msg = helloService.hello("msg");
        System.out.println(msg);
    }
}
```

运行上述代码，最终控制台会输出：

```
hi echo: msg
hello echo: msg
```

## 创建代理

```java
HiService hiService = RpcProxy.create(HiService.class);
String msg = hiService.hi("msg");
```

Client 需要通过 com.yano.RpcProxy#create 创建代理，之后就可以调用 hiService 的 hi 方法了。

```java
public class RpcProxy {

    public static <T> T create(final Class<?> cls) {
        return (T) Proxy.newProxyInstance(cls.getClassLoader(), new Class<?>[] {cls}, (o, method, objects) -> {

            Request request = new Request();
            request.setInterfaceName("/" + cls.getName());
            request.setRequestId(UUID.randomUUID().toString());
            request.setParameter(objects);
            request.setMethodName(method.getName());
            request.setParameterTypes(method.getParameterTypes());

            Response response = new NettyClient().client(request);
            return response.getResult();
        });
    }
}
```

Server 端要想能够通过反射调用 Client 端请求的方法，至少需要：
1. 类名 interfaceName
2. 方法名 methodName
3. 参数类型 Class<?>[] parameterTypes
4. 传入参数 Object parameter[]

```java
@Data
public class Request {

    private String requestId;
    private String interfaceName;
    private String methodName;
    private Class<?>[] parameterTypes;
    private Object parameter[];

}
```

## 远程调用

最终是通过下面这段代码远程调用的，其中 request 包含了调用方法的所有信息。

```java
Response response = new NettyClient().client(request);
```

```java
/**
 * @author yano
 * GitHub 项目： https://github.com/LjyYano/Thinking_in_Java_MindMapping
 * @date 2021-05-07
 */
public class NettyClient extends SimpleChannelInboundHandler<Response> {

    private Response response;

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        ctx.close();
    }

    @Override
    protected void channelRead0(ChannelHandlerContext channelHandlerContext, Response response) {
        this.response = response;
    }

    public Response client(Request request) throws Exception {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            // 创建并初始化 Netty 客户端 Bootstrap 对象
            Bootstrap bootstrap = new Bootstrap();
            bootstrap.group(group)
                    .channel(NioSocketChannel.class)
                    .option(ChannelOption.TCP_NODELAY, true)
                    .handler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        public void initChannel(SocketChannel channel) {
                            channel.pipeline()
                                    .addLast(new RpcDecoder(Response.class))
                                    .addLast(new RpcEncoder(Request.class))
                                    .addLast(NettyClient.this);
                        }
                    });

            // 连接 RPC 服务器
            String[] discover = ZooKeeperOp.discover(request.getInterfaceName()).split(":");
            ChannelFuture future = bootstrap.connect(discover[0], Integer.parseInt(discover[1])).sync();

            // 写入 RPC 请求数据并关闭连接
            Channel channel = future.channel();
            channel.writeAndFlush(request).sync();
            channel.closeFuture().sync();

            return response;
        } finally {
            group.shutdownGracefully();
        }
    }

}
```

这段代码是核心，主要做了两件事：
- 请求 ZooKeeper，找到对应节点下的 Server 地址。如果有多个服务提供方，ZooKeeperOp.discover 会随机返回 Server 地址
- 与获取到的 Server 地址建立 Socket 连接，请求并等待返回

# 编解码

```java
channel.pipeline()
    .addLast(new RpcDecoder(Response.class))
    .addLast(new RpcEncoder(Request.class))
    .addLast(NettyClient.this);
```

Client 和 Server 都需要对 Request、Response 编解码。本示例采用了最简单的 Json 格式。Netty 的消息编解码具体不详细讲解，具体代码如下。

## RpcDecoder

RpcDecoder 是一个 ChannelInboundHandler，在 Client 端是对 Response 解码。

```java
public class RpcDecoder extends MessageToMessageDecoder<ByteBuf> {

    private final Class<?> genericClass;

    public RpcDecoder(Class<?> genericClass) {
        this.genericClass = genericClass;
    }

    @Override
    public void decode(ChannelHandlerContext ctx, ByteBuf msg, List<Object> out) {
        if (msg.readableBytes() < 4) {
            return;
        }
        msg.markReaderIndex();
        int dataLength = msg.readInt();
        if (msg.readableBytes() < dataLength) {
            msg.resetReaderIndex();
            return;
        }
        byte[] data = new byte[dataLength];
        msg.readBytes(data);

        out.add(JSON.parseObject(data, genericClass));
    }
}
```

## RpcEncoder

RpcEncoder 是一个 ChannelOutboundHandler，在 Client 端是对 Request 编码。

```java
public class RpcEncoder extends MessageToByteEncoder {

    private final Class<?> genericClass;

    public RpcEncoder(Class<?> genericClass) {
        this.genericClass = genericClass;
    }

    @Override
    public void encode(ChannelHandlerContext ctx, Object msg, ByteBuf out) {
        if (genericClass.isInstance(msg)) {
            byte[] data = JSON.toJSONBytes(msg);
            out.writeInt(data.length);
            out.writeBytes(data);
        }
    }
}
```

# RpcServerInboundHandler

这个是 Server 反射调用的核心，这里单独拿出来讲解。Netty Server 在启动时，已经在 pipeline 中加入了 RpcServerInboundHandler。

```java
socketChannel.pipeline()
    .addLast(new RpcDecoder(Request.class))
    .addLast(new RpcEncoder(Response.class))
    .addLast(new RpcServerInboundHandler(params));
```

```java
@Override
public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
    Request request = (Request) msg;
    logger.info("request data {}", JSON.toJSONString(request));

    // jdk 反射调用
    Object bean = handle.get(request.getInterfaceName());
    Method method = bean.getClass().getMethod(request.getMethodName(), request.getParameterTypes());
    method.setAccessible(true);
    Object result = method.invoke(bean, request.getParameter());

    Response response = new Response();
    response.setRequestId(request.getRequestId());
    response.setResult(result);

    // client 接收到信息后主动关闭掉连接
    ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
}
```

# Server 在 ZooKeeper 的路径

Server 启动后的输出如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210508160741.png?x-oss-process=style/yano)

其中有 2 行 log：

```
create node /com.yano.service.HelloService/127.0.0.1:3000 
create node /com.yano.service.HiService/127.0.0.1:3000 
```

在 ZooKeeper 中查看节点，发现服务已经注册上去了。

```
[zk: 0.0.0.0:2181(CONNECTED) 0] ls /com.yano.service.HelloService
[127.0.0.1:3000]
[zk: 0.0.0.0:2181(CONNECTED) 1] ls /com.yano.service.HiService
[127.0.0.1:3000]
```

# 说明

使用 Netty、ZooKeeper 和 Spring Boot 手撸一个微服务 RPC 框架。这个 demo 只能作为一个实例，手动实现能加深理解，切勿在生产环境使用。

本文代码均可在 [GitHub 源码地址](https://github.com/LjyYano/NettyRpc) 中找到，欢迎大家 star 和 fork。

# 参考链接

[https://github.com/yanzhenyidai/netty-rpc-example](https://github.com/yanzhenyidai/netty-rpc-example)