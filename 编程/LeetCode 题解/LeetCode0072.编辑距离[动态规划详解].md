
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/edit-distance/)

给你两个单词 word1 和 word2，请你计算出将 word1 转换成 word2 所使用的最少操作数 。

你可以对一个单词进行如下三种操作：

	插入一个字符
	删除一个字符
	替换一个字符

 

示例 1：

```

输入：word1 = "horse", word2 = "ros"
输出：3
解释：
horse -> rorse （将 'h' 替换为 'r')
rorse -> rose （删除 'r')
rose -> ros （删除 'e')

```

示例 2：

```

输入：word1 = "intention", word2 = "execution"
输出：5
解释：
intention -> inention （删除 't')
inention -> enention （将 'i' 替换为 'e')
enention -> exention （将 'n' 替换为 'x')
exention -> exection （将 'n' 替换为 'c')
exection -> execution （插入 'u')

```

# 解题思路

定义 dp[i][j] 为 w1[0:i] 和 w2[0:j] 的编辑距离，则分为两种情况：
- w1[i] == w2[j]，则这个字符不用编辑，dp[i][j] = dp[i-1][j-1]
- w1[i] != w2[j]，则有三种情况：
  - 删除 w1[i]，则 dp[i][j] = dp[i-1][j] + 1
  - 删除 w2[j]，则 dp[i][j] = dp[i][j-1] + 1
  - 更改字符 w1[i] 或 w2[j]，则 dp[i][j] = dp[i-1][j-1] + 1

# 代码

```java
class Solution {
    public int minDistance(String w1, String w2) {
		int[][] dp = new int[w1.length() + 1][w2.length() + 1];
        for(int i = 0; i <= w1.length(); i++) {
            dp[i][0] = i;
        }
        for(int i = 0; i <= w2.length(); i++) {
            dp[0][i] = i;
        }
        
        for(int i = 1; i <= w1.length(); i++) {
           for(int j = 1; j <= w2.length(); j++) {
                if(w1.charAt(i - 1) == w2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    // 分别对应删、增、改
                    dp[i][j] = Math.min(Math.min(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1]) + 1;
                }
            } 
        }
        
        return dp[w1.length()][w2.length()];
    }
}
```

# 复杂度分析

- 时间复杂度：w1 的长度是 m，w2 的长度是 n，则复杂度是 O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！