
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/count-servers-that-communicate/)

这里有一幅服务器分布图，服务器的位置标识在 m * n 的整数矩阵网格 grid 中，1 表示单元格上有服务器，0 表示没有。

如果两台服务器位于同一行或者同一列，我们就认为它们之间可以进行通信。

请你统计并返回能够与至少一台其他服务器进行通信的服务器的数量。

 

示例 1：

![20210222193754](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210222193754.png)

```
输入：grid = [[1,0],[0,1]]
输出：0
解释：没有一台服务器能与其他服务器进行通信。
```

示例 2：

![20210222193827](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210222193827.png)

```
输入：grid = [[1,0],[1,1]]
输出：3
解释：所有这些服务器都至少可以与一台别的服务器进行通信。
```

示例 3：

![20210222193836](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210222193836.png)

```
输入：grid = [[1,1,0,0],[0,0,1,0],[0,0,1,0],[0,0,0,1]]
输出：4
解释：第一行的两台服务器互相通信，第三列的两台服务器互相通信，但右下角的服务器无法与其他服务器通信。
```

# 解题思路

新建 2 个数组 row 和 col，分别存储其所在行/列中 1 出现的次数，如果 row 中第 i 个元素>1，表示第 i 行存在多个服务器，并且这些服务器就可以计算在结果中；col 同理。

在组合好数组 row 和 col 后，再遍历数组中的每个元素，只要所在的行/列 1 出现的次数大于 1，即表明可以计算在结果中。

# 代码

```java
public int countServers(int[][] grid) {
	// 行/列出现 1 的次数
	int[] row = new int[grid.length];
	int[] col = new int[grid[0].length];
	for (int i = 0; i < grid.length; i++) {
		for (int j = 0; j < grid[0].length; j++) {
			if (grid[i][j] == 1) {
				row[i]++;
				col[j]++;
			}
		}
	}
	int ans = 0;
	for (int i = 0; i < grid.length; i++) {
		for (int j = 0; j < grid[0].length; j++) {
			if (grid[i][j] == 1 && (row[i] > 1 || col[j] > 1)) {
				ans++;
			}
		}
	}
	return ans;
}
```

# 复杂度分析

- 时间复杂度：设 grid 是 m*n，则复杂度是 O(max(m,n))
- 空间复杂度：O(max(m,n))

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！