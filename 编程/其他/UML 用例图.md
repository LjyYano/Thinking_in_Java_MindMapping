---
date: 2024-01-05
---

- [表示](#表示)
- [时序图](#时序图)

# 表示

- 系统：矩形块，语法是 `rectangle`
- 执行者：火柴人，语法是 `actor`
- 用例：椭圆，语法是 `usecase`
- 关系
  - 关联：执行者和用例之间的关系，`实线 + 实心箭头`，语法是 `->`
  - 包含：用例之间的关系，`虚线箭头 + <<include>>`，语法示例 `UC1 ..> UC2 : <<include>>`
  - 扩展：用例之间的关系，`虚线箭头 + <<extend>>`，语法示例 `UC1 ..> UC2 : <<extend>>`
  - 泛化：继承关系，`实线 + 空心箭头`，语法示例 `UC1 <|-- UC2`

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-05-15-37-37.png)

<details> <summary>View Code</summary>

```
@startuml
left to right direction
actor 客户 as Actor
actor 银行 as Actor2

rectangle "某银行App" {
	usecase "转账" as UC1
	usecase "查询余额" as UC2
	usecase "理财" as UC3
	usecase "贷款" as UC4
	usecase "评估资产" as UC5
	usecase "提示限额" as UC6
}

Actor <|-up- 个人用户
Actor <|-up- 企业用户
Actor --> UC1

Actor --> UC2
Actor --> UC3
Actor --> UC4
UC1 ----> Actor2
UC2 ----> Actor2
UC3 ----> Actor2
UC4 ----> Actor2

UC4 .left.> UC5 :<<include>>
UC1 <.down. UC6 :<<extend>>

@enduml
```
</details>

# 时序图

时序图是一种 UML 中的行为图，用于描述对象之间的交互行为。时序图显示了对象之间的交互顺序，它展示了对象之间的消息传递顺序，以及这些消息如何触发对象的行为和状态变化。

<details> <summary>示例</summary>

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-05-17-00-38.png)

```
@startuml
hide footbox
skinparam style strictuml
autonumber 1

actor "用户" as User
participant SyncPlusTopicChannel as SyncPlusTopicChannel
participant SyncManager as SyncManager
participant SyncDownTask as SyncDownTask
participant SyncPlusReliableChannel as SyncPlusReliableChannel
participant SyncPlusDatabaseManager as SyncPlusDatabaseManager
participant SyncPlusBizChannelPool as SyncPlusBizChannelPool
participant BizOrDataListener as Listener

activate User
User -> SyncPlusTopicChannel : dispatch
activate SyncPlusTopicChannel

SyncPlusTopicChannel -> SyncManager : startDownSync
activate SyncManager

SyncManager -> SyncDownTask : process
activate SyncDownTask

loop#lightblue
		opt#pink
			SyncDownTask -> SyncDownTask : getDifference
		end
		SyncDownTask -> SyncDownTask : parseData
		SyncDownTask -> SyncPlusReliableChannel : onReceived
		activate SyncPlusReliableChannel

		autonumber 7 "<font color=green>0</font>"
		group 第一个异步处理
				SyncPlusReliableChannel ->> SyncPlusDatabaseManager : Insert
				activate SyncPlusDatabaseManager
				return ack
				return ack
				deactivate SyncPlusDatabaseManager
				SyncDownTask -> SyncDownTask : updateSyncInfo
		end

autonumber 7 "<font color=red>0</font>"
			group 第二个异步处理
					loop#lightblue <color blue>如果第 15 步返回有缓存数据 </color>
							SyncPlusReliableChannel ->> SyncPlusBizChannelPool:AddSyncData
							activate SyncPlusReliableChannel
							activate SyncPlusBizChannelPool
							SyncPlusBizChannelPool -> Listener : OnReceived/OnToolong2
							activate Listener
							return
							return 
							SyncPlusReliableChannel -> SyncPlusReliableChannel :  onSyncDataObjectAckSuccess
							deactivate SyncPlusBizChannelPool
		
							SyncPlusReliableChannel -> SyncPlusDatabaseManager : Remove
							activate SyncPlusDatabaseManager
							/'可以用 return 来代替
								SyncPlusReliableChannel <-- SyncPlusDatabaseManager
								deactivate SyncPlusDatabaseManager
							'/
							return
							'可以用 ++ 来代替 activate'
							SyncPlusReliableChannel -> SyncPlusDatabaseManager ++ : Read
							return
					end
			end
			SyncDownTask <-- SyncPlusReliableChannel
			deactivate SyncPlusReliableChannel
end

autonumber 11 "<font color=black>0</font>"
SyncDownTask --> SyncManager
alt#Gold 第一个异步处理的loop结束
		SyncManager -> SyncManager : endDownSync
end
deactivate SyncDownTask
SyncPlusTopicChannel <-- SyncManager
deactivate SyncManager
User <-- SyncPlusTopicChannel
deactivate SyncPlusTopicChannel

@enduml
```
</details>
