
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/unique-paths-ii/)

一个机器人位于一个 m x n 网格的左上角 （起始点在下图中标记为“Start” ）。

机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角（在下图中标记为“Finish”）。

现在考虑网格中有障碍物。那么从左上角到右下角将会有多少条不同的路径？

![20210304103414](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210304103414.png)

网格中的障碍物和空位置分别用 1 和 0 来表示。

 

示例 1：

![20210304103433](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210304103433.png)

```

输入：obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]
输出：2
解释：
3x3 网格的正中间有一个障碍物。
从左上角到右下角一共有 2 条不同的路径：
1. 向右 -> 向右 -> 向下 -> 向下
2. 向下 -> 向下 -> 向右 -> 向右

```

示例 2：

![20210304103441](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210304103441.png)

```

输入：obstacleGrid = [[0,1],[0,0]]
输出：1

```

# 解题思路

跟第 62 题一样，只是加了一个障碍物。

定义 dp[i][j] 为走到方格 (i,j) 坐标的不同路径的条数，
- 如果 (i,j) 是障碍物，即 grid[i][j]==1，则 dp[i][j]=0
- 如果 (i,j) 不是障碍物，即 grid[i][j]!=1 到这个路径只有两种可能：从上面 (i-1,j) 到该点，或者从左边 (i,j-1) 到该点。

则`状态转移方程`为：

dp[i][j] = dp[i - 1][j] + dp[i][j - 1], grid[i][j] != 1;
dp[i][j] = 0, grid[i][j] == 1;

# 代码

```java
class Solution {
    public int uniquePathsWithObstacles(int[][] grid) {
        if(grid == null || grid.length == 0 ) return 0;
        int m = grid.length, n = grid[0].length;
        int[][] dp = new int[m][n];
        
        // 初始化行
        for(int i = 0; i < n; i++) {
            if(grid[0][i] == 1) break;
            dp[0][i] = 1;
        }
        
        // 初始化列
        for(int i = 0; i < m; i++) {
            if(grid[i][0] == 1) break;
            dp[i][0] = 1;
        }
        
        if (dp[0][0] == 0) return 0;
        
        for(int i = 1; i < m; i++) {
            for(int j = 1; j < n; j++) {
                if(grid[i][j] == 1) {
                    dp[i][j] = 0;
                } else {
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