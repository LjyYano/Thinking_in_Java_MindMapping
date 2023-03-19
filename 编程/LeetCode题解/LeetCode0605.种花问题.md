
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/can-place-flowers/)

假设有一个很长的花坛，一部分地块种植了花，另一部分却没有。可是，花不能种植在相邻的地块上，它们会争夺水源，两者都会死去。

给你一个整数数组  flowerbed 表示花坛，由若干 0 和 1 组成，其中 0 表示没种植花，1 表示种植了花。另有一个数 n ，能否在不打破种植规则的情况下种入 n 朵花？能则返回 true ，不能则返回 false。

示例 1：

```
输入：flowerbed = [1,0,0,0,1], n = 1
输出：true
```

示例 2：

```

输入：flowerbed = [1,0,0,0,1], n = 2
输出：false

```

# 解题思路

这道题跟 LeetCode 1552. 两球之间的磁力 很像，题意是那道题的降级版本。本道题要求是否能够中 n 个花，其实只要求出最大可以种多少个就行了。那什么时候可以种呢？

可以使用贪心算法，假设数组的中间一段是 1 0 0 0，那么第 1 个 0 不能种，第 2 个 0 就无脑种，因为只要在第 2 个地方种上，后面第 3 个 0 后面无论是 0 还是 1，都不会使结果更差。

根据题意，题目输入的数组 flowerbed 肯定是符合要求的，即绝对不可能有连续的 1。我们可以直接遍历数组，如果某个位置是 0，且下一个位置是 0，则直接种；如果某个位置是 0，且下一个位置是 1，则直接跳到下一位；此时索引所在的数组元素是 1，根据题意下一个肯定是 0，我们直接将 i=i+2，重复上述步骤。

# 代码

```java
class Solution {
    public boolean canPlaceFlowers(int[] flowerbed, int n) {
        // 贪心
        for (int i = 0; i < flowerbed.length; i += 2) {
            if (flowerbed[i] == 0) {
                // 当前位置是 0，下一位置也是 0，可以种
                if (i == flowerbed.length - 1 || flowerbed[i + 1] == 0) {
                    n--;
                } else {
                    // 下一个位置是 1，直接跳到下一位
                    i++;
                }
            }
        }
        return n <= 0;
    }
}
```

# 复杂度分析

- 时间复杂度：O(n)
- 空间复杂度：O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！