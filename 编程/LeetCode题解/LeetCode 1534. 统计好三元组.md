
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/count-good-triplets/)

给你一个整数数组 arr ，以及 a、b 、c 三个整数。请你统计其中好三元组的数量。

如果三元组 (arr[i], arr[j], arr[k]) 满足下列全部条件，则认为它是一个 好三元组 。

	0 
	|arr[i] - arr[j]| 
	|arr[j] - arr[k]| 
	|arr[i] - arr[k]| 

其中 |x| 表示 x 的绝对值。

返回 好三元组的数量 。

 

示例 1：

```
输入：arr = [3,0,1,1,9,7], a = 7, b = 2, c = 3
输出：4
解释：一共有 4 个好三元组：[(3,0,1), (3,0,1), (3,1,1), (0,1,1)] 。

```

示例 2：

```
输入：arr = [1,1,2,2,3], a = 0, b = 0, c = 1
输出：0
解释：不存在满足所有条件的三元组。

```

# 解题思路

使用循环暴力求解，循环依次枚举所有的 (i,j,k)，判断这个 (i,j,k) 是否满足条件。

但是这样的时间复杂度是 O(n^3)，其实复杂度还是能够优化的。详情参考：https://leetcode-cn.com/problems/count-good-triplets/solution/tong-ji-hao-san-yuan-zu-by-leetcode-solution/

# 代码

```java
class Solution {
    public int countGoodTriplets(int[] arr, int a, int b, int c) {
        int n = arr.length, cnt = 0;
        for (int i = 0; i < n; ++i) {
            for (int j = i + 1; j < n; ++j) {
                for (int k = j + 1; k < n; ++k) {
                    if (Math.abs(arr[i] - arr[j]) <= a && Math.abs(arr[j] - arr[k]) <= b && Math.abs(arr[i] - arr[k]) <= c) {
                        ++cnt;
                    }
                }
            }
        }
        return cnt;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n^3)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！