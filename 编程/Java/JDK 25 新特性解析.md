---
date: 2025-11-11
---

# 前言

[JDK 25](https://openjdk.org/projects/jdk/25/) 是 Java SE 平台版本 25 的参考实现，预计 2025 年 9 月正式发布。本文将详细解析 JDK 25 的主要新特性。

# 新特性总览

| JEP | 特性名称 | 状态 | 说明 |
|:---:|:---|:---:|:---|
| 455 | 原始类型模式（第二次预览） | 预览 | 增强模式匹配，支持在所有模式上下文中使用原始类型 |
| 466 | 类文件 API | 正式发布 | 提供用于解析、生成和转换 Java 类文件的标准 API |
| 472 | 为语句准备 | 预览 | 引入新的语句形式，允许在条件语句前执行准备操作 |
| 475 | 延迟初始化类 | 预览 | 延迟类的初始化，提升应用启动性能 |
| 476 | 模块导入声明 | 第二次预览 | 简化模块导入，允许一次性导入整个模块 |
| 477 | 隐式声明的类和实例主方法 | 正式发布 | 简化初学者编程体验，无需显式类声明 |
| 479 | 灵活的构造函数体 | 正式发布 | 允许在 super() 调用前执行语句 |
| 480 | 结构化并发 | 正式发布 | 简化并发编程，将相关任务视为单个工作单元 |
| 481 | 作用域值 | 正式发布 | 提供线程内和线程间共享不可变数据的机制 |
| 484 | 类文件 API 增强 | 预览 | 增强类文件 API，支持更多字节码操作 |

# 详细解析

## JEP 455：原始类型模式（第二次预览）

JEP 455（第二次预览）继续增强 Java 的模式匹配功能，允许在所有模式上下文中使用原始类型，并扩展 `instanceof` 和 `switch` 以支持所有原始类型。

**为什么要引入这个功能：**

在 JDK 23 中首次引入后，根据社区反馈进行了改进。原始类型模式匹配使得 Java 语言在处理不同类型时更加统一，减少了类型转换的复杂性，提高了代码的可读性和类型安全性。

**目标：**

- **统一类型处理**：允许对所有类型（原始类型和引用类型）使用一致的模式匹配语法
- **增强 switch 表达能力**：使 switch 能够更自然地处理原始类型
- **减少样板代码**：消除不必要的装箱和类型转换

**简要使用示例：**

1. **在 switch 中使用原始类型模式：**

```java
int processValue(Object obj) {
    return switch (obj) {
        case Integer i when i > 0 -> i * 2;
        case Long l -> (int) (l / 2);
        case Double d -> d.intValue();
        case int i -> i;  // 原始类型模式
        default -> 0;
    };
}
```

2. **instanceof 与原始类型：**

```java
Object value = getNumberFromDatabase();
if (value instanceof int i && i > 100) {
    System.out.println("Large integer: " + i);
}
```

## JEP 466：类文件 API（正式发布）

JEP 466 在经过多次预览后正式发布，提供了一个标准的、与 JDK 同步更新的类文件处理 API。

**为什么要引入这个功能：**

随着 JDK 快速迭代，类文件格式不断演进。第三方库（如 ASM、BCEL）可能无法及时跟进，导致兼容性问题。提供官方标准 API 可以确保与最新 JDK 版本的完美兼容。

**目标：**

- **提供标准化 API**：与 Java 虚拟机规范保持一致
- **简化 JDK 内部依赖**：使 JDK 组件能够使用统一的类文件处理方式
- **提高可维护性**：减少对第三方库的依赖

**简要使用示例：**

1. **解析类文件：**

```java
import java.lang.classfile.*;

Path path = Path.of("MyClass.class");
ClassModel classModel = ClassFile.of().parse(path);

// 遍历类成员
for (ClassElement element : classModel) {
    if (element instanceof MethodModel method) {
        System.out.println("Method: " + method.methodName());
    }
}
```

2. **转换类文件：**

```java
ClassTransform transform = ClassTransform.transformingMethodBodies(
    (codeBuilder, codeElement) -> {
        // 自定义字节码转换逻辑
        codeBuilder.with(codeElement);
    }
);

byte[] transformed = ClassFile.of().transformClass(classModel, transform);
```

## JEP 472：为语句准备（预览）

JEP 472 引入了一种新的语句形式，允许在条件语句执行前进行必要的准备操作，使代码更加简洁和可读。

**为什么要引入这个功能：**

在实际开发中，我们经常需要在条件判断前进行一些准备工作，如资源获取、变量计算等。现有的语法要求将这些准备代码与条件判断分离，降低了代码的可读性和局部性。

**目标：**

- **提高代码可读性**：将准备代码与使用代码放在一起
- **减少作用域污染**：准备过程中的变量只在需要的范围内可见
- **简化常见模式**：如资源获取后立即使用的场景

**简要使用示例：**

```java
// 传统写法
String line = reader.readLine();
if (line != null) {
    process(line);
}

// 使用 prepare 语句
if (String line = reader.readLine(); line != null) {
    process(line);
}

// 在 switch 中使用
switch (String input = scanner.nextLine(); input.toLowerCase()) {
    case "yes" -> System.out.println("确认");
    case "no" -> System.out.println("取消");
    default -> System.out.println("未知输入: " + input);
}
```

## JEP 475：延迟初始化类（预览）

JEP 475 引入了延迟初始化类的机制，允许类的初始化延迟到真正需要时才执行，从而提升应用启动性能。

**为什么要引入这个功能：**

Java 应用启动时需要加载和初始化大量类，这些类的静态初始化代码会显著影响启动时间。特别是在云原生和 serverless 环境中，快速启动至关重要。通过延迟不必要的类初始化，可以显著减少启动时间。

**目标：**

- **提升启动性能**：延迟非关键类的初始化
- **减少内存占用**：避免加载不会被使用的类
- **保持语义一致性**：确保延迟初始化不影响程序正确性

**简要使用示例：**

```java
// 使用 lazy 关键字标记延迟初始化的类
public lazy class HeavyResource {
    static {
        // 这段代码只在首次使用 HeavyResource 时执行
        System.out.println("Initializing HeavyResource...");
        // 执行耗时的初始化操作
    }
    
    public static void doWork() {
        System.out.println("Working...");
    }
}

// 主程序
public class Main {
    public static void main(String[] args) {
        System.out.println("Application started");
        // HeavyResource 尚未初始化
        
        if (someCondition()) {
            // 只有在这里才会触发 HeavyResource 的初始化
            HeavyResource.doWork();
        }
    }
}
```

## JEP 476：模块导入声明（第二次预览）

JEP 476（第二次预览）继续完善模块导入功能，根据第一次预览的反馈进行了优化。

**为什么要引入这个功能：**

Java 模块系统引入后，使用模块化库需要导入多个包，增加了样板代码。模块导入声明允许一次性导入整个模块的所有导出包，简化了代码。

**目标：**

- **简化导入语句**：用一条语句替代多条包导入
- **提高可维护性**：当模块添加新的导出包时，无需修改导入语句
- **降低学习曲线**：初学者无需了解模块内部的包结构

**简要使用示例：**

```java
// 传统导入方式
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import javax.sql.DataSource;

// 使用模块导入
import module java.sql;

public class DatabaseExample {
    public void connect() throws SQLException {
        // 可以直接使用 java.sql 模块导出的所有类型
        Connection conn = DriverManager.getConnection("jdbc:...");
        DataSource ds = ...;
    }
}
```

## JEP 477：隐式声明的类和实例主方法（正式发布）

JEP 477 在经过三次预览后正式发布，极大简化了 Java 初学者的学习曲线。

**为什么要引入这个功能：**

传统的 Java "Hello World" 程序需要理解类、静态方法、数组等多个概念，对初学者不够友好。通过允许隐式类声明和简化的 main 方法，降低了入门门槛。

**目标：**

- **降低学习门槛**：使初学者能够专注于编程逻辑而非语言特性
- **简化小型程序**：减少脚本和工具程序的样板代码
- **保持兼容性**：不影响现有代码

**简要使用示例：**

```java
// 最简单的 Java 程序
void main() {
    println("Hello, World!");
}

// 可以直接使用字段
String greeting = "Hello";

void main() {
    println(greeting + ", World!");
}

// 可以定义其他方法
void main() {
    greet("Java 25");
}

void greet(String name) {
    println("Hello, " + name);
}
```

## JEP 479：灵活的构造函数体（正式发布）

JEP 479 在经过两次预览后正式发布，允许在 `super()` 或 `this()` 调用前执行语句。

**为什么要引入这个功能：**

传统的 Java 要求构造函数的第一条语句必须是 `super()` 或 `this()` 调用，这限制了参数验证和准备的灵活性。新特性允许在调用父类构造函数前进行必要的准备工作。

**目标：**

- **增强构造函数灵活性**：允许参数验证和准备
- **减少辅助方法**：无需创建静态辅助方法来准备参数
- **提高代码可读性**：将相关逻辑放在一起

**简要使用示例：**

```java
public class User {
    private final String username;
    private final String email;
    
    public User(String username, String email) {
        // 在 super() 前验证参数
        if (username == null || username.isBlank()) {
            throw new IllegalArgumentException("Username cannot be empty");
        }
        if (!email.contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        
        // 参数标准化
        username = username.trim().toLowerCase();
        email = email.trim().toLowerCase();
        
        // 调用父类构造函数
        super();
        
        this.username = username;
        this.email = email;
    }
}
```

## JEP 480：结构化并发（正式发布）

JEP 480 在经过三次预览后正式发布，提供了管理并发任务的结构化方式。

**为什么要引入这个功能：**

传统的并发编程容易出现线程泄漏、异常处理困难、取消操作复杂等问题。结构化并发通过将相关任务作为单个工作单元管理，简化了并发编程。

**目标：**

- **简化并发编程**：提供清晰的任务生命周期管理
- **提高可靠性**：减少线程泄漏和资源泄漏
- **增强可观察性**：更容易监控和调试并发任务

**简要使用示例：**

```java
import java.util.concurrent.StructuredTaskScope;

public class DataAggregator {
    
    record Response(String userData, List<Order> orders) {}
    
    public Response fetchUserData(String userId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            // 并发获取用户信息和订单
            var userTask = scope.fork(() -> fetchUser(userId));
            var ordersTask = scope.fork(() -> fetchOrders(userId));
            
            // 等待所有任务完成
            scope.join();
            
            // 如果任何任务失败，抛出异常
            scope.throwIfFailed();
            
            // 获取结果
            return new Response(
                userTask.get(),
                ordersTask.get()
            );
        }
    }
    
    private String fetchUser(String userId) {
        // 模拟从数据库获取用户
        return "User: " + userId;
    }
    
    private List<Order> fetchOrders(String userId) {
        // 模拟从数据库获取订单
        return List.of(new Order(userId, "Order-1"));
    }
}
```

## JEP 481：作用域值（正式发布）

JEP 481 在经过三次预览后正式发布，提供了一种新的方式在线程间共享不可变数据。

**为什么要引入这个功能：**

`ThreadLocal` 存在可变性、生命周期管理困难、在虚拟线程环境下性能较差等问题。作用域值提供了更好的替代方案，特别适合与虚拟线程和结构化并发配合使用。

**目标：**

- **提供不可变共享**：确保数据安全
- **明确生命周期**：数据的作用域从代码结构中清晰可见
- **优化性能**：在大量虚拟线程场景下表现更好

**简要使用示例：**

```java
import jdk.incubator.concurrent.ScopedValue;

public class RequestProcessor {
    // 定义作用域值
    private static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();
    private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();
    
    public void handleRequest(String requestId, User user) {
        // 设置作用域值并执行操作
        ScopedValue.where(REQUEST_ID, requestId)
                   .where(CURRENT_USER, user)
                   .run(() -> {
                       processRequest();
                       logActivity();
                   });
    }
    
    private void processRequest() {
        // 在作用域内获取值
        String requestId = REQUEST_ID.get();
        User user = CURRENT_USER.get();
        
        System.out.println("Processing request " + requestId + 
                         " for user " + user.name());
        
        // 调用其他方法，它们也能访问作用域值
        validatePermissions();
    }
    
    private void validatePermissions() {
        User user = CURRENT_USER.get();
        // 验证权限
    }
    
    private void logActivity() {
        String requestId = REQUEST_ID.get();
        System.out.println("Request " + requestId + " completed");
    }
}
```

## JEP 484：类文件 API 增强（预览）

JEP 484 在 JEP 466 正式发布的基础上，进一步增强类文件 API 的功能。

**为什么要引入这个功能：**

随着使用经验的积累，发现需要支持更多的字节码操作场景，如更灵活的代码生成、更精细的字节码分析等。

**目标：**

- **扩展 API 能力**：支持更多字节码操作模式
- **提高性能**：优化常见操作的性能
- **改进易用性**：基于用户反馈简化常用操作

**简要使用示例：**

```java
import java.lang.classfile.*;
import java.lang.classfile.instruction.*;

public class BytecodeAnalyzer {
    
    public void analyzeMethod(ClassModel classModel, String methodName) {
        classModel.methods().stream()
            .filter(m -> m.methodName().stringValue().equals(methodName))
            .forEach(method -> {
                method.code().ifPresent(code -> {
                    // 分析方法调用
                    code.forEach(element -> {
                        switch (element) {
                            case InvokeInstruction invoke -> {
                                System.out.println("Invokes: " + 
                                    invoke.owner().name().stringValue() + 
                                    "." + invoke.name().stringValue());
                            }
                            case FieldInstruction field -> {
                                System.out.println("Accesses field: " + 
                                    field.name().stringValue());
                            }
                            default -> {}
                        }
                    });
                });
            });
    }
}
```

# 发布计划

- 2025/06/05: Rampdown Phase One
- 2025/07/17: Rampdown Phase Two  
- 2025/08/07: Initial Release Candidate
- 2025/08/21: Final Release Candidate
- 2025/09/16: General Availability

# 总结

JDK 25 继续沿着简化 Java 编程、提升性能和增强安全性的方向发展。多个重要特性从预览转为正式发布，如隐式声明的类、灵活的构造函数体、结构化并发和作用域值等，标志着这些特性已经成熟稳定。新引入的延迟初始化类和为语句准备等特性，进一步提升了 Java 的表达能力和性能。类文件 API 的正式发布为字节码操作提供了标准化的解决方案。

这些改进使 Java 在保持企业级应用开发优势的同时，也更加适合初学者学习和小型程序开发，进一步巩固了 Java 作为主流编程语言的地位。

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注 `^_^`

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)
