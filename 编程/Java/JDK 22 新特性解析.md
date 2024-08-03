---
date: 2024-08-03
---

# 前言

[JDK 22](https://openjdk.org/projects/jdk/22/) 是 Java SE 平台版本 22 的参考实现，2024 年 3 月 19 日正式发布。本文将详细解析 JDK 22 的主要新特性。

## 主要特性

### 1. Statements before super(...) (预览功能)

**目标**: 允许在构造函数中调用 `super(...)` 之前执行语句。

**背景**:

一个类继承另一个类时，子类继承父类，并且子类可以通过声明自己的字段和方法进而添加新的功能。子类声明字段的初始值可以依赖父类字段的初始值，因此在子类初始化之前，必须先初始化父类的字段。

按照顺序初始化字段，意味着构造函数必须从上到下执行：超类中的构造函数必须在子类中的构造函数运行之前完成字段初始化。这也意味着，某个类的构造函数在超类构造函数完成前，不能访问自身或任何超类中的字段。

为了确保构造方法能够从上到下执行，Java 语言规定 `super(...)` 必须是构造函数的第一条语句。这样做的目的是确保在子类构造函数执行之前，父类构造函数已经完成。如果没有显式地调用 `super(...)`，Java 编译器会自动插入 `super()`。

为了确保构造函数不能访问未初始化的字段，Java 语言要求如果给出了显式构造函数调用，参数不能以任何方式访问当前对象。但是上述要求有些过于严格：

示例：验证超类构造函数参数

我们可能需要验证传递给超类构造函数的参数。

```java
public class PositiveBigInteger extends BigInteger {

    public PositiveBigInteger(long value) {
        super(value);               // Potentially unnecessary work
        if (value <= 0)
            throw new IllegalArgumentException("non-positive value");
    }

}
```

如果我们可以在这段代码中，校验逻辑放在前面，那么就不需要调用 `super(value)` 了，而且也更容易理解。希望能改成下面这样：

```java
public class PositiveBigInteger extends BigInteger {

    public PositiveBigInteger(long value) {
        if (value <= 0)
            throw new IllegalArgumentException("non-positive value");
        super(value);
    }

}
```

示例：准备超类构造器函数

我们可能需要在调用超类构造函数之前，准备一些数据。下面的代码，由于超类构造函数必须是子类构造函数的第一条语句，所以我们只能声明辅助方法 prepareByteArray 来准备该调用的参数。

```java
public class Sub extends Super {

    public Sub(Certificate certificate) {
        super(prepareByteArray(certificate));
    }

    // Auxiliary method
    private static byte[] prepareByteArray(Certificate certificate) { 
        var publicKey = certificate.getPublicKey();
        if (publicKey == null) 
            throw new IllegalArgumentException("null certificate");
        return switch (publicKey) {
            case RSAKey rsaKey -> ...
            case DSAPublicKey dsaKey -> ...
            ...
            default -> ...
        };
    }

}
```

如果我们可以在调用超类构造函数之前，准备参数，那么就不需要声明辅助方法了，而且也更容易理解。希望能改成下面这样：

```java
public Sub(Certificate certificate) {
    var publicKey = certificate.getPublicKey();
    if (publicKey == null) 
        throw new IllegalArgumentException("null certificate");
    final byte[] byteArray = switch (publicKey) {
        case RSAKey rsaKey -> ...
        case DSAPublicKey dsaKey -> ...
        ...
        default -> ...
    };
    super(byteArray);
}
```


### 2. Foreign Function & Memory API

**目标**: 高效、安全地调用外部函数和访问本机的堆外内存。

**背景**：

Java 打造了一个跨平台的虚拟机，无论是访问远程数据（JDBC）、调用 Web 服务（HTTP 客户端）、为远程客户端提供服务（NIO 通道），还是与本地进程通信（Unix 域套接字）都很方便。但是 Java 开发人员访问本机对外内存时却很麻烦。

堆外内存的重要性：

在 Java 中，使用 new 关键字创建的对象存储在 JVM 的堆中。当不再需要时，这些对象可能会被垃圾回收。然而对于性能关键的库（如 TensorFlow、Ignite、Lucene 和 Netty）来说，垃圾回收的成本和不可预测性是无法接受的。这些库需要将数据存储在堆外内存中，这些库自己分配和释放这些内存。访问堆外内存还允许通过直接将文件映射到内存，例如通过 mmap 来对数据进行序列化和反序列化。

Java 之前已经提供了 2 个用于访问堆外内存的 API：

- ByteBuffer API：提供了 direct 字节缓冲区，这些是由固定大小的堆外内存区域支持的 Java 对象。区域的最大大小仅限于 2GB，而且用于读写内存的方法很基础且容易出错，仅提供对原始值的索引访问。直接字节缓冲区的内存只有在缓冲区对象被垃圾回收时才会被释放，而开发人员无法控制这一过程。
- sun.misc.Unsafe API：提供了对堆内、堆外内存的底层访问。

希望给 Java 开发人员提供一个更好的 API，能够灵活且安全分配、操作堆外内存。

**使用方法**:

JDK 22 引入了 Foreign Function & Memory API，下面的例子获取 C 库函数 radixsort 的方法句柄的 Java 代码，并使用它对四个起源于 Java 数组的字符串进行排序（省略了一些细节）。简要示例如下：

```java
// 1. Find foreign function on the C library path
Linker linker          = Linker.nativeLinker();
SymbolLookup stdlib    = linker.defaultLookup();
MethodHandle radixsort = linker.downcallHandle(stdlib.find("radixsort"), ...);
// 2. Allocate on-heap memory to store four strings
String[] javaStrings = { "mouse", "cat", "dog", "car" };
// 3. Use try-with-resources to manage the lifetime of off-heap memory
try (Arena offHeap = Arena.ofConfined()) {
    // 4. Allocate a region of off-heap memory to store four pointers
    MemorySegment pointers
        = offHeap.allocate(ValueLayout.ADDRESS, javaStrings.length);
    // 5. Copy the strings from on-heap to off-heap
    for (int i = 0; i < javaStrings.length; i++) {
        MemorySegment cString = offHeap.allocateFrom(javaStrings[i]);
        pointers.setAtIndex(ValueLayout.ADDRESS, i, cString);
    }
    // 6. Sort the off-heap data by calling the foreign function
    radixsort.invoke(pointers, javaStrings.length, MemorySegment.NULL, '\0');
    // 7. Copy the (reordered) strings from off-heap to on-heap
    for (int i = 0; i < javaStrings.length; i++) {
        MemorySegment cString = pointers.getAtIndex(ValueLayout.ADDRESS, i);
        javaStrings[i] = cString.reinterpret(...).getString(0);
    }
} // 8. All off-heap memory is deallocated here
assert Arrays.equals(javaStrings,
                     new String[] {"car", "cat", "dog", "mouse"});  // true
```

上面这段代码比任何使用 JNI 的方法都清晰，因为原本隐藏在 native 方法调用背后的隐式转换和内存访问现在直接使用 Java 代码表达。


### 3. Unnamed Variables & Patterns

**目标**: 

声明但不使用的变量可以使用 `_` 代替，以提高代码可读性。

**背景**:

无论是出于代码风格的考虑，还是在某些特殊情况下，开发者可能会声明一些他们并不打算使用的变量。在编写代码时，开发者明知道这些变量不会被使用，但是没有办法明确记录这一点，后面的维护者可能会意外使用这些变量。希望能引入一种机制，让开发者明确地表达这些变量不会被使用，使代码更具有信息性、可读性，并且跟不容易出错。

一个未命名变量通过使用下划线字符`_`（U+005F）来代替局部变量声明语句中的变量名。

例如之前在循环中计算 total，但是不实用循环变量 order：

```JAVA
static int count(Iterable<Order> orders) {
    int total = 0;
    for (Order order : orders)    // order is unused
        total++;
    return total;
}
```

可以改成：

```JAVA
static int count(Iterable<Order> orders) {
    int total = 0;
    for (Order _ : orders)    // Unnamed variable
        total++;
    return total;
}
```

另一个例子是，表达式的副作用比其结果更重要的情况，以下代码出队数据，但只需每三个元素中的两个即可，第三次调用 remove() 具有期望的副作用 — 即使其结果未分配给变量，也会出队一个元素，因此可以省略声明 z。


```JAVA
Queue<Integer> q = ... // x1, y1, z1, x2, y2, z2 ..
while (q.size() >= 3) {
   int x = q.remove();
   int y = q.remove();
   int z = q.remove();            // z is unused
    ... new Point(x, y) ...
}
```

可以改成：

```JAVA
Queue<Integer> q = ... // x1, y1, z1, x2, y2, z2 ..
while (q.size() >= 3) {
   int x = q.remove();
   int y = q.remove();
   int _ = q.remove();            // Unnamed variable
    ... new Point(x, y) ...
}
```

## 发布计划

- 2023/12/07: Rampdown Phase One
- 2024/01/18: Rampdown Phase Two
- 2024/02/08: Initial Release Candidate
- 2024/02/22: Final Release Candidate
- 2024/03/19: General Availability

## 总结

[JDK 22](https://openjdk.org/projects/jdk/22/) 引入了多个新特性和预览特性，旨在提升 Java 的性能、简化开发流程并增强代码安全性。。