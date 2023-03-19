
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/richest-customer-wealth/)

给你一个 m x n 的整数网格 accounts ，其中 accounts[i][j] 是第 i​​​​​​​​​​​​ 位客户在第 j 家银行托管的资产数量。返回最富有客户所拥有的 资产总量 。

客户的 资产总量 就是他们在各家银行托管的资产数量之和。最富有客户就是 资产总量 最大的客户。

 

示例 1：

```
输入：accounts = [[1,2,3],[3,2,1]]
输出：6
解释：
第 1 位客户的资产总量 = 1 + 2 + 3 = 6
第 2 位客户的资产总量 = 3 + 2 + 1 = 6
两位客户都是最富有的，资产总量都是 6 ，所以返回 6 。

```

示例 2：

```
输入：accounts = [[1,5],[7,3],[3,5]]
输出：10
解释：
第 1 位客户的资产总量 = 6
第 2 位客户的资产总量 = 10 
第 3 位客户的资产总量 = 8
第 2 位客户是最富有的，资产总量是 10
```

示例 3：

```
输入：accounts = [[2,8,7],[7,1,3],[1,9,5]]
输出：17

```

# 解题思路

没啥说的，直接按照题目的要求实现即可~通过 Java stream 能够实现一行代码。

# 代码

```java
class Solution {
    public int maximumWealth(int[][] accounts) {
        return Arrays.stream(accounts).map(ints ->
                Arrays.stream(ints).sum()
        ).max(Integer::compareTo).get();
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！