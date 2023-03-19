
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/word-break/)

给定一个非空字符串 s 和一个包含非空单词的列表 wordDict，判定 s 是否可以被空格拆分为一个或多个在字典中出现的单词。

说明：

	拆分时可以重复使用字典中的单词。
	你可以假设字典中没有重复的单词。

示例 1：

```
输入：s = "leetcode", wordDict = ["leet", "code"]
输出：true
解释：返回 true 因为 "leetcode" 可以被拆分成 "leet code"。
```

示例 2：

```
输入：s = "applepenapple", wordDict = ["apple", "pen"]
输出：true
解释：返回 true 因为 "applepenapple" 可以被拆分成 "apple pen apple"。
     注意你可以重复使用字典中的单词。
```

示例 3：

```
输入：s = "catsandog", wordDict = ["cats", "dog", "sand", "and", "cat"]
输出：false
```

# 解题思路

此题可以使用 dfs 求解，但是会超时。

定义 dp[i] 为从 0 到 i，是否能用 wordDict 表示。

则`状态转移方程`为：dp[i] = dp[j] & wordSet.contains(s.substring(j + 1, i + 1))

# 代码

```java
class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        boolean[] dp = new boolean[s.length()];
        Set<String> wordSet = new HashSet<>(wordDict);
        for (int i = 0; i < s.length(); i++) {
            for (int j = 0; j <= i; j++) {
                if (wordSet.contains(s.substring(0, i + 1))) {
                    dp[i] = true;
                    break;
                }
                if (dp[j] && wordSet.contains(s.substring(j + 1, i + 1))) {
                    dp[i] = true;
                    break;
                }
            }
        }
        return dp[s.length() - 1];
    }
}
```

# 复杂度分析

- 时间复杂度：记字符串 s 的长度是 n，则复杂度是 O(n^2)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！