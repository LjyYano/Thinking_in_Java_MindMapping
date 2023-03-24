---
date: 2022-11-30
---

- [RocketMQ 官网](#rocketmq-官网)
  - [安装](#安装)
  - [启动NameServer](#启动nameserver)
  - [启动 Broker 和 Proxy](#启动-broker-和-proxy)
  - [发送、接收消息](#发送接收消息)
- [通过 Java SDK 发送、接收消息](#通过-java-sdk-发送接收消息)


# RocketMQ 官网

RocketMQ 5.0：云原生“消息、事件、流”实时数据处理平台，覆盖云边端一体化数据处理场景。本系列文章会介绍 RocketMQ 的使用流程，并重点分析设计理念、架构及源码。

- [RocketMQ 官网](https://rocketmq.apache.org/)
- [Rocket 5.0 速览](https://rocketmq.apache.org/zh/version)
- [Github apache/rocketmq](https://github.com/apache/rocketmq)

## 安装

首先从官网下载最新源码包，然后本地编译。

```
$ unzip rocketmq-all-5.0.0-source-release.zip
$ cd rocketmq-all-5.0.0-source-release/
$ mvn -Prelease-all -DskipTests clean install -U
$ cd distribution/target/rocketmq-5.0.0/rocketmq-5.0.0
```

## 启动NameServer

```
### start namesrv
$ nohup sh bin/mqnamesrv &
 
### verify namesrv 
$ tail -f ~/logs/rocketmqlogs/namesrv.log
The Name Server boot success...
```

能看到启动日志如下：

```
2022-12-04 15:07:18 INFO main - name server address updated. NEW : [192.168.100.5:9876] , OLD: null
2022-12-04 15:07:18 INFO main - Try to start service thread:FileWatchService started:false lastThread:null
2022-12-04 15:07:18 INFO main - Try to start service thread:org.apache.rocketmq.namesrv.routeinfo.BatchUnregistrationService started:false lastThread:null
2022-12-04 15:07:18 INFO FileWatchService - FileWatchService service started
2022-12-04 15:07:18 INFO main - The Name Server boot success. serializeType=JSON
2022-12-04 15:07:18 INFO NettyClientScan_thread_1 - createChannel: begin to connect remote host[192.168.100.5:9876] asynchronously
```

## 启动 Broker 和 Proxy

```
### start broker
$ nohup sh bin/mqbroker -n localhost:9876 --enable-proxy &

### verify broker
$ tail -f ~/logs/rocketmqlogs/broker_default.log 
The broker[broker-a,192.169.1.2:10911] boot success...
```

## 发送、接收消息

```
$ export NAMESRV_ADDR=localhost:9876
$ sh bin/tools.sh org.apache.rocketmq.example.quickstart.Producer
```

命令行会输出：

```
SendResult [sendStatus=SEND_OK, msgId=7F00000122EF5B37E0D212B514EC03E5, offsetMsgId=C0A8640500002A9F000000000003AA27, messageQueue=MessageQueue [topic=TopicTest, brokerName=broker-a, queueId=3], queueOffset=249]
```

启动一个 Consumer 消费（）：

```
ConsumeMessageThread_please_rename_unique_group_name_4_10 Receive New Messages: [MessageExt [brokerName=broker-a, queueId=3, storeSize=241, queueOffset=249, sysFlag=0, bornTimestamp=1670137857260, bornHost=/192.168.100.5:52993, storeTimestamp=1670137857261, storeHost=/192.168.100.5:10911, msgId=C0A8640500002A9F000000000003AA27, commitLogOffset=240167, bodyCRC=1102156316, reconsumeTimes=0, preparedTransactionOffset=0, toString()=Message{topic='TopicTest', flag=0, properties={MIN_OFFSET=0, TRACE_ON=true, MAX_OFFSET=250, MSG_REGION=DefaultRegion, CONSUME_START_TIME=1670137898415, UNIQ_KEY=7F00000122EF5B37E0D212B514EC03E5, CLUSTER=DefaultCluster, WAIT=true, TAGS=TagA}, body=[72, 101, 108, 108, 111, 32, 82, 111, 99, 107, 101, 116, 77, 81, 32, 57, 57, 55], transactionId='null'}]] 
```

# 通过 Java SDK 发送、接收消息

1. 在 pom 文件中引入对应 jar 包：

```xml
<dependency>
    <groupId>org.apache.rocketmq</groupId>
    <artifactId>rocketmq-client-java</artifactId>
    <version>5.0.0</version>
</dependency> 
```

2. 通过命令行工具创建一个 topic，Topic 名字是 YanoTestTopic

```
sh bin/mqadmin updatetopic -n localhost:9876 -b localhost:10911  -t YanoTestTopic
```

3. 编写发送程序，指定 tag 是 tag1，发送的 messageBody 是随机数。

```java
String endpoint = "localhost:8081";
String topic = "YanoTestTopic";

@Test
public void send() throws Exception {
    ClientServiceProvider provider = ClientServiceProvider.loadService();
    ClientConfiguration configuration = ClientConfiguration.newBuilder().setEndpoints(endpoint).build();
    Producer producer = provider.newProducerBuilder()
            .setTopics(topic)
            .setClientConfiguration(configuration)
            .build();
    Message message = provider.newMessageBuilder()
            .setTopic(topic)
            .setKeys(UUID.randomUUID().toString())
            .setTag("tag1")
            .setBody(UUID.randomUUID().toString().getBytes())
            .build();

    // 发送消息
    SendReceipt sendReceipt = producer.send(message);

    log.info("send message {}, body {}", message, transfer(message.getBody()));
    log.info("messageId {}", sendReceipt.getMessageId());
}
```

4. 监听消息，将消息体打印出来

```java
@Test
public void push() throws Exception {
    // 初始化 PushConsumer，需要绑定消费者分组ConsumerGroup、通信参数以及订阅关系
    ClientServiceProvider.loadService().newPushConsumerBuilder()
            // 接入点地址，需要设置成Proxy的地址和端口列表，一般是xxx:8081;xxx:8081
            .setClientConfiguration(ClientConfiguration.newBuilder().setEndpoints(endpoint).build())
            // 设置消费者分组
            .setConsumerGroup("yano")
            // 订阅消息的过滤规则， * 表示订阅所有Tag的消息
            .setSubscriptionExpressions(Collections.singletonMap(topic, new FilterExpression("*", FilterExpressionType.TAG)))
            // 设置消费监听器
            .setMessageListener(messageView -> {
                // 处理消息并返回消费结果
                log.info("Consume message={}, body {}", messageView, transfer(messageView.getBody()));
                return ConsumeResult.SUCCESS;
            }).build();
    Thread.sleep(Long.MAX_VALUE);
}
```

完整代码：

```java
package com.example.rocketmqlearn;

import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.client.apis.ClientConfiguration;
import org.apache.rocketmq.client.apis.ClientServiceProvider;
import org.apache.rocketmq.client.apis.consumer.ConsumeResult;
import org.apache.rocketmq.client.apis.consumer.FilterExpression;
import org.apache.rocketmq.client.apis.consumer.FilterExpressionType;
import org.apache.rocketmq.client.apis.message.Message;
import org.apache.rocketmq.client.apis.producer.Producer;
import org.apache.rocketmq.client.apis.producer.SendReceipt;
import org.junit.jupiter.api.Test;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.UUID;

@Slf4j
public class SendMessageTest {

    String endpoint = "localhost:8081";
    String topic = "YanoTestTopic";

    @Test
    public void send() throws Exception {
        ClientServiceProvider provider = ClientServiceProvider.loadService();
        ClientConfiguration configuration = ClientConfiguration.newBuilder().setEndpoints(endpoint).build();
        Producer producer = provider.newProducerBuilder()
                .setTopics(topic)
                .setClientConfiguration(configuration)
                .build();
        Message message = provider.newMessageBuilder()
                .setTopic(topic)
                .setKeys(UUID.randomUUID().toString())
                .setTag("tag1")
                .setBody(UUID.randomUUID().toString().getBytes())
                .build();

        // 发送消息
        SendReceipt sendReceipt = producer.send(message);

        log.info("send message {}, body {}", message, transfer(message.getBody()));
        log.info("messageId {}", sendReceipt.getMessageId());
    }

    @Test
    public void push() throws Exception {
        // 初始化 PushConsumer，需要绑定消费者分组ConsumerGroup、通信参数以及订阅关系
        ClientServiceProvider.loadService().newPushConsumerBuilder()
                // 接入点地址，需要设置成Proxy的地址和端口列表，一般是xxx:8081;xxx:8081
                .setClientConfiguration(ClientConfiguration.newBuilder().setEndpoints(endpoint).build())
                // 设置消费者分组
                .setConsumerGroup("yano")
                // 订阅消息的过滤规则， * 表示订阅所有Tag的消息
                .setSubscriptionExpressions(Collections.singletonMap(topic, new FilterExpression("*", FilterExpressionType.TAG)))
                // 设置消费监听器
                .setMessageListener(messageView -> {
                    // 处理消息并返回消费结果
                    log.info("Consume message={}, body {}", messageView, transfer(messageView.getBody()));
                    return ConsumeResult.SUCCESS;
                }).build();
        Thread.sleep(Long.MAX_VALUE);
    }

    private String transfer(ByteBuffer buffer) {
        return StandardCharsets.UTF_8.decode(buffer).toString();
    }
}
```