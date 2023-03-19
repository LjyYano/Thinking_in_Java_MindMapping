
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/)

给你一个整数数组 nums ，和一个表示限制的整数 limit，请你返回最长连续子数组的长度，该子数组中的任意两个元素之间的绝对差必须小于或者等于 limit 。

如果不存在满足条件的子数组，则返回 0 。

 

示例 1：

    输入：nums = [8,2,4,7], limit = 4
    输出：2 
    解释：所有子数组如下：
    [8] 最大绝对差 |8-8| = 0 <= 4.
    [8,2] 最大绝对差 |8-2| = 6 > 4. 
    [8,2,4] 最大绝对差 |8-2| = 6 > 4.
    [8,2,4,7] 最大绝对差 |8-2| = 6 > 4.
    [2] 最大绝对差 |2-2| = 0 <= 4.
    [2,4] 最大绝对差 |2-4| = 2 <= 4.
    [2,4,7] 最大绝对差 |2-7| = 5 > 4.
    [4] 最大绝对差 |4-4| = 0 <= 4.
    [4,7] 最大绝对差 |4-7| = 3 <= 4.
    [7] 最大绝对差 |7-7| = 0 <= 4. 
    因此，满足题意的最长子数组的长度为 2 。
示例 2：

    输入：nums = [10,1,2,4,7,2], limit = 5
    输出：4 
    解释：满足题意的最长子数组是 [2,4,7,2]，其最大绝对差 |2-7| = 5 <= 5 。
示例 3：

    输入：nums = [4,2,2,2,4,4,2,2], limit = 0
    输出：3
 

提示：

    1 <= nums.length <= 10^5
    1 <= nums[i] <= 10^9
    0 <= limit <= 10^9

# 解题思路

本题的本质是`滑动窗口`，不过需要找到滑动窗口的滑动条件。

1. 如果滑动窗口内的最大元素-最小元素>limit，则表示窗口内有元素不符合题目的要求，则左边的索引应该向右移动，直到满足条件位置；
2. 接着移动右边的索引，直到不满足最大元素-最小元素<=limit 这个条件，重复步骤 1

# 代码

```java
public int longestSubarray(int[] nums, int limit) {
    TreeMap<Integer, Integer> treeMap = new TreeMap<>();
    int l = 0, r = 0, ans = 0;
    while (r < nums.length) {
        int n = nums[r];
        treeMap.put(n, treeMap.getOrDefault(n, 0) + 1);
        r++;
        // 若移动之后，不符合条件
        while (l <= r && treeMap.lastKey() - treeMap.firstKey() > limit) {
            if (treeMap.get(nums[l]) == 1) {
                treeMap.remove(nums[l]);
            } else {
                treeMap.put(nums[l], treeMap.get(nums[l]) - 1);
            }
            l++;
        }
        ans = Math.max(ans, r - l);
    }
    return ans;
}
```

# 复杂度分析

- 时间复杂度：$O(n)$
- 空间复杂度：$O(n)$

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！