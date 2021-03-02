
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/summary-ranges/)

给定一个无重复元素的有序整数数组 nums 。

返回 恰好覆盖数组中所有数字 的 最小有序 区间范围列表。也就是说，nums 的每个元素都恰好被某个区间范围所覆盖，并且不存在属于某个范围但不属于 nums 的数字 x 。

列表中的每个区间范围 [a,b] 应该按如下格式输出：

	"a->b" ，如果 a != b
	"a" ，如果 a == b

 

示例 1：

```

输入：nums = [0,1,2,4,5,7]
输出：["0->2","4->5","7"]
解释：区间范围是：
[0,2] --> "0->2"
[4,5] --> "4->5"
[7,7] --> "7"
```

示例 2：

```

输入：nums = [0,2,3,4,6,8,9]
输出：["0","2->4","6","8->9"]
解释：区间范围是：
[0,0] --> "0"
[2,4] --> "2->4"
[6,6] --> "6"
[8,9] --> "8->9"
```

示例 3：

```

输入：nums = []
输出：[]
```

示例 4：

```

输入：nums = [-1]
输出：["-1"]
```

示例 5：

```

输入：nums = [0]
输出：["0"]
```

# 解题思路

比较直白，直接按照题目要求实现即可。只要找到连续的数值所在的左右区间，进行合并合成结果即可。

# 代码

```java
public List<String> summaryRanges(int[] nums) {
    List<String> ans = new ArrayList<>();
    for (int i = 0; i < nums.length; i++) {
        int start = nums[i];
        int end = start;

        while (i + 1 < nums.length && nums[i + 1] - end == 1) {
            i++;
            end++;
        }

        if (end == start) {
            ans.add(start + "");
        } else {
            ans.add(start + "->" + end);
        }
    }
    return ans;
}
```

# 复杂度分析

- 时间复杂度：只是遍历了一遍数组，复杂度是 O(n)
- 空间复杂度：除去返回所创建的空间，没有创建额外的空间，复杂度为 O(1)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！