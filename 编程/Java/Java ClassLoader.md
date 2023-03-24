---
date: 2021-09-13
---

- [ClassLoader 简介](#classloader-简介)
  - [是什么](#是什么)
  - [ClassLoader 官方文档](#classloader-官方文档)
  - [加载器的类型](#加载器的类型)
- [双亲委派机制](#双亲委派机制)
  - [优势](#优势)
- [自定义 ClassLoader 类加载器](#自定义-classloader-类加载器)
  - [自定义一个从磁盘加载的 DiskClassLoader](#自定义一个从磁盘加载的-diskclassloader)
  - [自定义一个加解密的字节码类加载器](#自定义一个加解密的字节码类加载器)
- [自定义的类加载器，能加载 java.lang 包的核心 API 吗？](#自定义的类加载器能加载-javalang-包的核心-api-吗)
  - [验证](#验证)
  - [结论](#结论)
- [参考链接](#参考链接)
- [GitHub 项目](#github-项目)

# ClassLoader 简介

## 是什么

一个完整的 Java 应用程序由若干个 Java Class 文件组成，当程序在运行时，会通过一个入口函数来调用系统的各个功能，这些功能都被存放在不同的 Class 文件中。

因此，系统在运行时经常会调用不同 Class 文件中被定义的方法，如果某个 Class 文件不存在，则系统会抛出 ClassNotFoundException 异常。

系统程序在启动时，不会一次性加载所有程序要使用的 Class 文件到内存中，而是根据程序需要，通过 Java 的类加载机制动态将需要使用的 Class 文件加载到内存中；只有当某个 Class 文件被加载到内存后，该文件才能被其他 Class 文件调用。

这个 “类加载机制“ 就是 ClassLoader , 他的作用是动态加载 Java Class 文件到 JVM 的内存空间中，让 JVM 能够调用并执行 Class 文件中的字节码。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210913104947.png?x-oss-process=style/yano)

上面的流程图即为 ClassLoaderTest.java 是如何被动态加载到 JVM 内存空间的，类加载的过程主要由 5 步组成。

- `加载阶段` ：该阶段是类加载过程的第一个阶段，会通过一个类的完全限定名称来查找类的字节码文件，并利用字节码文件来创建一个 Class 对象。
- `验证阶段` ：该阶段是类加载过程的第二个阶段，其目的在于确保 Class 文件中包含的字节流信息符合当前 Java 虚拟机的要求。
- `准备阶段` ： 该阶段会为类变量在方法区中分配内存空间并设定初始值 ( 这里 “类变量” 为 static 修饰符修饰的字段变量 )
  - 不会分配并初始化用 final 修饰符修饰的 static 变量，因为该类变量在编译时就会被分配内存空间。
  - 不会分配并初始化实例变量，因为实例变量会随对象一起分配到 Java 堆中，而不是 Java 方法区。
- `解析阶段` ：该阶段会将常量池中的符号引用替换为直接引用。
- `初始化阶段` ：该阶段是类加载的最后阶段，如果当前类具有父类，则对其进行初始化，同时为类变量赋予正确的值。

## ClassLoader 官方文档

[Class ClassLoader(Java SE 15 & JDK 15)](https://docs.oracle.com/en/java/javase/15/docs/api/java.base/java/lang/ClassLoader.html)

A class loader is an object that is responsible for loading classes. The class ClassLoader is an abstract class. Given the binary name of a class, a class loader should attempt to locate or generate data that constitutes a definition for the class. A typical strategy is to transform the name into a file name and then read a "class file" of that name from a file system.
Every Class object contains a reference to the ClassLoader that defined it.

Class objects for array classes are not created by class loaders, but are created automatically as required by the Java runtime. The class loader for an array class, as returned by Class.getClassLoader() is the same as the class loader for its element type; if the element type is a primitive type, then the array class has no class loader.

Applications implement subclasses of ClassLoader in order to extend the manner in which the Java virtual machine dynamically loads classes.

## 加载器的类型

- 启动类加载器 BootstrapClassLoader：用于加载启动的基础模块类，JDK 核心类
- 平台类加载器 ( jdk8 以上） PlatformClassLoader：平台相关的模块
- 启动类加载器 AppClassLoader：应用级别的模块

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210913105430.png?x-oss-process=style/yano)

# 双亲委派机制

使用组合，除了启动类加载器外，其余的类加载器都应该有自己的父加载器。我们知道了 JVM 默认使用了三种类加载器，分别加载不同目录下的 Java 类库。当程序需要某个类时，JVM 会按需将生成的 Class 文件加载到内存中，生成对应实例对象。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210913105543.png?x-oss-process=style/yano)

顾名思义，该机制的实现分为两个阶段，即上图中的 “委托阶段” 与 “派发阶段”。java.lang.ClassLoader#loadClass 流程如下：

```java
protected Class<?> loadClass(String name, boolean resolve)
    throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // First, check if the class has already been loaded
        Class<?> c = findLoadedClass(name);
        if (c == null) {
            long t0 = System.nanoTime();
            try {
                if (parent != null) {
                    c = parent.loadClass(name, false);
                } else {
                    c = findBootstrapClassOrNull(name);
                }
            } catch (ClassNotFoundException e) {
                // ClassNotFoundException thrown if class not found
                // from the non-null parent class loader
            }

            if (c == null) {
                // If still not found, then invoke findClass in order
                // to find the class.
                long t1 = System.nanoTime();
                c = findClass(name);

                // this is the defining class loader; record the stats
                PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                PerfCounter.getFindClasses().increment();
            }
        }
        if (resolve) {
            resolveClass(c);
        }
        return c;
    }
}
```

## 优势

- `避免类被重复加载`，父加载器加载某个类之后，子加载器不会重复加载
- `保证 Java 核心库的安全`。比如 java.lang 包下的核心 API，不会被类加载器重复加载，肯定是被`启动类加载器`加载。（当然自定义的类加载器能够重写 loadClass 方法，不过还是不能加载核心 API，具体在本文后面部分分析）

# 自定义 ClassLoader 类加载器

自定义类加载器，一共需要 2 个步骤：
1. 自定义类加载器继承 java.lang.ClassLoader.class
2. 重写 findClass() 方法

## 自定义一个从磁盘加载的 DiskClassLoader

DiskClassLoader 类中有一个 path 变量，标识应该从哪个路径加载 class。然后就是继承了 ClassLoader，重写了其中的 findClass 方法，从 path 中读取 class 文件的字节数组。

```java
public class DiskClassLoader extends ClassLoader {

    private final String path;

    public DiskClassLoader(String path) {
        this.path = path;
    }

    private String getFileName(String name) {
        int index = name.lastIndexOf('.');
        if (index == -1) {
            return name + ".class";
        }
        return name.substring(index + 1) + ".class";
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        String fileName = getFileName(name);
        File file = new File(path, fileName);

        try {
            byte[] data = FileUtils.readFileToByteArray(file);
            return defineClass(name, data, 0, data.length);
        } catch (IOException e) {
            e.printStackTrace();
        }

        return super.findClass(name);
    }
}
```

之后在本机的 /Users/yano/tmp 目录下，新建 DiskClass 类，里面只有一个 test 方法。注意这里不能在自己的工程项目里新建文件，因为是有包名的，单独拿出 class 文件是没有办法直接使用的。

```java
public class DiskClass {

    public void test() {
        System.out.println("Hello Yano!");
    }
}
```

之后 `javac DiskClass.java`，编译成字节码文件。使用 javap 命令来查看字节码：`javap -p DiskClass`

```java
Compiled from "DiskClass.java"
public class DiskClass {
  public DiskClass();
  public void test();
}
```

写一个测试用例，用 DiskClassLoader 去加载 /Users/yano/tmp/DiskClass.class 字节码文件，并通过反射去调用该文件的 test 方法。测试用例的代码如下：

```java
@Test
public void load() throws Exception {
    DiskClassLoader diskClassLoader =
            new DiskClassLoader("/Users/yano/tmp");

    Class<?> c = diskClassLoader.loadClass("DiskClass");

    Method[] methods = c.getDeclaredMethods();
    for (Method method : methods) {
        System.out.println("methods: " + method.getName());
    }

    Object o = c.newInstance();
    Method method = c.getDeclaredMethod("test", null);
    method.invoke(o, null);
}
```

输出结果如下，我们可以看到 class 字节码已经加载成功，并且能够通过反射调用 test 方法。

```java
methods: test
Hello Yano!
```

## 自定义一个加解密的字节码类加载器

自定义类加载器的一个好处，是我们可以自由操作要加载的字节码。比如第三方 jar 包或者比较机密核心的 API，我们都可以提供加密后的字节码，然后自定义类加载器解密字节码。

我们使用文中上一小节中的 DiskClass.class，对齐进行加密，然后输出到/Users/yano/tmp 目录下，并把加密后的字节码保存到 EncryptDiskClass.class 文件中。

```java
public class EncryptClass {
    public static void main(String[] args) throws IOException {
        File in = new File("/Users/yano/tmp/DiskClass.class");
        File out = new File("/Users/yano/tmp/EncryptDiskClass.class");
        encrypt(in, out);
    }

    private static void encrypt(File in, File out) throws IOException {
        byte[] bytes = FileUtils.readFileToByteArray(in);
        for (int i = 0; i < bytes.length; i++) {
            bytes[i] = (byte) (bytes[i] ^ 0XFF);
        }
        FileUtils.writeByteArrayToFile(out, bytes);
    }
}
```

核心加密代码就是` bytes[i] = (byte) (bytes[i] ^ 0XFF)`，对字节码的每一位进行异或。我们使用 javap 命令，查看生成的字节码文件，发现已经无法正常解析。

```java
javap -p EncryptDiskClass
错误：读取 EncryptDiskClass 的常量池时出错：unexpected tag at #1: 245
```

DecryptClassLoader 代码如下，思路就是读取加密的 class 字节码，然后解密。解密的方法还是 `bytes[i] = (byte) (decryptBytes[i] ^ 0XFF)`，同时 defineClass 方法的 name 传参需要去掉前面的 Encrypt。

```java
public class DecryptClassLoader extends ClassLoader {
    private String path;

    public DecryptClassLoader(String path) {
        this.path = path;
    }

    @SneakyThrows
    @Override
    protected Class<?> findClass(String name) {
        byte[] classData = getClassData(name);
        return defineClass("DiskClass", classData, 0, classData.length);
    }

    public byte[] getClassData(String className) throws IOException {
        String decryptFilePath = path + className + ".class";
        byte[] decryptBytes = FileUtils.readFileToByteArray(new File(decryptFilePath));
        byte[] bytes = new byte[decryptBytes.length];
        for (int i = 0; i < decryptBytes.length; i++) {
            bytes[i] = (byte) (decryptBytes[i] ^ 0XFF);
        }
        return bytes;
    }
}
```

测试用例跟上面的没有太大区别，就是换了下 ClassLoader 和需要加载的字节码文件。

```java
@Test
public void decrypt() throws Exception {
    DecryptClassLoader decryptClassLoader = new DecryptClassLoader("/Users/yano/tmp/");
    Class<?> c = decryptClassLoader.loadClass("EncryptDiskClass");

    Method[] methods = c.getDeclaredMethods();
    for (Method method : methods) {
        System.out.println("methods: " + method.getName());
    }

    Object o = c.newInstance();
    Method method = c.getDeclaredMethod("test", null);
    method.invoke(o, null);
}
```

查看输出结果符合预期，正确加载了加密的字节码文件。

```java
methods: test
Hello Yano!
```

# 自定义的类加载器，能加载 java.lang 包的核心 API 吗？

有一个灵魂拷问：我们能自定义一个 String 类，然后去加载这个类吗？

从 JVM 的安全性和常理来说，肯定是不能的。但是这个问题要怎么验证呢？里面的原理究竟是什么样的？

## 验证

我们可以在项目中，新建 `java.lang` 包，写一个 String 方法：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210913172156.png?x-oss-process=style/yano)

```java
package java.lang;

public class String {

    public void say() {
        System.out.println("hello");
    }
}
```

javac 这个自定义的 String 类，我们发现会报下面的错误：

```
javac String.java
String.java:1: 错误：程序包已存在于另一个模块中：java.base
package java.lang;
^
1 个错误
```

发现根本就没法把自定义的 String 类编译成 class 文件。随便执行一个测试用例，发现在 build 阶段就会报错：

```
java: 通过 javax.lang.model.util.Elements.getTypeElement 在模块 'java.base, 未命名模块' 中找到了多个名为 'java.lang.String' 的元素。
```

参考网络上的文章 [java 类加载机制：到底能不能自己自定义 java.lang.String 类
](https://blog.csdn.net/liubenlong007/article/details/88574544?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_title~default-1.no_search_link&spm=1001.2101.3001.4242)，说是 JDK 8 及以前版本能编译，但是 JDK 11 无法编译。

## 结论

（结论有些仓促，等有时间再补充）

- JVM 不允许用户自定义 java.lang 包
- JDK 11 开始，用户自定义 java.lang 包后，直接会编译不通过
- 如果想打破双亲委派模型，重写 loadClass 方法，但是即使重写了，也无法覆盖加载 JDK 的核心 API

# 参考链接

- [基础补完计划 – Java 类加载器 ( ClassLoader )](https://www.guildhab.top/2021/03/java%E5%9F%BA%E7%A1%80%E7%AC%94%E8%AE%B0-%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8-classloader/)

# GitHub 项目

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~

原创不易，希望大家转载时请先联系我，并标注原文链接。