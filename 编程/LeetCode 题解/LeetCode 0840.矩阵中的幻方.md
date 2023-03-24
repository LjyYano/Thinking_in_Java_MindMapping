
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/magic-squares-in-grid/)

3 x 3 的幻方是一个填充有从 1 到 9 的不同数字的 3 x 3 矩阵，其中每行，每列以及两条对角线上的各数之和都相等。

给定一个由整数组成的 grid，其中有多少个 3 × 3 的 “幻方” 子矩阵？（每个子矩阵都是连续的）。

 

示例：

```
输入：[[4,3,8,4],
      [9,5,1,9],
      [2,7,6,2]]
输出：1
解释：
下面的子矩阵是一个 3 x 3 的幻方：
438
951
276

而这一个不是：
384
519
762

总的来说，在本示例所给定的矩阵中只有一个 3 x 3 的幻方子矩阵。

```

# 解题思路

以每个元素为左上角，判断是否符合条件。

- 3 行和 3 列的和分别为 15
- 以这个元素为左上角的 3*3 的矩形，要包含 1~9 这 9 个数字
- 两条对角线上的元素和分别为 15

# 代码

```java
class Solution {
    public int numMagicSquaresInside(int[][] grid) {
        int ans = 0;
        // 以每个元素为左上角，查看是否符合条件
        for (int i = 0; i < grid.length; i++) {
            for (int j = 0; j < grid[0].length; j++) {
                if (check(grid, i, j)) {
                    ans++;
                }
            }
        }
        return ans;
    }

    private boolean check(int[][] grid, int i, int j) {
        if (i + 2 >= grid.length || j + 2 >= grid[0].length) {
            return false;
        }
        // 1~9 这 9 个数字
        int[] nums = new int[9];
        for (int k = 0; k < 3; k++) {
            for (int l = 0; l < 3; l++) {
                int n = grid[i + k][j + l];
                if (n < 1 || n > 9) {
                    return false;
                }
                if (nums[n - 1] == 1) {
                    return false;
                }
                nums[n - 1] = 1;
            }
        }
        for (int k = 0; k < 3; k++) {
            if (grid[i + k][j] + grid[i + k][j + 1] + grid[i + k][j + 2] != 15) {
                return false;
            }
            if (grid[i][j + k] + grid[i + 1][j + k] + grid[i + 2][j + k] != 15) {
                return false;
            }
        }
        // 对角线
        if (grid[i][j] + grid[i + 1][j + 1] + grid[i + 2][j + 2] != 15) {
            return false;
        }
        if (grid[i + 2][j] + grid[i + 1][j + 1] + grid[i][j + 2] != 15) {
            return false;
        }
        return true;
    }
}
```

# 复杂度分析

- 时间复杂度：遍历每个元素，假设有 n 个元素，每个元素遍历 9 个元素，大概为 9n，所以复杂度是 O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！