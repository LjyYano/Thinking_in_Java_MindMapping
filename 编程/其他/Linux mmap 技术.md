---
date: 2021-09-23
---


- [虚拟内存：计算机系统的内存管理](#虚拟内存计算机系统的内存管理)
  - [虚拟内存是什么？](#虚拟内存是什么)
  - [虚拟内存的好处？](#虚拟内存的好处)
- [内存管理](#内存管理)
- [传统 IO 读写过程](#传统-io-读写过程)
- [mmap 简介](#mmap-简介)
- [Java 中的 mmap：MappedByteBuffer](#java-中的-mmapmappedbytebuffer)
- [参考文章](#参考文章)
- [GitHub 项目](#github-项目)

# 虚拟内存：计算机系统的内存管理

详情可以参考文章：[Linux 虚拟内存](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2021-03-21%20Linux%20%E8%99%9A%E6%8B%9F%E5%86%85%E5%AD%98.md)。

## 虚拟内存是什么？

计算机系统管理内存的技术，在应用程序的角度看，应用程序拥有连续可用的内存（一个连续的内存地址空间）。但是实际上会被分隔成多个物理内存碎片，还有部分可能存储在外部磁盘上，在必要的时候进行数据交换。

虚拟内存是操作系统物理内存和进程之间的中间层，为进程隐藏了物理内存。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923102846.png?x-oss-process)

## 虚拟内存的好处？

- 为进程提供独立的内存空间，简化程序的链接、加载过程并通过动态库共享内存；
- 控制进程对物理内存的访问，隔离不同进程的访问权限，提高系统的安全性；
- 以内存作为缓存，提高进程访问磁盘的速度。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923103051.png?x-oss-process)

# 内存管理

在 64 位的操作系统上，每个进程都会拥有 256 TiB 的内存空间，内核空间和用户空间分别占 128 TiB。因为每个进程的虚拟内存空间是完全独立的，所以它们都可以完整的使用 0x0000000000000000 到 0x00007FFFFFFFFFFF 的全部内存。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923103151.png?x-oss-process)

虚拟内存被分为`用户空间`和`内核空间`两部分：进程在用户态时，只能访问用户空间；进入内核态，才能访问内核空间。我们看一下 32 位地址和 64 位地址空间的分布：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923103421.png?x-oss-process=style/yano)

# 传统 IO 读写过程

初学 Java 时，我们在学习 IO 和 网络编程时，会使用以下代码：

```java
File file = new File("index.html");
RandomAccessFile raf = new RandomAccessFile(file, "rw");
 
byte[] arr = new byte[(int) file.length()];
raf.read(arr);
 
Socket socket = new ServerSocket(8080).accept();
socket.getOutputStream().write(arr);
```

我们会调用 read 方法读取 index.html 的内容—— 变成字节数组，然后调用 write 方法，将 index.html 字节流写到 socket 中，那么，我们调用这两个方法，在 OS 底层发生了什么呢？我这里借鉴了一张其他文章的图片，尝试解释这个过程。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923140321.png?x-oss-process=style/yano)

上图中，上半部分表示用户态和内核态的上下文切换。下半部分表示数据复制操作。下面说说他们的步骤：

- read 调用导致用户态到内核态的一次变化，同时，第一次复制开始：DMA（Direct Memory Access，直接内存存取，即不使用 CPU 拷贝数据到内存，而是 DMA 引擎传输数据到内存，用于解放 CPU） 引擎从磁盘读取 index.html 文件，并将数据放入到内核缓冲区。
- 发生第二次数据拷贝，即：将内核缓冲区的数据拷贝到用户缓冲区，同时，发生了一次用内核态到用户态的上下文切换。
- 发生第三次数据拷贝，我们调用 write 方法，系统将用户缓冲区的数据拷贝到 Socket 缓冲区。此时，又发生了一次用户态到内核态的上下文切换。
- 第四次拷贝，数据异步的从 Socket 缓冲区，使用 DMA 引擎拷贝到网络协议引擎。这一段，不需要进行上下文切换。
- write 方法返回，再次从内核态切换到用户态。

# mmap 简介

参考 [mmap 维基百科](https://en.wikipedia.org/wiki/Mmap)，mmap 通过内存映射，将文件映射到内核缓冲区，同时，用户空间可以共享内核空间的数据。这样，在进行网络传输时，就可以减少内核空间到用户空间的拷贝次数。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923140548.png?x-oss-process=style/yano)

如上图，user buffer 和 kernel buffer 共享 index.html。如果你想把硬盘的 index.html 传输到网络中，再也不用拷贝到用户空间，再从用户空间拷贝到 Socket 缓冲区。

现在，你只需要从内核缓冲区拷贝到 Socket 缓冲区即可，这将减少一次内存拷贝（从 4 次变成了 3 次），但不减少上下文切换次数。

# Java 中的 mmap：MappedByteBuffer

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210923141137.png?x-oss-process)

# 参考文章

- [https://pubs.opengroup.org/onlinepubs/009604499/functions/mmap.html](https://pubs.opengroup.org/onlinepubs/009604499/functions/mmap.html)
- [mmap Wikipedia](https://en.wikipedia.org/wiki/Mmap)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。