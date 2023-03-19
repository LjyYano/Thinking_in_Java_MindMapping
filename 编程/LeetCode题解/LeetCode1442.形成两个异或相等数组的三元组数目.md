
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/count-triplets-that-can-form-two-arrays-of-equal-xor/)

给你一个整数数组 arr 。

现需要从数组中取三个下标 i、j 和 k ，其中 (0  。

a 和 b 定义如下：

	a = arr[i] ^ arr[i + 1] ^ ... ^ arr[j - 1]
	b = arr[j] ^ arr[j + 1] ^ ... ^ arr[k]

注意：^ 表示 按位异或 操作。

请返回能够令 a == b 成立的三元组 (i, j , k) 的数目。

 

示例 1：

```
输入：arr = [2,3,1,6,7]
输出：4
解释：满足题意的三元组分别是 (0,1,2), (0,2,2), (2,3,4) 以及 (2,4,4)

```

示例 2：

```
输入：arr = [1,1,1,1,1]
输出：10

```

示例 3：

```
输入：arr = [2,3]
输出：0

```

示例 4：

```
输入：arr = [1,3,5,7,9]
输出：3

```

示例 5：

```
输入：arr = [7,11,12,9,5,2,7,17,22]
输出：8
```

# 解题思路

遍历数组中的每个元素，从这个元素为起点，只要找到一段区间 [i,k] 的 xor 为 0，则区间中的任意一个位置都可以作为 j（j≠i,k）

# 代码

```java
class Solution {
    public int countTriplets(int[] arr) {
        int n = arr.length;
        int ans = 0;
        // 遍历数组中的每个元素
        for (int i = 0; i < n; ++i) {
            int xorsum = 0;
            // 从这个元素为起点，只要找到一段区间 [i,k] 的 xor 为 0，则区间中的任意一个位置都可以作为 j（j≠i,k）
            for (int k = i; k < n; ++k) {
                xorsum ^= arr[k];
                if (xorsum == 0) {
                    ans += k - i;
                }
            }
        }
        return ans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n^2)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！