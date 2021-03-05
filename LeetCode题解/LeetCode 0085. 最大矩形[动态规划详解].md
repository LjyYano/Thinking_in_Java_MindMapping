
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/maximal-rectangle/)

给定一个仅包含 0 和 1 、大小为 rows x cols 的二维二进制矩阵，找出只包含 1 的最大矩形，并返回其面积。

 

示例 1：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210305102300.png)

```

输入：matrix = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]
输出：6
解释：最大矩形如上图所示。
```

示例 2：

```
输入：matrix = []
输出：0
```

示例 3：

```
输入：matrix = [["0"]]
输出：0
```

示例 4：

```

输入：matrix = [["1"]]
输出：1

```

示例 5：

```

输入：matrix = [["0","0"]]
输出：0

```

# 解题思路

这道题跟 [84. 柱状图中最大的矩形](https://leetcode-cn.com/problems/largest-rectangle-in-histogram/) 题目很像，是那道题目的变形，我们可以把矩形的每一行作为底，看每个柱形的面积，就可转换成 84 题。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210305102641.png)

比如本题中的示例 1：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210305102300.png)

- 第 1 行柱形图就为：[1,0,1,0,0]
- 第 2 行柱形图就为：[2,0,2,1,1]
- 第 3 行柱形图就为：[3,1,3,2,2]
- 第 2 行柱形图就为：[4,0,0,3,0]

# 代码

```java
class Solution {
    public int maximalRectangle(char[][] matrix) {
        if(matrix == null || matrix.length == 0 || matrix[0].length == 0) return 0;
        int m = matrix.length, n = matrix[0].length;
        int[][] height = new int[m][n];
        
        // height[i][j] 表示第 i 行 j 列的 1 的高度
        for(int i = 0; i < m; i++) {
            for(int j = 0; j < n; j++) {
                if(matrix[i][j] == '1') {
                    height[i][j] = (i >= 1 ? height[i - 1][j] : 0) + 1;
                }
            }
        }
                
        int area = 0;
        for(int i = 0; i < m; i++) {
            area = Math.max(area, largestRectangleArea(height[i]));
        }
        
        return area; 
    }
    
    public int largestRectangleArea(int[] A) {
		int area = 0;
		for (int i = 0; i < A.length; i++) {
            // 每找到局部峰值，向前遍历数组
            if(i + 1 < A.length && A[i + 1] >= A[i]) continue;
			int min = A[i];
			for (int j = i; j >= 0; j--) {
				min = Math.min(min, A[j]);
				area = Math.max(area, (i + 1 - j) * min);
			}
		}
		return area;
	}
}
```

# 复杂度分析

- 时间复杂度：matrix 为 m 行、n 列，则复杂度是 O(m*n*n)
- 空间复杂度：O(m*n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想-最全思维导图-GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！