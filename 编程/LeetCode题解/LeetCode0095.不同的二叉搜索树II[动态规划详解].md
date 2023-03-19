
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/unique-binary-search-trees-ii/)

给定一个整数 n，生成所有由 1 ... n 为节点所组成的 二叉搜索树 。

示例：

```
输入：3
输出：
[
  [1,null,3,2],
  [3,2,null,1],
  [3,1,null,null,2],
  [2,1,3],
  [1,null,2,null,3]
]
解释：
以上的输出对应以下 5 种不同结构的二叉搜索树：

   1         3     3      2      1
    \       /     /      / \      \
     3     2     1      1   3      2
    /     /       \                 \
   2     1         2                 3

```

# 解题思路

dfs

# 代码

```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode(int x) { val = x; }
 * }
 */
class Solution {
    public List<TreeNode> generateTrees(int n) {
        if(n <= 0) return new ArrayList<>();
        return build(1, n);
    }
    private List<TreeNode> build(int start, int end) {
        List<TreeNode> roots = new ArrayList<>();       
        if(start > end) {           
            // null也要放入，否则下面的双重循环进不去
            roots.add(null);
            return roots;
        }
        if(start == end) {
            roots.add(new TreeNode(start));
            return roots;
        }
        for(int i = start; i <= end; i++) {
            List<TreeNode> leftList = build(start, i - 1);
            List<TreeNode> rightList = build(i + 1, end);
            for(TreeNode left : leftList) {             
                for(TreeNode right : rightList) {
                    TreeNode root = new TreeNode(i);
                    root.left = left;
                    root.right = right;
                    roots.add(root);
                }
            }
        }
        return roots;
    }
}
```

# 复杂度分析

- 时间复杂度：O()
- 空间复杂度：O()

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！