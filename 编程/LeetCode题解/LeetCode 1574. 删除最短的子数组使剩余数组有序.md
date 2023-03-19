
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/shortest-subarray-to-be-removed-to-make-array-sorted/)

给你一个整数数组 arr ，请你删除一个子数组（可以为空），使得 arr 中剩下的元素是 非递减 的。

一个子数组指的是原数组中连续的一个子序列。

请你返回满足题目要求的最短子数组的长度。

示例 1：

```

输入：arr = [1,2,3,10,4,2,3,5]
输出：3
解释：我们需要删除的最短子数组是 [10,4,2] ，长度为 3 。剩余元素形成非递减数组 [1,2,3,3,5] 。
另一个正确的解为删除子数组 [3,10,4] 。
```

示例 2：

```

输入：arr = [5,4,3,2,1]
输出：4
解释：由于数组是严格递减的，我们只能保留一个元素。所以我们需要删除长度为 4 的子数组，要么删除 [5,4,3,2]，要么删除 [4,3,2,1]。
```

示例 3：

```
输入：arr = [1,2,3]
输出：0
解释：数组已经是非递减的了，我们不需要删除任何元素。
```

示例 4：

```
输入：arr = [1]
输出：0
```

# 解题思路

找到左边 sorted 段，和右边 sorted 段，从两边往里夹逼，找到最小的删除子数组。

比如对于数组 [1,2,3,10,4,2,3,5]，先找到左边排序的段 1,2,3,10，右边排序的段 2,3,5，对于左边数组的第 i 位，和右边数组的第 j 位进行比较
- 如果 num[i]<=num[j]，表示如果左边数组索引 i 向后移动一位的话，更新下结果，并移动下 i
- 否则 num[i]>num[j]，表示左边比右边大，那么结果肯定在 j+1 开始的数组中

# 代码

```java
public int findLengthOfShortestSubarray(int[] arr) {
    int n = arr.length;
    int left = 0;
    while (left + 1 < n && arr[left] <= arr[left + 1]) {
        left++;
    }
    if (left == n - 1) {
        return 0;
    }
    int right = n - 1;
    while (right > 0 && arr[right - 1] <= arr[right]) {
        right--;
    }

    int res = Math.min(n - left - 1, right);

    int i = 0, j = right;

    while (i <= left && j <= n - 1) {
        if (arr[i] <= arr[j]) {
            res = Math.min(res, j - i - 1);
            i++;
        } else {
            j++;
        }
    }
    return res;
}
```

# 复杂度分析

- 时间复杂度：O()
- 空间复杂度：O()

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！