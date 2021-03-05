
- [题目描述](#题目描述)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/maximum-subarray/)

给定一个整数数组 nums ，找到一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。

 

示例 1：

```

输入：nums = [-2,1,-3,4,-1,2,1,-5,4]
输出：6
解释：连续子数组 [4,-1,2,1] 的和最大，为 6 。

```

示例 2：

```

输入：nums = [1]
输出：1

```

示例 3：

```

输入：nums = [0]
输出：0

```

示例 4：

```

输入：nums = [-1]
输出：-1

```

示例 5：

```

输入：nums = [-100000]
输出：-100000

``` 

进阶：如果你已经实现复杂度为 O(n) 的解法，尝试使用更为精妙的 分治法 求解。

# 解题思路

定义 dp[i] 为 nums 中以 i 为结尾的连续子数组的最大和，则 dp[i] 要么是只使用了 nums[i]，要么是使用了 dp[i-1] + nums[i]

则`状态转移方程`为：

dp[i] = Math.max(nums[i] + dp[i - 1], nums[i]);

其实上述是可以优化的，只要 dp[i-1] 是>0 的，那么对结果就有贡献，dp 数组可以节省为 1 个变量，空间复杂度可以从 O(n) 减少到 O(1)。不过动态规划能把状态转移方程写出来就好了，其余的都是细节问题。

# 代码

```java
class Solution {
    public int maxSubArray(int[] nums) {
        if(nums == null) return 0;
        // 数组可省略
        int[] result = new int[nums.length];
        int max = nums[0];
        result[0] = nums[0];
        for(int i = 1; i < nums.length; i++) {
            // f(i + 1) = max(f(i) + n[i + 1], n[i + 1])
            result[i] = Math.max(nums[i] + result[i - 1], nums[i]);
            max = Math.max(max, result[i]);
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