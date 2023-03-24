
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/palindrome-partitioning/)

给你一个字符串 s，请你将 s 分割成一些子串，使每个子串都是 回文串 。返回 s 所有可能的分割方案。

回文串 是正着读和反着读都一样的字符串。

 

示例 1：

```
输入：s = "aab"
输出：[["a","a","b"],["aa","b"]]
```

示例 2：

```
输入：s = "a"
输出：[["a"]]
```

# 解题思路

这道题是深度优先搜索+回溯。分别对于索引 i，从 i 开始向后遍历所有回文，将其加入最终结果。同时可以通过动态规划，记录字符串 [i,j] 是否是回文，这样就不用在深搜时重复判断该区间是否是回文。

# 代码

```java
class Solution {
    public List<List<String>> partition(String s) {
        List<List<String>> ans = new ArrayList<>();
        if (s == null || s.length() == 0) {
            return ans;
        }

        dfs(s.toCharArray(), 0, s.length(), new ArrayDeque<>(), ans);
        return ans;
    }

    // 获取以 index 开始的所有组合
    private void dfs(char[] charArray, int index, int length, Deque<String> path, List<List<String>> ans) {
        if (index == length) {
            ans.add(new ArrayList<>(path));
            return;
        }

        for (int i = index; i < charArray.length; i++) {
            // 判断 index 到最后是否有回文
            if (!check(charArray, index, i)) {
                continue;
            }
            // [index, i] 为回文，则加入结果
            path.addLast(new String(charArray, index, i + 1 - index));
            // 对 i + 1 再次递归
            dfs(charArray, i + 1, length, path, ans);
            path.removeLast();
        }
    }

    private boolean check(char[] charArray, int start, int end) {
        while (start < end) {
            if (charArray[start++] != charArray[end--]) {
                return false;
            }
        }
        return true;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n*2^n)
- 空间复杂度：O(n^2)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！