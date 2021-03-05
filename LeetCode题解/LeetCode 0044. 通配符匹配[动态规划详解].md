
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/wildcard-matching/)

给定一个字符串 (s) 和一个字符模式 (p) ，实现一个支持 '?' 和 '*' 的通配符匹配。

```
'?' 可以匹配任何单个字符。
'*' 可以匹配任意字符串（包括空字符串）。

```

两个字符串完全匹配才算匹配成功。

说明：

	s 可能为空，且只包含从 a-z 的小写字母。
	p 可能为空，且只包含从 a-z 的小写字母，以及字符 ? 和 *。

示例 1:

```
输入：
s = "aa"
p = "a"
输出：false
解释："a" 无法匹配 "aa" 整个字符串。
```

示例 2:

```
输入：
s = "aa"
p = "*"
输出：true
解释：'*' 可以匹配任意字符串。

```

示例 3:

```
输入：
s = "cb"
p = "?a"
输出：false
解释：'?' 可以匹配 'c', 但第二个 'a' 无法匹配 'b'。

```

示例 4:

```
输入：
s = "adceb"
p = "*a*b"
输出：true
解释：第一个 '*' 可以匹配空字符串，第二个 '*' 可以匹配字符串 "dce".

```

示例 5:

```
输入：
s = "acdcb"
p = "a*c?b"
输出：false
```

# 解题思路

定义 dp[i][j] 为 s[0:i] 与 p[0:j] 是否完全匹配，可以对 p[j] 区分以下几种情况：

- p[j] 是 a~z 几个字符，此时 dp[i][j] = dp[i-1][j-1] & (s[i-1] == p[j-1])
- p[j] == '?'，因为'?'能够匹配任意字符，所以 p[j] 肯定能匹配到 s[i]，所以 dp[i][j]=dp[i-1][j-1]
- p[j] == '\*'，这种情况最复杂，因为 '\*' 可以匹配任意字符串
  - 若匹配空字符串，即 p[j] 不参与匹配，则 dp[i][j] = dp[i][j-1]
  - 若不匹配空字符串，因为 p[j] 能够匹配任意字符串，所以 p[j] 匹配了 s[i]，可能还能够继续匹配，则 dp[i][j] = dp[i-1][j]

则`状态转移方程`为：

![20210303180007](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210303180007.png)

下面以示例 4 为例：

![20210303180116](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210303180116.png)

假设已经分析到了图中绿色方框的部分，此时 p[3] 是星号，s[3] 是字符 c，那么 dp[3][3] 有两种可能：
- p[3] 不参与匹配，则看 dp[3][2]，值为 0
- p[3] 参与匹配，则看 dp[2][3]，值为 1

![20210303180610](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210303180610.png)

最终匹配到的流程是上图的红字路径。

# 代码

```java
class Solution {
    public boolean isMatch(String s, String p) {
		char[] string = s.toCharArray();
		char[] pattern = p.toCharArray();
		boolean[][] dp = new boolean[string.length + 1][pattern.length + 1];
		dp[0][0] = true;
        
        for(int i = 1; i <= pattern.length; i++) {
            if(pattern[i - 1] == '*') dp[0][i] = dp[0][i - 1];
        }

		for (int i = 1; i <= string.length; i++) {
			for (int j = 1; j <= pattern.length; j++) {
				if (pattern[j - 1] == '*') {
					dp[i][j] = dp[i - 1][j] || dp[i][j - 1];
				} else if (string[i - 1] == pattern[j - 1] || pattern[j - 1] == '?') {
					dp[i][j] = dp[i - 1][j - 1];
				}
			}
		}

		return dp[string.length][pattern.length];
	}
}
```

# 复杂度分析

- 时间复杂度：设 s 的长度是 m，p 的长度是 n，则复杂度是 O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！