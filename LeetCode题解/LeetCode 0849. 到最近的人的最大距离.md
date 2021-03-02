
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/maximize-distance-to-closest-person/)

给你一个数组 seats 表示一排座位，其中 seats[i] = 1 代表有人坐在第 i 个座位上，seats[i] = 0 代表座位 i 上是空的（下标从 0 开始）。

至少有一个空座位，且至少有一人已经坐在座位上。

亚历克斯希望坐在一个能够使他与离他最近的人之间的距离达到最大化的座位上。

返回他到离他最近的人的最大距离。

 

示例 1：

![20210223150541](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210223150541.png)

```

输入：seats = [1,0,0,0,1,0,1]
输出：2
解释：
如果亚历克斯坐在第二个空位（seats[2]）上，他到离他最近的人的距离为 2 。
如果亚历克斯坐在其它任何一个空位上，他到离他最近的人的距离为 1 。
因此，他到离他最近的人的最大距离是 2 。 

```

示例 2：

```

输入：seats = [1,0,0,0]
输出：3
解释：
如果亚历克斯坐在最后一个座位上，他离最近的人有 3 个座位远。
这是可能的最大距离，所以答案是 3 。

```

示例 3：

```

输入：seats = [0,1]
输出：1

```

# 解题思路

- 先判断开始的连续 0、结尾的连续 0，即为 offset
- 接着判断中间的连续 0，个数即为 max，结果是 (max + 1) / 2，因为 1 2 个连续 0 的距离为 1，3 4 个连续 0 的距离为 2

取 offset 和 (max + 1) / 2 的最大值。

核心就在于两端的连续 0，和中间的连续 0 的计算规则是不一样的。

# 代码

```java
public int maxDistToClosest(int[] seats) {
	// 找到最长的连续为 0 的长度
	int start = 0, end = seats.length - 1;
	while (seats[start] == 0 && start + 1 < seats.length && seats[start + 1] == 0) {
		start++;
	}
	while (seats[end] == 0 && end - 1 >= 0 && seats[end - 1] == 0) {
		end--;
	}
	int offset = Math.max(start + 1, seats.length - end);
	int max = 0;
	for (int i = start; i < end; i++) {
		if (seats[i] == 0) {
			int count = 1;
			while (i + 1 < seats.length && seats[i + 1] == 0) {
				i++;
				count++;
			}
			max = Math.max(count, max);
		}
	}
	// 1 2 为 1，3 4 为 2
	return Math.max((max + 1) / 2, offset);
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！