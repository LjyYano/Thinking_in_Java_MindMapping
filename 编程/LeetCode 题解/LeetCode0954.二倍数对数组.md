
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/array-of-doubled-pairs/)

给定一个长度为偶数的整数数组 arr，只有对 arr 进行重组后可以满足 “对于每个 0 ，都有 arr[2 * i + 1] = 2 * arr[2 * i]” 时，返回 true；否则，返回 false。

 

示例 1：

```

输入：arr = [3,1,3,6]
输出：false

```

示例 2：

```

输入：arr = [2,1,2,6]
输出：false

```

示例 3：

```

输入：arr = [4,-2,2,-4]
输出：true
解释：可以用 [-2,-4] 和 [2,4] 这两组组成 [-2,-4,2,4] 或是 [2,4,-2,-4]

```

示例 4：

```

输入：arr = [1,2,4,16,8,4]
输出：false

```

# 解题思路

题目稍微复杂一点的地方在于：有正数和负数的存在，两者的处理正好是相反的，因为一个负数* 2，这个数反而会更小。

整体思路是：
- 对数组按照绝对值排序
- 维护一个 map count，key 是数组里的数值，value 是该数值出现的次数
- 从左向右遍历数组（已经按照绝对值排序）
  - 如果该值 x 的 value 是 0，continue
  - 如果 x*2 的 value<=0，则不符合条件直接返回 false，因为 x 次数不为 0，却缺少 x*2
  - 对 x 和 x*2 的 value 分别-1

# 代码

```java
class Solution {
    public boolean canReorderDoubled(int[] A) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int x : A)
            count.put(x, count.getOrDefault(x, 0) + 1);

        Integer[] B = new Integer[A.length];
        for (int i = 0; i < A.length; ++i)
            B[i] = A[i];
        Arrays.sort(B, Comparator.comparingInt(Math::abs));

        for (int x : B) {
            if (count.get(x) == 0) continue;
            if (count.getOrDefault(2 * x, 0) <= 0) return false;
            
            count.put(x, count.get(x) - 1);
            count.put(2 * x, count.get(2 * x) - 1);
        }
        return true;
    }
}
```

# 复杂度分析

- 时间复杂度：因为进行了排序，所以复杂度是 O(nlogn)
- 空间复杂度：O(n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！