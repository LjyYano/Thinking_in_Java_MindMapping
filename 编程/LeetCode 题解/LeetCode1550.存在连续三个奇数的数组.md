
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/three-consecutive-odds/)

给你一个整数数组 arr，请你判断数组中是否存在连续三个元素都是奇数的情况：如果存在，请返回 true ；否则，返回 false 。

示例 1：

    输入：arr = [2,6,4,1]
    输出：false
    解释：不存在连续三个元素都是奇数的情况。
示例 2：

    输入：arr = [1,2,34,3,4,5,7,23,12]
    输出：true
    解释：存在连续三个元素都是奇数的情况，即 [5,7,23] 。
 

提示：

    1 <= arr.length <= 1000
    1 <= arr[i] <= 1000

# 解题思路

本题属于简单题，没啥好说的，就是直白地按照题目要求实现即可。

# 代码

```java
public boolean threeConsecutiveOdds(int[] arr) {
    int count = 0;
    for (int n : arr) {
        if (n % 2 == 0) {
            count = 0;
        } else {
            count++;
            if (count >= 3) {
                return true;
            }
        }
    }
    return false;
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！