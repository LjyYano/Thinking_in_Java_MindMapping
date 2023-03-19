
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/triangle/)

给定一个三角形 triangle ，找出自顶向下的最小路径和。

每一步只能移动到下一行中相邻的结点上。相邻的结点 在这里指的是 下标 与 上一层结点下标 相同或者等于 上一层结点下标 + 1 的两个结点。也就是说，如果正位于当前行的下标 i ，那么下一步可以移动到下一行的下标 i 或 i + 1 。

 

示例 1：

```

输入：triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
输出：11
解释：如下面简图所示：
   2
  3 4
 6 5 7
4 1 8 3
自顶向下的最小路径和为 11（即，2 + 3 + 5 + 1 = 11）。

```

示例 2：

```

输入：triangle = [[-10]]
输出：-10

```

进阶：

	你可以只使用 O(n) 的额外空间（n 为三角形的总行数）来解决这个问题吗？

# 解题思路

这道题和二叉树的节点路径和是一样的，只不过这道题是数组的形式。核心思想就是记录从根节点到每个子节点的最小和，然后在最后一行中找最小值即可。

# 代码

```java
class Solution {
    public int minimumTotal(List<List<Integer>> triangle) {
        List<Integer> pre = triangle.get(0);
        for (int i = 1; i < triangle.size(); i++) {
            List<Integer> now = triangle.get(i);
            List<Integer> ans = new ArrayList<>();
            for (int j = 0; j < now.size(); j++) {
                if (j == 0) {
                    ans.add(now.get(j) + pre.get(0));
                } else if (j == now.size() - 1) {
                    ans.add(now.get(j) + pre.get(j - 1));
                } else {
                    ans.add(now.get(j) + Math.min(pre.get(j), pre.get(j - 1)));
                }
            }
            pre = new ArrayList(ans);
            ans.clear();
        }
        return Collections.min(pre);
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！