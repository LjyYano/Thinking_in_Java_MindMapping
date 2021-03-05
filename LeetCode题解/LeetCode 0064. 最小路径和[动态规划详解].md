
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/minimum-path-sum/)

给定一个包含非负整数的 m x n 网格 grid ，请找出一条从左上角到右下角的路径，使得路径上的数字总和为最小。

说明：每次只能向下或者向右移动一步。

 

示例 1：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210304184827.png)

```

输入：grid = [[1,3,1],[1,5,1],[4,2,1]]
输出：7
解释：因为路径 1→3→1→1→1 的总和最小。

```

示例 2：

```

输入：grid = [[1,2,3],[4,5,6]]
输出：12

```

# 解题思路

定义 dp[i][j] 为从 (0,0) 到 (i,j) 的最大距离，其实这道题和第 62 题：不同路径在本质上是一样的，只不过这里每个格子不是 1，而是一个数值。只有两种可能：
- 从上面过来最小，即 dp[i-1][j]
- 从左面过来最小，即 dp[i][j-1]

则`状态转移方程`为：

dp[i][j] = Math.min(dp[i - 1][j], dp[i][j - 1]) + grid[i][j];

# 代码

```java
class Solution {
    public int minPathSum(int[][] grid) {
        if(grid == null || grid.length == 0 ) return 0;
        int m = grid.length, n = grid[0].length;
        int[][] dp = new int[m][n];
        dp[0][0] = grid[0][0];
        
        // 初始化行
        for(int i = 1; i < n; i++) {
            dp[0][i] = grid[0][i] + dp[0][i - 1];
        }
        
        // 初始化列
        for(int i = 1; i < m; i++) {
            dp[i][0] = grid[i][0] + dp[i - 1][0];
        }
        
        for(int i = 1; i < m; i++) {
            for(int j = 1; j < n; j++) {
                dp[i][j] = Math.min(dp[i - 1][j], dp[i][j - 1]) + grid[i][j];
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