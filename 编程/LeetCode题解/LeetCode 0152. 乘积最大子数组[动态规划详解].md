
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/maximum-product-subarray/)

给你一个整数数组 nums ，请你找出数组中乘积最大的连续子数组（该子数组中至少包含一个数字），并返回该子数组所对应的乘积。

 

示例 1:

```
输入：[2,3,-2,4]
输出：6
解释：子数组 [2,3] 有最大乘积 6。
```

示例 2:

```
输入：[-2,0,-1]
输出：0
解释：结果不能为 2, 因为 [-2,-1] 不是子数组。
```

# 解题思路

本题要求的是「乘积最大的子数组」，但是最大的乘积可能是两个正数相乘，也可能是两个负数相乘。定义 p[i] 为包含 i 的子数组最大乘积，n[i] 为包含 i 的子数组最小乘积。则记数组 nums[0:i] 的最大乘积值为 m：
- p[i] = max(p[i - 1] * nums[i], nums[i], n[i - 1] * nums[i])
- n[i] = min(p[i - 1] * nums[i], nums[i], n[i - 1] * nums[i])
- m = max(m, p[i])

# 代码

```java
class Solution {
    public int maxProduct(int[] nums) {
        int[] p = new int[nums.length];
        int[] n = new int[nums.length];
        int max = nums[0];
        p[0] = nums[0];
        n[0] = nums[0];
        for (int i = 1; i < nums.length; i++) {
            p[i] = Math.max(Math.max(p[i - 1] * nums[i], nums[i]), n[i - 1] * nums[i]);
            n[i] = Math.min(Math.min(p[i - 1] * nums[i], nums[i]), n[i - 1] * nums[i]);
            max = Math.max(max, p[i]);
        }
        return max;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！