
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/longest-palindromic-substring/)

给你一个字符串 s，找到 s 中最长的回文子串。

 

示例 1：

```

输入：s = "babad"
输出："bab"
解释："aba" 同样是符合题意的答案。

```

示例 2：

```

输入：s = "cbbd"
输出："bb"

```

示例 3：

```

输入：s = "a"
输出："a"

```

示例 4：

```

输入：s = "ac"
输出："a"

```

# 解题思路

本题可以使用动态规划来做，但是直接遍历每个字符串/每两个字符串空隙，向左右延展求最长回文子串也是可以的，思路比较暴力直接，详情见代码 1。

动态规划的思路：定义 f(i,j) 为字符串从 i 到 j 个字符组成的串是否为回文串，子串通过 s[i:j] 表示：

- f(i,j) = true, 如果 s[i:j] 是回文串
- f(i,j) = false, 如果 s[i:j] 不是回文串

则`状态转移方程`为：

	f(i,j) = f(i+1,j-1) & (s 的 i 字符==s 的 j 字符）

这个方程也很好理解，如果 s[4:5] 是回文串，且 s[3]==s[6]，那么 s[3:6] 肯定也是回文串。见代码2。

# 代码

代码 1

```java
class Solution {
	public String longestPalindrome(String s) {
		int pos = 0, ans = 0, p0 = 0, p1 = 0;
		while (pos < s.length()) {
			for (int i = 0; i <= 1; i++) {
				int start = pos, end = pos + i;
				while (start >= 0 && end < s.length()) {
					if (s.charAt(start) == s.charAt(end)) {
						start--;
						end++;
					} else {
						break;
					}
				}
				if (ans < end - start - 1) {
					ans = end - start - 1;
					p0 = start;
					p1 = end;
				}
			}
			pos++;
		}
		return s.substring(p0 + 1, p1);
	}
}
```

代码2：

```java
class Solution {
    public String longestPalindrome(String s) {
        int n = s.length();
        boolean[][] dp = new boolean[n][n];
        String ans = "";
        for (int l = 0; l < n; ++l) {
            for (int i = 0; i + l < n; ++i) {
                int j = i + l;
                if (l == 0) {
                    dp[i][j] = true;
                } else if (l == 1) {
                    dp[i][j] = (s.charAt(i) == s.charAt(j));
                } else {
                    dp[i][j] = (s.charAt(i) == s.charAt(j) && dp[i + 1][j - 1]);
                }
                if (dp[i][j] && l + 1 > ans.length()) {
                    ans = s.substring(i, i + l + 1);
                }
            }
        }
        return ans;
    }
}
```

# 复杂度分析

使用动态规划时：
- 时间复杂度：O(n^2)
- 空间复杂度：O(n^2)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！