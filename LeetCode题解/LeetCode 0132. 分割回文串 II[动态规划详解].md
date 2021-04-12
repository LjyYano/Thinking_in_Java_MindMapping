
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/palindrome-partitioning-ii/)

给你一个字符串 s，请你将 s 分割成一些子串，使每个子串都是回文。

返回符合要求的 最少分割次数。

 

示例 1：

```
输入：s = "aab"
输出：1
解释：只需一次分割就可将 s 分割成 ["aa","b"] 这样两个回文子串。
```

示例 2：

```
输入：s = "a"
输出：0
```

示例 3：

```
输入：s = "ab"
输出：1
```

# 解题思路

定义 dp[i][j] 为 s[i,j] 是否是回文。

则 dp[i][j] 的`状态转移方程`为：
- i==j，d[i][j]=true
- i+1==j && s.charAt(i) == s.charAt(j)，d[i][j]=true
- dp[i + 1][j - 1] && s.charAt(i) == s.charAt(j)，d[i][j]=true

记 f(i) 为字符串 s[0,i] 切割的最小分割次数，则 f(i) 的状态转移方程为：
- dp[0][i] 为 true，则表示 s[0,i] 本身就是一个回文字符串，并不需要切割，所以 f(i)=0
- dp[0][i] 为 false，则表示 s[0,i] 不是一个回文字符串，此时需要从 1 到 i-1 依次遍历（中间数值即为 j），如果 dp[j][i] 为 true 时，s[0,j-1] 的最小切割次数为 f(j-1)，且 s[j][i] 是回文字符串，所以从 j-1 到 j 这个位置分割依次就可以了，即 f[i] = Math.min(f[i], f[j - 1] + 1)。遍历后 f(i) 取最小值即可。

# 代码

```java
class Solution {
    public int minCut(String s) {
        int n = s.length();
        boolean[][] dp = new boolean[n][n];
        for (int j = 0; j < n; j++) {
            for (int i = j; i >= 0; i--) {
                if (i == j) {
                    // 本身就是回文
                    dp[i][j] = true;
                } else if (i + 1 == j) {
                    // 如果两个字符是相邻的，则需要判断
                    dp[i][j] = s.charAt(i) == s.charAt(j);
                } else {
                    dp[i][j] = dp[i + 1][j - 1] && s.charAt(i) == s.charAt(j);
                }
            }
        }

        int[] f = new int[n];
        for (int i = 1; i < n; i++) {
            if (dp[0][i]) {
                f[i] = 0;
            } else {
                f[i] = f[i - 1] + 1;
                for (int j = 1; j < i; j++) {
                    if (dp[j][i]) {
                        f[i] = Math.min(f[i], f[j - 1] + 1);
                    }
                }
            }
        }
        return f[n - 1];
    }
}
```

# 复杂度分析

- 时间复杂度：记字符串 s 的长度是 n，则复杂度是 O(n^2)
- 空间复杂度：O(n^2)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！