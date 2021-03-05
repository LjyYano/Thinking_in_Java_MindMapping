
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/unique-paths/)

一个机器人位于一个 m x n 网格的左上角 （起始点在下图中标记为 “Start” ）。

机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角（在下图中标记为 “Finish” ）。

问总共有多少条不同的路径？

 

示例 1：

![20210304104242](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210304104242.png)

```

输入：m = 3, n = 7
输出：28
```

示例 2：

```

输入：m = 3, n = 2
输出：3
解释：
从左上角开始，总共有 3 条路径可以到达右下角。
1. 向右 -> 向下 -> 向下
2. 向下 -> 向下 -> 向右
3. 向下 -> 向右 -> 向下

```

示例 3：

```

输入：m = 7, n = 3
输出：28

```

示例 4：

```

输入：m = 3, n = 3
输出：6
```

# 解题思路

定义 dp[i][j] 为走到方格 (i,j) 坐标的不同路径的条数，则到这个路径只有两种可能：从上面 (i-1,j) 到该点，或者从左边 (i,j-1) 到该点。

则`状态转移方程`为：

dp[i][j] = dp[i - 1][j] + dp[i][j - 1];

# 代码

```java
class Solution {
    public int uniquePaths(int m, int n) {
        if (m <= 0 || n <= 0) return 0;
        int[][] dp = new int[m][n];

        Arrays.fill(dp[0], 1);
        for (int i = 0; i < m; i++) {
            dp[i][0] = 1;
        }

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (i > 0 && j > 0) {
                    dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
                }
            }
        }

        return dp[m - 1][n - 1];
    }
}
```

# 复杂度分析

- 时间复杂度：O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！