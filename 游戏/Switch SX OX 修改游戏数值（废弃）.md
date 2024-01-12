---
date: 2021-08-09
---

- [前言](#前言)
- [确定要修改的游戏数值](#确定要修改的游戏数值)
- [作弊器初步搜索 Switch 内存值](#作弊器初步搜索-switch-内存值)
- [作弊器精确定位 Switch 内存值](#作弊器精确定位-switch-内存值)
- [修改数值](#修改数值)
- [大胆一点，多加一些](#大胆一点多加一些)
- [保存游戏进度](#保存游戏进度)
- [写在最后…… 什么时候应该使用作弊器？](#写在最后-什么时候应该使用作弊器)
- [GitHub LeetCode 项目](#github-leetcode-项目)


>大气层系统修改数值非常方便，完全不需要下面的方法了。本文就不删除，作为纪念吧~

# 前言

有些游戏是在是太肝了，适当修改经验 / 金钱，能够在游戏性和时间之间取得 ` 完美的平衡 ` o_0

经过摸索，找打了一个适用的修改游戏数值的方法，亲测有效。

# 确定要修改的游戏数值

以 ` 异度之刃 2` 为例，首先确定修改莱克斯的所持技能点数，当前是 3012（在下面图片的右下角），换算成十六进制是 BC4。

![](https://i.loli.net/2021/08/09/E6MFg2YuXkoRJps.png?x-oss-process=style/yano)

# 作弊器初步搜索 Switch 内存值

选择 ` 相册 - CHEAT - Cheat Searcher`，因为这个数值基本上不会超过 1w，就先选择 16 位无符号数。（事实证明，即使是 32 位的数值，我们也是可以按照 16 位搜索的，只是搜索出的候选集合会很多）

![](https://i.loli.net/2021/08/09/uF5YaML42np73VH.jpg?x-oss-process=style/yano)

![](https://i.loli.net/2021/08/09/hBXvgjpxHM1wCe3.jpg?x-oss-process=style/yano)

![](https://i.loli.net/2021/08/09/3zf17pCvGHiOMPK.jpg?x-oss-process=style/yano)

我们输入计算得来的十六进制数 BC4，注意如果位数不足，在前面补 0。

![](https://i.loli.net/2021/08/09/yngIKZJusq2EYeG.jpg?x-oss-process=style/yano)

点击确定，开始第一轮搜索，原理是把内存中所有是 BC4 的数值都列出来。

![](https://i.loli.net/2021/08/09/YCGW53cUinXs4Vo.jpg?x-oss-process=style/yano)

经过第 1 轮搜索后，发现有 4638 个符合条件的，太多了，系统都不想给列出来。

![](https://i.loli.net/2021/08/09/NvlsEejU2ZKOQSV.jpg?x-oss-process=style/yano)

# 作弊器精确定位 Switch 内存值

这个时候就需要第二步，我们在游戏内消耗或增加这个数值，比如我消耗了 1500 点，之后这个数值变成了 1512 了，换算成十六进制是 5E8。

![](https://i.loli.net/2021/08/09/igzryAPuOGanm8L.png?x-oss-process=style/yano)

之后我们再开启新一轮的搜索，在上次的候选集合中，选择「Exact Value」，进行精确搜索。

![](https://i.loli.net/2021/08/09/afBQ6xMr793GA8X.jpg?x-oss-process=style/yano)

输入我们刚才获得的新的数值 5E8。

![](https://i.loli.net/2021/08/09/CuzArg2RkvtXaqM.jpg?x-oss-process=style/yano)

再次搜索之后，发现只有 2 个候选集合了。其实 3 个及以下的候选集合也就足够了，都改下试试。如果发现候选集合还是太多的话，再次返回游戏通过游戏机制改动下数值，之后再搜一次，一般反复搜索 3 次就足够了。

![](https://i.loli.net/2021/08/09/ArcBibG3poSz1Ym.jpg?x-oss-process=style/yano)

# 修改数值

我们小心谨慎地将 5E8 改成 5E9。（注意游戏内存是小端，高位在后，即 05E8 存储为 E8 05）

![](https://i.loli.net/2021/08/09/M2VykoUFqBdEu8x.jpg?x-oss-process=style/yano)

再回到游戏，发现原来的游戏数值 1512（05E8）变成修改之后的 1513（05E9）了！

![](https://i.loli.net/2021/08/09/xLzIjmMbnhwRqTc.jpg?x-oss-process=style/yano)

# 大胆一点，多加一些

我们改低位没有意思，直接改高位，多加一点，改成 0108E9。这个数应该不是 16 位，而是 32 位，因为 16 位最多表示到 65535，这个数值肯定会比这个大。

![](https://i.loli.net/2021/08/09/HrjiUtsQ8hBDTa7.png?x-oss-process=style/yano)

我们发现游戏内的数值变成 67817（十六进制 0108E9）了，可以尽情愉快地游戏了！

![](https://i.loli.net/2021/08/09/FTAgWIS3ZqnUz46.jpg?x-oss-process=style/yano)

# 保存游戏进度

嗯，我们验证下数值没问题，先保存一下游戏，这样就 “落袋为安” 了。否则在内存中的值，还没来得及保存就关机了，岂不是白忙活一场~

# 写在最后…… 什么时候应该使用作弊器？

异度之刃 2 虽好，但是如果为了刷钱就刷了 30h，确实也不太值得，都是枯燥无味的重复工作。

我们可以适当修改一下游戏数值，能够更好地体验游戏中的风景，体验游戏中的风土人情和剧情。（数值也不能改太过了，否则就没有游戏性可言了……）

# GitHub LeetCode 项目

项目 [GitHub LeetCode 全解](https://github.com/LjyYano/LeetCode)，欢迎大家 star、fork、merge，共同打造最全 LeetCode 题解！

[Java 编程思想 - 最全思维导图 - GitHub 下载链接](https://github.com/LjyYano/Thinking_in_Java_MindMapping)，需要的小伙伴可以自取~！！！

原创不易，希望大家转载时请先联系我，并标注原文链接。