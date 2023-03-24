
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/minimum-time-visiting-all-points/)

平面上有 n 个点，点的位置用整数坐标表示 points[i] = [xi, yi] 。请你计算访问所有这些点需要的 最小时间（以秒为单位）。

你需要按照下面的规则在平面上移动：

	每一秒内，你可以：
	
		沿水平方向移动一个单位长度，或者
		沿竖直方向移动一个单位长度，或者
		跨过对角线移动 sqrt(2) 个单位长度（可以看作在一秒内向水平和竖直方向各移动一个单位长度）。
	
	必须按照数组中出现的顺序来访问这些点。
	在访问某个点时，可以经过该点后面出现的点，但经过的那些点不算作有效访问。

 

示例 1：

![20210226100804](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226100804.png)

```

输入：points = [[1,1],[3,4],[-1,0]]
输出：7
解释：一条最佳的访问路径是： [1,1] -> [2,2] -> [3,3] -> [3,4] -> [2,3] -> [1,2] -> [0,1] -> [-1,0]   
从 [1,1] 到 [3,4] 需要 3 秒 
从 [3,4] 到 [-1,0] 需要 4 秒
一共需要 7 秒
```

示例 2：

```

输入：points = [[3,2],[-2,2]]
输出：5

```

# 解题思路

按照题目的描述，2 个点之间如何能时间最短呢？

假设两个点分别在 (x1,y1)，(x2,y2)，那么差值 
- x = abs(x1 - x2)
- y = abs(y1 - y2)

分析一下，
- 如果 x=2，y=2，那么斜着走两次即可；
- 如果 x=2，y=3，那么斜着走两次，再沿着 y 轴方向走一次；
- 如果 x=3，y=2，那么斜着走两次，再沿着 x 轴方向走一次

也就是说，两个点之间最短距离是 Math.min(x, y) + Math.abs(x - y)

# 代码

```java
class Solution {
    public int minTimeToVisitAllPoints(int[][] points) {
        int ans = 0;
        for (int i = 1; i < points.length; i++) {
            int x = Math.abs(points[i][0] - points[i - 1][0]);
            int y = Math.abs(points[i][1] - points[i - 1][1]);
            ans += Math.min(x, y) + Math.abs(x - y);
        }
        return ans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(m*n)，points 是 m*n 的
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！