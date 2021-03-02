
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/word-search/)

给定一个二维网格和一个单词，找出该单词是否存在于网格中。

单词必须按照字母顺序，通过相邻的单元格内的字母构成，其中“相邻”单元格是那些水平相邻或垂直相邻的单元格。同一个单元格内的字母不允许被重复使用。

示例：

```
board =
[
  ['A','B','C','E'],
  ['S','F','C','S'],
  ['A','D','E','E']
]

给定 word = "ABCCED", 返回 true
给定 word = "SEE", 返回 true
给定 word = "ABCB", 返回 false
```

# 解题思路

这是一道套在数组下面的 dfs 题目，核心思路就是：以二元数组的每个元素作为起点，分别向上下左右遍历找到满足 word 的路径。注意使用一个新的 boolean[][] visited 数组来记录某个元素是否被使用过。

这是一道非常典型的题目！

# 代码

```java
class Solution {
    public boolean exist(char[][] board, String word) {
        boolean[][] visited = new boolean[board.length][board[0].length];
        for (int i = 0; i < board.length; i++) {
            for (int j = 0; j < board[0].length; j++) {
                if (wordSearchDfs(i, j, word, 0, visited, board)) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean wordSearchDfs(int row, int col, String word, int index, boolean[][] visited, char[][] board) {
        if (index == word.length()) {
            return true;
        }
        boolean hasPath = false;

        if (row >= 0 && row < board.length && col >= 0 && col < board[0].length && !visited[row][col] && board[row][col] == word.charAt(index)) {
            visited[row][col] = true;
            index++;

            hasPath = wordSearchDfs(row + 1, col, word, index, visited, board) ||
                    wordSearchDfs(row - 1, col, word, index, visited, board) ||
                    wordSearchDfs(row, col + 1, word, index, visited, board) ||
                    wordSearchDfs(row, col - 1, word, index, visited, board);

            if (!hasPath) {
                visited[row][col] = false;
                index--;
            }
        }

        return hasPath;
    }

}
```

# 复杂度分析

- 时间复杂度：设行为 m，列为 n，复杂度为 O(m * n)
- 空间复杂度：O(m * n)

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！