
- [Microprofile Fault Tolerance](#microprofile-fault-tolerance)
- [Resilience4J](#resilience4j)
- [Failsafe](#failsafe)
- [Conclusion](#conclusion)
- [To go further:](#to-go-further)

文章原文链接：https://blog.frankel.ch/comparison-fault-tolerance-libraries/

If you’re implementing microservices or not, the chances are that you’re calling HTTP endpoints. With HTTP calls, a lot of things can go wrong. Experienced developers plan for this and design beyond just the happy path. In general, fault tolerance encompasses the following features:

- Retry
- Timeout
- Circuit Breaker
- Fallback
- Rate Limiter to avoid server-side 429 responses
- Bulkhead: Rate Limiter limits the number of calls in a determined timeframe, while Bulkhead limits the number of concurrent calls

A couple of libraries implement these features on the JVM. In this post, we will look at Microprofile Fault Tolerance, [Failsafe](https://failsafe.dev/) and Resilience4J.

## Microprofile Fault Tolerance

[Microprofile Fault Tolerance](https://download.eclipse.org/microprofile/microprofile-fault-tolerance-1.1.2/microprofile-fault-tolerance-spec.html) comes from the Microprofile umbrella project. It differs from the two others because it’s a _specification_, which relies on a runtime to provide its capabilities. For example, Open Liberty is one such runtime. [SmallRye Fault Tolerance](https://smallrye.io/docs/smallrye-fault-tolerance/5.2.1/index.html) is another one. In turn, other components such as Quarkus and WildFly embed SmallRye.

Microprofile defines _annotations_ for each feature: `@Timeout`, `@Retry Policy`, `@Fallback`, `@Circuit Breaker`, and `@Bulkhead`. It also defines `@Asynchronous`.

Because the runtime reads annotations, one should carefully read the documentation to understand how they interact if more than one is set.

> A `@Fallback` can be specified and it will be invoked if the `TimeoutException` is thrown. If `@Timeout` is used together with `@Retry`, the `TimoutException` will trigger the retry. When `@Timeout` is used with `@CircuitBreaker` and if a `TimeoutException` occurs, the failure will contribute towards the circuit open.

— [Timeout Usage](https://download.eclipse.org/microprofile/microprofile-fault-tolerance-1.1.2/microprofile-fault-tolerance-spec.html#_timeout_usage)

## Resilience4J

I came upon [Resilience4J](https://resilience4j.readme.io/docs) when I was running my talk on the Circuit Breaker pattern. The talk included a demo, and it relied on [Hystrix](https://github.com/Netflix/Hystrix). One day, I wanted to update the demo to the latest Hystrix version and noticed that maintainers had deprecated it in favor of Resilience4J.

Resilience4J is based on several core concepts:

- One JAR per fault tolerance feature, with additional JARs for specific integrations, _e.g._, Kotlin
- Static factories
- Function composition via the _Decorator pattern_ applied to functions
- Integration with Java’s functional interfaces, _e.g._, `Runnable`, `Callable`, `Function`, etc.
- Exception propagation: one can use a functional interface that throws, and the library will propagate it across the call pipeline

Here’s a simplified class diagram for `Retry`.

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220116090708.png?x-oss-process=style/yano)

Each fault tolerance feature is built around the same template seen above. One can create a pipeline of several features by leveraging function composition, each one calling another one.

Let’s analyze a sample:

```
var retrySupplier = Retry.decorateSupplier(                                  (1)
    Retry.ofDefaults("retry"),                                               (2)
    () -> server.call()                                                      (1)
);
var config = new CircuitBreakerConfig.Builder()                                (3)
        .slowCallDurationThreshold(Duration.ofMillis(200))                   (4)
        .slidingWindowSize(2)                                                (5)
        .minimumNumberOfCalls(2)                                             (6)
        .build();
var breakerSupplier = CircuitBreaker.of("circuit-breaker", config)            (7)
                                    .decorateSupplier(retrySupplier);        (7)
supplier = SupplierUtils.recover(                                            (8)
    breakerSupplier,
    List.of(IllegalStateException.class, CallNotPermittedException.class),   (9)
    e -> "fallback"                                                          (10)
);
```

1. Decorate the base `server.call()` function with `Retry`: this function is the one to be protected
2. Use the default configuration
3. Create a new _Circuit Breaker_ config
4. Set the threshold above which a call is considered to be slow
5. Count over a sliding window of 2 calls
6. Minimum number of calls to decide whether to open the _Circuit Breaker_
7. Decorate the retry function with a _Circuit Breaker_ with the above config
8. Create a fallback value to return when the _Circuit Breaker_ is open
9. List of exceptions to handle: they won’t be propagated. Resilience4J throws a `CallNotPermittedException` when the circuit is open.
10. In case any of the configured exceptions are thrown, call this function instead

The order in which functions are composed can be hard to decipher. Hence, the project offers the `Decorators` class to combine functions using a fluent API. You can find it in the `resilience4j-all` module. One can rewrite the above code as:

```
var pipeline = Decorators.ofSupplier(() -> server.call())
    .withRetry(Retry.ofDefaults("retry"))
    .withCircuitBreaker(CircuitBreaker.of("circuit-breaker", config))
    .withFallback(
        List.of(IllegalStateException.class, CallNotPermittedException.class),
        e -> "fallback"
    );
```

It makes the intent much clearer.

## Failsafe

I stumbled upon Failsafe not long ago. Its tenets are similar to Resilience4J: static factories, function composition, and exception propagation.

While Resilience4J fault tolerance feature don’t share a class hierarchy, Failsafe provides the concept of `Policy`:

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220116090832.png)

I believe the main difference with Resilience4J lies in its pipelining approach. Resilience4J’s API requires you first to provide the "base" function and then embed it inside any wrapper function. You cannot reuse the pipeline on top of different base functions. Failsafe allows it via the `FailsafeExecutor` class.

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20220116091010.png)

Here’s how to create a pipeline, _i.e._, an instance of `FailsafeExecutor`. Notice there’s no reference to the base call:

```
var pipeline = Failsafe.with(                            (1)
    Fallback.of("fallback"),                             (2)
    Timeout.ofDuration(Duration.of(2000, MILLIS)),       (3)
    RetryPolicy.ofDefault()                              (4)
);
```

1. Define the list of policies applied from the last to the first in order
2. Fallback value
3. If the call exceeds 2000ms, throws a \` TimeoutExceededException\`
4. Default retry policy

At this point, it’s possible to wrap the call:

```
pipeline.get(() -> server.call());
```

Failsafe also provides a fluent API. One can rewrite the above code as:

```
var pipeline = Failsafe.with(Fallback.of("fallback"))
    .compose(RetryPolicy.ofDefault())
    .compose(Timeout.ofDuration(Duration.of(2000, MILLIS)));
```

## Conclusion

All three libraries provide more or less the same features. If you don’t use a CDI-compliant runtime such like regular application server or Quarkus, forget about Microprofile Fault Tolerance.

Failsafe and Resilience4J are both based on function composition and are pretty similar. If you need to define your function pipeline independently of the base call, prefer Failsafe. Otherwise, pick any of them.

As I’m more familiar with Resilience4J, I’ll probably use Failsafe in my next project to get more experience with it.

## To go further:

- [Microprofile Fault Tolerance specification](https://download.eclipse.org/microprofile/microprofile-fault-tolerance-1.1.2/microprofile-fault-tolerance-spec.html)
- [SmallRye Fault Tolerance Documentation](https://smallrye.io/docs/smallrye-fault-tolerance/5.0.0/index.html)
- [Introduction to Resilience4J](https://resilience4j.readme.io/docs)
- [Failsafe overview](https://failsafe.dev/)