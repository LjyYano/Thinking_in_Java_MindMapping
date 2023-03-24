---
date: 2019-10-10
---

<!-- TOC -->

- [题解](#题解)
- [LeetCode 树的定义](#leetcode-树的定义)
  - [二叉树](#二叉树)
  - [N叉树](#n叉树)
- [二叉树遍历](#二叉树遍历)
  - [二叉树前序遍历](#二叉树前序遍历)
    - [递归](#递归)
    - [迭代](#迭代)
  - [二叉树中序遍历](#二叉树中序遍历)
    - [递归](#递归-1)
    - [迭代](#迭代-1)
  - [二叉树后序遍历](#二叉树后序遍历)
    - [递归](#递归-2)
    - [迭代：利用辅助类](#迭代利用辅助类)
    - [迭代：逆序输出](#迭代逆序输出)
  - [二叉树的层次遍历](#二叉树的层次遍历)
    - [递归](#递归-3)
    - [迭代](#迭代-2)
  - [二叉树的右视图](#二叉树的右视图)
    - [递归](#递归-4)
    - [迭代](#迭代-3)
  - [在每个树行中找最大值](#在每个树行中找最大值)
    - [递归](#递归-5)
    - [迭代](#迭代-4)
  - [二叉树的垂序遍历](#二叉树的垂序遍历)
    - [解题思路](#解题思路)
    - [代码](#代码)
  - [二叉树的锯齿形层次遍历](#二叉树的锯齿形层次遍历)
    - [递归](#递归-6)
    - [迭代](#迭代-5)
  - [N 叉树遍历](#n-叉树遍历)
    - [N叉树的层序遍历](#n叉树的层序遍历)
    - [N叉树的前序遍历](#n叉树的前序遍历)
      - [递归](#递归-7)
      - [迭代](#迭代-6)
    - [N叉树的后序遍历](#n叉树的后序遍历)
      - [递归](#递归-8)
      - [迭代](#迭代-7)
- [二叉搜索树](#二叉搜索树)
  - [不同的二叉搜索树](#不同的二叉搜索树)
  - [不同的二叉搜索树 II](#不同的二叉搜索树-ii)
  - [验证二叉搜索树](#验证二叉搜索树)
  - [恢复二叉搜索树](#恢复二叉搜索树)
  - [修剪二叉搜索树](#修剪二叉搜索树)
  - [将有序数组转换为二叉搜索树](#将有序数组转换为二叉搜索树)
  - [二叉搜索树迭代器](#二叉搜索树迭代器)
  - [二叉搜索树中第K小的元素](#二叉搜索树中第k小的元素)
  - [二叉搜索树的最近公共祖先](#二叉搜索树的最近公共祖先)
  - [删除二叉搜索树中的节点](#删除二叉搜索树中的节点)
  - [二叉搜索树中的搜索](#二叉搜索树中的搜索)
  - [二叉搜索树中的插入操作](#二叉搜索树中的插入操作)
- [深搜、广搜](#深搜广搜)
  - [相同的树](#相同的树)
  - [对称二叉树](#对称二叉树)
    - [递归](#递归-9)
    - [迭代](#迭代-8)
  - [翻转二叉树](#翻转二叉树)
  - [二叉树的最大深度](#二叉树的最大深度)
  - [二叉树的最小深度](#二叉树的最小深度)
  - [平衡二叉树](#平衡二叉树)
  - [完全二叉树的节点个数](#完全二叉树的节点个数)
  - [二叉树最大宽度](#二叉树最大宽度)
  - [二叉树的直径](#二叉树的直径)
  - [二叉树的坡度](#二叉树的坡度)
  - [二叉树的所有路径](#二叉树的所有路径)
  - [二叉树的最近公共祖先](#二叉树的最近公共祖先)
  - [最深叶节点的最近公共祖先](#最深叶节点的最近公共祖先)
- [路径和](#路径和)
  - [左叶子之和](#左叶子之和)
  - [路径总和](#路径总和)
  - [路径总和 II](#路径总和-ii)
  - [路径总和 III](#路径总和-iii)
  - [二叉树中的最大路径和](#二叉树中的最大路径和)
  - [求根到叶子节点数字之和](#求根到叶子节点数字之和)
- [序列化二叉树、构造二叉树](#序列化二叉树构造二叉树)
  - [从前序与中序遍历序列构造二叉树](#从前序与中序遍历序列构造二叉树)
  - [从中序与后序遍历序列构造二叉树](#从中序与后序遍历序列构造二叉树)
  - [先序遍历构造二叉树](#先序遍历构造二叉树)
  - [序列化和反序列化二叉搜索树](#序列化和反序列化二叉搜索树)
  - [二叉树的序列化与反序列化](#二叉树的序列化与反序列化)

<!-- /TOC -->

# 题解


本文中所有题解，都在 https://github.com/LjyYano/LeetCode/tree/master/leetcode/src/main/java

# LeetCode 树的定义

## 二叉树

```java
public class TreeNode {

    int val;
    TreeNode left;
    TreeNode right;

    TreeNode(int x) {
        val = x;
    }
}
```

## N叉树

```java
public class Node {
    public int val;
    public List<Node> children;

    public Node() {
    }

    public Node(int _val, List<Node> _children) {
        val = _val;
        children = _children;
    }
}
```


# 二叉树遍历

二叉树最基本的遍历方式就是：前序遍历、中序遍历和后序遍历。

* 前序遍历首先访问根节点，然后遍历左子树，最后遍历右子树。
* 中序遍历是先遍历左子树，然后访问根节点，然后遍历右子树。
* 后序遍历是先遍历左子树，然后遍历右子树，最后访问树的根节点。

简单概况如下：

* 前序遍历：根左右
* 中序遍历：左根右
* 后序遍历：左右根

TIPS：前中后序遍历区别在于三字中的中间那个字，前、中、后序分别对应左、根、右。

## 二叉树前序遍历

144. 二叉树的前序遍历

给定一个二叉树，返回它的 `前序` 遍历。

 示例:

    输入: [1,null,2,3]  

       1
        \
         2
        /
       3 

    输出: [1,2,3]
`进阶`: 递归算法很简单，你可以通过迭代算法完成吗？


### 递归

```java
public List<Integer> preorderTraversal(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans);
    return ans;
}

private void robot(TreeNode p, List<Integer> ans) {
    if(p == null) return;
    // 根左右
    ans.add(p.val);
    robot(p.left, ans);
    robot(p.right, ans);
}
```

### 迭代

迭代步骤：

1. 从根节点开始，每次迭代弹出当前栈顶元素
2. 将其孩子节点压入栈中（先压右孩子再压左孩子）


```java
public List<Integer> preorderTraversal2(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    Stack<TreeNode> stack = new Stack<>();
    // 将根节点入栈
    stack.push(root);
    while (!stack.isEmpty()) {
        // 取出栈顶元素
        TreeNode tmp = stack.pop();
        if (tmp != null) {
            ans.add(tmp.val);
            // 将其孩子节点压入栈中（先右节点、再左节点）
            stack.add(tmp.right);
            stack.add(tmp.left);
        }
    }
    return ans;
}
```

算法复杂度:

- 时间复杂度：树中每个节点都遍历一次，因此时间复杂度为 O(N)，其中 N 为树中节点的数量。
- 空间复杂度：
    - 最坏情况：树为链表，树的高度=树的节点个数，此时空间复杂度是 O(N)。
    - 最好情况：树高度平衡，此时空间复杂度是 O(logn)。

## 二叉树中序遍历

94. 二叉树的中序遍历

给定一个二叉树，返回它的 `中序` 遍历。

示例:

    输入: [1,null,2,3]
       1
        \
         2
        /
       3

    输出: [1,3,2]

`进阶`: 递归算法很简单，你可以通过迭代算法完成吗？

### 递归

```java
public List<Integer> inorderTraversal(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans);
    return ans;
}

private void robot(TreeNode root, List<Integer> ans) {
    if (root == null) {
        return;
    }
    // 左根右
    robot(root.left, ans);
    ans.add(root.val);
    robot(root.right, ans);
}
```

### 迭代

```java
public List<Integer> inorderTraversal(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    Stack<TreeNode> stack = new Stack<>();
    while (!stack.isEmpty() || root != null) {
        // 一直放入左儿子（左）
        while (root != null) {
            stack.push(root);
            root = root.left;
        }
        // 访问当前元素（根），把右儿子入栈（右）
        if (!stack.isEmpty()) {
            root = stack.pop();
            ans.add(root.val);
            root = root.right;
        }
    }
    return ans;
}
```

算法复杂度

- 时间复杂度：O(n)。递归函数 T(n) = 2⋅T(n/2)+1。
- 空间复杂度：最坏情况下需要空间O(n)，平均情况为O(logn)。


## 二叉树后序遍历

145. 二叉树的后序遍历

给定一个二叉树，返回它的 `后序` 遍历。

示例:

    输入: [1,null,2,3]  
       1
        \
         2
        /
       3 

    输出: [3,2,1]

`进阶`: 递归算法很简单，你可以通过迭代算法完成吗？

### 递归

```java
public List<Integer> postorderTraversal(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans);
    return ans;
}

private void robot(TreeNode p, List<Integer> ans) {
    if (p == null) {
        return;
    }
    // 左右根
    robot(p.left, ans);
    robot(p.right, ans);
    ans.add(p.val);
}
```

后序遍历的非递归写法有些麻烦，因为节点第一次访问时并不打印，而是在第二次遍历时才打印。所以需要一个变量来标记该结点是否访问过。

### 迭代：利用辅助类

```java
public class StackNode {
    TreeNode root;
    boolean visit;

    StackNode(TreeNode root) {
        this.root = root;
    }
}

public List<Integer> postorderTraversal2(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }
    Stack<StackNode> stack = new Stack<>();
    StackNode node;
    stack.push(new StackNode(root));
    while (!stack.isEmpty()) {
        node = stack.pop();
        if (node == null) {
            continue;
        }
        if (!node.visit) {
            node.visit = true;
            stack.push(node);
            if (node.root.right != null) {
                stack.push(new StackNode(node.root.right));
            }
            if (node.root.left != null) {
                stack.push(new StackNode(node.root.left));
            }
        } else if (node.root != null) {
            ans.add(node.root.val);
        }
    }
    return ans;
}
```

### 迭代：逆序输出

```java
public List<Integer> postorderTraversal3(TreeNode root) {
    LinkedList<Integer> ans = new LinkedList<>();
    if (root == null) {
        return ans;
    }

    Stack<TreeNode> stack = new Stack<>();
    stack.push(root);

    while (!stack.isEmpty()) {
        TreeNode node = stack.pop();
        ans.addFirst(node.val);
        if (node.left != null) {
            stack.push(node.left);
        }
        if (node.right != null) {
            stack.push(node.right);
        }
    }
    return ans;
}
```

算法复杂度：

- 时间复杂度：访问每个节点恰好一次，因此时间复杂度为 O(N)，其中 N 是节点的个数，也就是树的大小。
- 空间复杂度：取决于树的结构，最坏情况需要保存整棵树，因此空间复杂度为 O(N)。

## 二叉树的层次遍历

102. 二叉树的层次遍历

给定一个二叉树，返回其按层次遍历的节点值。 （即逐层地，从左到右访问所有节点）。

例如：给定二叉树: [3,9,20,null,null,15,7],

        3
       / \
      9  20
        /  \
       15   7
   
返回其层次遍历结果：

    [
      [3],
      [9,20],
      [15,7]
    ]

### 递归

首先确认树非空，然后调用递归函数 helper(node, level)，参数是当前节点和节点的层次。

算法过程:

1. ans 为结果列表，level 为当前遍历的层数（初始为0）
2. 若 ans 的长度 = level，向 ans 增加一个空列表
3. 将节点值放入 ans 的第 level 个列表结尾
4. 遍历左右子节点，此时 level + 1

```java
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> ans = new ArrayList<>();
    robot(root, ans, 0);
    return ans;
}

private void robot(TreeNode root, List<List<Integer>> ans, int level) {
    if (root == null) {
        return;
    }
    if (ans.size() == level) {
        ans.add(new ArrayList());
    }
    ans.get(level).add(root.val);
    robot(root.left, ans, level + 1);
    robot(root.right, ans, level + 1);
}
```

复杂度分析

- 时间复杂度：O(N)，因为每个节点恰好会被运算一次。
- 空间复杂度：O(N)，保存输出结果的数组包含 N 个节点的值。

### 迭代

算法过程：

第 0 层只包含根节点 root ，算法实现如下：

1. 初始化队列只包含一个节点 root 和层次编号 0 ： level = 0。
2. 当队列非空的时候：
    * 新建一个空列表，表示当前层结果 current。
    * 计算当前层有多少个元素：等于队列的长度。
    * 将这些元素从队列中弹出，并加入 current 列表中。
    * 将他们的孩子节点作为下一层压入队列中。
    * 将 当前层结果 current 放入 ans 中。
    * 进入下一层循环。


```java
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }

    Queue<TreeNode> queue = new LinkedList<>();
    queue.add(root);

    while (!queue.isEmpty()) {
        List<Integer> current = new ArrayList<>();

        // 当前层的元素个数
        int length = queue.size();
        for (int i = 0; i < length; ++i) {
            TreeNode node = queue.remove();

            // 放入结果
            current.add(node.val);

            // 依次将 node 的左右子节点加入队列
            if (node.left != null) {
                queue.add(node.left);
            }
            if (node.right != null) {
                queue.add(node.right);
            }
        }
        ans.add(current);
    }
    return ans;
}
```

复杂度分析

- 时间复杂度：O(N)，因为每个节点恰好会被运算一次。
- 空间复杂度：O(N)，保存输出结果的数组包含 N 个节点的值。


## 二叉树的右视图

199. 二叉树的右视图

给定一棵二叉树，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看到的节点值。

示例:

    输入: [1,2,3,null,5,null,4]
    输出: [1, 3, 4]
    解释:

       1            <---
     /   \
    2     3         <---
     \     \
      5     4       <---


本题是`层序遍历`的变种，层序遍历是存储二叉树每行的每个元素，而本题仅存储二叉树每行的最后一个元素。

### 递归

```java
public List<Integer> rightSideView(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans, 0);
    return ans;
}

private void robot(TreeNode root, List<Integer> ans, int level) {
    if (root == null) {
        return;
    }
    if (ans.size() == level) {
        ans.add(root.val);
    }
    // 层序遍历的 ans 是一个 List<List<Integer>，是 ans.get(level).add(root.val);
    ans.set(level, root.val);
    robot(root.left, ans, level + 1);
    robot(root.right, ans, level + 1);
}
```

### 迭代

```java
public List<Integer> rightSideView(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }

    Queue<TreeNode> queue = new LinkedList<>();
    queue.add(root);

    while (!queue.isEmpty()) {
        int current = 0;

        // 当前层的元素个数
        int length = queue.size();
        for (int i = 0; i < length; ++i) {
            TreeNode node = queue.remove();

            // 放入结果
            current = node.val;

            // 依次将 node 的左右子节点加入队列
            if (node.left != null) {
                queue.add(node.left);
            }
            if (node.right != null) {
                queue.add(node.right);
            }
        }
        ans.add(current);
    }
    return ans;
}
```

## 在每个树行中找最大值

515. 在每个树行中找最大值

您需要在二叉树的每一行中找到最大的值。

示例：

输入: 

          1
         / \
        3   2
       / \   \  
      5   3   9 

    输出: [1, 3, 9]

本题也是`层序遍历`的变种，层序遍历是存储二叉树每行的每个元素，而本题仅存储二叉树每行的最大元素。

### 递归

```java
public List<Integer> largestValues(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans, 0);
    return ans;
}

private void robot(TreeNode root, List<Integer> ans, int level) {
    if (root == null) {
        return;
    }

    if (ans.size() <= level) {
        ans.add(Integer.MIN_VALUE);
    }

    ans.set(level, Math.max(ans.get(level), root.val));
    robot(root.left, ans, level + 1);
    robot(root.right, ans, level + 1);
}
```

### 迭代

```java
public List<Integer> largestValues(TreeNode root) {
    List<Integer> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }

    Queue<TreeNode> queue = new LinkedList<>();
    queue.add(root);

    while (!queue.isEmpty()) {
        int current = Integer.MIN_VALUE;

        // 当前层的元素个数
        int length = queue.size();
        for (int i = 0; i < length; ++i) {
            TreeNode node = queue.remove();

            // 放入结果（变化的地方）
            current = Math.max(current, node.val);

            // 依次将 node 的左右子节点加入队列
            if (node.left != null) {
                queue.add(node.left);
            }
            if (node.right != null) {
                queue.add(node.right);
            }
        }
        ans.add(current);
    }
    return ans;
}
```

## 二叉树的垂序遍历

987. 二叉树的垂序遍历

给定二叉树，按垂序遍历返回其结点值。

对位于 (X, Y) 的每个结点而言，其左右子结点分别位于 (X-1, Y-1) 和 (X+1, Y-1)。

把一条垂线从 X = -infinity 移动到 X = +infinity ，每当该垂线与结点接触时，我们按从上到下的顺序报告结点的值（ Y 坐标递减）。

如果两个结点位置相同，则首先报告的结点值较小。

按 X 坐标顺序返回非空报告的列表。每个报告都有一个结点值列表。

示例 1：

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-142733.jpg)

    输入：[3,9,20,null,null,15,7]
    输出：[[9],[3,15],[20],[7]]
    解释： 
    在不丧失其普遍性的情况下，我们可以假设根结点位于 (0, 0)：
    然后，值为 9 的结点出现在 (-1, -1)；
    值为 3 和 15 的两个结点分别出现在 (0, 0) 和 (0, -2)；
    值为 20 的结点出现在 (1, -1)；
    值为 7 的结点出现在 (2, -2)。

示例 2：

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-142746.jpg)@w=400

    输入：[1,2,3,4,5,6,7]
    输出：[[4],[2],[1,5,6],[3],[7]]
    解释：
    根据给定的方案，值为 5 和 6 的两个结点出现在同一位置。
    然而，在报告 "[1,5,6]" 中，结点值 5 排在前面，因为 5 小于 6。
 
提示：

树的结点数介于 1 和 1000 之间。
每个结点值介于 0 和 1000 之间。

### 解题思路

设根节点的(x,y)=(0,0)，对于节点坐标(x,y)，其左节点坐标为(x-1,y-1)，右节点坐标为(x+1,y-1)。

1. 构造 List<PositionNode> posNodes，遍历二叉树每个节点，填入 PositionNode 的 x 坐标、y 坐标、val 值。
2. 将 posNodes 展开成 key 是 x 坐标、value 是对应 PositionNode 的 positionMap，注意这里使用 TreeMap，因为要对 x 坐标排序。
3. 构建结果 ans：遍历 positionMap，相同位置节点，按照自然顺序排序（即先按照 Y 降序排列；若 Y 相同，则按照 val 升序排列）

### 代码

```java
public class PositionNode {
    int val;
    int x;
    int y;

    PositionNode(int val, int x, int y) {
        this.val = val;
        this.x = x;
        this.y = y;
    }

    public int getVal() {
        return val;
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }
}

public List<List<Integer>> verticalTraversal(TreeNode root) {

    // 构建节点的位置信息
    List<PositionNode> posNodes = new ArrayList<>();
    robot(root, posNodes, 0, 0);

    // 将 posNodes 展开成 key 是 x 坐标、value 是对应 PositionNode 的 map
    // 注意这里使用 TreeMap，因为要对 x 坐标排序
    Map<Integer, List<PositionNode>> positionMap = posNodes.stream().collect(
            Collectors.groupingBy(PositionNode::getX, TreeMap::new, Collectors.toList()));

    // 构建结果
    List<List<Integer>> ans = new ArrayList<>();
    positionMap.forEach((k, v) -> {
        // 题目要求：相同位置节点，按照自然顺序排序（即先按照 Y 降序排列；若 Y 相同，则按照 val 升序排列）
        v.sort(Comparator.comparing(PositionNode::getY).reversed()
                .thenComparing(PositionNode::getVal));
        ans.add(v.stream().map(PositionNode::getVal).collect(Collectors.toList()));
    });
    return ans;
}

private void robot(TreeNode root, List<PositionNode> posNodes, int x, int y) {
    if (root == null) {
        return;
    }

    posNodes.add(new PositionNode(root.val, x, y));

    // 根节点的(x,y)=(0,0)，若某个节点坐标为(x,y)，则左节点坐标为(x-1,y-1)，右节点坐标为(x+1,y-1)
    robot(root.left, posNodes, x - 1, y - 1);
    robot(root.right, posNodes, x + 1, y - 1);
}
```

## 二叉树的锯齿形层次遍历

103. 二叉树的锯齿形层次遍历

给定一个二叉树，返回其节点值的锯齿形层次遍历。（即先从左往右，再从右往左进行下一层遍历，以此类推，层与层之间交替进行）。

例如：
给定二叉树 [3,9,20,null,null,15,7],

        3
       / \
      9  20
        /  \
       15   7
   
返回锯齿形层次遍历如下：

    [
      [3],
      [20,9],
      [15,7]
    ]

本题是`层序遍历`的变种，仅需将层序遍历的偶数行逆序即可。

### 递归

```java
public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
    List<List<Integer>> ans = new ArrayList<>();
    robot(root, ans, 0);
    // 与层序遍历相比，变化的部分
    for (int i = 1; i < ans.size(); i += 2) {
        Collections.reverse(ans.get(i));
    }
    return ans;
}

private void robot(TreeNode root, List<List<Integer>> ans, int level) {
    if (root == null) {
        return;
    }
    if (ans.size() == level) {
        ans.add(new ArrayList());
    }
    ans.get(level).add(root.val);
    robot(root.left, ans, level + 1);
    robot(root.right, ans, level + 1);
}
```

### 迭代

```java
public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
    List<List<Integer>> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }

    Queue<TreeNode> queue = new LinkedList<>();
    queue.add(root);

    while (!queue.isEmpty()) {
        List<Integer> current = new ArrayList<>();

        // 当前层的元素个数
        int length = queue.size();
        for (int i = 0; i < length; ++i) {
            TreeNode node = queue.remove();

            // 放入结果
            current.add(node.val);

            // 依次将 node 的左右子节点加入队列
            if (node.left != null) {
                queue.add(node.left);
            }
            if (node.right != null) {
                queue.add(node.right);
            }
        }
        ans.add(current);
    }
    // 与层序遍历相比，变化的部分
    for (int i = 1; i < ans.size(); i += 2) {
        Collections.reverse(ans.get(i));
    }
    return ans;
}
```

## N 叉树遍历

### N叉树的层序遍历

429. N叉树的层序遍历

给定一个 N 叉树，返回其节点值的层序遍历。 (即从左到右，逐层遍历)。

例如，给定一个 3叉树 :

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-145322.jpg)@w=400

返回其层序遍历:

    [
         [1],
         [3,2,4],
         [5,6]
    ]
 

说明:

1. 树的深度不会超过 1000。
2. 树的节点总数不会超过 5000。


```java
public List<List<Integer>> levelOrder(Node root) {
    List<List<Integer>> ans = new ArrayList<>();
    robot(root, ans, 0);
    return ans;
}

private void robot(Node root, List<List<Integer>> ans, int level) {
    if (root == null) {
        return;
    }

    if (ans.size() <= level) {
        ans.add(new ArrayList<>());
    }

    ans.get(level).add(root.val);

    if (root.children == null) {
        return;
    }
    for (Node child : root.children) {
        robot(child, ans, level + 1);
    }
}
```

### N叉树的前序遍历

589. N叉树的前序遍历

给定一个 N 叉树，返回其节点值的前序遍历。

例如，给定一个 3叉树 :

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-145342.jpg)@w=400

返回其前序遍历: [1,3,5,6,2,4]。

说明: 递归法很简单，你可以使用`迭代`法完成此题吗？

#### 递归

```java
public List<Integer> preorder(Node root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans);
    return ans;
}

private void robot(Node root, List<Integer> ans) {
    if (root == null) {
        return;
    }

    ans.add(root.val);
    if (root.children == null) {
        return;
    }

    for (Node child : root.children) {
        robot(child, ans);
    }
}
```

#### 迭代

```java
public List<Integer> preorder(Node root) {
    List<Integer> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }
    Deque<Node> deque = new ArrayDeque<>();
    deque.push(root);
    while (!deque.isEmpty()) {
        Node tmp = deque.pop();
        if (tmp != null) {
            ans.add(tmp.val);
            if (tmp.children == null) {
                continue;
            }
            for (int i = tmp.children.size() - 1; i >= 0; i--) {
                deque.push(tmp.children.get(i));
            }
        }
    }
    return ans;
}
```

### N叉树的后序遍历

590. N叉树的后序遍历

给定一个 N 叉树，返回其节点值的后序遍历。

例如，给定一个 3叉树 :

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-145416.jpg)@w=400

返回其后序遍历: [5,6,3,2,4,1].

说明: 递归法很简单，你可以使用迭代法完成此题吗?

#### 递归

```java
public List<Integer> postorder(Node root) {
    List<Integer> ans = new ArrayList<>();
    robot(root, ans);
    return ans;
}

private void robot(Node root, List<Integer> ans) {
    if (root == null) {
        return;
    }

    if (root.children != null) {
        for (Node child : root.children) {
            robot(child, ans);
        }
    }
    ans.add(root.val);
}
```

#### 迭代

```java
// 后续遍历：左右中
// 迭代顺序：中右左
public List<Integer> postorder(Node root) {
    List<Integer> ans = new ArrayList<>();
    if (root == null) {
        return ans;
    }
    Stack<Node> stack = new Stack<>();
    stack.push(root);
    while (!stack.isEmpty()) {
        Node pop = stack.pop();
        ans.add(pop.val);
        List<Node> children = pop.children;
        if (children == null) {
            continue;
        }
        for (Node child : children) {
            stack.push(child);
        }
    }
    Collections.reverse(ans);
    return ans;
}
```

# 二叉搜索树

## 不同的二叉搜索树

96. 不同的二叉搜索树

给定一个整数 n，求以 1 ... n 为节点组成的二叉搜索树有多少种？

示例:

    输入: 3
    输出: 5
    解释:
    给定 n = 3, 一共有 5 种不同结构的二叉搜索树:

       1         3     3      2      1
        \       /     /      / \      \
         3     2     1      1   3      2
        /     /       \                 \
       2     1         2                 3

```java
public int numTrees(int n) {
    int[] ans = new int[n + 2];
    ans[0] = 1; ans[1] = 1; ans[2] = 2;
    // f(n) = f(0)*f(n-1) + f(1)*f(n-2) + ……
    for(int i = 3; i <= n; i++) {
        for(int j = 0; j <= i - 1; j++) {
            ans[i] += ans[j] * ans[i - j - 1];
        }
    }
    return ans[n];
}
```

## 不同的二叉搜索树 II

95. 不同的二叉搜索树 II

给定一个整数 n，生成所有由 1 ... n 为节点所组成的二叉搜索树。

示例:

    输入: 3
    输出:
    [
      [1,null,3,2],
      [3,2,null,1],
      [3,1,null,null,2],
      [2,1,3],
      [1,null,2,null,3]
    ]
    解释:
    以上的输出对应以下 5 种不同结构的二叉搜索树：

       1         3     3      2      1
        \       /     /      / \      \
         3     2     1      1   3      2
        /     /       \                 \
       2     1         2                 3

```java
public List<TreeNode> generateTrees(int n) {
    if(n <= 0) return new ArrayList<>();
    return build(1, n);
}
private List<TreeNode> build(int start, int end) {
    List<TreeNode> roots = new ArrayList<>();       
    if(start > end) {           
        // null也要放入，否则下面的双重循环进不去
        roots.add(null);
        return roots;
    }
    if(start == end) {
        roots.add(new TreeNode(start));
        return roots;
    }
    for(int i = start; i <= end; i++) {
        List<TreeNode> leftList = build(start, i - 1);
        List<TreeNode> rightList = build(i + 1, end);
        for(TreeNode left : leftList) {             
            for(TreeNode right : rightList) {
                TreeNode root = new TreeNode(i);
                root.left = left;
                root.right = right;
                roots.add(root);
            }
        }
    }
    return roots;
}
```

## 验证二叉搜索树

98. 验证二叉搜索树

给定一个二叉树，判断其是否是一个有效的二叉搜索树。

假设一个二叉搜索树具有如下特征：

- 节点的左子树只包含`小于`当前节点的数。
- 节点的右子树只包含`大于`当前节点的数。
- 所有左子树和右子树自身必须也是二叉搜索树。

示例 1:

    输入:
        2
       / \
      1   3
    输出: true
    
示例 2:

    输入:
        5
       / \
      1   4
         / \
        3   6
    输出: false
    解释: 输入为: [5,1,4,null,null,3,6]。
         根节点的值为 5 ，但是其右子节点值为 4 。

```java
public boolean isValidBST(TreeNode root) {
    // 用long型
    return isValidBST(root, Long.MIN_VALUE, Long.MAX_VALUE);
}

private boolean isValidBST(TreeNode root, long min, long max) {
    if (root == null) {
        return true;
    }
    if (root.val >= max || root.val <= min) {
        return false;
    }
    return isValidBST(root.left, min, root.val) && isValidBST(root.right, root.val, max);
}
```

## 恢复二叉搜索树

99. 恢复二叉搜索树

二叉搜索树中的两个节点被错误地交换。

请在不改变其结构的情况下，恢复这棵树。

示例 1:

    输入: [1,3,null,null,2]

       1
      /
     3
      \
       2

    输出: [3,1,null,null,2]

       3
      /
     1
      \
       2
       
示例 2:

    输入: [3,1,4,null,null,2]

      3
     / \
    1   4
       /
      2

    输出: [2,1,4,null,null,3]

      2
     / \
    1   4
       /
      3

进阶:
- 使用 O(n) 空间复杂度的解法很容易实现。
- 你能想出一个只使用常数空间的解决方案吗？

```java
TreeNode first = null, second = null;
TreeNode pre = new TreeNode(Integer.MIN_VALUE);
public void recoverTree(TreeNode root) {
    if(root == null) return;
    robot(root);
    if(first != null && second != null) {
        int tmp = first.val;
        first.val = second.val;
        second.val = tmp;
    }
}
private void robot(TreeNode root) {
    if(root == null) return;
    robot(root.left);
    // 找到交换的两个节点
    if(first == null && pre.val > root.val) {
        first = pre;
    }
    if(first != null && pre.val > root.val) {
        second = root;
    }
    pre = root;
    robot(root.right);
}
```

## 修剪二叉搜索树

669. 修剪二叉搜索树

给定一个二叉搜索树，同时给定最小边界L 和最大边界 R。通过修剪二叉搜索树，使得所有节点的值在[L, R]中 (R>=L) 。你可能需要改变树的根节点，所以结果应当返回修剪好的二叉搜索树的新的根节点。

示例 1:

    输入: 
        1
       / \
      0   2

      L = 1
      R = 2

    输出: 
        1
          \
           2
       
示例 2:

    输入: 
        3
       / \
      0   4
       \
        2
       /
      1

      L = 1
      R = 3

    输出: 
          3
         / 
       2   
      /
     1

```java
public TreeNode trimBST(TreeNode root, int L, int R) {
    if (root == null) {
        return null;
    }
    if (root.val > R) {
        return trimBST(root.left, L, R);
    }
    if (root.val < L) {
        return trimBST(root.right, L, R);
    }

    root.left = trimBST(root.left, L, R);
    root.right = trimBST(root.right, L, R);
    return root;
}
```

## 将有序数组转换为二叉搜索树

108. 将有序数组转换为二叉搜索树

将一个按照升序排列的有序数组，转换为一棵高度平衡二叉搜索树。

本题中，一个高度平衡二叉树是指一个二叉树每个节点 的左右两个子树的高度差的绝对值不超过 1。

示例:

    给定有序数组: [-10,-3,0,5,9],

    一个可能的答案是：[0,-3,9,-10,null,5]，它可以表示下面这个高度平衡二叉搜索树：

          0
         / \
       -3   9
       /   /
     -10  5

```java
public TreeNode sortedArrayToBST(int[] nums) {
    if (nums == null || nums.length == 0) {
        return null;
    }
    return robot(nums, 0, nums.length - 1);
}

private TreeNode robot(int[] nums, int start, int end) {
    if (start > end) {
        return null;
    }
    int mid = start + (end - start) / 2;
    TreeNode root = new TreeNode(nums[mid]);
    root.left = robot(nums, start, mid - 1);
    root.right = robot(nums, mid + 1, end);
    return root;
}
```

## 二叉搜索树迭代器

173. 二叉搜索树迭代器

实现一个二叉搜索树迭代器。你将使用二叉搜索树的根节点初始化迭代器。

调用 `next()` 将返回二叉搜索树中的下一个最小的数。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-150349.jpg)

示例：

    BSTIterator iterator = new BSTIterator(root);
    iterator.next();    // 返回 3
    iterator.next();    // 返回 7
    iterator.hasNext(); // 返回 true
    iterator.next();    // 返回 9
    iterator.hasNext(); // 返回 true
    iterator.next();    // 返回 15
    iterator.hasNext(); // 返回 true
    iterator.next();    // 返回 20
    iterator.hasNext(); // 返回 false
 

提示：

- next() 和 hasNext() 操作的时间复杂度是 O(1)，并使用 O(h) 内存，其中 h 是树的高度。
- 你可以假设 next() 调用总是有效的，也就是说，当调用 next() 时，BST 中至少存在一个下一个最小的数。

```java
class BSTIterator {

    Stack<TreeNode> vector = new Stack<>();
    TreeNode current;

    public BSTIterator(TreeNode root) {
        current = root;
        // 一直放入左儿子（左）
        while (current != null) {
            vector.push(current);
            current = current.left;
        }
    }

    /** @return whether we have a next smallest number */
    public boolean hasNext() {
        return !vector.isEmpty() || current != null;
    }

    /** @return the next smallest number */
    public int next() {
        // 一直放入左儿子（左）
        while (current != null) {
            vector.push(current);
            current = current.left;
        }
        int ans = 0;
        // 访问当前元素（中），把右儿子入栈（右）
        if (!vector.isEmpty()) {
            current = vector.pop();
            ans = current.val;
            current = current.right;
        }
        return ans;
    }
}

/**
 * Your BSTIterator object will be instantiated and called as such:
 * BSTIterator obj = new BSTIterator(root);
 * int param_1 = obj.next();
 * boolean param_2 = obj.hasNext();
 */
```

## 二叉搜索树中第K小的元素

230. 二叉搜索树中第K小的元素

给定一个二叉搜索树，编写一个函数 `kthSmallest` 来查找其中第 **k** 个最小的元素。

说明：
你可以假设 k 总是有效的，1 ≤ k ≤ 二叉搜索树元素个数。

示例 1:

    输入: root = [3,1,4,null,2], k = 1
       3
      / \
     1   4
      \
       2
    输出: 1

示例 2:

    输入: root = [5,3,6,2,4,null,null,1], k = 3
           5
          / \
         3   6
        / \
       2   4
      /
     1
    输出: 3

进阶：
如果二叉搜索树经常被修改（插入/删除操作）并且你需要频繁地查找第 k 小的值，你将如何优化 `kthSmallest` 函数？

```java
int ans = 0;
int count = 0;

public int kthSmallest(TreeNode root, int k) {
    count = k;
    robot(root);
    return ans;
}

private void robot(TreeNode root) {
    if (root == null) {
        return;
    }
    robot(root.left);
    if (--count == 0) {
        ans = root.val;
        return;
    }
    robot(root.right);
}
```

## 二叉搜索树的最近公共祖先

235. 二叉搜索树的最近公共祖先

给定一个二叉搜索树, 找到该树中两个指定节点的最近公共祖先。

百度百科中最近公共祖先的定义为：“对于有根树 T 的两个结点 p、q，最近公共祖先表示为一个结点 x，满足 x 是 p、q 的祖先且 x 的深度尽可能大（**一个节点也可以是它自己的祖先**）。”

例如，给定如下二叉搜索树:  root = [6,2,8,0,4,7,9,null,null,3,5]

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-150407.jpg)

示例 1:

    输入: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8
    输出: 6 
    解释: 节点 2 和节点 8 的最近公共祖先是 6。

示例 2:

    输入: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 4
    输出: 2
    解释: 节点 2 和节点 4 的最近公共祖先是 2, 因为根据定义最近公共祖先节点可以为节点本身。
 
说明:

- 所有节点的值都是唯一的。
- p、q 为不同节点且均存在于给定的二叉搜索树中。

```java
public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    if (root == null || p == null || q == null) {
        return null;
    }
    TreeNode left = lowestCommonAncestor(root.left, p, q);
    if (root.val <= Math.max(p.val, q.val) && root.val >= Math.min(p.val, q.val)) {
        return root;
    }
    TreeNode right = lowestCommonAncestor(root.right, p, q);
    return left == null ? right : left;
}
```

## 删除二叉搜索树中的节点

450. 删除二叉搜索树中的节点

给定一个二叉搜索树的根节点 **root** 和一个值 **key**，删除二叉搜索树中的 **key** 对应的节点，并保证二叉搜索树的性质不变。返回二叉搜索树（有可能被更新）的根节点的引用。

一般来说，删除节点可分为两个步骤：

1. 首先找到需要删除的节点；
2. 如果找到了，删除它。

说明： 要求算法时间复杂度为 O(h)，h 为树的高度。

示例:

    root = [5,3,6,2,4,null,7]
    key = 3

        5
       / \
      3   6
     / \   \
    2   4   7

    给定需要删除的节点值是 3，所以我们首先找到 3 这个节点，然后删除它。

    一个正确的答案是 [5,4,6,2,null,null,7], 如下图所示。

        5
       / \
      4   6
     /     \
    2       7

    另一个正确答案是 [5,2,6,null,4,null,7]。

        5
       / \
      2   6
       \   \
        4   7

```java
// todo 题目复杂，面试时不会常考，考虑忽略此题目
```

## 二叉搜索树中的搜索

700. 二叉搜索树中的搜索

给定二叉搜索树（BST）的根节点和一个值。 你需要在BST中找到节点值等于给定值的节点。 返回以该节点为根的子树。 如果节点不存在，则返回 NULL。

例如，

    给定二叉搜索树:

            4
           / \
          2   7
         / \
        1   3

    和值: 2

你应该返回如下子树:

          2     
         / \   
        1   3

在上述示例中，如果要找的值是 5，但因为没有节点值为 5，我们应该返回 NULL。

```java
public TreeNode searchBST(TreeNode root, int val) {
    if (root == null || root.val == val) {
        return root;
    }

    if (root.val < val) {
        return searchBST(root.right, val);
    }

    if (root.val > val) {
        return searchBST(root.left, val);
    }

    return null;
}
```

## 二叉搜索树中的插入操作

给定二叉搜索树（BST）的根节点和要插入树中的值，将值插入二叉搜索树。 返回插入后二叉搜索树的根节点。 保证原始二叉搜索树中不存在新值。

注意，可能存在多种有效的插入方式，只要树在插入后仍保持为二叉搜索树即可。 你可以返回任意有效的结果。

例如, 

    给定二叉搜索树:

            4
           / \
          2   7
         / \
        1   3

    和 插入的值: 5

你可以返回这个二叉搜索树:

             4
           /   \
          2     7
         / \   /
        1   3 5
    
或者这个树也是有效的:

             5
           /   \
          2     7
         / \   
        1   3
             \
              4

```java
public TreeNode insertIntoBST(TreeNode root, int val) {
    if (root == null) {
        return new TreeNode(val);
    }

    if (root.val > val) {
        root.left = insertIntoBST(root.left, val);
    } else {
        root.right = insertIntoBST(root.right, val);
    }

    return root;
}
```

# 深搜、广搜

## 相同的树

给定两个二叉树，编写一个函数来检验它们是否相同。

如果两个树在结构上相同，并且节点具有相同的值，则认为它们是相同的。

示例 1:

    输入:       1         1
              / \       / \
             2   3     2   3

            [1,2,3],   [1,2,3]

    输出: true

示例 2:

    输入:      1          1
              /           \
             2             2

            [1,2],     [1,null,2]

    输出: false

示例 3:

    输入:       1         1
              / \       / \
             2   1     1   2

            [1,2,1],   [1,1,2]

    输出: false

```java
public boolean isSameTree(TreeNode p, TreeNode q) {
    if (p == q) {
        return true;
    }

    if (p == null || q == null) {
        return false;
    }

    return p.val == q.val && isSameTree(p.left, q.left) && isSameTree(p.right, q.right);
}
```

## 对称二叉树

给定一个二叉树，检查它是否是镜像对称的。

例如，二叉树 [1,2,2,3,4,4,3] 是对称的。

        1
       / \
      2   2
     / \ / \
    3  4 4  3

但是下面这个 [1,2,2,null,3,null,3] 则不是镜像对称的:

        1
       / \
      2   2
       \   \
       3    3
   
说明:

如果你可以运用递归和迭代两种方法解决这个问题，会很加分。

### 递归

```java
public boolean isSymmetric(TreeNode root) {
    return robot(root, root);
}

boolean robot(TreeNode p, TreeNode q) {

    if (p == null && q == null) {
        return true;
    }

    if (p == null || q == null) {
        return false;
    }

    return p.val == q.val && robot(p.left, q.right) && robot(p.right, q.left);
}
```

### 迭代

```java
public boolean isSymmetric2(TreeNode root) {

    if (root == null) {
        return true;
    }

    Stack<TreeNode> stack = new Stack<>();

    stack.push(root.left);
    stack.push(root.right);

    while (!stack.isEmpty()) {
        TreeNode p = stack.pop();
        TreeNode q = stack.pop();

        if (p == null && q == null) {
            continue;
        }

        if (p == null || q == null) {
            return false;
        }

        if (p.val != q.val) {
            return false;
        }

        stack.push(p.left);
        stack.push(q.right);

        stack.push(p.right);
        stack.push(q.left);
    }

    return true;
}
```

## 翻转二叉树

226. 翻转二叉树

示例：

输入：

         4
       /   \
      2     7
     / \   / \
    1   3 6   9

输出：

         4
       /   \
      7     2
     / \   / \
    9   6 3   1

备注:
这个问题是受到 Max Howell 的 原问题 启发的 ：

    谷歌：我们90％的工程师使用您编写的软件(Homebrew)，但是您却无法在面试时在白板上写出翻转二叉树这道题，这太糟糕了。

```java
public TreeNode invertTree(TreeNode root) {
    if (root == null) {
        return null;
    }

    TreeNode tmp = root.left;
    root.left = root.right;
    root.right = tmp;

    invertTree(root.left);
    invertTree(root.right);

    return root;
}
```

## 二叉树的最大深度

104. 二叉树的最大深度

给定一个二叉树，找出其最大深度。

二叉树的深度为根节点到最远叶子节点的最长路径上的节点数。

说明: 叶子节点是指没有子节点的节点。

示例：
给定二叉树 [3,9,20,null,null,15,7]，

        3
       / \
      9  20
        /  \
       15   7
   
返回它的最大深度 3 。

```java
public int maxDepth(TreeNode root) {

    if (root == null) {
        return 0;
    }

    int left = maxDepth(root.left);
    int right = maxDepth(root.right);

    return left > right ? (left + 1) : (right + 1);
}
```

## 二叉树的最小深度

111. 二叉树的最小深度

给定一个二叉树，找出其最小深度。

最小深度是从根节点到最近叶子节点的最短路径上的节点数量。

说明: 叶子节点是指没有子节点的节点。

示例:

给定二叉树 [3,9,20,null,null,15,7],

        3
       / \
      9  20
        /  \
       15   7
   
返回它的最小深度  2.

```java
public int minDepth(TreeNode root) {
    if (root == null) {
        return 0;
    }
    int left = minDepth(root.left);
    int right = minDepth(root.right);
    return (left == 0 || right == 0) ? (left + right + 1) : Math.min(left, right) + 1;
}
```

## 平衡二叉树

110. 平衡二叉树

给定一个二叉树，判断它是否是高度平衡的二叉树。

本题中，一棵高度平衡二叉树定义为：

一个二叉树每个节点 的左右两个子树的高度差的绝对值不超过1。

示例 1:

给定二叉树 [3,9,20,null,null,15,7]

        3
       / \
      9  20
        /  \
       15   7

返回 `true` 。

示例 2:

给定二叉树 [1,2,2,3,3,null,null,4,4]

           1
          / \
         2   2
        / \
       3   3
      / \
     4   4

返回 `false` 。

```java
public boolean isBalanced(TreeNode root) {
    if (root == null) {
        return true;
    }

    return Math.abs(depth(root.left) - depth(root.right)) <= 1 && isBalanced(root.left)
            && isBalanced(root.right);
}

int depth(TreeNode node) {
    if (node == null) {
        return 0;
    }

    return Math.max(depth(node.left), depth(node.right)) + 1;
}
```

## 完全二叉树的节点个数

给出一个完全二叉树，求出该树的节点个数。

说明：

完全二叉树的定义如下：在完全二叉树中，除了最底层节点可能没填满外，其余每层节点数都达到最大值，并且最下面一层的节点都集中在该层最左边的若干位置。若最底层为第 h 层，则该层包含 1~ 2^h 个节点。

示例:

输入: 

        1
       / \
      2   3
     / \  /
    4  5 6

    输出: 6


```java
public int countNodes(TreeNode root) {
    if (root == null) {
        return 0;
    }

    int left = 0;
    int right = 0;

    TreeNode p = root;
    while (p != null) {
        p = p.left;
        left++;
    }

    p = root;
    while (p != null) {
        p = p.right;
        right++;
    }

    if (left == right) {
        return (1 << left) - 1;
    }

    return countNodes(root.left) + countNodes(root.right) + 1;
}
```

## 二叉树最大宽度

662. 二叉树最大宽度

给定一个二叉树，编写一个函数来获取这个树的最大宽度。树的宽度是所有层中的最大宽度。这个二叉树与 **满二叉树（full binary tree）** 结构相同，但一些节点为空。

每一层的宽度被定义为两个端点（该层最左和最右的非空节点，两端点间的null节点也计入长度）之间的长度。

示例 1:

    输入: 

               1
             /   \
            3     2
           / \     \  
          5   3     9 

    输出: 4
    解释: 最大值出现在树的第 3 层，宽度为 4 (5,3,null,9)。

示例 2:

    输入: 

              1
             /  
            3    
           / \       
          5   3     

    输出: 2
    解释: 最大值出现在树的第 3 层，宽度为 2 (5,3)。

示例 3:

    输入: 

              1
             / \
            3   2 
           /        
          5      

    输出: 2
    解释: 最大值出现在树的第 2 层，宽度为 2 (3,2)。

示例 4:

    输入: 

              1
             / \
            3   2
           /     \  
          5       9 
         /         \
        6           7
    输出: 8
    解释: 最大值出现在树的第 4 层，宽度为 8 (6,null,null,null,null,null,null,7)。

注意: 答案在32位有符号整数的表示范围内。

```java
public int widthOfBinaryTree(TreeNode root) {
    int[] ans = new int[1];
    robot(root, ans, new ArrayList<>(), 0, 1);
    return ans[0];
}

private void robot(TreeNode root, int[] ans, ArrayList<Integer> leftIndexes, int level,
        int index) {
    if (root == null) {
        return;
    }

    if (leftIndexes.size() <= level) {
        leftIndexes.add(index);
    }

    ans[0] = Math.max(ans[0], index - leftIndexes.get(level) + 1);
    robot(root.left, ans, leftIndexes, level + 1, 2 * index);
    robot(root.right, ans, leftIndexes, level + 1, 2 * index + 1);
}
```

## 二叉树的直径

543. 二叉树的直径

给定一棵二叉树，你需要计算它的直径长度。一棵二叉树的直径长度是任意两个结点路径长度中的最大值。这条路径可能穿过根结点。

示例 :
给定二叉树

              1
             / \
            2   3
           / \     
          4   5    
      
返回 3, 它的长度是路径 [4,2,1,3] 或者 [5,2,1,3]。

**注意**：两结点之间的路径长度是以它们之间边的数目表示。

```java
public int diameterOfBinaryTree(TreeNode root) {
    int[] ans = new int[1];
    robot(root, ans);
    return ans[0];
}

private int robot(TreeNode root, int[] ans) {
    if (root == null) {
        return 0;
    }

    int left = robot(root.left, ans);
    int right = robot(root.right, ans);

    // 维护直径最大值
    ans[0] = Math.max(left + right, ans[0]);

    // 返回当前节点的最大直径
    return Math.max(left, right) + 1;
}
```

## 二叉树的坡度

563. 二叉树的坡度

给定一个二叉树，计算**整个树**的坡度。

一个树的**节点的坡度**定义即为，该节点左子树的结点之和和右子树结点之和的**差的绝对值**。空结点的的坡度是0。

**整个树**的坡度就是其所有节点的坡度之和。

示例:

    输入: 
             1
           /   \
          2     3
    输出: 1
    解释: 
    结点的坡度 2 : 0
    结点的坡度 3 : 0
    结点的坡度 1 : |2-3| = 1
    树的坡度 : 0 + 0 + 1 = 1

注意:

- 任何子树的结点的和不会超过32位整数的范围。
- 坡度的值不会超过32位整数的范围。

```java
public int findTilt(TreeNode root) {
    int[] ans = new int[1];
    robot(root, ans);
    return ans[0];

}

private int robot(TreeNode root, int[] ans) {
    if (root == null) {
        return 0;
    }

    int left = robot(root.left, ans);
    int right = robot(root.right, ans);
    ans[0] += Math.abs(left - right);
    return left + right + root.val;
}
```

## 二叉树的所有路径

257. 二叉树的所有路径

给定一个二叉树，返回所有从根节点到叶子节点的路径。

说明: 叶子节点是指没有子节点的节点。

示例:

    输入:

       1
     /   \
    2     3
     \
      5

    输出: ["1->2->5", "1->3"]

    解释: 所有根节点到叶子节点的路径为: 1->2->5, 1->3

```java
public List<String> binaryTreePaths(TreeNode root) {
    List<String> ans = new ArrayList<>();
    robot(root, ans, "");
    return ans;
}

private void robot(TreeNode root, List<String> ans, String path) {
    if (root == null) {
        return;
    }
    if (root.left == null && root.right == null) {
        ans.add(path + root.val);
        return;
    }
    robot(root.left, ans, path + root.val + "->");
    robot(root.right, ans, path + root.val + "->");
}
```

## 二叉树的最近公共祖先

236. 二叉树的最近公共祖先

给定一个二叉树, 找到该树中两个指定节点的最近公共祖先。

百度百科中最近公共祖先的定义为：“对于有根树 T 的两个结点 p、q，最近公共祖先表示为一个结点 x，满足 x 是 p、q 的祖先且 x 的深度尽可能大（**一个节点也可以是它自己的祖先**）。”

例如，给定如下二叉树:  root = [3,5,1,6,2,0,8,null,null,7,4]

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-150439.jpg)

示例 1:

    输入: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
    输出: 3
    解释: 节点 5 和节点 1 的最近公共祖先是节点 3。

示例 2:

    输入: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
    输出: 5
    解释: 节点 5 和节点 4 的最近公共祖先是节点 5。因为根据定义最近公共祖先节点可以为节点本身。
 

说明:

- 所有节点的值都是唯一的。
- p、q 为不同节点且均存在于给定的二叉树中。

```java
public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {

    if (root == null || root == p || root == q) {
        return root;
    }

    TreeNode left = lowestCommonAncestor(root.left, p, q);
    TreeNode right = lowestCommonAncestor(root.right, p, q);

    if (left != null && right != null) {
        return root;
    }

    return left == null ? right : left;
}
```

## 最深叶节点的最近公共祖先

1123. 最深叶节点的最近公共祖先

给你一个有根节点的二叉树，找到它最深的叶节点的最近公共祖先。

回想一下：

- **叶节点** 是二叉树中没有子节点的节点
- 树的根节点的 **深度** 为 0，如果某一节点的深度为 d，那它的子节点的深度就是 d+1
- 如果我们假定 A 是一组节点 S 的 **最近公共祖先** 中的每个节点都在以 A 为根节点的子树中，且 A 的深度达到此条件下可能的最大值。
 

示例 1：

    输入：root = [1,2,3]
    输出：[1,2,3]

示例 2：

    输入：root = [1,2,3,4]
    输出：[4]

示例 3：

    输入：root = [1,2,3,4,5]
    输出：[2,4,5]
 

提示：

- 给你的树中将有 1 到 1000 个节点。
- 树中每个节点的值都在 1 到 1000 之间。

```java
public TreeNode lcaDeepestLeaves(TreeNode root) {
    if (root == null) {
        return null;
    }

    int left = depth(root.left);
    int right = depth(root.right);

    if (left == right) {
        return root;
    }

    return left > right ? lcaDeepestLeaves(root.left) : lcaDeepestLeaves(root.right);
}

private int depth(TreeNode root) {
    if (root == null) {
        return 0;
    }

    int left = depth(root.left);
    int right = depth(root.right);

    return Math.max(left, right) + 1;
}
```

# 路径和

## 左叶子之和

404. 左叶子之和

计算给定二叉树的所有左叶子之和。

示例：

        3
       / \
      9  20
        /  \
       15   7

在这个二叉树中，有两个左叶子，分别是 9 和 15，所以返回 24

```java
public int sumOfLeftLeaves(TreeNode root) {
    int[] ans = new int[1];
    robot(root, ans, false);
    return ans[0];
}

private void robot(TreeNode root, int[] ans, boolean isLeft) {
    if (root == null) {
        return;
    }

    if (root.left == null && root.right == null && isLeft) {
        ans[0] += root.val;
    }

    robot(root.left, ans, true);
    robot(root.right, ans, false);
}
```

## 路径总和

112. 路径总和

给定一个二叉树和一个目标和，判断该树中是否存在根节点到叶子节点的路径，这条路径上所有节点值相加等于目标和。

说明: 叶子节点是指没有子节点的节点。

示例: 
给定如下二叉树，以及目标和 `sum = 22`，

                  5
                 / \
                4   8
               /   / \
              11  13  4
             /  \      \
            7    2      1
        
返回 true, 因为存在目标和为 22 的根节点到叶子节点的路径 `5->4->11->2`。

```java
public boolean hasPathSum(TreeNode root, int sum) {
    if (root == null) {
        return false;
    }

    // 叶子节点 && 和为 sum
    if (root.left == null && root.right == null && sum - root.val == 0) {
        return true;
    }
    return hasPathSum(root.left, sum - root.val) || hasPathSum(root.right, sum - root.val);
}
```

## 路径总和 II

113. 路径总和 II

给定一个二叉树和一个目标和，找到所有从根节点到叶子节点路径总和等于给定目标和的路径。

说明: 叶子节点是指没有子节点的节点。

示例:
给定如下二叉树，以及目标和 sum = 22，

              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1

返回:

    [
       [5,4,11,2],
       [5,8,4,5]
    ]

```java
public List<List<Integer>> pathSum(TreeNode root, int sum) {
    List<List<Integer>> ans = new ArrayList<>();
    robot(root, sum, ans, new ArrayList<>());
    return ans;
}

private void robot(TreeNode root, int sum, List<List<Integer>> ans, List<Integer> tmp) {
    if (root == null) {
        return;
    }
    tmp.add(root.val);
    if (root.left == null && root.right == null && sum == root.val) {
        ans.add(new ArrayList(tmp));
        tmp.remove(tmp.size() - 1);
        return;
    }
    robot(root.left, sum - root.val, ans, tmp);
    robot(root.right, sum - root.val, ans, tmp);
    tmp.remove(tmp.size() - 1);
}
```

## 路径总和 III

437. 路径总和 III

给定一个二叉树，它的每个结点都存放着一个整数值。

找出路径和等于给定数值的路径总数。

路径不需要从根节点开始，也不需要在叶子节点结束，但是路径方向必须是向下的（只能从父节点到子节点）。

二叉树不超过1000个节点，且节点数值范围是 [-1000000,1000000] 的整数。

示例：

root = [10,5,-3,3,2,null,11,3,-2,null,1], sum = 8

          10
         /  \
        5   -3
       / \    \
      3   2   11
     / \   \
    3  -2   1

返回 3。和等于 8 的路径有:

    1.  5 -> 3
    2.  5 -> 2 -> 1
    3.  -3 -> 11

```java
public int pathSum(TreeNode root, int sum) {
    if (root == null) {
        return 0;
    }
    return robot(root, sum) + pathSum(root.left, sum) + pathSum(root.right, sum);
}

private int robot(TreeNode root, int sum) {
    if (root == null) {
        return 0;
    }
    int ans = 0;
    sum -= root.val;

    if (sum == 0) {
        ans++;
    }

    ans += robot(root.left, sum);
    ans += robot(root.right, sum);

    return ans;
}
```

## 二叉树中的最大路径和

124. 二叉树中的最大路径和

给定一个**非空**二叉树，返回其最大路径和。

本题中，路径被定义为一条从树中任意节点出发，达到任意节点的序列。该路径至少包含一个节点，且不一定经过根节点。

示例 1:

    输入: [1,2,3]

           1
          / \
         2   3

    输出: 6

示例 2:

    输入: [-10,9,20,null,null,15,7]

       -10
       / \
      9  20
        /  \
       15   7

    输出: 42

```java
public int maxPathSum(TreeNode root) {
    int[] ans = new int[] { Integer.MIN_VALUE };
    robot(root, ans);
    return ans[0];
}

private int robot(TreeNode root, int[] ans) {
    if (root == null) {
        return 0;
    }
    int left = robot(root.left, ans);
    int right = robot(root.right, ans);

    int res = root.val;
    if (Math.max(left, right) > 0) {
        res += Math.max(left, right);
    }

    int gain = Math.max(Math.max(left, right), left + right);

    ans[0] = Math.max(ans[0], root.val);
    ans[0] = Math.max(ans[0], root.val + gain);
    return res;
}
```

## 求根到叶子节点数字之和

129. 求根到叶子节点数字之和

给定一个二叉树，它的每个结点都存放一个 0-9 的数字，每条从根到叶子节点的路径都代表一个数字。

例如，从根到叶子节点路径 1->2->3 代表数字 123。

计算从根到叶子节点生成的所有数字之和。

说明: 叶子节点是指没有子节点的节点。

示例 1:

    输入: [1,2,3]
        1
       / \
      2   3
    输出: 25
    解释:
    从根到叶子节点路径 1->2 代表数字 12.
    从根到叶子节点路径 1->3 代表数字 13.
    因此，数字总和 = 12 + 13 = 25.

示例 2:

    输入: [4,9,0,5,1]
        4
       / \
      9   0
     / \
    5   1
    输出: 1026
    解释:
    从根到叶子节点路径 4->9->5 代表数字 495.
    从根到叶子节点路径 4->9->1 代表数字 491.
    从根到叶子节点路径 4->0 代表数字 40.
    因此，数字总和 = 495 + 491 + 40 = 1026.
    
```java
public int sumNumbers(TreeNode root) {
    return robot(root, 0);
}

private int robot(TreeNode root, int p) {
    if (root == null) {
        return 0;
    }

    p = p * 10 + root.val;

    if (root.left == null && root.right == null) {
        return p;
    }

    return robot(root.left, p) + robot(root.right, p);
}
```

# 序列化二叉树、构造二叉树

## 从前序与中序遍历序列构造二叉树

105. 从前序与中序遍历序列构造二叉树

根据一棵树的前序遍历与中序遍历构造二叉树。

注意:
你可以假设树中没有重复的元素。

例如，给出

    前序遍历 preorder = [3,9,20,15,7]
    中序遍历 inorder = [9,3,15,20,7]

返回如下的二叉树：

        3
       / \
      9  20
        /  \
       15   7

```java
public TreeNode buildTree(int[] pre, int[] in) {
    return robot(pre, in, 0, 0, in.length - 1);
}

private TreeNode robot(int[] pre, int[] in, int preStart, int inStart, int inEnd) {
    if (preStart >= pre.length || inStart > inEnd) {
        return null;
    }
    // 找到pos
    TreeNode root = new TreeNode(pre[preStart]);
    int index = 0;
    for (int i = inStart; i <= inEnd; i++) {
        if (in[i] == root.val) {
            index = i;
            break;
        }
    }
    root.left = robot(pre, in, preStart + 1, inStart, index - 1);
    root.right = robot(pre, in, preStart + 1 + index - inStart, index + 1, inEnd);
    return root;
}
```

## 从中序与后序遍历序列构造二叉树

106. 从中序与后序遍历序列构造二叉树

根据一棵树的中序遍历与后序遍历构造二叉树。

注意:
你可以假设树中没有重复的元素。

例如，给出

    中序遍历 inorder = [9,3,15,20,7]
    后序遍历 postorder = [9,15,7,20,3]

返回如下的二叉树：

        3
       / \
      9  20
        /  \
       15   7

```java
public TreeNode buildTree(int[] in, int[] post) {
    return robot(in, post, 0, in.length - 1, 0, post.length - 1);
}

private TreeNode robot(int[] in, int[] post, int inStart, int inEnd, int postStart,
        int postEnd) {
    if (postStart > postEnd) {
        return null;
    }
    TreeNode root = new TreeNode(post[postEnd]);
    int pos = 0;
    // 找到pos
    for (int i = inStart; i <= inEnd; i++) {
        if (in[i] == root.val) {
            pos = i;
            break;
        }
    }
    root.left = robot(in, post, inStart, pos - 1, postStart, postStart + pos - inStart - 1);
    root.right = robot(in, post, pos + 1, inEnd, postEnd + pos - inEnd, postEnd - 1);
    return root;
}
```

## 先序遍历构造二叉树

1008. 先序遍历构造二叉树

返回与给定先序遍历 preorder 相匹配的二叉搜索树（binary search tree）的根结点。

(回想一下，二叉搜索树是二叉树的一种，其每个节点都满足以下规则，对于 node.left 的任何后代，值总 < node.val，而 node.right 的任何后代，值总 > node.val。此外，先序遍历首先显示节点的值，然后遍历 node.left，接着遍历 node.right。）

 

示例：

    输入：[8,5,1,7,10,12]
    输出：[8,5,10,1,7,null,12]

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-10-09-150510.jpg)@w=400

提示：

- 1 <= preorder.length <= 100
- 先序 preorder 中的值是不同的。

```java
int index = 0;

public TreeNode bstFromPreorder(int[] preorder) {
    return robot(preorder, Integer.MIN_VALUE, Integer.MAX_VALUE);
}

private TreeNode robot(int[] preorder, int min, int max) {
    if (index == preorder.length) {
        return null;
    }

    int val = preorder[index];
    if (val < min || val > max) {
        return null;
    }
    index++;
    TreeNode root = new TreeNode(val);
    root.left = robot(preorder, min, val);
    root.right = robot(preorder, val, max);
    return root;
}
```

## 序列化和反序列化二叉搜索树

449. 序列化和反序列化二叉搜索树

序列化是将数据结构或对象转换为一系列位的过程，以便它可以存储在文件或内存缓冲区中，或通过网络连接链路传输，以便稍后在同一个或另一个计算机环境中重建。

设计一个算法来序列化和反序列化**二叉搜索树**。 对序列化/反序列化算法的工作方式没有限制。 您只需确保二叉搜索树可以序列化为字符串，并且可以将该字符串反序列化为最初的二叉搜索树。

**编码的字符串应尽可能紧凑**。

**注意**：不要使用类成员/全局/静态变量来存储状态。 你的序列化和反序列化算法应该是无状态的。

```java
public class Codec {

    // Encodes a tree to a single string.
    // BST 的前序遍历
    public String serialize(TreeNode root) {
        if (root == null) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        robot(root, sb);
        return sb.substring(0, sb.length() - 1);
    }

    private void robot(TreeNode root, StringBuilder sb) {
        if (root == null) {
            return;
        }
        sb.append(root.val).append(",");
        robot(root.left, sb);
        robot(root.right, sb);
    }

    // Decodes your encoded data to tree.
    public TreeNode deserialize(String data) {
        if (data == null || Objects.equals(data, "")) {
            return null;
        }
        String[] pre = data.split(",");
        return build(pre, 0, pre.length - 1);
    }

    private TreeNode build(String[] pre, int start, int end) {
        if (start > end) {
            return null;
        }
        TreeNode root = new TreeNode(Integer.valueOf(pre[start]));

        // 找到对应的 index
        int index = end + 1;
        for (int i = start + 1; i <= end; i++) {
            if (Integer.valueOf(pre[i]) > root.val) {
                index = i;
                break;
            }
        }

        root.left = build(pre, start + 1, index - 1);
        root.right = build(pre, index, end);
        return root;
    }

}
// Your Codec object will be instantiated and called as such:
// Codec codec = new Codec();
// codec.deserialize(codec.serialize(root));
```

## 二叉树的序列化与反序列化

297. 二叉树的序列化与反序列化

序列化是将一个数据结构或者对象转换为连续的比特位的操作，进而可以将转换后的数据存储在一个文件或者内存中，同时也可以通过网络传输到另一个计算机环境，采取相反方式重构得到原数据。

请设计一个算法来实现二叉树的序列化与反序列化。这里不限定你的序列 / 反序列化算法执行逻辑，你只需要保证一个二叉树可以被序列化为一个字符串并且将这个字符串反序列化为原始的树结构。

示例: 

    你可以将以下二叉树：

        1
       / \
      2   3
         / \
        4   5

    序列化为 "[1,2,3,null,null,4,5]"

提示: 这与 LeetCode 目前使用的方式一致，详情请参阅 LeetCode 序列化二叉树的格式。你并非必须采取这种方式，你也可以采用其他的方法解决这个问题。

说明: 不要使用类的成员 / 全局 / 静态变量来存储状态，你的序列化和反序列化算法应该是无状态的。

```java
public String serialize(TreeNode root) {

    if (root == null) {
        return "";
    }

    StringBuilder sb = new StringBuilder();

    Deque<TreeNode> deque = new LinkedList<>();
    deque.add(root);

    while (!deque.isEmpty()) {
        TreeNode p = deque.pop();

        if (p == null) {
            sb.append(",#");
        } else {
            sb.append(",").append(p.val);
            deque.add(p.left);
            deque.add(p.right);
        }
    }

    return sb.toString().substring(1);
}

public TreeNode deserialize(String data) {

    if (data == null || Objects.equals(data, "")) {
        return null;
    }

    String[] s = data.split(",");

    TreeNode[] root = new TreeNode[s.length];

    for (int i = 0; i < root.length; i++) {
        if (!Objects.equals(s[i], "#")) {
            root[i] = new TreeNode(Integer.valueOf(s[i]));
        }
    }

    int parent = 0;

    for (int i = 0; parent * 2 + 2 < s.length; i++) {
        if (root[i] != null) {
            root[i].left = root[parent * 2 + 1];
            root[i].right = root[parent * 2 + 2];
            parent++;
        }
    }

    return root[0];
}
```

