
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/diagonal-traverse-ii/)

给你一个列表 nums ，里面每一个元素都是一个整数列表。请你依照下面各图的规则，按顺序返回 nums 中对角线上的整数。

 

示例 1：

![20210226101407](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226101407.png)

```
输入：nums = [[1,2,3],[4,5,6],[7,8,9]]
输出：[1,4,2,7,5,3,8,6,9]

```

示例 2：

![20210226101413](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210226101413.png)

```
输入：nums = [[1,2,3,4,5],[6,7],[8],[9,10,11],[12,13,14,15,16]]
输出：[1,6,2,8,7,3,9,4,12,10,5,13,11,14,15,16]

```

示例 3：

```
输入：nums = [[1,2,3],[4],[5,6,7],[8],[9,10,11]]
输出：[1,4,2,5,3,8,6,9,7,10,11]

```

示例 4：

```
输入：nums = [[1,2,3,4,5,6]]
输出：[1,2,3,4,5,6]

```

# 解题思路

假设 nums 是 m*n 的，按照题目的要求：
- 第 1 条对角线为 (0,0)
- 第 2 条对角线为 (1,0),(0,1)
- 第 3 条对角线为 (2,0),(1,1),(0,2)
- ……
- 最后一条对角线为 (m-1,n-1)

我们可以维护一个 LinkedHashMap（注意是 LinkedHashMap，因为需要插入的顺序），依次遍历 List<List<Integer>> nums 中的每个元素，将元素索引 i+j 作为 key 放入 map，value 是所有的元素（一个 list）。

最终的结果其实也就是将 map 顺序遍历出来，组合一下。不过每个 list 要 reverse 一下。

# 代码

```java
class Solution {
    public int[] findDiagonalOrder(List<List<Integer>> nums) {
        Map<Integer, List<Integer>> map = new LinkedHashMap<>();
        for (int i = 0; i < nums.size(); i++) {
            List<Integer> list = nums.get(i);
            for (int j = 0; j < list.size(); j++) {
                List<Integer> res = map.getOrDefault(i + j, new ArrayList<>());
                res.add(list.get(j));
                map.put(i + j, res);
            }
        }
        List<Integer> ans = map.values().stream().peek(Collections::reverse).flatMap(List::stream).collect(Collectors.toList());
        int[] result = new int[ans.size()];
        for (int i = 0; i < ans.size(); i++) {
            result[i] = ans.get(i);
        }
        return result;
    }
}
```

# 复杂度分析

- 时间复杂度：O(m*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！