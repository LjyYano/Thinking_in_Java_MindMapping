---
date: 2019-10-14
---

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

Java NIO 有三大组件：

1. Buffer
2. Channel
3. Selector

# Buffer

Buffer 是一个特定**原始类型的容器**。Buffer 是一个原始类型的线性的、有限序列，除了 Buffer 存储的内容外，关键属性还包括：capacity, limit 和 position。

* **capacity**：Buffer 包含的元素的数量，capacity 永远不会为负，也不会改变。
* **limit**：Buffer 中第一个不能读取或写入的元素索引。limit 永远不会为负，且永远小于等于 capacity
* **position**：下一个待读取、写入的元素索引。position 永远不会为负，且永远小于等于 limit

每个基本类型（布尔类型除外），都有一个 Buffer 的子类。Java NIO 中 Buffer 的一些实现，其中最重要的是 **ByteBuffer**，其余类如 IntBuffer 的实现类未画出。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-14-084412.png)

我个人理解，Buffer 就是一个内存数组，并通过 capacity, limit 和 position 三个变量对读写操作进行控制。

## position、limit、capacity

Buffer 的属性主要有：

```java
// 恒等式: mark <= position <= limit <= capacity
private int mark = -1;
private int position = 0;
private int limit;
private int capacity;

// 仅在 direct buffers 中使用
long address;
```

ByteBuffer 中额外定义了字节数组（其余 Buffer 的子类同理）：

```java
// 该字节数组仅在分配在堆上时才非空（参考下面的 Direct vs. non-direct buffers）
final byte[] hb;
```

Buffer 就是根据这 4 个 int 型字段来配合内存数组的读写。这 4 个属性分别为：

* **mark**：临时保存 position 的值，每次调用 mark() 方法都会将 mark 设值为当前的 position
* **capacity**：Buffer 缓冲区容量，capacity 永远不会为负，也不会改变。
* **limit**：Buffer 中第一个不能读取或写入的元素索引。limit 永远不会为负，且永远小于等于 capacity。写模式下，limit 代表的是最大能写入的数据，limit = capacity；读模式下，limit = Buffer 实际写入的数据大小。
* **position**：下一个待读取、写入的元素索引。position 永远不会为负，且永远小于等于 limit。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-14-113021.jpg)


## ByteBuffer

从上图中我们可以看到，ByteBuffer 类有 2 个实现类：

1. **MappedByteBuffer**：DirectByteBuffer 的抽象类，JVM 会尽可能交给本地方法操作 I/O，其内存不会分配在堆上，不会占用应用程序的内存。
2. **HeapByteBuffer**：顾名思义是存储在堆上的 Buffer，我们直接调用 `ByteBuffer.allocate(1024);` 时会创建此类 Buffer。

```java
public static ByteBuffer allocate(int capacity) {
    if (capacity < 0)
        throw new IllegalArgumentException();
    return new HeapByteBuffer(capacity, capacity);
}
```

## Direct vs. non-direct buffers

一个 byte buffer 可以是 direct，也可以是非 direct 的。对于 direct byte buffer，JVM 将尽量在本机上执行 I/O 操作。也就是说，JVM 尽量避免每次在调用操作系统 I/O 操作前，将缓冲区内容复制到中间缓冲区。

可以通过类中的 allocateDirect 工厂方法创建 direct buffer，这个方法创建的 direct buffer 通常比 non-direct buffer 具有更高的分配和释放成本。Direct buffer 内存可能分配在 GC 堆的外部，所以对应用程序的内存占用影响并不明显。所以建议将 direct buffer 分配给大型、寿命长的、受底层操作系统 I/O 操作约束的缓冲区。

可以通过调用 isDirect 方法判断 byte buffer 是否是 direct 的。

## Buffer 初始化

Buffer 可以通过 allocation 方法创建，也可以通过字节数组的 wrapping 方法创建并填充。

```
ByteBuffer byteBuf = ByteBuffer.allocate(1024);
```

```
public static ByteBuffer wrap(byte[] array) {
    ...
}
```

## 填充 Buffer

```java
// 填充一个 byte
public abstract ByteBuffer put(byte b);

// 在指定位置填充一个 byte
public abstract ByteBuffer put(int index, byte b);

// 批量将 src buffer 填充到本 buffer
public ByteBuffer put(ByteBuffer src) {
    ...
}

// 批量将 src 数组的特定区间填充到本 buffer
public ByteBuffer put(byte[] src, int offset, int length) {
    ...
}

// 批量将 src 数组填充到本 buffer
public final ByteBuffer put(byte[] src) {
    ...
}
```

我们还可以将 Channel 的数据填充到 Buffer 中，数据是从外部（文件、网络）读到内存中。

```java
int read = channel.read(buffer);
```

## 读取 Buffer

对于前面的写操作，每写一个值，position 都会自增 1，所以 position 会指向最后写入位置的后面一位。

如果要读取 Buffer 的值，需要调用 **flip()** 方法，从**写模式切换到读模式**。

```java
public final Buffer flip() {
    limit = position; // 将 limit 设置为实际写入的数据数量
    position = 0; // 重置 position
    mark = -1; // 将 mark 设置为未标记
    return this;
}
```

读操作的 get 方法如下：

```java
// 读取当前 position 的字节，然后 position 自增 1
public abstract byte get();

// 读取 index 的字节（ position 不会自增！）
public abstract byte get(int index);

// 批量将缓冲区数据传递到 dst 数组中，position 自增 dst 的长度
public ByteBuffer get(byte[] dst) {
    ...
}

// 批量将缓冲区数据传递到 dst 数组中
public ByteBuffer get(byte[] dst, int offset, int length) {
    ...
}
```

我们可以将缓冲区的数据传输到 Channel 中：

1. 通过 FileChannel 将数据写到文件中
2. 通过 SocketChannel 将数据写入网络，发送到远程机器

```java
int write = channel.write(buffer);
```

## mark(), reset()

mark 用于临时保存 position 的值，每次调用 mark() 方法都会将 position 赋值给 mark。

```java
public final Buffer mark() {
    mark = position;
    return this;
}
```

reset() 方法就是将 position 赋值到上次 mark 的位置上（也就是上一次调用 mark() 方法的时候），通过 mark(), reset() 两个方法的配合，我们可以重复读取某个区间的数据。

```java
public final Buffer reset() {
    int m = mark;
    if (m < 0)
        throw new InvalidMarkException();
    position = m;
    return this;
}
```

注意 mark 构造初始化时数值是 -1，如果 >= 0 则表示可以读取。

## rewind(), clear(), compact()

rewind() 重置 position 为 0。通常在 channel-write 和 get 前调用此方法。

```java
public final Buffer rewind() {
    position = 0;
    mark = -1;
    return this;
}
```

clear() 会重置 position，将 limit 设置为最大值 capacity，并将 mark 置成 -1。通常在 channel-read 和填充此 buffer 时，会先调用此方法。

```java
public final Buffer clear() {
    position = 0;
    limit = capacity;
    mark = -1;
    return this;
}
```

compact() 方法并不常用，忽略。

```java
public abstract ByteBuffer compact();
```

## 恒等式

mark, position, limit和 capacity 永远遵循以下关系：

    0 <= mark <= position <= limit <= capacity

新创建的 buffer position = 0，mark 是未定义的（-1）。limit 的初始值可能是 0，也可能是构造时传入的其他值。新分配的缓冲区元素都初始化为 0。

# Channel

Channel 是 I/O 操作的「桥梁」。Channel 可以是对硬件设备、文件、网络套接字、程序组件等实体的连接，该实体能够执行不同的 I/O 操作（读取或写入）。

Channel 只有 2 种状态：开启和关闭。在创建时就是开启的，一旦关闭就不会再回到打开状态。Channel 一旦关闭，任何对 Channel 调用的 I/O 操作都会抛出 ClosedChannelException 异常，可以通过方法 isOpen() 来检测 Channel 是否开启。

Channel 接口定义如下：

```java
public interface Channel extends Closeable {

    public boolean isOpen();

    public void close() throws IOException;
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-14-114136.png)

- FileChannel：文件通道，用于文件读写
- DatagramChannel：UDP 连接
- SocketChannel：TCP 连接通道，TCP 客户端
- ServerSocketChannel：TCP 对应的服务端，用于监听某个端口进来的请求

读操作：将数据从 Channel 读取到 Buffer 中

```java
int read = channel.read(buffer);
```

写操作：将数据从 Buffer 写入到 Channel 中

```java
int write = channel.write(buffer);
```

## FileChannel

读取文件内容，详细说明见注释。

```java
@Test
public void testFileChannelRead() throws IOException {
    // 获取文件的 FileChannel
    FileInputStream fileInputStream = new FileInputStream("/abc");
    FileChannel channel = fileInputStream.getChannel();

    // 创建 ByteBuffer
    ByteBuffer buffer = ByteBuffer.allocate(30);

    // 将文件内容读取到 buffer 中
    channel.read(buffer);

    // buffer 从写模式，切换到读模式
    buffer.flip();

    // 打印 buffer（文件）的内容
    while (buffer.hasRemaining()) {
        System.out.print((char)buffer.get());
    }
}
```

写入文件内容，详细说明见注释。

```java
@Test
public void testFileChannelWrite() throws IOException {
    // 获取文件的 FileChannel
    FileOutputStream fileOutputStream = new FileOutputStream("/abc");
    FileChannel channel = fileOutputStream.getChannel();

    // 创建 ByteBuffer
    ByteBuffer buffer = ByteBuffer.allocate(30);
    buffer.put("123456".getBytes());

    // Buffer 切换为读模式
    buffer.flip();
    while(buffer.hasRemaining()) {
        // 将 Buffer 中的内容写入文件
        channel.write(buffer);
    }
}
```

## SocketChannel

SocketChannel 顾名思义，就是 Socket 的 Channel，能够读写 Socket。操作缓冲区同 FileChannel。

```java
@Test
public void testSocketChannel() throws IOException {
    SocketChannel socketChannel = SocketChannel.open(new InetSocketAddress("localhost", 80));

    // 创建 ByteBuffer
    ByteBuffer buffer = ByteBuffer.allocate(30);
    // 读取数据
    socketChannel.read(buffer);

    // 写入数据到网络连接中
    while(buffer.hasRemaining()) {
        socketChannel.write(buffer);
    }
}
```

## ServerSocketChannel

ServerSocketChannel 用于监听机器端口，管理从这个端口进来的 TCP 连接。

```java
// 实例化
ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
// 监听 8080 端口
serverSocketChannel.socket().bind(new InetSocketAddress(8080));

while (true) {
    // 一旦有一个 TCP 连接进来，就对应创建一个 SocketChannel 进行处理
    SocketChannel socketChannel = serverSocketChannel.accept();
}
```

    这里可以看到 SocketChannel 的另一种实例化方式，SocketChannel 可读可写，操作一个网络通道。

ServerSocketChannel 不和 Buffer 打交道了，因为它并不实际处理数据，它一旦接收到请求后，实例化 SocketChannel，之后在这个连接通道上的数据传递它就不管了，因为它需要继续监听端口，等待下一个连接。

## DatagramChannel

处理 UDP 连接（面向无连接的，不需要握手，只要把数据丢出去就好了），操作字节数组，同 FileChannel，不作过多介绍。

# Selector

Selector 是非阻塞的，**多路复用**就是基于 Selector 的，Java 能通过 Selector 实现一个线程管理多个 Channel。

## 基本操作

1. 开启一个 Selector（经常被翻译成选择器、多路复用器）

```java
Selector selector = Selector.open();
```

2. 将 Channel 注册到 Selector 上。前面我们说了，Selector 建立在非阻塞模式之上，所以注册到 Selector 的 Channel 必须要支持非阻塞模式，**FileChannel 不支持非阻塞**，我们这里讨论最常见的 SocketChannel 和 ServerSocketChannel。

```java
// 将通道设置为非阻塞模式，因为默认都是阻塞模式的
channel.configureBlocking(false);
// 注册
SelectionKey key = channel.register(selector, SelectionKey.OP_READ);
```

register 方法的第二个参数是 SelectionKey 中的常量，代表要监听感兴趣的事件，总共有以下 4 种：

```java
// 通道有数据可读
public static final int OP_READ = 1 << 0;
// 可以向通道中写数据
public static final int OP_WRITE = 1 << 2;
// 成功建立 TCP 连接
public static final int OP_CONNECT = 1 << 3;
// 接受 TCP 连接
public static final int OP_ACCEPT = 1 << 4;
```

注册方法返回值是 SelectionKey 实例，它包含了 Channel 和 Selector 信息，也包括了一个叫做 Interest Set 的信息，即我们设置的我们感兴趣的正在监听的事件集合。

3. 调用 select() 方法获取通道信息。用于判断是否有我们感兴趣的事件已经发生了。

## 基本用法

```java
Selector selector = Selector.open();

channel.configureBlocking(false);

SelectionKey key = channel.register(selector, SelectionKey.OP_READ);

while(true) {
  // 判断是否有事件准备好
  int readyChannels = selector.select();
  if(readyChannels == 0) continue;

  // 遍历
  Set<SelectionKey> selectedKeys = selector.selectedKeys();
  Iterator<SelectionKey> keyIterator = selectedKeys.iterator();
  while(keyIterator.hasNext()) {
    SelectionKey key = keyIterator.next();

    if(key.isAcceptable()) {
        // a connection was accepted by a ServerSocketChannel.

    } else if (key.isConnectable()) {
        // a connection was established with a remote server.

    } else if (key.isReadable()) {
        // a channel is ready for reading

    } else if (key.isWritable()) {
        // a channel is ready for writing
    }

    keyIterator.remove();
  }
}
```

## I/O 多路复用原理

这里放上一张原来总结的思维导图截图，具体原理需要另行写篇文章。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-14-123829.png)

# 总结

- Buffer 和数组差不多，它有 position、limit、capacity 几个重要属性。put() 一下数据、flip() 切换到读模式、然后用 get() 获取数据、clear() 一下清空数据、重新回到 put() 写入数据。

- Channel 基本上只和 Buffer 打交道，最重要的接口就是 channel.read(buffer) 和 channel.write(buffer)。

- Selector 用于实现非阻塞 IO，这里仅仅介绍接口使用，后续请关注非阻塞 IO 的介绍。
