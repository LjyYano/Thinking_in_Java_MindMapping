
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/minimum-increment-to-make-array-unique/)

给定整数数组 A，每次 move 操作将会选择任意 A[i]，并将其递增 1。

返回使 A 中的每个值都是唯一的最少操作次数。

示例 1:

```
输入：[1,2,2]
输出：1
解释：经过一次 move 操作，数组将变为 [1, 2, 3]。
```

示例 2:

```
输入：[3,2,1,2,1,7]
输出：6
解释：经过 6 次 move 操作，数组将变为 [3, 4, 1, 2, 5, 7]。
可以看出 5 次或 5 次以下的 move 操作是不能让数组的每个值唯一的。

```

# 解题思路

先对数组排序，之后对于每个元素，如果比前一个元素小，就一直加到比前一个元素大即可。每加一次，就是一次增量。

# 代码

```java
class Solution {
    public int minIncrementForUnique(int[] A) {
        Arrays.sort(A);
        int ans = 0;
        for (int i = 1; i < A.length; i++) {
            if (A[i] <= A[i - 1]) {
                ans += A[i - 1] - A[i] + 1;
                A[i] = A[i - 1] + 1;
            }
        }
        return ans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(nlogn)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！