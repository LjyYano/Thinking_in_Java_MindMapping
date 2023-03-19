
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/longest-valid-parentheses/)

给你一个只包含 '(' 和 ')' 的字符串，找出最长有效（格式正确且连续）括号子串的长度。

示例 1：

```

输入：s = "(()"
输出：2
解释：最长有效括号子串是 "()"

```

示例 2：

```

输入：s = ")()())"
输出：4
解释：最长有效括号子串是 "()()"

```

示例 3：

```

输入：s = ""
输出：0

```

# 解题思路

定义 dp[i] 为以 i 结尾的最长有效括号

- 当 s[i] 为 (,dp[i] 必然等于 0，因为不可能组成有效的括号；
- 那么 s[i] 为 )
  - 当 s[i-1] 为 (，那么 dp[i] = dp[i-2] + 2；
  - 当 s[i-1] 为 ) 并且 s[i-dp[i-1] - 1] 为 (，那么 dp[i] = dp[i-1] + 2 + dp[i-dp[i-1]-2]

最后一点不太好理解，其实可以这样理解，s[i] 和 s[i-1] 都是右括号），那么看第 i-1 的位置，当然是匹配到了 dp[i-1] 个，如果 s[i-1] 匹配到的 dp[i-1] 个之前的第 s[i-dp[i-1] - 1] 是左括号 (，那么其实仍然是最长的有效括号。i-dp[i-1]-1 就是与最后一个左括号匹配的位置，i-dp[i-1]-2 就是左括号之前的匹配位置，这个最长有效括号也要加到结果里。

# 代码

```java
class Solution {
    public int longestValidParentheses(String s) {
        int maxans = 0;
        int[] dp = new int[s.length()];
        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i) == ')') {
                if (s.charAt(i - 1) == '(') {
                    dp[i] = (i >= 2 ? dp[i - 2] : 0) + 2;
                } else if (i - dp[i - 1] > 0 && s.charAt(i - dp[i - 1] - 1) == '(') {
                    dp[i] = dp[i - 1] + ((i - dp[i - 1]) >= 2 ? dp[i - dp[i - 1] - 2] : 0) + 2;
                }
                maxans = Math.max(maxans, dp[i]);
            }
        }
        return maxans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！