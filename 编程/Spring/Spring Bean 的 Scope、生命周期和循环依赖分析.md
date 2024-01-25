---
date: 2021-05-13
---

- [Scope](#scope)
  - [Scope 测试](#scope-测试)
  - [源码分析](#源码分析)
- [生命周期](#生命周期)
  - [BeanFactory](#beanfactory)
- [循环依赖](#循环依赖)
  - [循环依赖的 3 种类型](#循环依赖的-3-种类型)
    - [构造器循环依赖](#构造器循环依赖)
    - [setter/field 循环依赖](#setterfield-循环依赖)
    - [prototype 范围的依赖处理](#prototype-范围的依赖处理)
  - [Spring 如何解决循环依赖？](#spring-如何解决循环依赖)
    - [三级缓存](#三级缓存)
    - [源码分析](#源码分析-1)
  - [Spring Boot 2.6.0 开启循环依赖](#spring-boot-260-开启循环依赖)
- [GitHub LeetCode 项目](#github-leetcode-项目)


# Scope

[Spring 官方文档 #Bean Scopes](https://docs.spring.io/spring-framework/docs/current/reference/html/core.html#beans-factory-scopes)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513153755.png?x-oss-process=style/yano)

官网文档是最权威的，Spring Framework 支持 6 种 Scope，其中 4 种仅在 web-aware ApplicationContext 中才可以使用，剩下的两种是：
1. `singleton`：每个 Spring IoC 容器中仅有一个实例（单例）。
2. `prototype`：每次注入都会新建一个对象，Spring IoC 容器并不会缓存 prototype 的 bean。

```java
public interface BeanDefinition extends AttributeAccessor, BeanMetadataElement {

	/**
	 * Scope identifier for the standard singleton scope: {@value}.
	 * <p>Note that extended bean factories might support further scopes.
	 * @see #setScope
	 * @see ConfigurableBeanFactory#SCOPE_SINGLETON
	 */
	String SCOPE_SINGLETON = ConfigurableBeanFactory.SCOPE_SINGLETON;

	/**
	 * Scope identifier for the standard prototype scope: {@value}.
	 * <p>Note that extended bean factories might support further scopes.
	 * @see #setScope
	 * @see ConfigurableBeanFactory#SCOPE_PROTOTYPE
	 */
	String SCOPE_PROTOTYPE = ConfigurableBeanFactory.SCOPE_PROTOTYPE;
```

## Scope 测试

SingletonBean 是一个 Singleton Scope 的 bean，里面的 Scope 注解不设置也可以，默认是 Singleton 的。

```java
@Component
@Scope
@Data
@Slf4j
public class SingletonBean {
    private int i;

    @PostConstruct
    public void init() {
        log.info("SingletonBean init ...");
    }
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513155241.png?x-oss-process=style/yano)

ProtoTypeBean 是一个 Prototype Scope 的 bean。

```java
@Component
@Scope(scopeName = SCOPE_PROTOTYPE)
@Data
@Slf4j
public class ProtoTypeBean {
    private int i;

    @PostConstruct
    public void init() {
        log.info("ProtoTypeBean init ...");
    }
}
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513155254.png?x-oss-process=style/yano)

测试代码中对于每个 bean，分别从容器中获取 2 次，看 log 输出。

```java
@RunWith(SpringRunner.class)
@Slf4j
@SpringBootTest(classes = Application.class)
public class BeanTest {

    @Autowired
    private ApplicationContext context;

    @Test
    public void testScope() {
        context.getBean(SingletonBean.class);
        context.getBean(SingletonBean.class);

        context.getBean(ProtoTypeBean.class);
        context.getBean(ProtoTypeBean.class);
    }
}
```

最终输出了 1 次 SingletonBean，2 次 ProtoTypeBean。

```
SingletonBean init ...
ProtoTypeBean init ...
ProtoTypeBean init ...
```

## 源码分析

在 Scope 注解定义上查找引用，发现 Scope 作为实例变量只有 AnnotationScopeMetadataResolver 中。

```java
public class AnnotationScopeMetadataResolver implements ScopeMetadataResolver {

	private final ScopedProxyMode defaultProxyMode;

	protected Class<? extends Annotation> scopeAnnotationType = Scope.class;
```

```java
@Override
public ScopeMetadata resolveScopeMetadata(BeanDefinition definition) {
    ScopeMetadata metadata = new ScopeMetadata();
    if (definition instanceof AnnotatedBeanDefinition) {
        AnnotatedBeanDefinition annDef = (AnnotatedBeanDefinition) definition;
        AnnotationAttributes attributes = AnnotationConfigUtils.attributesFor(
                annDef.getMetadata(), this.scopeAnnotationType);
        if (attributes != null) {
            metadata.setScopeName(attributes.getString("value"));
            ScopedProxyMode proxyMode = attributes.getEnum("proxyMode");
            if (proxyMode == ScopedProxyMode.DEFAULT) {
                proxyMode = this.defaultProxyMode;
            }
            metadata.setScopedProxyMode(proxyMode);
        }
    }
    return metadata;
}
```

为了观察 Spring 如何处理 SingletonBean 的 Scope 注解，我们可以在这里加一个断点调试，Condition 是 `Objects.equals("yano.spring.bean.SingletonBean", annDef.getBeanClassName())`。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513181555.png?x-oss-process=style/yano)

接着一步步断点向上调试，最终会调用到 org.springframework.context.annotation.ClassPathBeanDefinitionScanner#doScan。具体代码就不分析了，只要理解 Spring 框架，就能看懂源码。

```java
protected Set<BeanDefinitionHolder> doScan(String... basePackages) {
    Assert.notEmpty(basePackages, "At least one base package must be specified");
    Set<BeanDefinitionHolder> beanDefinitions = new LinkedHashSet<>();
    for (String basePackage : basePackages) {
        Set<BeanDefinition> candidates = findCandidateComponents(basePackage);
        for (BeanDefinition candidate : candidates) {
            ScopeMetadata scopeMetadata = this.scopeMetadataResolver.resolveScopeMetadata(candidate);
            candidate.setScope(scopeMetadata.getScopeName());
            String beanName = this.beanNameGenerator.generateBeanName(candidate, this.registry);
            if (candidate instanceof AbstractBeanDefinition) {
                postProcessBeanDefinition((AbstractBeanDefinition) candidate, beanName);
            }
            if (candidate instanceof AnnotatedBeanDefinition) {
                AnnotationConfigUtils.processCommonDefinitionAnnotations((AnnotatedBeanDefinition) candidate);
            }
            if (checkCandidate(beanName, candidate)) {
                BeanDefinitionHolder definitionHolder = new BeanDefinitionHolder(candidate, beanName);
                definitionHolder =
                        AnnotationConfigUtils.applyScopedProxyMode(scopeMetadata, definitionHolder, this.registry);
                beanDefinitions.add(definitionHolder);
                registerBeanDefinition(definitionHolder, this.registry);
            }
        }
    }
    return beanDefinitions;
}
```

关于 Spring IoC 容器的详细分析，见 [最简 Spring IOC 容器源码分析](https://github.com/LjyYano/Thinking_in_Java_MindMapping/blob/master/2019-09-24%20%E6%9C%80%E7%AE%80%20Spring%20IOC%20%E5%AE%B9%E5%99%A8%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90.md)

# 生命周期

首先通过一个测试用例，了解 Spring Bean 的生命周期。下面定义了一个 LifeBean：

```java
@Component
@Data
@Slf4j
public class LifeBean implements BeanNameAware, BeanClassLoaderAware, InitializingBean, DisposableBean {
    private int i;

    @PostConstruct
    public void init() {
        log.info("LifeBean init ...");
    }

    @Override
    public void setBeanName(String s) {
        log.info("LifeBean setBeanName {}", s);
    }

    @Override
    public void setBeanClassLoader(ClassLoader classLoader) {
        log.info("LifeBean setBeanClassLoader {}", classLoader);
    }

    @Override
    public void afterPropertiesSet() {
        log.info("LifeBean afterPropertiesSet i = {}", i);
    }

    @Override
    public void destroy() {
        log.info("LifeBean destroy ...");
    }
}
```

单元测试代码：

```java
@Test
public void testLife() {
    LifeBean bean = context.getBean(LifeBean.class);
    bean.setI(1);
}
```

log 输出：

```
LifeBean setBeanName lifeBean
LifeBean setBeanClassLoader jdk.internal.loader.ClassLoaders$AppClassLoader@55f96302
LifeBean init ...
LifeBean afterPropertiesSet i = 0
LifeBean destroy ...
```

## BeanFactory

BeanFactory 接口文件上的注释如下。里面包含了 bean 的生命周期以及对应的顺序。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513182455.png?x-oss-process=style/yano)

[Spring 官方文档：Customizing the Nature of a Bean](https://docs.spring.io/spring-framework/docs/current/reference/html/core.html#beans-factory-nature)

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210513183117.png?x-oss-process=style/yano)


# 循环依赖

> 💡 Spring Boot 在 2.6.0 版本开始默认不允许出现循环引用，出现循环引用肯定是程序的问题。
>
> 如果需要允许循环引用，需要在配置文件中添加 `spring.main.allow-circular-references=true`。

` 循环依赖 ` 就是循环引用，两个或多个 bean 相互之间持有对方。那么 Spring 是如何解决循环依赖的？

## 循环依赖的 3 种类型

在 Spring 中循环依赖一共有 3 种情况：

- 构造器循环依赖：无法解决
- setter/field 循环依赖：` 只能解决单例作用域的 bean 循环依赖 `
- prototype 范围的依赖处理：无法解决

### 构造器循环依赖

构造器循环依赖是无法解决的，因为一个 bean 创建时首先要经过构造器，但是构造器相互依赖，就相当于 Java 中多线程死锁。

```java
@Service
public class CircleBean1 {

    private CircleBean2 circleBean2;

    public CircleBean1(CircleBean2 circleBean2) {
        this.circleBean2 = circleBean2;
    }
}
```

```java
@Service
public class CircleBean2 {

    private CircleBean1 circleBean1;

    public CircleBean2(CircleBean1 circleBean1) {
        this.circleBean1 = circleBean1;
    }
}
```

启动后会报下面的错误：

```java
The dependencies of some of the beans in the application context form a cycle:

┌─────┐
|  circleBean1
↑     ↓
|  circleBean2
└─────┘
```

### setter/field 循环依赖

setter 注入循环依赖：

```java
@Service
public class CircleBean1 {

    private CircleBean2 circleBean2;

    public CircleBean2 getCircleBean2() {
        return circleBean2;
    }

    @Autowired
    public void setCircleBean2(CircleBean2 circleBean2) {
        this.circleBean2 = circleBean2;
    }
}
```

```java
@Service
public class CircleBean2 {

    private CircleBean1 circleBean1;

    public CircleBean1 getCircleBean1() {
        return circleBean1;
    }

    @Autowired
    public void setCircleBean1(CircleBean1 circleBean1) {
        this.circleBean1 = circleBean1;
    }
}
```

field 注入循环依赖：

```java
@Service
public class CircleBean1 {

    @Autowired
    private CircleBean2 circleBean2;

}
```

```java
@Service
public class CircleBean2 {

    @Autowired
    private CircleBean1 circleBean1;

}
```

能够正常启动。

### prototype 范围的依赖处理

通过 `@Scope(scopeName = SCOPE_PROTOTYPE)` 注解，可以将 bean 的作用域设置为 prototype，每次注入都会新建一个对象，Spring IoC 容器并不会缓存 prototype 的 bean。

```java
@Service
@Scope(scopeName = SCOPE_PROTOTYPE)
public class CircleBean1 {

    @Autowired
    private CircleBean2 circleBean2;

}
```

```java
@Service
@Scope(scopeName = SCOPE_PROTOTYPE)
public class CircleBean2 {

    @Autowired
    private CircleBean1 circleBean1;

}
```

启动后会报下面的错误：

```java
The dependencies of some of the beans in the application context form a cycle:

┌─────┐
|  circleBean1
↑     ↓
|  circleBean2
└─────┘
```

## Spring 如何解决循环依赖？

### 三级缓存

参考链接：[浅谈 Spring 如何解决 Bean 的循环依赖问题](https://juejin.cn/post/7218080360403615804#heading-6)

```java
// 一级缓存：缓存的是已经实例化、属性注入、初始化后的 Bean 对象。
/** Cache of singleton objects: bean name to bean instance. */
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);

// 二级缓存：缓存的是实例化后，但未属性注入、初始化的 Bean 对象（用于提前暴露 Bean）。
/** Cache of early singleton objects: bean name to bean instance. */
private final Map<String, Object> earlySingletonObjects = new ConcurrentHashMap<>(16);

// 三级缓存：缓存的是一个 ObjectFactory，主要作用是生成原始对象进行 AOP 操作后的代理对象
/** Cache of singleton factories: bean name to ObjectFactory. */
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);

```

### 源码分析

> 并没有深入分析，待后面补充

setter 注入造成的依赖是通过 Spring 容器提前暴露刚完成构造器注入但未完成其他步骤（如 setter 注入）的 bean 来完成的，而且只能解决单例作用域的 bean 循环依赖。通过提前暴露一个单例工厂方法，从而使其他 bean 能引用到该 bean，org.springframework.beans.factory.support.DefaultSingletonBeanRegistry#getSingleton(java.lang.String, boolean) 代码如下：

```java
/**
    * Return the (raw) singleton object registered under the given name.
    * <p>Checks already instantiated singletons and also allows for an early
    * reference to a currently created singleton (resolving a circular reference).
    * @param beanName the name of the bean to look for
    * @param allowEarlyReference whether early references should be created or not
    * @return the registered singleton object, or {@code null} if none found
    */
@Nullable
protected Object getSingleton(String beanName, boolean allowEarlyReference) {
    // Quick check for existing instance without full singleton lock
    Object singletonObject = this.singletonObjects.get(beanName);
    if (singletonObject == null && isSingletonCurrentlyInCreation(beanName)) {
        singletonObject = this.earlySingletonObjects.get(beanName);
        if (singletonObject == null && allowEarlyReference) {
            synchronized (this.singletonObjects) {
                // Consistent creation of early reference within full singleton lock
                singletonObject = this.singletonObjects.get(beanName);
                if (singletonObject == null) {
                    singletonObject = this.earlySingletonObjects.get(beanName);
                    if (singletonObject == null) {
                        ObjectFactory<?> singletonFactory = this.singletonFactories.get(beanName);
                        if (singletonFactory != null) {
                            singletonObject = singletonFactory.getObject();
                            this.earlySingletonObjects.put(beanName, singletonObject);
                            this.singletonFactories.remove(beanName);
                        }
                    }
                }
            }
        }
    }
    return singletonObject;
}
```

## Spring Boot 2.6.0 开启循环依赖

> 💡 并不建议这样做，程序最好就没有循环依赖。

项目启动的时候添加参数 `spring.main.allow-circular-references=true`，或者在代码中添加：

```java
new SpringApplicationBuilder(Application.class).allowCircularReferences(true).run(args);
```

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想 - 最全思维导图 - GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！