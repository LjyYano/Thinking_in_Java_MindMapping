
# 前言

最近在研究 Spring 源码，Spring 最核心的功能就是 `IOC 容器`和 `AOP`。本文定位是以最简的方式，分析 Spring AOP 源码。

# 基本概念

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-09-23-000553.png)

上面的思维导图能够概括了 Spring AOP，其最重要的是 Spring AOP `只能作用于 Bean`，而 AspectJ 能够在编译期、类加载期对字节码进行更改。

# 猜测实现原理

Spring AOP 的实现原理是`动态代理`，但是具体又是怎么实现的呢？

在 Spring 容器中，我们使用的每个 bean 都是 BeanDefinition 的实例，容器会在合适的时机根据 BeanDefinition 的基本信息实例化 bean 对象。

所以比较简单的做法是，Spring 会自动生成代理对象的代理类。我们在获取 bean 时，Spring 容器返回代理类对象，而不是实际的 bean。

# 调试代码

本文使用的代码，安装了 `lombok`，并基于 `Spring Boot`，是一个完全基于注解的最简调试代码。

注解配置类 AopConfig：

```java
@Slf4j
@Component
@Aspect
public class AopConfig {

    @Pointcut("within(com.life.demo..*)")
    public void pointCut() {
    }

    @Before("com.life.demo.AopConfig.pointCut()")
    public void log() {
        log.info("this is point cut...");
    }
}
```

Spring 启动类 AppApplication：

```java
@SpringBootApplication
@EnableAspectJAutoProxy
public class AppApplication {

    public static void main(String[] args) {
        SpringApplication.run(AppApplication.class, args);
    }
}
```

Controller HelloWorldController：

```java
package com.life.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.extern.slf4j.Slf4j;

@RestController
@Slf4j
public class HelloWorldController {

    @GetMapping("/hello")
    public String greeting() {
        return "hello!";
    }
}
```

运行 Web 应用，在浏览器输入网址 http://localhost:11111/hello，会看到 log：

```
INFO 96257 --- [io-11111-exec-1] com.life.demo.AopConfig                  : this is point cut...
```

验证出成功配置了代理。

# 使用说明

1. @EnableAspectJAutoProxy 开启 AOP。
2. 使用 @Aspect 注解的 bean 都会被 Spring 当做用来实现 AOP 的配置类。
3. 配置 Advice，不做详细介绍，具体参考 [Spring AOP 官方文档](https://docs.spring.io/spring/docs/2.0.x/reference/aop.html)。
3. @Pointcut，用来匹配 Spring 容器中的所有 bean 的方法的。

```java
@Pointcut("execution(* transfer(..))")// the pointcut expression
private void anyOldTransfer() {}// the pointcut signature
```

@Pointcut 中使用了 execution 来正则匹配方法签名，这也是最常用的，除了 execution，我们再看看其他的几个比较常用的匹配方式：

- within：指定所在类或所在包下面的方法（Spring AOP 独有）
`如 @Pointcut("within(com.javadoop.springaoplearning.service..*)")`

- @annotation：方法上具有特定的注解，如 @Subscribe 用于订阅特定的事件。
`如 @Pointcut("execution(* .(..)) && @annotation(com.javadoop.annotation.Subscribe)")`

- bean(idOrNameOfBean)：匹配 bean 的名字（Spring AOP 独有）
`如 @Pointcut("bean(*Service)")`

Tips：上面匹配中，通常 "." 代表一个包名，".." 代表包及其子包，方法参数任意匹配使用两个点 ".."。

# 源码深入分析

## @EnableAspectJAutoProxy 开启 AOP

@EnableAspectJAutoProxy 注解定义：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Import(AspectJAutoProxyRegistrar.class)
public @interface EnableAspectJAutoProxy {
	boolean proxyTargetClass() default false;
	boolean exposeProxy() default false;
}
```

```java
class AspectJAutoProxyRegistrar implements ImportBeanDefinitionRegistrar {

	@Override
	public void registerBeanDefinitions(
			AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry) {

		AopConfigUtils.registerAspectJAnnotationAutoProxyCreatorIfNecessary(registry);

		AnnotationAttributes enableAspectJAutoProxy =
				AnnotationConfigUtils.attributesFor(importingClassMetadata, EnableAspectJAutoProxy.class);
		if (enableAspectJAutoProxy != null) {
			if (enableAspectJAutoProxy.getBoolean("proxyTargetClass")) {
				AopConfigUtils.forceAutoProxyCreatorToUseClassProxying(registry);
			}
			if (enableAspectJAutoProxy.getBoolean("exposeProxy")) {
				AopConfigUtils.forceAutoProxyCreatorToExposeProxy(registry);
			}
		}
	}

}
```

在 AppApplication 启动类上要加入 `@EnableAspectJAutoProxy` 注解开启 AOP，查看该注解源码，其 proxyTargetClass() 是在 AspectJAutoProxyRegistrar 类中调用，而 AspectJAutoProxyRegistrar 是一个 ImportBeanDefinitionRegistrar。再往上追根溯源，可以看到是在接口 ConfigurableApplicationContext 中 void refresh() 调用。

## IOC 容器管理 AOP 实例

在创建 bean 时，会调用 AbstractAutowireCapableBeanFactory#doCreateBean(...)。

```java
protected Object doCreateBean(final String beanName, final RootBeanDefinition mbd, final Object[] args)
            throws BeanCreationException {

    // 初始化 bean
    BeanWrapper instanceWrapper = null;
    if (mbd.isSingleton()) {
        instanceWrapper = this.factoryBeanInstanceCache.remove(beanName);
    }
    if (instanceWrapper == null) {
        // 1. 创建实例
        instanceWrapper = createBeanInstance(beanName, mbd, args);
    }
    ...

    // Initialize the bean instance.
    Object exposedObject = bean;
    try {
        // 2. 装载属性
        populateBean(beanName, mbd, instanceWrapper);
        if (exposedObject != null) {
            // 3. 初始化
            exposedObject = initializeBean(beanName, exposedObject, mbd);
        }
    }
    ...
}
```

着重看第3步 initializeBean(...) 方法：

```java
protected Object initializeBean(final String beanName, final Object bean, @Nullable RootBeanDefinition mbd) {
	if (System.getSecurityManager() != null) {
		AccessController.doPrivileged((PrivilegedAction<Object>) () -> {
			invokeAwareMethods(beanName, bean);
			return null;
		}, getAccessControlContext());
	}
	else {
		invokeAwareMethods(beanName, bean);
	}

	Object wrappedBean = bean;
	if (mbd == null || !mbd.isSynthetic()) {
		wrappedBean = applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
	}

	try {
		invokeInitMethods(beanName, wrappedBean, mbd);
	}
	catch (Throwable ex) {
		throw new BeanCreationException(
				(mbd != null ? mbd.getResourceDescription() : null),
				beanName, "Invocation of init method failed", ex);
	}
	if (mbd == null || !mbd.isSynthetic()) {
		// 执行每个 BeanPostProcessor 的 postProcessAfterInitialization 方法！
		wrappedBean = applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
	}

	return wrappedBean;
}
```

Spring IOC 容器创建 bean 实例时，最后都会对 bean 进行处理，来实现增强。对于 Spring AOP 来说，就是创建代理类。

上面代码中函数 applyBeanPostProcessorsAfterInitialization(...) 最终调用了 AbstractAutoProxyCreator 实现的 postProcessAfterInitialization() 方法。

```java
/**
 * Create a proxy with the configured interceptors if the bean is
 * identified as one to proxy by the subclass.
 * @see #getAdvicesAndAdvisorsForBean
 */
@Override
public Object postProcessAfterInitialization(@Nullable Object bean, String beanName) {
	if (bean != null) {
		Object cacheKey = getCacheKey(bean.getClass(), beanName);
		if (this.earlyProxyReferences.remove(cacheKey) != bean) {
			return wrapIfNecessary(bean, beanName, cacheKey);
		}
	}
	return bean;
}
```

`wrapIfNecessary(...)`方法在需要时返回了代理类。

```java
protected Object wrapIfNecessary(Object bean, String beanName, Object cacheKey) {
	if (StringUtils.hasLength(beanName) && this.targetSourcedBeans.contains(beanName)) {
		return bean;
	}
	if (Boolean.FALSE.equals(this.advisedBeans.get(cacheKey))) {
		return bean;
	}
	if (isInfrastructureClass(bean.getClass()) || shouldSkip(bean.getClass(), beanName)) {
		this.advisedBeans.put(cacheKey, Boolean.FALSE);
		return bean;
	}

	// 1. Create proxy if we have advice.
	Object[] specificInterceptors = getAdvicesAndAdvisorsForBean(bean.getClass(), beanName, null);
	if (specificInterceptors != DO_NOT_PROXY) {
		this.advisedBeans.put(cacheKey, Boolean.TRUE);
		// 2. 核心！重点！重要！
		Object proxy = createProxy(
				bean.getClass(), beanName, specificInterceptors, new SingletonTargetSource(bean));
		this.proxyTypes.put(cacheKey, proxy.getClass());
		return proxy;
	}

	this.advisedBeans.put(cacheKey, Boolean.FALSE);
	return bean;
}
```

上述代码第 1 步 getAdvicesAndAdvisorsForBean(...) 方法是返回某个 beanName 下的 Advice 和 Advisor，如果返回结果不为空的话，才会创建代理。其核心方法就是 createProxy(...)。

```java
protected Object createProxy(Class<?> beanClass, @Nullable String beanName,
		@Nullable Object[] specificInterceptors, TargetSource targetSource) {

	if (this.beanFactory instanceof ConfigurableListableBeanFactory) {
		AutoProxyUtils.exposeTargetClass((ConfigurableListableBeanFactory) this.beanFactory, beanName, beanClass);
	}

	// 1. 获取合适的 ProxyFactory
	ProxyFactory proxyFactory = new ProxyFactory();
	proxyFactory.copyFrom(this);

	if (!proxyFactory.isProxyTargetClass()) {
		if (shouldProxyTargetClass(beanClass, beanName)) {
			proxyFactory.setProxyTargetClass(true);
		}
		else {
			evaluateProxyInterfaces(beanClass, proxyFactory);
		}
	}

	Advisor[] advisors = buildAdvisors(beanName, specificInterceptors);
	proxyFactory.addAdvisors(advisors);
	proxyFactory.setTargetSource(targetSource);
	customizeProxyFactory(proxyFactory);

	proxyFactory.setFrozen(this.freezeProxy);
	if (advisorsPreFiltered()) {
		proxyFactory.setPreFiltered(true);
	}

	// 2. 创建并返回合适的 AOP 对象
	return proxyFactory.getProxy(getProxyClassLoader());
}
```

## ProxyFactory

```java
@Override
public AopProxy createAopProxy(AdvisedSupport config) throws AopConfigException {
	if (config.isOptimize() || config.isProxyTargetClass() || hasNoUserSuppliedProxyInterfaces(config)) {
		Class<?> targetClass = config.getTargetClass();
		if (targetClass == null) {
			throw new AopConfigException("TargetSource cannot determine target class: " +
					"Either an interface or a target is required for proxy creation.");
		}
		if (targetClass.isInterface() || Proxy.isProxyClass(targetClass)) {
			return new JdkDynamicAopProxy(config);
		}
		return new ObjenesisCglibAopProxy(config);
	}
	else {
		return new JdkDynamicAopProxy(config);
	}
}
```

查看代码最终发现是在 DefaultAopProxyFactory#createAopProxy(...) 方法中实现。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-09-23-011625.png)

AopProxy 接口的 2 个实现类：CglibAopProxy 和 JdkDynamicAopProxy。这里就不分析 JdkDynamicAopProxy 类，仅分析 CglibAopProxy 类。CglibAopProxy 类实现的 getProxy(...) 方法如下：

```java
@Override
public Object getProxy(@Nullable ClassLoader classLoader) {
	if (logger.isTraceEnabled()) {
		logger.trace("Creating CGLIB proxy: " + this.advised.getTargetSource());
	}

	try {
		Class<?> rootClass = this.advised.getTargetClass();
		Assert.state(rootClass != null, "Target class must be available for creating a CGLIB proxy");

		Class<?> proxySuperClass = rootClass;
		if (ClassUtils.isCglibProxyClass(rootClass)) {
			proxySuperClass = rootClass.getSuperclass();
			Class<?>[] additionalInterfaces = rootClass.getInterfaces();
			for (Class<?> additionalInterface : additionalInterfaces) {
				this.advised.addInterface(additionalInterface);
			}
		}

		// Validate the class, writing log messages as necessary.
		validateClassIfNecessary(proxySuperClass, classLoader);

		// Configure CGLIB Enhancer...
		Enhancer enhancer = createEnhancer();
		if (classLoader != null) {
			enhancer.setClassLoader(classLoader);
			if (classLoader instanceof SmartClassLoader &&
					((SmartClassLoader) classLoader).isClassReloadable(proxySuperClass)) {
				enhancer.setUseCache(false);
			}
		}
		enhancer.setSuperclass(proxySuperClass);
		enhancer.setInterfaces(AopProxyUtils.completeProxiedInterfaces(this.advised));
		enhancer.setNamingPolicy(SpringNamingPolicy.INSTANCE);
		enhancer.setStrategy(new ClassLoaderAwareUndeclaredThrowableStrategy(classLoader));

		Callback[] callbacks = getCallbacks(rootClass);
		Class<?>[] types = new Class<?>[callbacks.length];
		for (int x = 0; x < types.length; x++) {
			types[x] = callbacks[x].getClass();
		}
		// fixedInterceptorMap only populated at this point, after getCallbacks call above
		enhancer.setCallbackFilter(new ProxyCallbackFilter(
				this.advised.getConfigurationOnlyCopy(), this.fixedInterceptorMap, this.fixedInterceptorOffset));
		enhancer.setCallbackTypes(types);

		// Generate the proxy class and create a proxy instance.
		return createProxyClassAndInstance(enhancer, callbacks);
	}
	catch (CodeGenerationException | IllegalArgumentException ex) {
		throw new AopConfigException("Could not generate CGLIB subclass of " + this.advised.getTargetClass() +
				": Common causes of this problem include using a final class or a non-visible class",
				ex);
	}
	catch (Throwable ex) {
		// TargetSource.getTarget() failed
		throw new AopConfigException("Unexpected AOP exception", ex);
	}
}
```

CGLIB 生成代理的核心是 `Enhancer`，详情见[Enhancer API 文档](https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/cglib/proxy/Enhancer.html)、[cglib 官网](https://github.com/cglib/cglib)。

# 总结

Spring AOP 使用了动态代理，作用于 IOC 容器管理的 bean。在获取 bean 时会根据需要创建代理类，并返回代理类。在 Spring Boot 中使用 Spring AOP 时应该先用 @EnableAspectJAutoProxy 注解开启代理，定义代理类和代理规则，不需要 XML 或其他配置。

Spring 的源码太庞杂，调用链太深，`在研究源码的时候应该明确目标，掌握核心原理`。就像学汉语字典，并不需要掌握其中的每一个汉字（况且 Spring 源码更新频率很快）。

# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，希望大家关注^_^

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

