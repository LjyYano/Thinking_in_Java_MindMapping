
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/word-break-ii/)

给定一个非空字符串 s 和一个包含非空单词列表的字典 wordDict，在字符串中增加空格来构建一个句子，使得句子中所有的单词都在词典中。返回所有这些可能的句子。

说明：

	分隔时可以重复使用字典中的单词。
	你可以假设字典中没有重复的单词。

示例 1：

```
输入：
s = "catsanddog"
wordDict = ["cat", "cats", "and", "sand", "dog"]
输出：
[
  "cats and dog",
  "cat sand dog"
]
```

示例 2：

```
输入：
s = "pineapplepenapple"
wordDict = ["apple", "pen", "applepen", "pine", "pineapple"]
输出：
[
  "pine apple pen apple",
  "pineapple pen apple",
  "pine applepen apple"
]
解释：注意你可以重复使用字典中的单词。
```

示例 3：

```
输入：
s = "catsandog"
wordDict = ["cats", "dog", "sand", "and", "cat"]
输出：
[]
```

# 解题思路

典型的 dfs 题目，因为要考虑所有结果，所以直接深度搜索即可。

# 代码

```java
class Solution {
    public List<String> wordBreak(String s, List<String> wordDict) {
        Set<String> wordSet = new HashSet<>(wordDict);
        List<String> ans = new ArrayList<>();
        dfs(s, 0, wordSet, ans, "");
        return ans;
    }

    private void dfs(String s, int start, Set<String> wordSet, List<String> ans, String tmp) {
        if (start == s.length()) {
            ans.add(tmp.trim());
            return;
        }
        for (int i = start; i < s.length(); i++) {
            if (wordSet.contains(s.substring(start, i + 1))) {
                dfs(s, i + 1, wordSet, ans, tmp + " " + s.substring(start, i + 1));
            }
        }
    }
}
```

# 复杂度分析

- 时间复杂度：记字符串 s 的长度为 n，则对于每个字符，都有拆和不拆 2 个选项，则分割方法为 2^n。同时每种方法都需要一个长度是 n 的字符串进行存储，则时间复杂度是 O(n*2^n)
- 空间复杂度：O(n*2^n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！