
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/interleaving-string/)

给定三个字符串 s1、s2、s3，请你帮忙验证 s3 是否是由 s1 和 s2 交错 组成的。

两个字符串 s 和 t 交错 的定义与过程如下，其中每个字符串都会被分割成若干 非空 子字符串：

	s = s1 + s2 + ... + sn
	t = t1 + t2 + ... + tm
	|n - m| 
	交错 是 s1 + t1 + s2 + t2 + s3 + t3 + ... 或者 t1 + s1 + t2 + s2 + t3 + s3 + ...

提示：a + b 意味着字符串 a 和 b 连接。

 

示例 1：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210320102012.png?x-oss-process=style/yano)

```

输入：s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"
输出：true

```

示例 2：

```

输入：s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"
输出：false

```

示例 3：

```

输入：s1 = "", s2 = "", s3 = ""
输出：true

```

# 解题思路

定义 dp[i][j] 为 s1[i-1] 和 s2[j-1] 能否组成 s3[i+j-1]

则`状态转移方程`为：
- dp[i][j] = (dp[i][j-1] == 1 && s3[i+j-1] == s2[j])，即假设 dp[i][j-1] 是符合要求的，那么 s2[j] 和 s3[i+j-1] 相同，则 s2[j-1] 可以组成答案。
- dp[i][j] = (dp[i-1][j] == 1 && s3[i+j-1] == s1[i])，即假设 dp[i-1][j] 是符合要求的，那么 s1[i] 和 s3[i+j-1] 相同，则 s1[i-1] 可以组成答案。

下面以题目中的示例 1 为例：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210320102215.png?x-oss-process=style/yano)

最终 dp[s1.length()][s2.length()] 就是最终的答案，如果有答案的话，红色字体的路径即为答案（当然路径可能有多条）。

# 代码

```java
class Solution {
    public boolean isInterleave(String s1, String s2, String s3) {
        if (s1.length() + s2.length() != s3.length()) {
            return false;
        }
        int n1 = s1.length(), n2 = s2.length();
        boolean[][] dp = new boolean[n1 + 1][n2 + 1];
        dp[0][0] = true;
        for (int i = 0; i < s1.length(); i++) {
            if (s3.charAt(i) == s1.charAt(i)) {
                dp[i + 1][0] = true;
            } else {
                break;
            }
        }
        for (int i = 0; i < s2.length(); i++) {
            if (s3.charAt(i) == s2.charAt(i)) {
                dp[0][i + 1] = true;
            } else {
                break;
            }
        }
        // dp[i][j] = (dp[i][j-1] == 1 && s3[i+j-1] == s2[j-1]) || (dp[i-1][j] == 1 && s3[i+j-1] == s1[i-1])
        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                if (dp[i][j - 1] && s3.charAt(i + j - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = true;
                }
                if (dp[i - 1][j] && s3.charAt(i + j - 1) == s1.charAt(i - 1)) {
                    dp[i][j] = true;
                }
            }
        }
        return dp[n1][n2];
    }
}
```

# 复杂度分析

- 时间复杂度：设 s1 的长度是 m，s2 的长度是 n，则时间复杂度是 O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！