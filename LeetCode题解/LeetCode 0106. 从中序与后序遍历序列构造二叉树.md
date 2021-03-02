
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)

根据一棵树的中序遍历与后序遍历构造二叉树。

注意：
你可以假设树中没有重复的元素。

例如，给出

```
中序遍历 inorder = [9,3,15,20,7]
后序遍历 postorder = [9,15,7,20,3]
```

返回如下的二叉树：

```
    3
   / \
  9  20
    /  \
   15   7

```

# 解题思路

非常非常典型的题目，首先解决这道题我们需要明确给定一棵二叉树，我们是如何对其进行中序遍历与后序遍历的：

- 中序遍历的顺序是每次遍历左孩子，再遍历根节点，最后遍历右孩子。
- 后序遍历的顺序是每次遍历左孩子，再遍历右孩子，最后遍历根节点。

![20210224101000](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210224101000.png)

因为后序遍历的顺序是`左右中`，所以后序遍历的最后一个元素即为根节点，那么我们在中序遍历中找到这个节点，这个元素左边的即为左子树的中序遍历，右边的即为右子树的中序遍历。接下来根据这个方法，对每个部分采取同样的方法递归构造。

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
    public TreeNode buildTree(int[] in, int[] post) {
        return robot(in, post, 0, in.length - 1, 0, post.length - 1);
    }

    private TreeNode robot(int[] in, int[] post, int inStart, int inEnd, int postStart,
            int postEnd) {
        if (postStart > postEnd) {
            return null;
        }
        TreeNode root = new TreeNode(post[postEnd]);
        int pos = 0;
        // 在中序数组里，找到后序遍历的最后一个元素 post[postEnd](根节点)所在的索引
        for (int i = inStart; i <= inEnd; i++) {
            if (in[i] == root.val) {
                pos = i;
                break;
            }
        }
        // 左子树：中序遍历 [inStart, pos - 1]，后序遍历 [postStart, postStart + pos - inStart - 1]
        // pos - inStart - 1 即为中序数组的长度
        root.left = robot(in, post, inStart, pos - 1, postStart, postStart + pos - inStart - 1);
        // 右子树：中序遍历 [pos + 1,inEnd]，后序遍历 [postEnd + pos - inEnd, postEnd - 1]
        root.right = robot(in, post, pos + 1, inEnd, postEnd + pos - inEnd, postEnd - 1);
        return root;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！