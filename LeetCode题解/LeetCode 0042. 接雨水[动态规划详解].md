
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/trapping-rain-water/)

给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。

 

示例 1：

![20210302095753](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210302095753.png)

```

输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]
输出：6
解释：上面是由数组 [0,1,0,2,1,0,1,3,2,1,2,1] 表示的高度图，在这种情况下，可以接 6 个单位的雨水（蓝色部分表示雨水）。 

```

示例 2：

```

输入：height = [4,2,0,3,2,5]
输出：9

```

# 解题思路

这道题理解起来有点困难，解法也有很多，这里介绍一种我认为比较好理解的思路：每个元素能在结果中贡献多少个雨水呢？以上面的示例 1 为例，输入：

[0,1,0,2,1,0,1,3,2,1,2,1]

- i = 0，无法接住雨水，因为左边没有数值
- i = 1，无法接住雨水，因为左边的高度都小于 1
- i = 2，能接住 1 单位的雨水，因为左边最高是 1，右边最高是 2，而该列本身的高度是 0，那么能够接住 min(1,2)-0=1 单位的雨水
- i = 3，无法接住雨水，因为左边的高度都小于 2
- i = 4，能够接住 1 单位的雨水，因为左边最高是 2，右边最高是 3，而该列本身的高度是 1，即能接住 min(2,3)-1 = 1 单位的雨水
- ……

通过推断可以看到，列 i 对结果的贡献是：

max(min(left_max(i),right_max(i)) - height[i],0)

# 代码

```java
class Solution {
    public int trap(int[] height) {
        int[] left = new int[height.length];
        int[] right = new int[height.length];
        for(int i = 1; i < height.length - 1; i++) {
            left[i] = Math.max(left[i - 1], height[i - 1]);
        }
        for(int i = height.length - 2; i >= 0; i--) {
            right[i] = Math.max(right[i + 1], height[i + 1]);
        }
        // 遍历每个元素，分别找到左右第一个比它大的元素
        int ans = 0;
        for(int i = 1; i < height.length - 1; i++) {
            int min = Math.min(left[i], right[i]);
            if(min > height[i]) {
                ans += min - height[i];
            }
        }
        return ans;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！