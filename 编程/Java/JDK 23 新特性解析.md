---
2024-12-30
---

# 1. 前言

[JDK 23](https://openjdk.org/projects/jdk/23/) 是 Java SE 平台版本 23 的参考实现，2024 年 9 月 17 日正式发布。本文将详细解析 JDK 23 的主要新特性。

# 2. 新特性总览

1. **JEP 455：模式中的原始类型、`instanceof` 和 `switch`（预览）**
    
    - 扩展模式匹配，允许在所有模式上下文中使用原始类型，并在 `instanceof` 和 `switch` 中支持原始类型。
2. **JEP 456：类文件 API（第二次预览）**
    
    - 提供用于解析、生成和转换 Java 类文件的标准 API，简化对类文件的操作。
3. **JEP 467：Markdown 文档注释**
    
    - 允许在 JavaDoc 中使用 Markdown 语法编写文档注释，提高文档的可读性和编写效率。
4. **JEP 469：向量 API（第八次孵化）**
    
    - 提供用于表达向量计算的 API，支持在运行时编译为最优的向量指令，提升数值计算性能。
5. **JEP 473：流收集器（第二次预览）**
    
    - 增强流 API，支持自定义中间操作，使流管道能够以更灵活和富有表现力的方式转换数据。
6. **JEP 471：弃用 `sun.misc.Unsafe` 中的内存访问方法**
    
    - 计划移除 `sun.misc.Unsafe` 中的内存访问方法，鼓励开发者迁移到更安全的替代 API，如 `VarHandle` 和外部函数与内存 API。
7. **JEP 474：ZGC：默认的分代模式**
    
    - 将 Z 垃圾收集器（ZGC）的默认模式切换为分代模式，以提升垃圾回收性能和应用程序响应速度。
8. **JEP 476：模块导入声明（预览）**
    
    - 引入模块导入声明，允许开发者简洁地导入模块导出的所有包，简化模块化库的重用。
9. **JEP 477：隐式声明的类和实例主方法（第三次预览）**
    
    - 允许在没有显式声明类的情况下编写主方法，简化初学者的编程体验。
10. **JEP 480：结构化并发（第三次预览）**
    
    - 通过引入结构化并发，将相关任务视为单个工作单元，简化并发编程中的错误处理和取消操作，提高程序的可靠性。
11. **JEP 481：作用域值（第三次预览）**
    
    - 提供一种在线程内和线程之间共享不可变数据的机制，比线程局部变量更适合大量虚拟线程的场景。
12. **JEP 482：灵活的构造函数体（第二次预览）**
    
    - 允许在构造函数中，在显式的 `super()` 或 `this()` 调用之前出现语句，以初始化类的属性，增强构造函数的灵活性。

# 3. 详细解析

## 3.1 JEP 455：模式中的原始类型、`instanceof` 和 `switch`（预览）

JEP 455（预览版）旨在增强 Java 的模式匹配功能，允许在所有模式上下文中使用原始类型，并扩展 `instanceof` 和 `switch` 以支持所有原始类型。

**为什么要引入这个功能：**

在现有的 Java 版本中，模式匹配主要针对引用类型，限制了对原始类型的处理能力。这导致在处理原始类型时需要额外的类型转换和检查，增加了代码复杂性。通过支持原始类型的模式匹配，Java 语言将变得更加统一和表达力更强，减少开发者在处理不同类型时的心智负担。

**目标：**

- **统一数据处理**：允许对所有类型（无论是原始类型还是引用类型）使用类型模式进行匹配。
- **简化类型检查**：使 `instanceof` 操作符能够直接处理原始类型，减少不安全的类型转换。
- **增强 `switch` 语句**：使 `switch` 能够处理任何原始类型的值，提升代码的可读性和简洁性。

**简要使用示例：**

1. **在 `switch` 中使用原始类型模式：**

```JAVA
switch (x.getStatus()) {
    case 0 -> System.out.println("Status: OK");
    case 1 -> System.out.println("Status: Warning");
    case 2 -> System.out.println("Status: Error");
    case int i -> System.out.println("Unknown status: " + i);
}
```


在这个示例中，`switch` 语句直接对 `int` 类型的 `status` 进行匹配，并在默认情况下使用 `int i` 模式捕获未明确列出的状态值。
    
2. **在 `instanceof` 中使用原始类型模式：**

```JAVA
Object obj = ...;
if (obj instanceof int i) {
    System.out.println("Integer value: " + i);
} else {
    System.out.println("Not an integer");
}
```

此示例展示了使用 `instanceof` 检查对象是否为 `int` 类型，并在匹配时直接将其赋值给变量 `i`。

## 3.2 JEP 456：类文件 API（第二次预览）

JEP 466（第二次预览）旨在提供一个用于解析、生成和转换 Java 类文件的标准 API。

**为什么要引入这个功能：**

随着 JDK 的六个月发布周期，类文件格式演变的频率增加，现有的第三方库（如 ASM、BCEL 等）可能无法及时跟上这些变化。这导致框架开发者在处理比其捆绑的类文件库更新的类文件时，可能遇到错误或需要进行不安全的假设。因此，需要一个与 JDK 同步更新的标准类文件库，以确保兼容性和可靠性。

**目标：**

- **提供标准 API**：提供一个与 Java 虚拟机规范中定义的类文件格式保持一致的 API。
- **支持 JDK 组件迁移**：使 JDK 组件能够迁移到该标准 API，减少对第三方库的依赖。

**简要使用示例：**

1. **解析类文件并收集依赖项：**

```JAVA
CodeModel code = ...;
Set<ClassDesc> deps = new HashSet<>();
for (CodeElement e : code) {
    switch (e) {
        case FieldInstruction f  -> deps.add(f.owner());
        case InvokeInstruction i -> deps.add(i.owner());
        // 处理其他类型的指令
    }
}
```

在这个示例中，`CodeModel` 描述了一个 `Code` 属性。通过迭代其 `CodeElement`，可以匹配感兴趣的指令类型，并收集相关的类依赖项。
    
2. **生成类文件中的方法：**

假设我们希望在类文件中生成以下方法：

```JAVA
void fooBar(boolean z, int x) {
    if (z)
        foo(x);
    else
        bar(x);
}
```

使用 Class-File API，可以通过构建器模式生成该方法的字节码。


通过引入 Class-File API，JEP 466 使得 Java 开发者能够更方便地处理类文件，确保与最新的类文件格式兼容，并减少对第三方库的依赖。

## 3.3 JEP 467：Markdown 文档注释

JEP 467 引入了在 JavaDoc 文档注释中使用 Markdown 语法的功能，使得文档注释的编写和阅读更加简洁易懂。

**为什么要引入这个功能：**

传统的 JavaDoc 注释主要使用 HTML 和特定的 JavaDoc 标签进行标记，这在 1995 年是合理的选择。然而，HTML 语法繁琐，手动编写既费时又容易出错，尤其对于不熟悉 HTML 的开发者而言更是如此。Markdown 是一种轻量级标记语言，具有简洁、易读、易写的特点，已在开发者社区中广泛使用。引入 Markdown 语法可以简化文档注释的编写过程，提高代码的可读性和可维护性。

**目标：**

- **简化文档编写**：允许在文档注释中使用 Markdown 语法，使注释更易于编写和阅读。
- **保持兼容性**：确保现有的文档注释不会受到影响，继续支持 HTML 和 JavaDoc 标签。
- **扩展编译器 API**：增强编译器树 API，使其他工具能够处理文档注释中的 Markdown 内容。

**简要使用示例：**

1. **传统 JavaDoc 注释：**

```JAVA
/**
 * 返回对象的哈希码值。此方法用于支持像 {@link java.util.HashMap} 这样的哈希表。
 * <p>
 * {@code hashCode} 的一般约定是：
 * <ul>
 * <li>在 Java 应用程序的执行期间，当在同一对象上多次调用时，
 *     只要对象上用于 {@code equals} 比较的信息没有被修改，
 *     {@code hashCode} 方法必须始终返回相同的整数。
 *     该整数在同一应用程序的不同执行中不需要保持一致。
 * <li>如果根据 {@link #equals(Object) equals} 方法，两个对象是相等的，
 *     那么对这两个对象中的每一个调用 {@code hashCode} 方法必须产生相同的整数结果。
 * <li>如果两个对象根据 {@link #equals(Object) equals} 方法不相等，
 *     则不要求对每个对象调用 {@code hashCode} 方法必须产生不同的整数结果。
 *     但是，程序员应该意识到，为不相等的对象生成不同的整数结果可以提高哈希表的性能。
 * </ul>
 */

```


2. **使用 Markdown 的 JavaDoc 注释：**

```JAVA
/**
 * 返回对象的哈希码值。此方法用于支持像 {@link java.util.HashMap} 这样的哈希表。
 *
 * `hashCode` 的一般约定是：
 *
 * - 在 Java 应用程序的执行期间，当在同一对象上多次调用时，
 *   只要对象上用于 `equals` 比较的信息没有被修改，
 *   `hashCode` 方法必须始终返回相同的整数。
 *   该整数在同一应用程序的不同执行中不需要保持一致。
 * - 如果根据 {@link #equals(Object) equals} 方法，两个对象是相等的，
 *   那么对这两个对象中的每一个调用 `hashCode` 方法必须产生相同的整数结果。
 * - 如果两个对象根据 {@link #equals(Object) equals} 方法不相等，
 *   则不要求对每个对象调用 `hashCode` 方法必须产生不同的整数结果。
 *   但是，程序员应该意识到，为不相等的对象生成不同的整数结果可以提高哈希表的性能。
 */

```

通过引入 Markdown 语法，文档注释变得更加`简洁明了`，`减少了对繁琐 HTML 标签的依赖`，提高了代码的可读性。

## 3.4 JEP 469：向量 API（第八次孵化）

JEP 469（第八次孵化）旨在引入一个 API，用于表达向量计算，使其在运行时可靠地编译为支持的 CPU 架构上的最优向量指令，从而实现比等效标量计算更高的性能。

**为什么要引入这个功能：**

向量计算（SIMD）允许在单个指令中对多个数据进行并行处理，显著提高性能。然而，Java 缺乏直接支持向量计算的标准 API，开发者需要依赖平台特定的解决方案或手动优化。引入统一的向量 API，可以使开发者编写的代码在不同硬件平台上具有可移植性，并充分利用底层硬件的向量指令集，提高计算效率。

**目标：**

- **清晰简洁的 API**：提供一个能够清晰、简洁地表达各种向量计算的 API，使其可在循环和可能的控制流中组合使用。开发者应能够编写与向量大小无关的通用计算，从而在支持不同向量大小的硬件上实现可移植性。
    
- **平台无关性**：API 应该是 CPU 架构无关的，支持在多个具有向量指令的架构上实现。在平台优化和可移植性冲突的情况下，API 将偏向于可移植性，即使这意味着某些平台特定的习惯用法无法在可移植代码中表达。
    
- **可靠的运行时编译和性能**：在支持的 x64 和 AArch64 架构上，Java 运行时（特别是 HotSpot C2 编译器）应将向量操作编译为相应的高效向量指令，如 SSE、AVX（x64）和 NEON、SVE（AArch64）。开发者应确信他们表达的向量操作将可靠地映射到相关的向量指令。
    
- **优雅的降级**：当在运行时无法将向量计算完全表达为向量指令序列时，API 实现应优雅地降级并继续工作。这可能涉及在无法高效编译为向量指令时发出警告。在不支持向量的平台上，优雅的降级将产生与手动展开循环相当的代码，其中展开因子是所选向量的通道数。
    
- **与 Project Valhalla 的对齐**：长期目标是利用 Project Valhalla 对 Java 对象模型的增强，特别是将当前的值基类更改为值类，使程序能够处理没有对象标识的值对象。
    

**简要使用示例：**

以下是使用向量 API 进行向量加法的示例：

```JAVA
import jdk.incubator.vector.*;

public class VectorAddition {
    public static void main(String[] args) {
        // 创建向量规范，指定向量类型和长度
        VectorSpecies<Integer> SPECIES = IntVector.SPECIES_PREFERRED;

        // 初始化数组
        int[] a = {1, 2, 3, 4, 5, 6, 7, 8};
        int[] b = {8, 7, 6, 5, 4, 3, 2, 1};
        int[] c = new int[a.length];

        // 使用向量 API 进行加法运算
        for (int i = 0; i < a.length; i += SPECIES.length()) {
            // 将数组加载到向量
            var va = IntVector.fromArray(SPECIES, a, i);
            var vb = IntVector.fromArray(SPECIES, b, i);
            // 向量加法
            var vc = va.add(vb);
            // 将结果存储回数组
            vc.intoArray(c, i);
        }

        // 输出结果
        System.out.println(Arrays.toString(c));
    }
}
```

在这个示例中，`VectorSpecies` 定义了向量的类型和长度。通过将数组的数据加载到向量中，执行向量化的加法操作，然后将结果存储回数组，实现了高效的并行计算。

## 3.5 JEP 473：流收集器（第二次预览）

JEP 473（第二次预览）旨在增强 Stream API，以支持自定义的中间操作，从而使流管道能够以现有内置中间操作难以实现的方式来转换数据。

**为什么要引入这个功能：**

Java 8 引入了 Stream API，提供了一组固定的中间和终端操作，如映射、过滤、归约、排序等。然而，对于某些复杂任务，这些固定的中间操作可能不足以表达所需的流处理逻辑。例如，假设需要对字符串流进行去重，但基于字符串长度而非内容的唯一性。现有的 `distinct` 操作基于对象的相等性，无法满足这一需求。为此，需要引入自定义的中间操作，以实现更灵活的流数据转换。

**目标：**

- **提高流管道的灵活性和表达能力**：允许开发者定义自定义的中间操作，以满足特定的数据处理需求。
    
- **支持对无限大小的流进行操作**：确保自定义的中间操作能够有效地处理无限流。
    

**简要使用示例：**

假设我们希望对字符串流进行基于字符串长度的去重操作。通过引入自定义的中间操作 `distinctBy`，可以实现如下功能：

```JAVA
var result = Stream.of("foo", "bar", "baz", "quux")
                   .distinctBy(String::length) // 假设的自定义操作
                   .toList();

// result ==> [foo, quux]
```


在这个示例中，`distinctBy` 是一个自定义的中间操作，基于提供的键提取函数（此处为 `String::length`）来确定元素的唯一性。这样，结果列表中将包含每个长度的第一个字符串。

通过引入自定义的中间操作，JEP 473 使得开发者能够以更直观和可维护的方式来表达复杂的流处理逻辑，提升了代码的可读性和灵活性。

## 3.6 JEP 471：弃用 `sun.misc.Unsafe` 中的内存访问方法

JEP 471 提议将 `sun.misc.Unsafe` 类中的内存访问方法标记为弃用，计划在未来的 JDK 版本中移除这些方法。这些不受支持的方法已被标准 API 所取代，主要包括在 JDK 9 中引入的 VarHandle API（JEP 193）和在 JDK 22 中引入的外部函数与内存 API（JEP 454）。我们强烈建议库开发者从 `sun.misc.Unsafe` 迁移到受支持的替代方案，以便应用程序能够顺利迁移到现代 JDK 版本。

**为什么要引入这个功能：**

`sun.misc.Unsafe` 类于 2002 年引入，旨在让 JDK 内部的 Java 类执行低级操作。然而，其内存访问方法可能导致未定义行为，包括 JVM 崩溃。因此，这些方法并未作为标准 API 暴露。随着时间的推移，已经引入了安全且高效的标准 API 来替代这些不安全的方法。因此，现在是时候弃用并最终移除 `sun.misc.Unsafe` 中的内存访问方法。

**目标：**

- **为未来的移除做准备**：为在未来的 JDK 版本中移除 `sun.misc.Unsafe` 中的内存访问方法做好准备。
    
- **提高开发者意识**：帮助开发者意识到他们的应用程序何时直接或间接地依赖于 `sun.misc.Unsafe` 中的内存访问方法。
    

**简要使用示例：**

以下是使用 VarHandle API 替代 `sun.misc.Unsafe` 的示例：

```JAVA
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

public class VarHandleExample {
    private int value;

    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException {
        VarHandleExample example = new VarHandleExample();
        VarHandle varHandle = MethodHandles.lookup().findVarHandle(VarHandleExample.class, "value", int.class);

        // 使用 VarHandle 读取字段值
        int currentValue = (int) varHandle.get(example);
        System.out.println("Current value: " + currentValue);

        // 使用 VarHandle 更新字段值
        varHandle.set(example, 42);
        System.out.println("Updated value: " + example.value);
    }
}
```

在这个示例中，VarHandle API 提供了一种安全且高效的方式来访问和修改对象的字段，而无需使用不安全的 `sun.misc.Unsafe` 方法。

## 3.7 JEP 474：ZGC：默认的分代模式

JEP 474 提议在 Java 23 中将 Z 垃圾收集器（ZGC）的默认模式切换为分代模式，并弃用非分代模式，计划在未来的版本中移除。

**为什么要引入这个功能：**

维护非分代 ZGC 会减缓新特性的开发。正如 JEP 439 所述，分代 ZGC 应该在大多数用例中优于非分代 ZGC。因此，最终用分代 ZGC 取代非分代 ZGC 可以降低长期的维护成本。

**目标：**

- **聚焦分代 ZGC 的未来开发**：通过将默认模式切换为分代模式，表明未来的开发将专注于分代 ZGC。
    
- **减少维护成本**：支持两种不同模式会增加维护成本，切换默认模式并弃用非分代模式有助于降低这些成本。
    

**简要使用示例：**

在此更改之前，启用 ZGC 的默认模式是非分代模式，需要显式指定分代模式：

`java -XX:+UseZGC -XX:+ZGenerational ...` 

在应用 JEP 474 后，默认模式将是分代模式，因此只需启用 ZGC 即可：

`java -XX:+UseZGC ...` 

如果仍需使用非分代模式，可以显式禁用分代模式，但会收到弃用警告：

`java -XX:+UseZGC -XX:-ZGenerational ...` 

请注意，使用 `-XX:-ZGenerational` 将启用非分代 ZGC，并会收到以下警告：

`警告: 选项 ZGenerational 已被弃用，将在未来版本中移除。
警告: 非分代模式已被弃用，计划在未来版本中移除。` 

因此，建议迁移到分代 ZGC，以确保未来版本的兼容性和性能优化。

## 3.8 JEP 476：模块导入声明（预览）

JEP 476 提议在 Java 编程语言中引入模块导入声明，使开发者能够简洁地导入模块所导出的所有包，从而简化模块化库的重用。

**为什么要引入这个功能：**

随着 Java 平台的发展，许多关键类和接口（如 `List`、`Map`、`Stream` 和 `Path`）并不位于 `java.lang` 包中，因此需要手动导入多个包。这增加了代码的复杂性，特别是在使用模块化库时。通过引入模块导入声明，开发者可以一次性导入模块所导出的所有包，减少样板代码，提高开发效率。

**目标：**

- **简化模块化库的重用**：允许一次性导入整个模块，减少多个包导入声明的冗余。
    
- **降低学习曲线**：使初学者无需深入了解包层次结构即可使用第三方库和 Java 标准类。
    
- **无需模块化自身代码**：使用模块导入功能的开发者不需要将自己的代码模块化。
    

**简要使用示例：**

假设我们需要使用 `java.sql` 模块中的功能，传统方式需要导入多个包：

```JAVA
import java.sql.*;
import javax.sql.*;
```

使用模块导入声明，可以简化为：

```JAVA
import module java.sql;
```

这将导入 `java.sql` 模块导出的所有包中的公共顶级类和接口，简化了代码编写。

需要注意的是，模块导入声明是一个预览语言特性，默认情况下是禁用的。要在 JDK 23 中使用此功能，需要在编译和运行时启用预览特性。

## 3.9 JEP 477：ZGC：支持多线程堆处理

JEP 477 提议在 Java 编程语言中引入隐式声明的类和实例 `main` 方法，旨在使初学者能够编写简洁的程序，而无需理解为大型程序设计的语言特性。

**为什么要引入这个功能：**

Java 语言以其丰富的特性在构建大型、复杂的应用程序方面表现出色。然而，对于初学者而言，这些特性可能显得过于复杂。通过引入隐式声明的类和实例 `main` 方法，初学者可以在不涉及复杂概念的情况下编写简单程序，从而降低学习曲线。

**目标：**

- **提供平滑的 Java 编程入门途径**：使讲师能够逐步引入概念，帮助学生以简洁的方式编写基本程序，并随着技能的提升，优雅地扩展他们的代码。
    
- **减少编写小型程序的繁琐**：例如脚本和命令行工具，无需引入为大型程序设计的构造。
    
- **避免引入独立的 Java 方言或工具链**：小型 Java 程序应使用与大型程序相同的工具进行编译和运行。

**简要使用示例：**

传统的 "Hello, World!" 程序需要包含类声明和静态 `main` 方法：

```JAVA
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

使用隐式声明的类和实例 `main` 方法，可以简化为：

```JAVA
void main() {
    System.out.println("Hello, World!");
}
```

在此示例中，省略了类声明和静态方法修饰符，使代码更简洁，便于初学者理解。

需要注意的是，隐式声明的类和实例 `main` 方法是一个预览语言特性，默认情况下是禁用的。要在 JDK 23 中使用此功能，需要在编译和运行时启用预览特性。

## 3.10 JEP 480：结构化并发（第三次预览）

JEP 480 提议在 Java 编程语言中引入结构化并发的 API，以简化并发编程。结构化并发将一组在不同线程中运行的相关任务视为一个工作单元，从而简化错误处理和取消操作，提高可靠性，并增强可观察性。

**为什么要引入这个功能：**

在传统的非结构化并发模型中，开发者需要手动管理线程的生命周期、错误处理和取消操作，这增加了代码的复杂性和出错的风险。结构化并发通过将相关任务作为一个整体进行管理，确保任务的启动和终止具有明确的结构，减少了线程泄漏和取消延迟等常见问题，提高了代码的可维护性和可靠性。

**目标：**

- **推广结构化并发编程风格**：通过引入新的 API，鼓励开发者采用结构化并发的方式编写代码，减少并发编程中的常见错误。
    
- **提高并发代码的可观察性**：提供更好的工具和方法来监控并发任务的执行状态，便于调试和性能优化。
    

**简要使用示例：**

以下是使用结构化并发 API 的示例代码：

```JAVA
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
`try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String>  user  = scope.fork(() -> findUser());
    Future<Integer> order = scope.fork(() -> fetchOrder());
    scope.join();           // 等待所有子任务完成
    scope.throwIfFailed();  // 如果有子任务失败，则抛出异常
    // 所有子任务成功，获取结果
    String theUser  = user.resultNow();
    int    theOrder = order.resultNow();
    return new Response(theUser, theOrder);
}
```

在这个示例中，`StructuredTaskScope` 用于管理并发任务的生命周期。`fork()` 方法用于启动子任务，`join()` 方法等待所有子任务完成，`throwIfFailed()` 方法在任何子任务失败时抛出异常。这样，相关的并发任务被作为一个整体进行管理，简化了错误处理和资源管理。

需要注意的是，结构化并发 API 是一个预览特性，默认情况下是禁用的。要在 JDK 23 中使用此功能，需要在编译和运行时启用预览特性。

## 3.11 JEP 481：作用域值（第三次预览）

JEP 481 提议在 Java 编程语言中引入作用域值（Scoped Values），使方法能够在同一线程内与其被调用的方法以及子线程共享不可变数据。与线程局部变量相比，作用域值更易于理解，并且在与虚拟线程（JEP 444）和结构化并发（JEP 480）结合使用时，具有更低的空间和时间成本。

**为什么要引入这个功能：**

在传统的 Java 并发编程中，线程局部变量（ThreadLocal）用于在同一线程内共享数据。然而，线程局部变量存在一些缺点，例如可变性、不受限制的生命周期以及在多线程环境下的性能开销。作用域值通过提供不可变且受限生命周期的数据共享机制，解决了这些问题，提高了代码的可维护性和性能。

**目标：**

- **易用性**：使数据流更易于理解。
- **可理解性**：共享数据的生命周期应从代码的语法结构中清晰体现。
- **健壮性**：调用者共享的数据应仅能被合法的被调用者获取。
- **性能**：应能够在大量线程之间高效地共享数据。

**简要使用示例：**

以下是使用作用域值的示例代码：

```JAVA
import jdk.incubator.concurrent.ScopedValue;

public class Example {
    // 定义一个作用域值
    private static final ScopedValue<String> USER_ID = ScopedValue.newInstance();

    public static void main(String[] args) {
        // 设置作用域值并调用方法
        ScopedValue.where(USER_ID, "user123").run(() -> {
            process();
        });
    }

    public static void process() {
        // 在作用域内获取值
        String userId = USER_ID.get();
        System.out.println("Processing for user: " + userId);
    }
}
```

在此示例中，`USER_ID` 被定义为一个作用域值。在 `main` 方法中，通过 `ScopedValue.where` 方法设置 `USER_ID` 的值，并在作用域内调用 `process` 方法。在 `process` 方法中，可以通过 `USER_ID.get()` 获取设置的值。

## 3.12 JEP 482：灵活的构造函数体（第二次预览）

JEP 482 提议在 Java 编程语言中允许构造函数体中的语句可以出现在显式构造函数调用（如 `super(..)` 或 `this(..)`）之前。这些语句不能引用正在构建的实例，但可以初始化其字段。在调用其他构造函数之前初始化字段，使得在方法被重写的情况下，类的构造函数更加可靠。

**为什么要引入这个功能：**

在 Java 中，构造函数的首条语句必须是对另一个构造函数的显式调用（如 `super(..)` 或 `this(..)`）。这种限制有时会导致代码不够灵活，特别是在需要在调用父类构造函数之前进行参数验证或字段初始化的情况下。通过允许在显式构造函数调用之前添加语句，开发者可以更自然地编写构造函数逻辑，而无需依赖辅助静态方法或中间构造函数。

**目标：**

- **提供更大的构造函数表达自由度**：使开发者能够更自然地编写构造函数逻辑，减少对辅助方法的依赖。
    
- **保持构造顺序的保证**：确保在类实例化过程中，构造函数仍然按照从上到下的顺序执行，子类构造函数的代码不会干扰父类的实例化过程。
    

**简要使用示例：**

以下是使用灵活构造函数体的示例代码：

```JAVA
public class PositiveBigInteger extends BigInteger {

    public PositiveBigInteger(long value) {
        if (value <= 0) throw new IllegalArgumentException("Value must be positive");
        super(value);
    }
}
```

在此示例中，在调用父类构造函数 `super(value)` 之前，先验证了参数 `value` 是否为正值。这在以前的 Java 版本中是不允许的，但通过 JEP 482 的引入，这种模式现在是合法的。

