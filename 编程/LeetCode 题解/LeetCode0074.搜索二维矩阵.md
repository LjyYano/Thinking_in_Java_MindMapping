
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/search-a-2d-matrix/)

编写一个高效的算法来判断 m x n 矩阵中，是否存在一个目标值。该矩阵具有如下特性：

	每行中的整数从左到右按升序排列。
	每行的第一个整数大于前一行的最后一个整数。

 

示例 1：

![20210226094001](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226094001.png)

```

输入：matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
输出：true

```

示例 2：

![20210226094007](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226094007.png)

```

输入：matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13
输出：false
```

# 解题思路

这道题本质上是一个二分查找的题目，因为二维数组在本质上是有序的，只不过是将有序的一维数组转换成为了二维数组。

可以将 int[][] matrix 想象成一维数组 nums[]，nums[] 总长度就是 matrix 的 m*n，则 nums 中的第 i 个元素，对应到二维数组中第 i/n 行，第 i%y 列的元素。

# 代码

```java
public class Solution {
    public boolean searchMatrix(int[][] matrix, int target) {
		int mx = matrix.length;
		int my = matrix[0].length;

		int l = 0;
		int r = mx * my;

		while (l < r) {		
			int m = l + (r - l) / 2;
			int x = m / my;
			int y = m % my;

			if (matrix[x][y] == target) {
				return true;
			} else if (matrix[x][y] < target) {
				l = m + 1;
			} else {
				r = m;
			}
		}
		return false;
    }
}
```

# 复杂度分析

- 时间复杂度：O(log(m*n))
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！