
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/regular-expression-matching/)

给你一个字符串 s 和一个字符规律 p，请你来实现一个支持 '.' 和 '*' 的正则表达式匹配。

	'.' 匹配任意单个字符
	'*' 匹配零个或多个前面的那一个元素

所谓匹配，是要涵盖 整个 字符串 s 的，而不是部分字符串。
 

示例 1：

```

输入：s = "aa" p = "a"
输出：false
解释："a" 无法匹配 "aa" 整个字符串。

```

示例 2:

```

输入：s = "aa" p = "a*"
输出：true
解释：因为 '*' 代表可以匹配零个或多个前面的那一个元素，在这里前面的元素就是 'a'。因此，字符串 "aa" 可被视为 'a' 重复了一次。

```

示例 3：

```

输入：s = "ab" p = ".*"
输出：true
解释：".*" 表示可匹配零个或多个（'*'）任意字符（'.'）。

```

示例 4：

```

输入：s = "aab" p = "c*a*b"
输出：true
解释：因为 '*' 表示零个或多个，这里 'c' 为 0 个，'a' 被重复一次。因此可以匹配字符串 "aab"。

```

示例 5：

```

输入：s = "mississippi" p = "mis*is*p*."
输出：false
```

# 解题思路

要判断正则表达式匹配，题目中正则的要求是：
- '.' 匹配任意单个字符
- '*' 匹配零个或多个前面的那一个元素

定义用 f[i][j] 表示 s 的前 i 个字符与 p 中的前 j 个字符是否能够匹配。其是一个布尔变量，true 表示能够匹配，false 表示不能匹配。

我们考虑 p 的第 j 个字符，一共有 3 种情况：

- 是普通字符，则在 s[i]==p[j] 的情况下，f[i][j]=f[i-1][j-1]；否则 f[i][j]=false
- 是字符。，这个无论 s[i] 是什么字符，都可以匹配，f[i][j]=f[i-1][j-1]
- 是字符*，这个要分几种情况：
  - 在 s[i]!=p[j-1] 时，p[j-1] 这个字符不使用，则 f[i][j]=f[i][j-2]，这个可以理解为 p[j-1]+p[j] 这个组合没有参与到匹配当中
  - 在 s[i]==p[j-1] 时，有两种情况
    - 不使用该组合，这个情况和上面的一样，此时 f[i][j]=f[i][j-2]
    - p[j-1][j](即 p[j-1]*) 这个组合匹配了 s[i]，同时该组合可能仍然可以继续向前匹配，此时 f[i][j]=f[i-1][j] or f[i][j-2]

则`状态转移方程`为：

![20210301222210](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210301222210.png)

# 代码

```java
class Solution {
    public boolean isMatch(String s, String p) {
        int m = s.length();
        int n = p.length();

        boolean[][] f = new boolean[m + 1][n + 1];
        f[0][0] = true;
        for (int i = 0; i <= m; ++i) {
            for (int j = 1; j <= n; ++j) {
                if (p.charAt(j - 1) == '*') {
                    f[i][j] = f[i][j - 2];
                    if (matches(s, p, i, j - 1)) {
                        f[i][j] = f[i][j] || f[i - 1][j];
                    }
                } else {
                    if (matches(s, p, i, j)) {
                        f[i][j] = f[i - 1][j - 1];
                    }
                }
            }
        }
        return f[m][n];
    }

    public boolean matches(String s, String p, int i, int j) {
        if (i == 0) {
            return false;
        }
        if (p.charAt(j - 1) == '.') {
            return true;
        }
        return s.charAt(i - 1) == p.charAt(j - 1);
    }
}
```

# 复杂度分析

- 时间复杂度：O(n^2)
- 空间复杂度：O(n^2)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！