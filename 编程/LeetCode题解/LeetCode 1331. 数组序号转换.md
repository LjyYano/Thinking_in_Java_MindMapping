
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/rank-transform-of-an-array/)

给你一个整数数组 arr ，请你将数组中的每个元素替换为它们排序后的序号。

序号代表了一个元素有多大。序号编号的规则如下：

	序号从 1 开始编号。
	一个元素越大，那么序号越大。如果两个元素相等，那么它们的序号相同。
	每个数字的序号都应该尽可能地小。

示例 1：

```
输入：arr = [40,10,20,30]
输出：[4,1,2,3]
解释：40 是最大的元素。 10 是最小的元素。 20 是第二小的数字。 30 是第三小的数字。
```

示例 2：

```
输入：arr = [100,100,100]
输出：[1,1,1]
解释：所有元素有相同的序号。

```

示例 3：

```
输入：arr = [37,12,28,9,100,56,80,5,12]
输出：[5,3,4,2,8,6,7,1,3]

```

# 解题思路

可以维护一个 TreeMap，key 是数组 arr 中的元素，value 是这些元素所对应的所有下标。这样在遍历 TreeMap 时，遍历的顺序正好是按照元素大小的顺序，则第一个 entry 里的 key 就是最小的，对应的索引下标全都赋值成 1；第二个 entry 对应的索引下标全部赋值为 2……以此类推。

# 代码

```java
class Solution {
    public int[] arrayRankTransform(int[] arr) {
        Map<Integer, List<Integer>> sortedMap = new TreeMap<>();
        for (int i = 0; i < arr.length; i++) {
            List<Integer> list = sortedMap.getOrDefault(arr[i], new ArrayList<>());
            list.add(i);
            sortedMap.put(arr[i], list);
        }
        int c = 1;
        int[] ans = new int[arr.length];
        for (Map.Entry<Integer, List<Integer>> entry : sortedMap.entrySet()) {
            for (Integer index : entry.getValue()) {
                ans[index] = c;
            }
            c++;
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