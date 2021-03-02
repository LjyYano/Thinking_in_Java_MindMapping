
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/largest-number-at-least-twice-of-others/)

在一个给定的数组 nums 中，总是存在一个最大元素 。

查找数组中的最大元素是否至少是数组中每个其他数字的两倍。

如果是，则返回最大元素的索引，否则返回-1。

示例 1:

```
输入：nums = [3, 6, 1, 0]
输出：1
解释：6 是最大的整数，对于数组中的其他整数，
6 大于数组中其他元素的两倍。6 的索引是 1, 所以我们返回 1.

```

示例 2:

```
输入：nums = [1, 2, 3, 4]
输出：-1
解释：4 没有超过 3 的两倍大，所以我们返回 -1.

```

# 解题思路

题目要找到「至少是其他数字两倍的最大数」，可以维护两个数，最大数和第二大的数，最终判断是否最大数>=第二大的数* 2 就可以了~

下面代码的 result 数组其实可以省略，维护两个数字即可，这里就不优化了。

# 代码

```java
class Solution {
	public int minCostClimbingStairs(int[] cost) {
		int n = cost.length;
		int[] result = new int[n];
		result[0] = cost[0];
		result[1] = cost[1];
		
		for(int i = 2; i < n; i++) {
			result[i] = Math.min(result[i-1], result[i-2]) + cost[i];
		}
		return Math.min(result[n - 1], result[n - 2]);
	}
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！