
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/best-time-to-buy-and-sell-stock-iii/)

给定一个数组，它的第 i 个元素是一支给定的股票在第 i 天的价格。

设计一个算法来计算你所能获取的最大利润。你最多可以完成 两笔 交易。

注意：你不能同时参与多笔交易（你必须在再次购买前出售掉之前的股票）。

 

示例 1:

```

输入：prices = [3,3,5,0,0,3,1,4]
输出：6
解释：在第 4 天（股票价格 = 0）的时候买入，在第 6 天（股票价格 = 3）的时候卖出，这笔交易所能获得利润 = 3-0 = 3 。
     随后，在第 7 天（股票价格 = 1）的时候买入，在第 8 天 （股票价格 = 4）的时候卖出，这笔交易所能获得利润 = 4-1 = 3 。
```

示例 2：

```

输入：prices = [1,2,3,4,5]
输出：4
解释：在第 1 天（股票价格 = 1）的时候买入，在第 5 天 （股票价格 = 5）的时候卖出，这笔交易所能获得利润 = 5-1 = 4 。   
     注意你不能在第 1 天和第 2 天接连购买股票，之后再将它们卖出。   
     因为这样属于同时参与了多笔交易，你必须在再次购买前出售掉之前的股票。

```

示例 3：

```

输入：prices = [7,6,4,3,1] 
输出：0 
解释：在这个情况下，没有交易完成，所以最大利润为 0。
```

示例 4：

```

输入：prices = [1]
输出：0

```

# 解题思路

# 代码

```java
class Solution {
	public int maxProfit(int[] prices) {
		if (prices == null || prices.length == 0) {
			return 0;
		}
		int n = prices.length;
		/**
		 *  l[i][j]： 第 i 天可进行 j 次交易，且最后一次交易在最后一天卖出
		 *  g[i][j]： 第 i 天最多 j 次交易的最大利润
		 *  
		 *  l[i][j] = max(l[i-1][j], g[i-1][j-1]) + diff 
		 *  g[i][j] = max(l[i][j], g[i-1][j])
		 *  
		 *  l[i][j](最后一次交易在最后一天卖出)公式分 2 种情况：
		 *  1. l[i-1][j] + diff：最后一次交易在 i-1 天卖出，加上 diff 相当于 i-1 天没卖，最后一天卖，不增加交易次数
		 *  2. g[i-1][j-1] + diff： i-1 天卖出，结果不会比 1 好；i-1 天未卖出，则可以卖，增加交易次数
		 *  
		 *  可以转化为一维数组 int[3]
		 */
		int[][] l = new int[n][3];
		int[][] g = new int[n][3];

		for (int i = 1; i < n; i++) {
			int diff = prices[i] - prices[i - 1];
			for (int j = 1; j <= 2; j++) {
				l[i][j] = Math.max(l[i - 1][j], g[i - 1][j - 1]) + diff;
				g[i][j] = Math.max(l[i][j], g[i - 1][j]);
			}
		}

		return g[n - 1][2];
	}
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！