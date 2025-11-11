---
date: 2025-11-11
---

# 前言

[JDK 24](https://openjdk.org/projects/jdk/24/) 是 Java SE 平台版本 24 的参考实现，预计 2025 年 3 月正式发布。本文将详细解析 JDK 24 的主要新特性。

# 新特性总览

| JEP | 特性名称 | 状态 | 说明 |
|:---:|:---|:---:|:---|
| 467 | Markdown 文档注释 | 正式发布 | 允许在 JavaDoc 中使用 Markdown 语法，提高文档可读性 |
| 469 | 向量 API | 第九次孵化 | 提供向量计算 API，支持 SIMD 指令优化 |
| 471 | 弃用 `sun.misc.Unsafe` 中的内存访问方法 | 正式发布 | 继续推进弃用不安全的内存访问方法 |
| 474 | ZGC：默认的分代模式 | 正式发布 | 分代 ZGC 成为默认模式，提升垃圾回收性能 |
| 476 | 模块导入声明 | 预览 | 简化模块导入，允许一次性导入整个模块 |
| 477 | 隐式声明的类和实例主方法 | 第三次预览 | 简化初学者编程体验 |
| 480 | 结构化并发 | 第三次预览 | 简化并发编程模型 |
| 481 | 作用域值 | 第三次预览 | 提供线程间共享不可变数据的新机制 |
| 482 | 灵活的构造函数体 | 第二次预览 | 允许在 `super()` 调用前执行语句 |
| 483 | 提前编译工具改进 | 正式发布 | 改进 AOT 编译工具，提升启动性能 |

# 详细解析

## JEP 467：Markdown 文档注释（正式发布）

JEP 467 在经过预览后正式发布，允许在 JavaDoc 文档注释中使用 Markdown 语法。

**为什么要引入这个功能：**

传统的 JavaDoc 主要使用 HTML 标签进行标记，语法繁琐且容易出错。Markdown 作为一种轻量级标记语言，具有简洁、易读、易写的特点，已在开发者社区广泛使用。引入 Markdown 支持可以显著简化文档编写过程，提高代码的可读性和可维护性。

**目标：**

- **简化文档编写**：使用简洁的 Markdown 语法替代繁琐的 HTML
- **提高可读性**：Markdown 文档在源代码中也易于阅读
- **保持兼容性**：继续支持传统的 HTML 和 JavaDoc 标签
- **降低学习成本**：开发者无需深入学习 HTML 即可编写文档

**简要使用示例：**

1. **使用 Markdown 语法的文档注释：**

```java
/**
 * 用户服务类，提供用户管理的核心功能。
 * 
 * ## 主要功能
 * 
 * - 用户注册和登录
 * - 用户信息管理
 * - 权限验证
 * 
 * ### 使用示例
 * 
 * ```java
 * UserService service = new UserService();
 * User user = service.createUser("john", "john@example.com");
 * ```
 * 
 * **注意事项：**
 * 
 * 1. 用户名必须唯一
 * 2. 邮箱格式必须有效
 * 3. 密码长度至少 8 位
 * 
 * @param username 用户名
 * @param email 邮箱地址
 * @return 创建的用户对象
 * @throws IllegalArgumentException 如果参数无效
 */
public class UserService {
    // ...
}
```

2. **Markdown 表格支持：**

```java
/**
 * 订单状态枚举
 * 
 * | 状态 | 描述 | 可执行操作 |
 * |------|------|-----------|
 * | PENDING | 待处理 | 确认、取消 |
 * | CONFIRMED | 已确认 | 发货、取消 |
 * | SHIPPED | 已发货 | 签收 |
 * | COMPLETED | 已完成 | 评价、退货 |
 */
public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, COMPLETED
}
```

## JEP 469：向量 API（第九次孵化）

JEP 469（第九次孵化）继续改进向量 API，提供更高效的向量计算能力。

**为什么要引入这个功能：**

现代 CPU 普遍支持 SIMD（Single Instruction, Multiple Data）指令，可以在单条指令中处理多个数据，显著提升计算性能。然而 Java 缺乏直接利用这些硬件能力的标准 API。向量 API 填补了这一空白，使开发者能够编写高性能的数值计算代码。

**目标：**

- **跨平台可移植性**：编写一次，在不同 CPU 架构上都能高效运行
- **可预测的性能**：向量操作可靠地编译为高效的机器指令
- **优雅降级**：在不支持向量指令的平台上自动降级为标量操作
- **易于使用**：提供清晰简洁的 API

**简要使用示例：**

1. **向量化数组加法：**

```java
import jdk.incubator.vector.*;

public class VectorExample {
    static final VectorSpecies<Float> SPECIES = FloatVector.SPECIES_PREFERRED;
    
    public static void vectorAdd(float[] a, float[] b, float[] result) {
        int i = 0;
        int upperBound = SPECIES.loopBound(a.length);
        
        // 向量化循环
        for (; i < upperBound; i += SPECIES.length()) {
            var va = FloatVector.fromArray(SPECIES, a, i);
            var vb = FloatVector.fromArray(SPECIES, b, i);
            var vc = va.add(vb);
            vc.intoArray(result, i);
        }
        
        // 处理剩余元素
        for (; i < a.length; i++) {
            result[i] = a[i] + b[i];
        }
    }
}
```

2. **向量化点积计算：**

```java
public static float dotProduct(float[] a, float[] b) {
    var sum = FloatVector.zero(SPECIES);
    int i = 0;
    int upperBound = SPECIES.loopBound(a.length);
    
    for (; i < upperBound; i += SPECIES.length()) {
        var va = FloatVector.fromArray(SPECIES, a, i);
        var vb = FloatVector.fromArray(SPECIES, b, i);
        sum = va.fma(vb, sum);  // Fused multiply-add
    }
    
    float result = sum.reduceLanes(VectorOperators.ADD);
    
    // 处理剩余元素
    for (; i < a.length; i++) {
        result += a[i] * b[i];
    }
    
    return result;
}
```

## JEP 471：弃用 `sun.misc.Unsafe` 中的内存访问方法（正式发布）

JEP 471 正式将 `sun.misc.Unsafe` 类中的内存访问方法标记为弃用，为未来移除做准备。

**为什么要引入这个功能：**

`sun.misc.Unsafe` 是一个非标准的内部 API，其内存访问方法可能导致未定义行为甚至 JVM 崩溃。随着 VarHandle API（JDK 9）和 Foreign Function & Memory API（JDK 22）的引入，已经有了安全且高效的替代方案。

**目标：**

- **促进迁移**：鼓励开发者使用标准 API
- **提高安全性**：减少不安全内存操作导致的问题
- **为移除做准备**：在未来版本中完全移除这些方法

**简要使用示例：**

1. **使用 VarHandle 替代 Unsafe：**

```java
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

public class SafeMemoryAccess {
    private volatile int value;
    private static final VarHandle VALUE_HANDLE;
    
    static {
        try {
            VALUE_HANDLE = MethodHandles.lookup()
                .findVarHandle(SafeMemoryAccess.class, "value", int.class);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }
    
    // 原子性读取
    public int getValue() {
        return (int) VALUE_HANDLE.getVolatile(this);
    }
    
    // 原子性写入
    public void setValue(int newValue) {
        VALUE_HANDLE.setVolatile(this, newValue);
    }
    
    // CAS 操作
    public boolean compareAndSet(int expected, int newValue) {
        return VALUE_HANDLE.compareAndSet(this, expected, newValue);
    }
}
```

2. **使用 Foreign Memory API：**

```java
import java.lang.foreign.*;

public class OffHeapMemory {
    public static void allocateAndUseMemory() {
        try (Arena arena = Arena.ofConfined()) {
            // 分配堆外内存
            MemorySegment segment = arena.allocate(1024);
            
            // 写入数据
            segment.set(ValueLayout.JAVA_INT, 0, 42);
            segment.set(ValueLayout.JAVA_INT, 4, 100);
            
            // 读取数据
            int value1 = segment.get(ValueLayout.JAVA_INT, 0);
            int value2 = segment.get(ValueLayout.JAVA_INT, 4);
            
            System.out.println("Values: " + value1 + ", " + value2);
        } // 内存自动释放
    }
}
```

## JEP 474：ZGC：默认的分代模式（正式发布）

JEP 474 正式将 Z 垃圾收集器（ZGC）的默认模式切换为分代模式。

**为什么要引入这个功能：**

分代 ZGC 在大多数使用场景下性能优于非分代模式，能够更好地处理不同生命周期的对象。维护两种模式增加了开发和测试成本，统一为分代模式可以集中资源进行优化。

**目标：**

- **提升默认性能**：大多数应用无需调优即可获得更好的性能
- **简化维护**：专注于分代 ZGC 的发展
- **降低内存占用**：分代模式通常使用更少的内存

**简要使用示例：**

1. **启用 ZGC（分代模式，JDK 24 默认）：**

```bash
# JDK 24 中，直接启用 ZGC 即使用分代模式
java -XX:+UseZGC -Xmx4g MyApplication

# 查看 GC 日志
java -XX:+UseZGC -Xlog:gc* -Xmx4g MyApplication
```

2. **如果需要使用非分代模式（已弃用）：**

```bash
# 显式禁用分代模式（会收到弃用警告）
java -XX:+UseZGC -XX:-ZGenerational -Xmx4g MyApplication

# 警告信息：
# Warning: Option ZGenerational was deprecated.
# Warning: Non-generational mode is deprecated and will likely be removed in a future release.
```

3. **ZGC 调优参数：**

```bash
# 设置并发 GC 线程数
java -XX:+UseZGC -XX:ConcGCThreads=2 MyApplication

# 设置最大堆大小
java -XX:+UseZGC -Xmx8g MyApplication

# 启用详细的 GC 日志
java -XX:+UseZGC -Xlog:gc*=info:file=gc.log MyApplication
```

## JEP 476：模块导入声明（预览）

JEP 476 引入模块导入声明，简化了模块化库的使用。

**为什么要引入这个功能：**

使用模块化库时，开发者通常需要导入多个包。模块导入声明允许一次性导入整个模块的所有导出包，减少样板代码，提高开发效率。

**目标：**

- **简化代码**：用一条语句替代多条包导入
- **降低学习曲线**：无需了解模块内部的包结构
- **提高可维护性**：模块添加新包时无需修改导入语句

**简要使用示例：**

```java
// 传统方式：需要导入多个包
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.sql.DataSource;

// 使用模块导入：一条语句导入整个模块
import module java.sql;

public class DatabaseExample {
    public void queryDatabase() throws SQLException {
        // 可以直接使用 java.sql 模块的所有导出类型
        Connection conn = DriverManager.getConnection("jdbc:...");
        PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users");
        ResultSet rs = stmt.executeQuery();
        
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }
}
```

## JEP 477：隐式声明的类和实例主方法（第三次预览）

JEP 477（第三次预览）继续简化 Java 程序的编写，特别适合初学者和小型程序。

**为什么要引入这个功能：**

传统的 Java 程序需要理解类、访问修饰符、静态方法、数组参数等多个概念，这对初学者构成了不必要的障碍。通过允许省略这些样板代码，降低了学习门槛。

**目标：**

- **降低入门门槛**：使初学者能够快速上手
- **简化脚本编写**：减少工具脚本的冗余代码
- **平滑学习曲线**：随着需求增长逐步引入高级特性

**简要使用示例：**

1. **最简单的程序：**

```java
// HelloWorld.java
void main() {
    println("Hello, World!");
}
```

2. **使用实例字段和方法：**

```java
// Calculator.java
int accumulator = 0;

void main() {
    add(10);
    add(20);
    println("Total: " + accumulator);
}

void add(int value) {
    accumulator += value;
}
```

3. **逐步扩展到完整的类：**

```java
// 初学者版本
void main() {
    println("Hello");
}

// 进阶版本 - 添加字段和方法
String name = "Java";

void main() {
    greet();
}

void greet() {
    println("Hello, " + name);
}

// 最终版本 - 标准类结构
public class Greeter {
    private String name = "Java";
    
    public static void main(String[] args) {
        new Greeter().greet();
    }
    
    public void greet() {
        System.out.println("Hello, " + name);
    }
}
```

## JEP 480：结构化并发（第三次预览）

JEP 480（第三次预览）继续完善结构化并发 API，简化并发编程。

**为什么要引入这个功能：**

传统的并发编程模型容易出现线程泄漏、异常处理复杂、取消操作困难等问题。结构化并发通过将相关任务作为单个工作单元管理，提供了更清晰、更安全的并发编程模式。

**目标：**

- **简化并发代码**：提供清晰的任务生命周期管理
- **提高可靠性**：自动处理任务取消和资源清理
- **增强可观察性**：更容易监控和调试并发任务

**简要使用示例：**

```java
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Subtask;

public class UserDataService {
    
    record UserData(User user, List<Order> orders, Profile profile) {}
    
    /**
     * 并发获取用户的所有相关数据
     */
    public UserData fetchUserData(String userId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            // 并发执行多个任务
            Subtask<User> userTask = scope.fork(() -> fetchUser(userId));
            Subtask<List<Order>> ordersTask = scope.fork(() -> fetchOrders(userId));
            Subtask<Profile> profileTask = scope.fork(() -> fetchProfile(userId));
            
            // 等待所有任务完成
            scope.join();
            
            // 如果任何任务失败，抛出异常
            scope.throwIfFailed();
            
            // 所有任务成功，组装结果
            return new UserData(
                userTask.get(),
                ordersTask.get(),
                profileTask.get()
            );
        }
    }
    
    /**
     * 获取第一个成功响应的结果
     */
    public String fetchFromMultipleServers(List<String> serverUrls) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
            // 并发请求多个服务器
            for (String url : serverUrls) {
                scope.fork(() -> httpGet(url));
            }
            
            // 等待第一个成功的结果
            scope.join();
            
            // 返回第一个成功的结果
            return scope.result();
        }
    }
    
    private User fetchUser(String userId) {
        // 模拟数据库查询
        return new User(userId, "John Doe");
    }
    
    private List<Order> fetchOrders(String userId) {
        // 模拟订单查询
        return List.of(new Order("Order1"), new Order("Order2"));
    }
    
    private Profile fetchProfile(String userId) {
        // 模拟用户档案查询
        return new Profile(userId, "Premium");
    }
    
    private String httpGet(String url) {
        // 模拟 HTTP 请求
        return "Response from " + url;
    }
}
```

## JEP 481：作用域值（第三次预览）

JEP 481（第三次预览）提供了一种新的方式在线程间共享不可变数据，作为 `ThreadLocal` 的更好替代方案。

**为什么要引入这个功能：**

`ThreadLocal` 存在多个问题：可变性导致的线程安全隐患、不受控制的生命周期、在虚拟线程场景下的性能问题等。作用域值通过提供不可变的、生命周期明确的数据共享机制，解决了这些问题。

**目标：**

- **不可变性**：确保共享数据的安全性
- **明确的生命周期**：从代码结构中清晰可见
- **高性能**：特别是在虚拟线程场景下

**简要使用示例：**

```java
import jdk.incubator.concurrent.ScopedValue;

public class WebRequestHandler {
    // 定义作用域值
    private static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();
    private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();
    private static final ScopedValue<Locale> LOCALE = ScopedValue.newInstance();
    
    /**
     * 处理 HTTP 请求
     */
    public void handleRequest(HttpRequest request) {
        String requestId = generateRequestId();
        User user = authenticate(request);
        Locale locale = determineLocale(request);
        
        // 设置作用域值并执行请求处理
        ScopedValue.where(REQUEST_ID, requestId)
                   .where(CURRENT_USER, user)
                   .where(LOCALE, locale)
                   .run(() -> processRequest(request));
    }
    
    private void processRequest(HttpRequest request) {
        // 在作用域内可以访问值
        log("Processing request");
        
        // 调用业务逻辑
        var data = fetchData();
        var response = transformData(data);
        sendResponse(response);
        
        log("Request completed");
    }
    
    private Object fetchData() {
        // 可以在任何嵌套的方法中访问作用域值
        User user = CURRENT_USER.get();
        return database.query("SELECT * FROM data WHERE user_id = ?", user.id());
    }
    
    private Object transformData(Object data) {
        Locale locale = LOCALE.get();
        // 根据语言环境转换数据
        return localizer.transform(data, locale);
    }
    
    private void sendResponse(Object response) {
        String requestId = REQUEST_ID.get();
        // 发送响应
        System.out.println("Sending response for request: " + requestId);
    }
    
    private void log(String message) {
        String requestId = REQUEST_ID.get();
        User user = CURRENT_USER.get();
        System.out.printf("[%s] [User: %s] %s%n", requestId, user.name(), message);
    }
    
    private String generateRequestId() {
        return java.util.UUID.randomUUID().toString();
    }
    
    private User authenticate(HttpRequest request) {
        return new User("user123", "John Doe");
    }
    
    private Locale determineLocale(HttpRequest request) {
        return Locale.US;
    }
}
```

## JEP 482：灵活的构造函数体（第二次预览）

JEP 482（第二次预览）继续完善灵活的构造函数体功能，根据第一次预览的反馈进行了改进。

**为什么要引入这个功能：**

Java 要求构造函数的第一条语句必须是 `super()` 或 `this()` 调用，这限制了参数验证和数据准备的灵活性。新特性允许在调用父类构造函数前执行必要的准备工作。

**目标：**

- **增强灵活性**：允许在 `super()` 前进行参数验证和准备
- **减少辅助方法**：无需创建静态方法来准备参数
- **提高代码质量**：使构造函数逻辑更清晰

**简要使用示例：**

1. **参数验证：**

```java
public class Email {
    private final String address;
    
    public Email(String address) {
        // 在 super() 前验证参数
        if (address == null || address.isBlank()) {
            throw new IllegalArgumentException("Email address cannot be empty");
        }
        if (!address.contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        
        // 标准化处理
        address = address.trim().toLowerCase();
        
        super();
        this.address = address;
    }
}
```

2. **复杂参数准备：**

```java
public class SecureConnection extends Connection {
    
    public SecureConnection(Certificate certificate, int port) {
        // 验证证书
        if (certificate == null) {
            throw new IllegalArgumentException("Certificate is required");
        }
        if (certificate.isExpired()) {
            throw new IllegalArgumentException("Certificate has expired");
        }
        
        // 提取和处理证书信息
        var publicKey = certificate.getPublicKey();
        byte[] keyBytes = switch (publicKey) {
            case RSAPublicKey rsa -> encodeRSAKey(rsa);
            case ECPublicKey ec -> encodeECKey(ec);
            default -> throw new IllegalArgumentException("Unsupported key type");
        };
        
        // 调用父类构造函数
        super(keyBytes, port);
    }
    
    private byte[] encodeRSAKey(RSAPublicKey key) {
        // RSA 密钥编码逻辑
        return key.getEncoded();
    }
    
    private byte[] encodeECKey(ECPublicKey key) {
        // EC 密钥编码逻辑
        return key.getEncoded();
    }
}
```

## JEP 483：提前编译工具改进（正式发布）

JEP 483 改进了提前编译（AOT）工具，进一步提升 Java 应用的启动性能。

**为什么要引入这个功能：**

在云原生和 serverless 环境中，应用的启动时间至关重要。传统的 JIT（即时编译）需要在运行时编译热点代码，导致启动阶段性能较差。AOT 编译可以在构建时完成编译，显著减少启动时间。

**目标：**

- **加快启动速度**：预编译代码可立即执行
- **减少预热时间**：避免 JIT 编译导致的性能波动
- **降低资源消耗**：减少运行时的 CPU 使用

**简要使用示例：**

1. **使用 AOT 编译应用：**

```bash
# 分析应用运行时行为
java -XX:ArchiveClassesAtExit=app.jsa -cp app.jar com.example.Main

# 使用存档文件启动应用（更快的启动速度）
java -XX:SharedArchiveFile=app.jsa -cp app.jar com.example.Main
```

2. **结合 CDS（Class Data Sharing）：**

```bash
# 创建应用的类数据共享存档
java -Xshare:dump -XX:SharedClassListFile=classes.lst \
     -XX:SharedArchiveFile=app.jsa -cp app.jar

# 使用共享存档启动
java -Xshare:on -XX:SharedArchiveFile=app.jsa \
     -cp app.jar com.example.Main
```

3. **性能对比：**

```bash
# 传统启动
$ time java -cp app.jar com.example.Main
real    0m2.345s

# AOT + CDS 启动
$ time java -Xshare:on -XX:SharedArchiveFile=app.jsa \
       -cp app.jar com.example.Main
real    0m0.856s
```

# 发布计划

- 2024/12/05: Rampdown Phase One
- 2025/01/16: Rampdown Phase Two
- 2025/02/06: Initial Release Candidate
- 2025/02/20: Final Release Candidate
- 2025/03/18: General Availability

# 总结

JDK 24 延续了 Java 平台的持续演进，在简化开发、提升性能和增强安全性方面取得了重要进展。

**正式发布的特性**包括 Markdown 文档注释、弃用 `sun.misc.Unsafe`、分代 ZGC 默认模式和 AOT 工具改进，这些特性已经成熟稳定，可以在生产环境中放心使用。

**持续预览的特性**如模块导入声明、隐式声明的类、结构化并发、作用域值和灵活的构造函数体，继续收集社区反馈，为最终正式发布做准备。

**向量 API** 进入第九次孵化，表明 Java 在高性能计算领域持续发力，为科学计算、机器学习等场景提供更好的支持。

总体而言，JDK 24 在保持企业级应用稳定性的同时，也积极拥抱现代编程实践，使 Java 更加易学易用、高效安全。

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注 `^_^`

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)
