
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)


# 题目描述

[题目链接](https://leetcode-cn.com/problems/magnetic-force-between-two-balls/)

在代号为 C-137 的地球上，Rick 发现如果他将两个球放在他新发明的篮子里，它们之间会形成特殊形式的磁力。Rick 有 n 个空的篮子，第 i 个篮子的位置在 position[i] ，Morty 想把 m 个球放到这些篮子里，使得任意两球间 最小磁力 最大。

已知两个球如果分别位于 x 和 y ，那么它们之间的磁力为 |x - y| 。

给你一个整数数组 position 和一个整数 m ，请你返回最大化的最小磁力。

示例 1：

![20210220143302](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210220143302.png)

    输入：position = [1,2,3,4,7], m = 3
    输出：3
    解释：将 3 个球分别放入位于 1，4 和 7 的三个篮子，两球间的磁力分别为 [3, 3, 6]。最小磁力为 3 。我们没办法让最小磁力大于 3 。
示例 2：

    输入：position = [5,4,3,2,1,1000000000], m = 2
    输出：999999999
    解释：我们使用位于 1 和 1000000000 的篮子时最小磁力最大。
 

提示：

    n == position.length
    2 <= n <= 10^5
    1 <= position[i] <= 10^9
    所有 position 中的整数 互不相同 。
    2 <= m <= position.length

# 解题思路

这道题思考了半天，其实只要理解了`二分查找`，二分的究竟是什么就很好办了。

可以很容易估算出`最小磁力的可能最小值 min`和`最小磁力的可能最大值 max`，然后取 min 和 max 的中间值 mid，遍历数组看看如果最小距离是 mid 的话，数组是否会满足要求：
- 如果满足，则表明最小磁力的最大值在 mid 和 max 之间，更新 min 为 mid
- 如果不满足，则表明最小磁力的最大声在 min 和 mid 之间，更新 max 为 mid

# 代码

```java
public int maxDistance(int[] position, int m) {
    Arrays.sort(position);
    // 最小磁力的可能最小值
    int min = 1;
    // 最小磁力的可能最大值
    int max = (position[position.length - 1] - position[0]) / (m - 1);
    int ans = -1;
    while (min <= max) {
        int mid = (min + max) / 2;
        if (checkDistance(mid, position, m)) {
            ans = mid;
            min = mid + 1;
        } else {
            max = mid - 1;
        }
    }
    return ans;
}

private boolean checkDistance(int mid, int[] position, int m) {
    int count = 1;
    int pre = position[0];
    for (int i = 1; i < position.length; i++) {
        if (position[i] - pre >= mid) {
            count++;
            if (count >= m) {
                return true;
            }
            pre = position[i];
        }
    }
    return false;
}
```

# 复杂度分析

时间复杂度：因为 check 函数是需要遍历一次数组，时间不定，记为 n；而距离 m 是二分查找的，时间为 logm，所以整体的复杂度为$O(n*logm)$

空间复杂度：$O(1)$
