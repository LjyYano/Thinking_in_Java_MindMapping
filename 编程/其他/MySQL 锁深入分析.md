
# MySQL 锁

官方文档：[https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html)

## Lock Mode

> 下面后面优化

[https://dev.mysql.com/blog-archive/innodb-data-locking-part-2-locks/](https://dev.mysql.com/blog-archive/innodb-data-locking-part-2-locks/)


One thing that emerges here is a distinction between “whole table” and “part of the table” when we try to specify required access rights at the table level. You can imagine following combinations:

- **X** → I want to be the only one who has access to the **whole** table
- **S** → I want to be able assume that **whole** table is protected from modification
- **IX** → I intend to modify some **part** of the table
- **IS** → I intend to read some **part** of the table

中文：

- S 锁：共享锁，行级锁，已加 S 锁的行，不允许其它事务再加 X 锁，但可以继续加 S 锁
- X 锁：排它锁，行级锁，已加 S 锁的行，不允行其它事务再加 S 或 X 锁
- IS: 意向共享锁，表级锁，已加 S 锁的表，肯定会有 IS 锁，反过来，有 IS 锁的表，不一定会有 S 锁
- IX: 意向排它锁，表级锁，已加 X 锁的表，肯定会有 IX 锁，反过来，有 IX 锁的表，不一定会有 X 锁

## 锁与索引的关系

[MySQL next-key lock 加锁范围总结](https://developer.aliyun.com/article/935403?spm=a2c6h.12873639.article-detail.55.55565366PGN6fk&scm=20140722.ID_community@@article@@935403._.ID_community@@article@@935403-OR_rec-V_1-RL_community@@article@@872705)

### 主键索引

1. 加锁时，会先给表添加意向锁，IX 或 IS；
2. 加锁是如果是多个范围，是分开加了多个锁，每个范围都有锁；（这个可以实践下 id < 20 的情况）
3. 主键等值查询，数据存在时，会对该主键索引的值加行锁 `X,REC_NOT_GAP`；
4. 主键等值查询，数据不存在时，会对查询条件主键值所在的间隙添加间隙锁 `X,GAP`；
5. 主键等值查询，范围查询时情况则比较复杂：
   1. 8.0.17 版本是前开后闭，而 8.0.18 版本及以后，修改为了 ` 前开后开 ` 区间；
   2. 临界 `<=` 查询时，8.0.17 会锁住下一个 next-key 的前开后闭区间，而 8.0.18 及以后版本，修复了这个 bug。

### 非主键唯一索引

1. 非主键唯一索引等值查询，数据存在，for update 是会在主键加锁的，而 for share 只有在走覆盖索引的情况下，会仅在自己索引上加锁；
2. 非主键索引等值查询，数据不存在，无论是否索引覆盖，相当于一个范围查询，仅仅会在非主键索引上加锁，加的还是间隙锁，前开后开区间；
3. 在非主键唯一索引范围查询时，不是覆盖索引的时候，会对相应的范围加前开后闭区间，并且如果存在数据，会对对应的主键加行锁；
4. 在非主键唯一索引范围查询时，如果是覆盖索引时，会对所有的后闭区间对应的主键，加行锁；
5. 在非主键唯一索引加锁时，还是存在 next-key 锁住下一个区间的 bug。

### 普通索引

1. 普通索引等值查询，因为不能确定唯一性，所以即使定位到记录，也是会向后查询，直到查询到不为该值的记录，从而锁定该值的区间；
2. 普通索引的锁也是加载该索引上的，如果涉及到存在的记录，会对该主键加行锁；
3. 普通索引的范围查询，同样出现 next-key 查询下一个区间的 bug。

### 普通字段

普通字段查询，会查询全表，这里锁的话就会锁住主键的所有区间。

# 实践

## 准备工作

1. 安装 `docker`，下载 MySQL 镜像。

```bash
docker pull mysql
```

2. 启动 MySQL 容器。

```bash
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 -d mysql
```

3. 查看 MySQL 是否启动。

```bash
docker ps
```

查看已经启动并映射了本机端口号。

```
CONTAINER ID   IMAGE          COMMAND                   CREATED          STATUS          PORTS                               NAMES
df75447a15aa   mysql:latest   "docker-entrypoint.s…"   16 seconds ago   Up 15 seconds   0.0.0.0:3306->3306/tcp, 33060/tcp   yano-mysql
```

4. 创建数据

```sql
CREATE TABLE `people`
(
    `id` int(11) NOT NULL,
    `a`  int(11) DEFAULT NULL,
    `b`  int(11) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `a` (`a`)
) ENGINE = InnoDB;
```

```sql
insert into people
values (0, 0, 0),
       (5, 5, 5),
       (10, 10, 10);
```

5. 确认版本

```sql
SELECT @@version;
```

结果是：

```
8.3.0
```

6. 确认隔离级别

查看当前会话隔离级别

```sql
select @@transaction_isolation;
```

查看系统当前隔离级别

```sql
select @@global.transaction_isolation;
```

结果是：

```
REPEATABLE-READ
```

当前查询的数据为：

| id | a | b |
| :--- | :--- | :--- |
| 0 | 0 | 0 |
| 5 | 5 | 5 |
| 10 | 10 | 10 |

## 如何查询锁

查询表 people 的锁状态：

```sql
select *
from performance_schema.data_locks
where OBJECT_NAME = 'people';
```

下图是一个示例（字段没有截全）：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-23-20-36-29.png)

# 加锁范围验证

## case 1：查询非索引字段

表中字段 b 是 ` 非索引字段 `。会话 1 执行以下语句：

```SQL
begin;

select *
from people
where b = 5 for update;
```

此时查出结果：

| id | a | b |
| :--- | :--- | :--- |
| 5 | 5 | 5 |

```SQL
select *
from performance_schema.data_locks
where OBJECT_NAME = 'people';
```

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2024-01-23-19-44-34.png)

为了查看方便，下面就只查询重要的列：

```SQL
select ENGINE_TRANSACTION_ID, INDEX_NAME, LOCK_TYPE, LOCK_MODE, LOCK_STATUS, LOCK_DATA
from performance_schema.data_locks
where OBJECT_NAME = 'people';
```

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1984 | null | TABLE | IX | GRANTED | null |
| 1984 | PRIMARY | RECORD | X | GRANTED | supremum pseudo-record |
| 1984 | PRIMARY | RECORD | X | GRANTED | 0 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 5 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 10 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 6 |

可以看到，会话 1 对整个表加了 `IX 表锁 `，对 id = 0、id = 5、id = 10、id = 6 的记录加了 X 行锁。

此时在会话 2 中执行以下语句：

```SQL
select *
from people
where b = 5 for update ;
```

会话 2 会 ` 阻塞 `。即使查询下面的语句也是会阻塞的：

```SQL
select *
from people
where id = 5 for update ;
```

此时 data_locks 的数据为：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1985 | null | TABLE | IX | GRANTED | null |
| 1985 | PRIMARY | RECORD | X | WAITING | 0 |
| 1984 | null | TABLE | IX | GRANTED | null |
| 1984 | PRIMARY | RECORD | X | GRANTED | supremum pseudo-record |
| 1984 | PRIMARY | RECORD | X | GRANTED | 0 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 5 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 10 |
| 1984 | PRIMARY | RECORD | X | GRANTED | 6 |

可以看到会话 2 的事务 ID = 1985，对 id = 0 的记录加了 X 行锁，但是是 WAITING 状态阻塞。

## case 2：查询索引字段（行锁）

表中字段 a 是索引字段。会话 1 执行以下语句：

```SQL
begin;

select *
from people
where id = 5 for update;
```

此时查出结果：

| id | a | b |
| :--- | :--- | :--- |
| 5 | 5 | 5 |

此时 data_locks 的数据为：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1986 | null | TABLE | IX | GRANTED | null |
| 1986 | PRIMARY | RECORD | X,REC\_NOT\_GAP | GRANTED | 5 |

可以看到，会话 1 对整个表加了 IX 表锁，对 id = 5 的记录加了 X 行锁。

此时在会话 2 中执行以下语句：

```SQL
select *
from people
where id = 5 for update;
```

此时 data_locks 的数据为：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1987 | null | TABLE | IX | GRANTED | null |
| 1987 | PRIMARY | RECORD | X,REC\_NOT\_GAP | WAITING | 5 |
| 1986 | null | TABLE | IX | GRANTED | null |
| 1986 | PRIMARY | RECORD | X,REC\_NOT\_GAP | GRANTED | 5 |


会话 2 的事务 ID 是 1987，第二行是 WAITING 状态会阻塞。但是只要查询的 id 不是 5，就不会阻塞。例如下面的语句是不会阻塞的。

> 这是因为表中有 id = 5 这条记录，这里只是行锁。

```SQL
select *
from people
where id = 10 for update;
```

## case 3：查询索引字段（间隙锁）

会话 1 执行以下语句：

```SQL
begin;

select *
from people
where id = 3 for update;
```

此时查出结果为空，因为没有 id = 3 的记录。

此时 data_locks 的数据为：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1988 | null | TABLE | IX | GRANTED | null |
| 1988 | PRIMARY | RECORD | X,GAP | GRANTED | 5 |

可以看到，会话 1 对整个表加了 IX 表锁，对 id = 3 的记录加了 X ` 间隙锁 `（不包含 id = 5 这行数据）。

此时在会话 2 中执行以下语句：

```SQL
select *
from people
where id = 3 for update;
```

并没有阻塞。虽然会话 1 和会话 2 都会对 id = 3 的记录加上间隙锁，但是查询间隙锁并不会冲突，只有 `“往这个间隙中插入记录”` 才会冲突。

例如在会话 2 中执行以下语句：

```SQL
insert into people
values (3, 3, 3);
```

```SQL
insert into people
values (4, 4, 4);
```

会话 2 会阻塞，直到会话 1 提交事务或者回滚事务。此时 data_locks 的数据为：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1990 | null | TABLE | IX | GRANTED | null |
| 1990 | PRIMARY | RECORD | X,GAP,INSERT\_INTENTION | WAITING | 5 |
| 1988 | null | TABLE | IX | GRANTED | null |
| 1988 | PRIMARY | RECORD | X,GAP | GRANTED | 5 |

但是会话 2 执行下面的语句不会阻塞：

```SQL
insert into people
values (6, 6, 6);
```

# 可重复读下的幻读

一个灵魂问题，` 可重复读隔离级别完全解决了幻读吗 `？

## 幻读定义

参考官方文档：[15.7.4 Phantom Rows
](https://dev.mysql.com/doc/refman/8.0/en/innodb-next-key-locking.html)

The so-called phantom problem occurs within a transaction when the same query produces different sets of rows at different times. For example, if a [`SELECT`](https://dev.mysql.com/doc/refman/8.0/en/select.html "13.2.13 SELECT Statement") is executed twice, but returns a row the second time that was not returned the first time, the row is a “phantom” row.

同一个查询在不同的时间，产生不同的结果集，就是所谓的幻读问题。例如，一个 `SELECT` 语句在第一次执行时，结果集为空；但是第二次执行时，返回了一行数据，这行数据在第一次执行时并不存在，这就是幻读。

## ` 快照读 ` 不会出现幻读

从本篇文章上面可以看出，可重复读隔离级别下，快照读几乎不会出现幻读。是通过 MVCC 实现的。

> 待详细补充

## ` 当前读 ` 不会出现幻读

本篇文章上面的例子，可以看出在正常的情况下，` 行锁 ` 和 ` 间隙锁 ` 已经解决幻读。

## 出现幻读的 case

还是 `people` 表，初始数据：

| id | a | b |
| :--- | :--- | :--- |
| 0 | 0 | 0 |
| 5 | 5 | 5 |
| 10 | 10 | 10 |

在会话 1 查询 id = 100 的数据：

```SQL
begin;

select *
from people
where id = 100;
```

可以看到查询结果集为空，而且并没有加锁（下面查询语句为空）。

```SQL
select ENGINE_TRANSACTION_ID, INDEX_NAME, LOCK_TYPE, LOCK_MODE, LOCK_STATUS, LOCK_DATA
from performance_schema.data_locks
where OBJECT_NAME = 'people';
```

此时在会话 2 中插入 id = 100 的数据：

```SQL
insert into people
values (100, 100, 100);
```

此时在会话 1 再次查询 id = 100 的数据：

```SQL
select *
from people
where id = 100;
```

发现结果还是空的。但是此时在会话 1 中更新 id = 100 的数据：

```SQL
update people
set a = 99 where id = 100;
```

之后再次查询 id = 100 的数据：

```SQL
select *
from people
where id = 100;
```

能查到以下结果：

| id | a | b |
| :--- | :--- | :--- |
| 100 | 99 | 100 |

此时查看 data_locks 的数据：

| ENGINE\_TRANSACTION\_ID | INDEX\_NAME | LOCK\_TYPE | LOCK\_MODE | LOCK\_STATUS | LOCK\_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2025 | null | TABLE | IX | GRANTED | null |
| 2025 | PRIMARY | RECORD | X,REC\_NOT\_GAP | GRANTED | 100 |

发现会话 1 对 id = 100 的记录加了 X 行锁，但是这一行在会话 1 开始时并没有查询出来，出现了幻读。

出现幻读的原因，在于会话 1 在查询 id = 100 的时候，没有对 id = 100 的记录加锁，所以会话 2 可以插入 id = 100 的记录。但是会话 1 在更新 id = 100 的时候，对 id = 100 的记录加了 X 行锁，在会话 1 中就能够查询到 id = 100 的记录了。