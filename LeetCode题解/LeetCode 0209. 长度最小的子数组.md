
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/minimum-size-subarray-sum/)

给定一个含有 n 个正整数的数组和一个正整数 target 。

找出该数组中满足其和 ≥ target 的长度最小的 连续子数组 [numsl, numsl+1, ..., numsr-1, numsr] ，并返回其长度。如果不存在符合条件的子数组，返回 0 。

 

示例 1：

```

输入：target = 7, nums = [2,3,1,2,4,3]
输出：2
解释：子数组 [4,3] 是该条件下的长度最小的子数组。

```

示例 2：

```

输入：target = 4, nums = [1,4,4]
输出：1

```

示例 3：

```

输入：target = 11, nums = [1,1,1,1,1,1,1,1]
输出：0

```

进阶：

	如果你已经实现 O(n) 时间复杂度的解法，请尝试设计一个 O(n log(n)) 时间复杂度的解法。

# 解题思路

这道题是要找长度最小的连续子数组，可以使用滑动窗口，核心思路就是维护滑动窗口的两个数值，start 和 end：
- 如果 sum[start, end]<target，就 end++，此时 start,end-1] 是可能的结果
- 如果 sum[start, end]>=target，就 start++，直到 sum[start, end]<target，此时 [start-1,end] 是可能的结果（因为 start 已经++了）

# 代码

```java
class Solution {
    public int minSubArrayLen(int s, int[] nums) {
        int start = 0, end = 0, sum = 0, ans = Integer.MAX_VALUE;
        while (end < nums.length && start < nums.length) {

            // 滑动窗口，end，找到 [start, end] 的和>=s
            while (end < nums.length && sum < s) {
                sum += nums[end++];
                // [start,end-1] 是可能的结果
                if (sum >= s) {
                    ans = Math.min(ans, end - start);
                }
            }

            // 滑动窗口，start，找到 [start, end] 的和<s
            while (start < nums.length && sum >= s) {
                sum -= nums[start++];
                // [start-1,end] 是可能的结果
                if (sum < s) {
                    ans = Math.min(ans, end - start + 1);
                }
            }
        }

        return ans == Integer.MAX_VALUE ? 0 : ans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！