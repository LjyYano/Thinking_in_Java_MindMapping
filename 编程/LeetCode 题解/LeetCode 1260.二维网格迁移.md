
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/shift-2d-grid/)

给你一个 m 行 n 列的二维网格 grid 和一个整数 k。你需要将 grid 迁移 k 次。

每次「迁移」操作将会引发下述活动：

	位于 grid[i][j] 的元素将会移动到 grid[i][j + 1]。
	位于 grid[i][n - 1] 的元素将会移动到 grid[i + 1][0]。
	位于 grid[m - 1][n - 1] 的元素将会移动到 grid[0][0]。

请你返回 k 次迁移操作后最终得到的 二维网格。

 

示例 1：

![20210226095201](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226095201.png)

```

输入：grid = [[1,2,3],[4,5,6],[7,8,9]], k = 1
输出：[[9,1,2],[3,4,5],[6,7,8]]

```

示例 2：

![20210226095208](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226095208.png)

```

输入：grid = [[3,8,1,9],[19,7,2,5],[4,6,11,10],[12,0,21,13]], k = 4
输出：[[12,0,21,13],[3,8,1,9],[19,7,2,5],[4,6,11,10]]

```

示例 3：

```

输入：grid = [[1,2,3],[4,5,6],[7,8,9]], k = 9
输出：[[1,2,3],[4,5,6],[7,8,9]]

```

# 解题思路

参考 https://leetcode-cn.com/problems/shift-2d-grid/solution/er-wei-wang-ge-qian-yi-by-leetcode/

其实题目中的描述，每次就是向右移动一位，右下角的数字变到左上角。

![20210226095313](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226095313.png)

优化：如果 k 非常大，可以对数组元素长度取模，因为假如是 2*2 的二维数组，移动 4 次、400 次、4000 次结果都是一样的。

# 代码

```java
class Solution {
    public List<List<Integer>> shiftGrid(int[][] grid, int k) {
        List<List<Integer>> res = new ArrayList<>();
        List<Integer> list = new ArrayList<>();
        int m = grid.length, n = grid[0].length;
        int total = m * n;
        // 寻找到开头位置
        int index = total - k;
        while (index < 0)
            index += total;
        index++;
        // 遍历一遍数组，通过数组中的位置获取其横纵坐标，然后塞进 list
        for (int i = 0; i < total; i++) {
            list.add(grid[(index + i - 1) % total / n][(index + i - 1) % total % n]);
            // 每次达到 n 个就塞进去
            if ((i + 1) % n == 0) {
                res.add(list);
                list = new ArrayList<>();
            }
        }
        return res;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n*m)，网格数量是 n*m
- 空间复杂度：O(n*m)，因为输出结果是一个与输入等大的 list

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！