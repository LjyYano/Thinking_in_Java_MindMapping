
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/decrease-elements-to-make-array-zigzag/)

给你一个整数数组 nums，每次 操作 会从中选择一个元素并 将该元素的值减少 1。

如果符合下列情况之一，则数组 A 就是 锯齿数组：

	每个偶数索引对应的元素都大于相邻的元素，即 A[0] > A[1]  A[3]  ...
	或者，每个奇数索引对应的元素都大于相邻的元素，即 A[0]  A[2]  A[4] 

返回将数组 nums 转换为锯齿数组所需的最小操作次数。

 

示例 1：

```
输入：nums = [1,2,3]
输出：2
解释：我们可以把 2 递减到 0，或把 3 递减到 1。

```

示例 2：

```
输入：nums = [9,6,1,6,2]
输出：4

```

# 解题思路

这道题第一眼看上去很难，但是细想一共就两种情况：
- 每个偶数索引对应的元素都大于相邻的元素
- 每个奇数索引对应的元素都大于相邻的元素

如果只是上述一种情况的话，就比较简单。题目需要将 2 种情况都计算一遍即可。

# 代码

```java
class Solution {
    public int movesToMakeZigzag(int[] nums) {
        int oddNumberCount = 0;
        int evenNumberCount = 0;
        for (int i = 0; i < nums.length; i++) {
            int l = i - 1;
            int r = i + 1;
            int leftGap = 0;
            int rightGap = 0;
            //计算自身比左边大多少->自身需要递减几步能达到小于左边
            if (l >= 0) {
                leftGap = Math.max(nums[i] - nums[l] + 1, 0);
            }
            //计算自身比右边大多少->自身需要递减几步能达到小于右边
            if (r <= nums.length - 1) {
                rightGap = Math.max(nums[i] - nums[r] + 1, 0);
            }
            //如果自身时偶数，则 count 在偶数需要递减的次数
            if (i % 2 == 0) {
                evenNumberCount += Math.max(leftGap, rightGap);
            } else {
                //否则，则 count 在奇数需要递减的次数
                oddNumberCount += Math.max(leftGap, rightGap);
            }
        }
        //返回小值
        return Math.min(oddNumberCount, evenNumberCount);
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！