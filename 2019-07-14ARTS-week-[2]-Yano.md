每周完成一个ARTS： 每周至少做一个 leetcode 的算法题、阅读并点评至少一篇英文技术文章、学习至少一个技术技巧、分享一篇有观点和思考的技术文章。（也就是 Algorithm、Review、Tip、Share 简称ARTS）

# Algorithm

https://leetcode.com/problems/relative-sort-array/

## 题目描述

1122. Relative Sort Array

Given two arrays arr1 and arr2, the elements of arr2 are distinct, and all elements in arr2 are also in arr1.

Sort the elements of arr1 such that the relative ordering of items in arr1 are the same as in arr2.  Elements that don't appear in arr2 should be placed at the end of arr1 in ascending order.

 

Example 1:

	Input: arr1 = [2,3,1,3,2,4,6,7,9,2,19], arr2 = [2,1,4,3,9,6]
	Output: [2,2,2,1,4,3,3,9,6,7,19]
 

Constraints:

	arr1.length, arr2.length <= 1000
	0 <= arr1[i], arr2[i] <= 1000
	Each arr2[i] is distinct.
	Each arr2[i] is in arr1.
	
## 题解

没有考虑时间、空间复杂度，仅仅是先将统计数组arr1中出现的arr2数字的次数，没有出现的……用list排序最终拼到最终结果中。

```
public int[] relativeSortArray(int[] arr1, int[] arr2) {
    Map<Integer, Integer> countMap = new HashMap<>();
    for (int i : arr2) {
        countMap.put(i, 0);
    }

    List<Integer> others = new ArrayList<>();
    for (int i : arr1) {
        if (countMap.containsKey(i)) {
            countMap.put(i, countMap.get(i) + 1);
        } else {
            others.add(i);
        }
    }

    int[] rt = new int[arr1.length];
    int j = 0;

    for (int i : arr2) {
        Integer count = countMap.get(i);
        for (int k = 0; k < count; k++) {
            rt[j++] = i;
        }
    }
    Collections.sort(others);
    for (int i = j; i < rt.length; i++) {
        rt[i] = others.get(i - j);
    }
    return rt;
}
```

# Review

本周忽略……

# Tip

## Alfred 的『Snippets』功能

Alfred 中的「Snippets」功能，图片、视频、文字，只要复制过的都能够保存下来，极大地提高了工作效率。界面如下：

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-14-124914.png)

Alfred 设置界面：

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-14-125319.png)

我的快捷键是：`option + command + c`

# Share

本周背诵了两篇宋词，分别为范仲淹的《渔家傲》和《苏幕遮（怀旧）》。

## 渔家傲

	塞下秋来风景异
	衡阳雁去无留意
	四面边声连角起
	千嶂里
	长烟落日孤城闭
	
	浊酒一杯家万里
	燕然未勒归无计
	羌管悠悠霜满地
	人不寐
	将军白发征夫泪

## 苏幕遮（怀旧）

	碧云天
	黄叶地
	秋风连波
	波上寒烟翠
	山映斜阳天接水
	芳草无情
	更在斜阳外
	
	黯乡魂
	追旅思
	夜夜除非
	好梦留人睡
	明月楼高休独倚
	酒入愁肠
	化作相思泪



