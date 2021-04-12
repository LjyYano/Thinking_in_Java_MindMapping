
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/decode-ways/)

一条包含字母 A-Z 的消息通过以下映射进行了 编码 ：

```

'A' -> 1
'B' -> 2
...
'Z' -> 26

```

要 解码 已编码的消息，所有数字必须基于上述映射的方法，反向映射回字母（可能有多种方法）。例如，"111" 可以将 "1" 中的每个 "1" 映射为 "A" ，从而得到 "AAA" ，或者可以将 "11" 和 "1"（分别为 "K" 和 "A" ）映射为 "KA" 。注意，"06" 不能映射为 "F" ，因为 "6" 和 "06" 不同。

给你一个只含数字的 非空 字符串 num ，请计算并返回 解码 方法的 总数 。

题目数据保证答案肯定是一个 32 位 的整数。

 

示例 1：

```

输入：s = "12"
输出：2
解释：它可以解码为 "AB"（1 2）或者 "L"（12）。

```

示例 2：

```

输入：s = "226"
输出：3
解释：它可以解码为 "BZ" (2 26), "VF" (22 6), 或者 "BBF" (2 2 6) 。

```

示例 3：

```

输入：s = "0"
输出：0
解释：没有字符映射到以 0 开头的数字。含有 0 的有效映射是 'J' -> "10" 和 'T'-> "20" 。由于没有字符，因此没有有效的方法对此进行解码，因为所有数字都需要映射。

```

示例 4：

```

输入：s = "06"
输出：0
解释："06" 不能映射到 "F" ，因为字符串开头的 0 无法指向一个有效的字符。 

```

# 解题思路

这个和爬楼梯是一个类型，爬楼梯是可以爬一个台阶，也可以爬两个台阶，没有限制。但是这道题是有限制的，假设当前位置是 i，则 
- s[i] 不是 0，才能走到下一步；
- s[i, i + 1] >= 10 && s[i, i + 1] <= 26，才能走两步。

定义 dp[i] 为到第 i 个字符的解码方法总数，则：
- s[i - 1] != 0，则 dp[i] += dp[i - 1]
- s[i-2, i-1] >= 10 && s[i-2, i-1] <= 26，则 dp[i] += dp[i - 2]

# 代码

```java
class Solution {
    public int numDecodings(String s) {
        if(s == null || s.length() == 0) return 0;
        int len = s.length();
        int[] dp = new int[len + 1];
        dp[0] = 1;
        if(s.charAt(0) != '0') dp[1] = 1;
        
        for(int i = 2; i < len + 1; i ++){
            if(s.charAt(i - 1) != '0')
                dp[i] += dp[i - 1];
            int val = Integer.valueOf(s.substring(i - 2, i));
            if(val >= 10 && val <= 26)
                dp[i] += dp[i - 2];
        }
        return dp[len];
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！