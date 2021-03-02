
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/contains-duplicate-ii/)

给定一个整数数组和一个整数 k，判断数组中是否存在两个不同的索引 i 和 j，使得 nums [i] = nums [j]，并且 i 和 j 的差的 绝对值 至多为 k。

示例 1:

    输入：nums = [1,2,3,1], k = 3
    输出：true
示例 2:

    输入：nums = [1,0,1,1], k = 1
    输出：true
示例 3:

    输入：nums = [1,2,3,1,2,3], k = 2
    输出：false

# 解题思路

维护一个 map，key 是 nums 里的各项元素，value 是对应数值最后出现的索引。在遍历时：
- 如果发现一个元素曾经出现过，则判断 index 的差值是否满足要求，满足要求直接返回
- 元素没有出现过或不满足要求，直接更新 map 里对应元素的值

# 代码

```java
public boolean containsNearbyDuplicate(int[] nums, int k) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        if (map.containsKey(nums[i]) && i - map.get(nums[i]) <= k) {
            return true;
        } else {
            map.put(nums[i], i);
        }
    }
    return false;
}
```

# 复杂度分析

时间复杂度：$O(n)$

空间复杂度：$O(n)$

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！