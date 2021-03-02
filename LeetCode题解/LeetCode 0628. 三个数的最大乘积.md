
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/maximum-product-of-three-numbers/)

给你一个整型数组 nums ，在数组中找出由三个数组成的最大乘积，并输出这个乘积。

示例 1：

    输入：nums = [1,2,3]
    输出：6
示例 2：

    输入：nums = [1,2,3,4]
    输出：24
示例 3：

    输入：nums = [-1,-2,-3]
    输出：-6
 

提示：

    3 <= nums.length <= 10^4
    -1000 <= nums[i] <= 1000

# 解题思路

因为题目说 nums 是整数，里面可能有负数存在，2 个负数的乘积也为正数。所以结果的可能取值为：
- 最小的负数 * 次小的负数 * 最大的正数
- 最大的正数*次大的正数*第 3 大的正数

下面的代码直接使用了排序，如果不使用排序的话，就维护上面的 5 个遍历，能把时间复杂度降低到 O(n)，空间复杂度降低到 O(1)

# 代码

```java
public int maximumProduct(int[] nums) {
    Arrays.sort(nums);
    int n = nums.length;
    return Math.max(nums[0] * nums[1] * nums[n - 1], nums[n - 3] * nums[n - 2] * nums[n - 1]);
}
```

# 复杂度分析

时间复杂度：$O(nlogn)$

空间复杂度：$O(logn)$ （因为快排的空间复杂度）

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！