
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/distinct-subsequences/)

给定一个字符串 s 和一个字符串 t ，计算在 s 的子序列中 t 出现的个数。

字符串的一个 子序列 是指，通过删除一些（也可以不删除）字符且不干扰剩余字符相对位置所组成的新字符串。（例如，"ACE" 是 "ABCDE" 的一个子序列，而 "AEC" 不是）

题目数据保证答案符合 32 位带符号整数范围。

 

示例 1：

```

输入：s = "rabbbit", t = "rabbit"
输出：3
解释：
如下图所示，有 3 种可以从 s 中得到 "rabbit" 的方案。
（上箭头符号 ^ 表示选取的字母）
rabbbit
^^^^ ^^
rabbbit
^^ ^^^^
rabbbit
^^^ ^^^

```

示例 2：

```

输入：s = "babgbag", t = "bag"
输出：5
解释：
如下图所示，有 5 种可以从 s 中得到 "bag" 的方案。 
（上箭头符号 ^ 表示选取的字母）
babgbag
^^ ^
babgbag
^^    ^
babgbag
^    ^^
babgbag
  ^  ^^
babgbag
    ^^^
```

# 解题思路

定义 dp[i][j] 为 s[i] 和 t[j] 所组成的不同的子序列数量。

则`状态转移方程`为：

- s[i]==t[j]：dp[i][j]=dp[i-1][j-1]+dp[i-1][j]，dp[i-1][j-1] 表示用了 s[i]，dp[i-1][j] 表示不用 s[i]
- s[i]!=t[j]：dp[i][j]=dp[i-1][j]，表示不用 s[i]

下面以题目中的示例 1 为例：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210321095320.png?x-oss-process=style/yano)

# 代码

```java
class Solution {
    public int numDistinct(String s, String t) {
        int[][] dp = new int[s.length() + 1][t.length() + 1];
        for (int i = 0; i < dp.length; i++) {
            dp[i][0] = 1;
        }
        for (int i = 0; i < s.length(); i++) {
            for (int j = 0; j < t.length(); j++) {
                if (s.charAt(i) == t.charAt(j)) {
                    dp[i + 1][j + 1] = dp[i][j] + dp[i][j + 1];
                } else {
                    dp[i + 1][j + 1] = dp[i][j + 1];
                }
            }
        }
        return dp[s.length()][t.length()];
    }
}
```

# 复杂度分析

- 时间复杂度：设 s 的长度是 t 的长度是 n，则时间复杂度是 O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！