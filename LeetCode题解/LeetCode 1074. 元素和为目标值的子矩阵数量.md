
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/number-of-submatrices-that-sum-to-target/)

给出矩阵 matrix 和目标值 target，返回元素总和等于目标值的非空子矩阵的数量。

子矩阵 x1, y1, x2, y2 是满足 x1 <= x <= x2 且 y1 <= y <= y2 的所有单元 matrix[x][y] 的集合。

如果 (x1, y1, x2, y2) 和 (x1', y1', x2', y2') 两个子矩阵中部分坐标不同（如：x1 != x1'），那么这两个子矩阵也不同。

 
示例 1：

    输入：matrix = [[0,1,0],[1,1,1],[0,1,0]], target = 0
    输出：4
    解释：四个只含 0 的 1x1 子矩阵。
示例 2：

    输入：matrix = [[1,-1],[-1,1]], target = 0
    输出：5
    解释：两个 1x2 子矩阵，加上两个 2x1 子矩阵，再加上一个 2x2 子矩阵。
 

提示：

    1 <= matrix.length <= 300
    1 <= matrix[0].length <= 300
    -1000 <= matrix[i] <= 1000
    -10^8 <= target <= 10^8

# 解题思路

根据题目，肯定要求从 (x1,y1,x2,y2) 的和，那么最好能将从 (0,0,x,y) 的矩阵和计算出来，否则复杂度会很高。

可以设 sum[i][j] 为矩阵 matrix[0][0] 到 matrix[i][j] 的元素和，那么 sum[i][j] 的推导公式为：

- i == 0 && j == 0 时，sum[i][j] = matrix[i][j]
- i == 0 && j != 0 时，sum[i][j] = matrix[i][j] + sum[i][j - 1]
- i != 0 && j == 0 时，sum[i][j] = matrix[i][j] + sum[i - 1][j]
- i != 0 && j != 0 时，sum[i][j] = matrix[i][j] - sum[i - 1][j - 1] + sum[i - 1][j] + sum[i][j - 1]

解释一下最后一个，对于 (0,0,i,j) 这个矩阵，在已知 (0,0,i-1,j-1) 的情况下，需要加上第 j 列和第 i 行，不过这 2 个加入的话，就会把 (0,0,i-1,j-1) 多计算一遍，减去即可。

![20210220105354](http://yano.oss-cn-beijing.aliyuncs.com/blog/20210220105354.png)

接下来就是在计算出 sun[i][j] 之后，对于每行遍历 0~i，对于每列遍历 0~j，分别计算每个矩阵。

# 代码

```java
public int numSubmatrixSumTarget(int[][] matrix, int target) {
    int row = matrix.length, col = matrix[0].length;
    int[][] sum = new int[row][col];
    int ans = 0;
    for (int i = 0; i < row; i++) {
        for (int j = 0; j < col; j++) {
            if (i == 0 && j == 0) {
                sum[i][j] = matrix[i][j];
            } else if (i == 0) {
                sum[i][j] = matrix[i][j] + sum[i][j - 1];
            } else if (j == 0) {
                sum[i][j] = matrix[i][j] + sum[i - 1][j];
            } else {
                sum[i][j] = matrix[i][j] - sum[i - 1][j - 1] + sum[i - 1][j] + sum[i][j - 1];
            }
            for (int k = 0; k <= i; k++) {
                for (int l = 0; l <= j; l++) {
                    int main = (k != 0 && l != 0) ? sum[k - 1][l - 1] : 0;
                    int left = k != 0 ? sum[i - 1][l] : 0;
                    int up = l != 0 ? sum[k][j - 1] : 0;
                    if (sum[i][j] - left - up + main == target) {
                        ans++;
                    }
                }
            }
        }
    }
    return ans;
}
```

# 复杂度分析

时间复杂度：$O(row^2 * col^2)$

空间复杂度：因为新建了一个数组矩阵 sum，复杂度为 $O(row*col)$

