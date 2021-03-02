
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/largest-rectangle-in-histogram/)

给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1 。

求在该柱状图中，能够勾勒出来的矩形的最大面积。

 
![20210222192315](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210222192315.png)

以上是柱状图的示例，其中每个柱子的宽度为 1，给定的高度为 [2,1,5,6,2,3]。

 
![20210222192328](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210222192328.png)

图中阴影部分为所能勾勒出的最大矩形面积，其面积为 10 个单位。

 

示例：

```
输入：[2,1,5,6,2,3]
输出：10
```

# 解题思路

最暴力的思路就是，对于数组中的每个元素，以这个元素的值为高，分别向左、向右寻找第一个小于该元素的边界，计算并更新矩形的面积。

下面的代码会超时：

```java
public int largestRectangleArea(int[] heights) {
    // 分别以每个元素的高度为基准，左右找最大长度
    int ans = 0;
    for (int i = 0; i < heights.length; i++) {
        int min = heights[i], left = i - 1, right = i + 1;
        while (left >= 0 && heights[left] >= min) {
            left--;
        }
        while (right < heights.length && heights[right] >= min) {
            right++;
        }
        ans = Math.max(ans, (right - left - 1) * min);
    }
    return ans;
}
```

超时的原因就在于，如果相邻的两个元素相等，那么这个矩形的面积就是重复计算的。LeetCode 中的超时用例就是几万个相同的数值。

为了解决超时问题，LeetCode 官方的解法是使用单调栈，但是在遍历数组元素的时候，直接遍历下是否与前一个相同即可。这种方法就能够击败 95%的人，而且非常简单易懂，都不用画图分析，囧。

# 代码

```java
public int largestRectangleArea(int[] heights) {
    // 分别以每个元素的高度为基准，左右找最大长度
    int ans = 0;
    for (int i = 0; i < heights.length; i++) {
        // 如果相邻的两个元素相等，那么肯定是重复计算了
        // 不加这个逻辑，超时；加上这个逻辑，击败 95% 的人
        if (i > 0 && heights[i] == heights[i - 1]) {
            continue;
        }
        int min = heights[i], left = i - 1, right = i + 1;
        while (left >= 0 && heights[left] >= min) {
            left--;
        }
        while (right < heights.length && heights[right] >= min) {
            right++;
        }
        ans = Math.max(ans, (right - left - 1) * min);
    }
    return ans;
}
```

# 复杂度分析

- 时间复杂度：对于每个元素，最坏的情况下要向左右遍历一遍数组，所以最坏情况下的复杂度是 O(n^n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！