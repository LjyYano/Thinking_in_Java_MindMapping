
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/best-time-to-buy-and-sell-stock/)

给定一个数组 prices ，它的第 i 个元素 prices[i] 表示一支给定股票第 i 天的价格。

你只能选择 某一天 买入这只股票，并选择在 未来的某一个不同的日子 卖出该股票。设计一个算法来计算你所能获取的最大利润。

返回你可以从这笔交易中获取的最大利润。如果你不能获取任何利润，返回 0 。

 

示例 1：

```

输入：[7,1,5,3,6,4]
输出：5
解释：在第 2 天（股票价格 = 1）的时候买入，在第 5 天（股票价格 = 6）的时候卖出，最大利润 = 6-1 = 5 。
     注意利润不能是 7-1 = 6, 因为卖出价格需要大于买入价格；同时，你不能在买入前卖出股票。

```

示例 2：

```

输入：prices = [7,6,4,3,1]
输出：0
解释：在这种情况下，没有交易完成，所以最大利润为 0。

```

# 解题思路

最容易想到的就是暴力法，假设第 i 天买的，那就遍历 i+1 到最后一天的股票，找最大的利润即可。这样时间复杂度是 O(n^2)，空间复杂度是 O(1)。

但是本题说是最高的利润，分析一下可以想到，如果我们在最低点买入就好了。那可以遍历数组，在遍历数组的时候，每次记录从第 1 天到现在的最小值，然后今天卖出能赚多少钱？当考虑完所有天数之时，我们就得到了最好的答案。

# 代码

```java
class Solution {
    public int maxProfit(int[] prices) {
        int maxProfit = 0;
        // 存储从 prices[0..i] 的最小值
        int lowest = Integer.MAX_VALUE;

        for (int v : prices) {
            lowest = Math.min(v, lowest);
            maxProfit = Math.max(maxProfit, v - lowest);
        }

        return maxProfit;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！