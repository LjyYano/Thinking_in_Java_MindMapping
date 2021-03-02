
- [题目描述](#题目描述)
- [解题思路](#解题思路)
- [代码](#代码)
- [复杂度分析](#复杂度分析)
- [GitHub LeetCode 项目](#github-leetcode-项目)

# 题目描述

[题目链接](https://leetcode-cn.com/problems/insert-delete-getrandom-o1-duplicates-allowed/)

设计一个支持在平均 时间复杂度 O(1) 下， 执行以下操作的数据结构。

注意：允许出现重复元素。

insert(val)：向集合中插入元素 val。
remove(val)：当 val 存在时，从集合中移除一个 val。
getRandom：从现有集合中随机获取一个元素。每个元素被返回的概率应该与其在集合中的数量呈线性相关。
示例：

    // 初始化一个空的集合。
    RandomizedCollection collection = new RandomizedCollection();

    // 向集合中插入 1 。返回 true 表示集合不包含 1 。
    collection.insert(1);

    // 向集合中插入另一个 1 。返回 false 表示集合包含 1 。集合现在包含 [1,1] 。
    collection.insert(1);

    // 向集合中插入 2 ，返回 true 。集合现在包含 [1,1,2] 。
    collection.insert(2);

    // getRandom 应当有 2/3 的概率返回 1 ，1/3 的概率返回 2 。
    collection.getRandom();

    // 从集合中删除 1 ，返回 true 。集合现在包含 [1,2] 。
    collection.remove(1);

    // getRandom 应有相同概率返回 1 和 2 。
    collection.getRandom();

# 解题思路

RandomizedCollection 类里维护 2 个数据结构：
- countMap，其中 key 为插入的数值 val，value 是对应数值出现的次数
- list，存入的每个元素

insert、remove 只要维护 countMap 和 list 即可。

# 代码

```java
class RandomizedCollection {

    Map<Integer, Integer> countMap;
    List<Integer> list;

    /**
        * Initialize your data structure here.
        */
    public RandomizedCollection() {
        list = new ArrayList<>();
        countMap = new HashMap<>();
    }

    /**
        * Inserts a value to the collection. Returns true if the collection did not already contain the specified element.
        */
    public boolean insert(int val) {
        int before = countMap.getOrDefault(val, 0);
        countMap.put(val, before + 1);
        list.add(val);
        return before == 0;
    }

    /**
        * Removes a value from the collection. Returns true if the collection contained the specified element.
        */
    public boolean remove(int val) {
        int before = countMap.getOrDefault(val, 0);
        if (before == 0) {
            return false;
        }
        countMap.put(val, before - 1);
        list.remove((Integer) val);
        return before > 0;
    }

    /**
        * Get a random element from the collection.
        */
    public int getRandom() {
        if (list.size() == 0) {
            return -1;
        }
        int index = ThreadLocalRandom.current().nextInt(0, list.size());
        return list.get(index);
    }
}
```

# 复杂度分析

时间复杂度：insert 仅需把元素加到 list 的末尾，所以复杂度是 $O(1)$，remove 需要遍历 list，所以复杂度是 $O(n)$

空间复杂度：$O(n)$

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！