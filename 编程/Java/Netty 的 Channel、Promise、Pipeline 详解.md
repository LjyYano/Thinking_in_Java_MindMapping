---
date: 2019-10-26
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

[toc]

# Netty Demo 示例

首先通过一个示例来分析，创建一个 `NioServerSocketChannel` 监听本机端口 11111 的 `Socket` 连接，将收到的消息原样返回；然后再创建一个 `NioSocketChannel`，发起对本机的 11111 端口的 Socket 连接，发送字符串 ”Netty rocks!“。预期能收到服务端返回的 “Netty rocks!” 响应。

## Maven 依赖

本文使用的 Netty 版本是 **5.0.0.Alpha2**，与 4.x 版本相比变化还是挺大的。pom 文件添加：

```java
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-all</artifactId>
    <version>5.0.0.Alpha2</version>
</dependency>
```

## 创建一个 Server

创建一个 NioServerSocketChannel，监听本机端口 11111 的 Socket 连接。

```java
public class EchoServer {

    private final int port;

    public EchoServer(int port) {
        this.port = port;
    }

    public static void main(String[] args) throws InterruptedException {
        new EchoServer(11111).start();
    }

    public void start() throws InterruptedException {
        final EchoServerHandler serverHandler = new EchoServerHandler();
        NioEventLoopGroup group = new NioEventLoopGroup();
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(group).channel(NioServerSocketChannel.class)
                    .localAddress(new InetSocketAddress(port))
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel socketChannel) throws Exception {
                            socketChannel.pipeline().addLast(serverHandler);
                        }
                    });

            ChannelFuture channelFuture = b.bind().sync();
            channelFuture.channel().closeFuture().sync();
        } finally {
            group.shutdownGracefully().sync();
        }
    }
}
```

EchoServerHandler 的实现如下，在 channelRead 时将数据写入 ChannelHandlerContext，并将数据输出到控制台。

```java
@ChannelHandler.Sharable
public class EchoServerHandler extends ChannelHandlerAdapter {

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        ByteBuf in = (ByteBuf) msg;
        System.out.println("Server received : " + in.toString(CharsetUtil.UTF_8));
        ctx.write(in);
    }

    @Override
    public void channelReadComplete(ChannelHandlerContext ctx) {
        ctx.writeAndFlush(Unpooled.EMPTY_BUFFER) .addListener(ChannelFutureListener.CLOSE);
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx,
            Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }
}
```

## 创建一个 Client

创建一个 NioSocketChannel，发起对本机的 11111 端口的 Socket 连接。

```java
public class EchoClient {

    private final String host;
    private final int port;

    public EchoClient(String host, int port) { this.host = host;
        this.port = port;
    }

    public static void main(String[] args) throws InterruptedException {
        new EchoClient("localhost", 11111).start();
    }

    public void start() throws InterruptedException {
        NioEventLoopGroup group = new NioEventLoopGroup();
        try {
            Bootstrap bootstrap = new Bootstrap();
            bootstrap.group(group).channel(NioSocketChannel.class)
                    .remoteAddress(new InetSocketAddress(host, port))
                    .handler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel socketChannel) throws Exception {
                            socketChannel.pipeline().addLast(new EchoClientHandler());
                        }
                    });
            ChannelFuture channelFuture = bootstrap.connect().sync();
            channelFuture.channel().closeFuture().sync();
        }finally {
            group.shutdownGracefully().sync();
        }
    }
}
```

EchoClientHandler 的实现如下，messageReceived（在 Netty 4.x 为 channelRead0）对于泛型 I（本例中是 ByteBuf）进行处理，将数据输出到控制台。

```java
@ChannelHandler.Sharable
public class EchoClientHandler extends SimpleChannelInboundHandler<ByteBuf> {

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        ctx.writeAndFlush(Unpooled.copiedBuffer("Netty rocks!",
                CharsetUtil.UTF_8));
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }

    @Override
    public void messageReceived(ChannelHandlerContext ctx, ByteBuf msg) throws Exception {
        System.out.println(
                "Client received: " + msg.toString(CharsetUtil.UTF_8));
    }
}
```

# io.netty.channel.Channel 类

上面 demo 中直接使用到的 2 个类是：NioServerSocketChannel 和 NioSocketChannel，这两个类底层都是实现了 Channel 接口，注意这个 Channel 接口是 `io.netty.channel.Channel`，而不是 JDK 自带的 java.nio.channels.Channel！两个类的继承关系如下：

![NioServerSocketChannel](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-15-060744.png)

![NioSocketChannel](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-16-115532.png)

Channel 提供应用程序网络套接字或其他组件连接，提供读、写、连接和绑定等 I/O 操作。

- Channel 的当前状态（开启、关闭）
- Channel 的配置参数（接收缓冲区大小）
- I/O 操作（读、写、连接、绑定）
- ChannelPipeline，处理所有与 Channel 绑定的 I/O 事件和请求

## 所有 I/O 操作都是`异步`的

Netty 中所有 I/O 操作都是异步的。这意味着所有的 I/O 调用都会立即返回，不能保证在调用结束时请求的 I/O 操作是否完成。调用者会得到一个 ChannelFuture 实例，该实例会在请求的 I/O 操作成功、失败、取消时通知调用者。

## Channel 是分层级的

Channel 可以有 parent，这取决于 Channel 的创建方式。例如被 ServerSocketChannel 接收的 SocketChannel，会得到一个 ServerSocketChannel 作为它的 parent。

## 释放资源

使用完毕后，调用 close() 或 close(ChannelPromise) 释放资源非常重要。

# ChannelFuture

ChannelFuture 是一个`异步 Channel I/O 操作的结果`。如上面所说，Netty 中所有 I/O 操作都是异步的。这意味着所有的 I/O 调用都会立即返回，不能保证在调用结束时请求的 I/O 操作是否完成。调用者会得到一个 ChannelFuture 实例。

ChannelFuture 只有 2 种状态：未完成、已完成。I/O 操作开始时，将会创建一个新的 ChannelFuture 对象，初始时是未完成状态 —— 不是成功、失败或取消的任何一种状态，因为 I/O 操作还没有完成。如果 I/O 操作结束（无论成功、失败、取消），ChannelFuture 都会处于完成状态。注意即使是失败也属于完成状态。

                                          +---------------------------+
                                          | Completed successfully    |
                                          +---------------------------+
                                     +---->      isDone() = true      |
     +--------------------------+    |    |   isSuccess() = true      |
     |        Uncompleted       |    |    +===========================+
     +--------------------------+    |    | Completed with failure    |
     |      isDone() = false    |    |    +---------------------------+
     |   isSuccess() = false    |----+---->   isDone() = true         |
     | isCancelled() = false    |    |    |    cause() = non-null     |
     |       cause() = null     |    |    +===========================+
     +--------------------------+    |    | Completed by cancellation |
                                     |    +---------------------------+
                                     +---->      isDone() = true      |
                                          | isCancelled() = true      |
                                          +---------------------------+
                                          

我们还可以添加 ChannelFutureListener，以便在 I/O 操作完成时收到通知。

## 使用 addListener(GenericFutureListener) 而不是 await()

addListener(GenericFutureListener) 是非阻塞的，只需要将特定的 ChannelFutureListener 添加到ChannelFuture 即可，I/O 线程会在 ChannelFuture 绑定的 I/O 操作完成时通知监听器。`ChannelFutureListener` 完全非阻塞，因此效率极高。

而 await() 是阻塞操作，一旦调用，调用者线程就会阻塞直到操作完成。使用 await() 操作更容易，但是成本更高。此外，在特定的情况下还可能出现死锁。

## 使用 ChannelHandler 而不是 await()

`ChannelHandler` 中的事件处理方法通常由 I/O 线程调用，如果 await() 是由事件处理方法（I/O 线程）调用的，那么它正在等待的 I/O 操作可能永远也不会完成，因为 await() 方法可以阻止它正在等待的 I/O 操作，也就是发生了死锁。

```java
 // BAD - NEVER DO THIS
 @Override
 public void channelRead(ChannelHandlerContext ctx, GoodByeMessage msg) {
     ChannelFuture future = ctx.channel().close();
     future.awaitUninterruptibly();
     // Perform post-closure operation
     // ...
 }

 // GOOD
 @Override
 public void channelRead(ChannelHandlerContext ctx,  GoodByeMessage msg) {
     ChannelFuture future = ctx.channel().close();
     future.addListener(new ChannelFutureListener() {
         public void operationComplete(ChannelFuture future) {
             // Perform post-closure operation
             // ...
         }
     });
 }
```

# 创建 Channel

在 Bootstrap（客户端） 和 ServerBootstrap（服务端） 的启动过程中都会调用 AbstractBootstrap#channel(…) 方法（参考文章开头的 Demo）：

```java
public B channel(Class<? extends C> channelClass) {
    if (channelClass == null) {
        throw new NullPointerException("channelClass");
    }
    return channelFactory(new ReflectiveChannelFactory<C>(channelClass));
}
```

对于上一行的 return 语句，首先看里面的 ReflectiveChannelFactory 对象，它是一个 ChannelFactory，通过反射调用对应 Class 的默认构造函数来实例化新的 Channel。其定义如下：

```java
public class ReflectiveChannelFactory<T extends Channel> implements ChannelFactory<T> {
    private final Class<? extends T> clazz;
    ...
}
```

clazz 是 Channel 的子类，其中 newChannel 方法仅仅是调用的 Class 的 newInstance() 方法。

再来看 return 语句中的 channelFactory 方法：

```java
public B channelFactory(io.netty.channel.ChannelFactory<? extends C> channelFactory) {
    return channelFactory((ChannelFactory<C>) channelFactory);
}
```

下面代码可以看出，就是将上面通过 ReflectiveChannelFactory 创建出来的 channelFactory 赋值到对应字段。注意此时并没有创建 Channel，而是在：

- 对于 NioSocketChannel，由于它充当客户端的功能，它的创建时机在 connect(…) 的时候；
- 对于 NioServerSocketChannel 来说，它充当服务端功能，它的创建时机在绑定端口 bind(…) 的时候。

```java
public B channelFactory(ChannelFactory<? extends C> channelFactory) {
    if (channelFactory == null) {
        throw new NullPointerException("channelFactory");
    }
    if (this.channelFactory != null) {
        throw new IllegalStateException("channelFactory set already");
    }

    this.channelFactory = channelFactory;
    return (B) this;
}
```

接下来，我们看下 ServerBootstrap 是如何创建 NioServerSocketChannel 的，以及 NioSocketChannel 是如何与 JDK 交互的。

```java
public ChannelFuture bind() {
    validate();
    SocketAddress localAddress = this.localAddress;
    if (localAddress == null) {
        throw new IllegalStateException("localAddress not set");
    }
    return doBind(localAddress);
}
```

首先是 validate() 方法，验证 group 和 channelFactory 不能为 null，否则会抛出异常。

```java
public B validate() {
    if (group == null) {
        throw new IllegalStateException("group not set");
    }
    if (channelFactory == null) {
        throw new IllegalStateException("channel or channelFactory not set");
    }
    return (B) this;
}
```

然后是验证 localAddress 不为空，之后就是核心的 doBind() 逻辑了。

```java
private ChannelFuture doBind(final SocketAddress localAddress) {
    final ChannelFuture regFuture = initAndRegister();
    final Channel channel = regFuture.channel();
    if (regFuture.cause() != null) {
        return regFuture;
    }

    if (regFuture.isDone()) {
        // At this point we know that the registration was complete and successful.
        ChannelPromise promise = channel.newPromise();
        doBind0(regFuture, channel, localAddress, promise);
        return promise;
    } else {
        // Registration future is almost always fulfilled already, but just in case it's not.
        final PendingRegistrationPromise promise = new PendingRegistrationPromise(channel);
        regFuture.addListener(new ChannelFutureListener() {
            @Override
            public void operationComplete(ChannelFuture future) throws Exception {
                Throwable cause = future.cause();
                if (cause != null) {
                    // Registration on the EventLoop failed so fail the ChannelPromise directly to not cause an
                    // IllegalStateException once we try to access the EventLoop of the Channel.
                    promise.setFailure(cause);
                } else {
                    // Registration was successful, so set the correct executor to use.
                    // See https://github.com/netty/netty/issues/2586
                    promise.executor = channel.eventLoop();
                }
                doBind0(regFuture, channel, localAddress, promise);
            }
        });
        return promise;
    }
}
```

首先就是 initAndRegister()，返回一个注册的 ChannelFuture，通过它来获取 Channel。

```java
final ChannelFuture initAndRegister() {
    final Channel channel = channelFactory().newChannel();
    try {
        init(channel);
    } catch (Throwable t) {
        channel.unsafe().closeForcibly();
        // as the Channel is not registered yet we need to force the usage of the GlobalEventExecutor
        return new DefaultChannelPromise(channel, GlobalEventExecutor.INSTANCE).setFailure(t);
    }

    ChannelFuture regFuture = group().register(channel);
    if (regFuture.cause() != null) {
        if (channel.isRegistered()) {
            channel.close();
        } else {
            channel.unsafe().closeForcibly();
        }
    }
    return regFuture;
}
```

其中比较重要的是 `init(channel)`，它有 ServerBootstrap 和 Bootstrap 两个实现，这里就不细致展开。

还有一个重要的语句是：`ChannelFuture regFuture = group().register(channel);`，其中 group() 就是 ServerBootstrap 或 Bootstrap 的 EventLoopGroup 成员变量，每个 Bootstrap 还有一个 `private volatile EventLoopGroup childGroup;` 。

io.netty.channel.AbstractChannel.AbstractUnsafe#register 方法实现如下，

```java
@Override
public final void register(EventLoop eventLoop, final ChannelPromise promise) {
    ...

    // 需要重用 eventloop 对象，否则用户就会得到具有不同状态的多个对象
    if (AbstractChannel.this.eventLoop == null) {
        AbstractChannel.this.eventLoop = new PausableChannelEventLoop(eventLoop);
    } else {
        AbstractChannel.this.eventLoop.unwrapped = eventLoop;
    }

    // 当前线程是否被 event loop 执行
    if (eventLoop.inEventLoop()) {
        register0(promise);
    } else {
        try {
            eventLoop.execute(new OneTimeTask() {
                @Override
                public void run() {
                    register0(promise);
                }
            });
        } catch (Throwable t) {
            ...
        }
    }
}
```

# NioSocketChannel

NioSocketChannel 的无参构造参数：

```java
public NioSocketChannel() {
    this(DEFAULT_SELECTOR_PROVIDER);
}

public NioSocketChannel(SelectorProvider provider) {
    // newSocket(provider) 方法会创建 JDK 的 SocketChannel
    this(newSocket(provider));
}
```

其最终会调用：io.netty.channel.nio.AbstractNioChannel#AbstractNioChannel

```java
protected AbstractNioByteChannel(Channel parent, SelectableChannel ch) {
    // 客户端关心 OP_READ 事件，等待读取服务端返回数据
    super(parent, ch, SelectionKey.OP_READ);
}

protected AbstractNioChannel(Channel parent, SelectableChannel ch, int readInterestOp) {
    super(parent);
    this.ch = ch;
    this.readInterestOp = readInterestOp;
    try {
        // 将 SelectableChannel 配置为「非阻塞」模式
        ch.configureBlocking(false);
    } catch (IOException e) {
        ...
    }
}
```

# ServerSocketChannel

ServerSocketChannel 是一个 TCP/IP ServerChannel，处理 TCP/IP 连接请求。

# NioServerSocketChannel

NioServerSocketChannel 是一个 ServerSocketChannel 的实现，基于 NIO 选择器来接收新的连接。

# ChannelPipeline

ChannelHandler 列表处理和拦截 Channel 的传入事件和传出操作。ChannelPipeline 是 Intercepting Filter 模式的扩展，用户可以完全控制事件的处理方式和管道中 ChannelHandlers 如何交互。

## Pipeline 创建

每个 Channel 都有自己的 Pipeline，并且在创建 Channel 时会自动创建 Pipeline。

## 事件是如何在 Pipeline 中传递的

下图描述了 ChannelPipeline 是如何处理 ChannelHandler 的 I/O 事件的。 I/O 事件由 ChannelInboundHandler 或 ChannelOutboundHandler 处理，并通过调用 ChannelHandlerContext 中定义的事件传播方法（例如 ChannelHandlerContext.fireChannelRead(Object) 和 ChannelOutboundInvoker.write(Object)）转发到其最近的 handler。

                                                   I/O Request
                                              via Channel or
                                          ChannelHandlerContext
                                                        |
    +---------------------------------------------------+---------------+
    |                           ChannelPipeline         |               |
    |                                                  \|/              |
    |    +----------------------------------------------+----------+    |
    |    |                   ChannelHandler  N                     |    |
    |    +----------+-----------------------------------+----------+    |
    |              /|\                                  |               |
    |               |                                  \|/              |
    |    +----------+-----------------------------------+----------+    |
    |    |                   ChannelHandler N-1                    |    |
    |    +----------+-----------------------------------+----------+    |
    |              /|\                                  .               |
    |               .                                   .               |
    | ChannelHandlerContext.fireIN_EVT() ChannelHandlerContext.OUT_EVT()|
    |          [method call]                      [method call]         |
    |               .                                   .               |
    |               .                                  \|/              |
    |    +----------+-----------------------------------+----------+    |
    |    |                   ChannelHandler  2                     |    |
    |    +----------+-----------------------------------+----------+    |
    |              /|\                                  |               |
    |               |                                  \|/              |
    |    +----------+-----------------------------------+----------+    |
    |    |                   ChannelHandler  1                     |    |
    |    +----------+-----------------------------------+----------+    |
    |              /|\                                  |               |
    +---------------+-----------------------------------+---------------+
                    |                                  \|/
    +---------------+-----------------------------------+---------------+
    |               |                                   |               |
    |       [ Socket.read() ]                    [ Socket.write() ]     |
    |                                                                   |
    |  Netty Internal I/O Threads (Transport Implementation)            |
    +-------------------------------------------------------------------+

比如下面的例子，以 Inbound 开头的类表示是入站处理程序，以 Outbound 开头的类表示是出站处理程序。

```java
 ChannelPipeline p = ...;
 p.addLast("1", new InboundHandlerA());
 p.addLast("2", new InboundHandlerB());
 p.addLast("3", new OutboundHandlerA());
 p.addLast("4", new OutboundHandlerB());
 p.addLast("5", new InboundOutboundHandlerX());
```

上面的示例配置中，事件进入时处理顺序是1，2，3，4，5；事件出站顺序为5，4，3，2，1。

- 3 和 4 没有实现 ChannelInboundHandler，因此入站事件实际顺序是 1，2，5
- 1 和 2 没有实现 ChannelOutboundHandler，因此出站事件实际顺序是 5，4，3
- 5 同时实现了 ChannelInboundHandler 和 ChannelOutboundHandler

## 将事件转发到下一个 Handler

处理程序必须调用 ChannelHandlerContext 中的事件传播方法，将事件转发到其下一个处理程序。这些方法包括：

- 入站事件传播方法：
    - ChannelHandlerContext.fireChannelRegistered()
    - ChannelHandlerContext.fireChannelActive()
    - ChannelHandlerContext.fireChannelRead(Object)
    - ChannelHandlerContext.fireChannelReadComplete()
    - ChannelHandlerContext.fireExceptionCaught(Throwable)
    - ChannelHandlerContext.fireUserEventTriggered(Object)
    - ChannelHandlerContext.fireChannelWritabilityChanged()
    - ChannelHandlerContext.fireChannelInactive()
    - ChannelHandlerContext.fireChannelUnregistered()

- 出站事件传播方法：
    - ChannelOutboundInvoker.bind(SocketAddress, ChannelPromise)
    - ChannelOutboundInvoker.connect(SocketAddress, SocketAddress, ChannelPromise)
    - ChannelOutboundInvoker.write(Object, ChannelPromise)
    - ChannelHandlerContext.flush()
    - ChannelHandlerContext.read()
    - ChannelOutboundInvoker.disconnect(ChannelPromise)
    - ChannelOutboundInvoker.close(ChannelPromise)
    - ChannelOutboundInvoker.deregister(ChannelPromise)

下面的示例说明了事件是如何传播的：

```java
public class MyInboundHandler extends ChannelInboundHandlerAdapter {

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        System.out.println("Connected!");
        ctx.fireChannelActive();
    }
}

public class MyOutboundHandler extends ChannelOutboundHandlerAdapter {

    @Override
    public void close(ChannelHandlerContext ctx, ChannelPromise promise) {
        System.out.println("Closing ..");
        ctx.close(promise);
    }
}
```

## 建立 Pipeline

假定用户在 Pipeline 中具有一个或多个 ChannelHandler，用于处理 I/O 事件。比如：

- 协议解码器：将二进制数据（例如 ByteBuf）转换为 Java 对象。
- 协议编码器：将 Java 对象转换为二进制数据。
- 业务逻辑处理程序：执行实际的业务逻辑（数据库访问）。

一个代码示例：

```java
static final EventExecutorGroup group = new DefaultEventExecutorGroup(16);
...

ChannelPipeline pipeline = ch.pipeline();

pipeline.addLast("decoder", new MyProtocolDecoder());
pipeline.addLast("encoder", new MyProtocolEncoder());

// Tell the pipeline to run MyBusinessLogicHandler's event handler methods
// in a different thread than an I/O thread so that the I/O thread is not blocked by
// a time-consuming task.
// If your business logic is fully asynchronous or finished very quickly, you don't
// need to specify a group.
pipeline.addLast(group, "handler", new MyBusinessLogicHandler());
```

## 线程安全性

ChannelHandler 可以在任何时候添加到 ChannelPipeline中，也可以随时从 ChannelPipeline 中移出，它是**线程安全**的。

# EventExecutorGroup

定义如下：

```java
public interface EventExecutorGroup
extends java.util.concurrent.ScheduledExecutorService, java.lang.Iterable<EventExecutor>
```

`EventExecutorGroup` 顾名思义，就是 `EventExecutor 的 group`，负责通过其 next() 方法`提供要使用的 EventExecutor`。除此之外，它还负责处理 EventExecutor 的生命周期，并允许以全局方式关闭它们。

# EventExecutor

EventExecutor 是一个特殊的 EventExecutorGroup，它提供一些方便的方法来查看某个线程是否在事件循环中执行。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-16-030302.png)

# EventLoop

在一个 Channel 注册后，将处理这个 Channel 的所有 I/O 操作。`一个 EventLoop 实例通常将处理多个 Channel`。

# Promise

可写的 Future。

# ChannelPromise

可写的 ChannelFuture。下图中上面的 Future 是 JDK 的 Future，下面的 Future 是 Netty 自定义的 Future，具有异步操作的结果。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-16-120128.png)

Netty 自定义的 Future 接口其方法如下图，增加了很多方法：

- addListener：添加 listener
- await：等待 future 完成
- sync：等待 future 完成，如果失败会抛出失败原因

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-16-120511.png)
