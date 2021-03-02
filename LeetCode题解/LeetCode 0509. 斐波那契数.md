
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/fibonacci-number/)

斐波那契数，通常用 F(n) 表示，形成的序列称为 斐波那契数列 。该数列由 0 和 1 开始，后面的每一项数字都是前面两项数字的和。也就是：

```

F(0) = 0，F(1) = 1
F(n) = F(n - 1) + F(n - 2)，其中 n > 1

```

给你 n ，请计算 F(n) 。

 

示例 1：

```

输入：2
输出：1
解释：F(2) = F(1) + F(0) = 1 + 0 = 1

```

示例 2：

```

输入：3
输出：2
解释：F(3) = F(2) + F(1) = 1 + 1 = 2

```

示例 3：

```

输入：4
输出：3
解释：F(4) = F(3) + F(2) = 2 + 1 = 3

```

# 解题思路

非常经典的题目，不解释（就是这么高冷）~

# 代码

```java
class Solution {
    public int fib(int n) {
        if(n <= 1) {
            return n;
        }
        int f0 = 0, f1 = 1;
        for(int i = 2; i < n; i++) {
            int f = f0 + f1;
            f0 = f1;
            f1 = f;
        }
        return f0 + f1;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！