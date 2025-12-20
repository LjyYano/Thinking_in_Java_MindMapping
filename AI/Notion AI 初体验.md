---
date: 2025-12-20
---

# Notion AI 初体验

## 前言

作为一个 Notion 的重度用户，一直心痒痒想体验一下 Notion AI。虽然它不像 ChatGPT 或 Claude 那样可以让你自由切换各种最新模型，但它最大的杀手锏在于：**它就在你的笔记里，而且能读懂你的笔记、操作你的笔记**。

最近试着用它来整理我的「书影清单」数据库，体验确实有点“回不去了”。不用在浏览器和 Notion 之间切来切去，这种沉浸式的自动化体验真的很爽。

## 我的书影清单

我一直在用 Notion 记录我的「书影清单」，包括阅读、观影、游戏等，目前已经积累了 294 条记录。入口在这里：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-27-05.png" /></div>

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-29-20.png" /></div>

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-28-57.png" /></div>

## Notion AI 的杀手锏

以前用外部 AI 工具时，最大的痛点就是上下文割裂：
- 我得先把页面内容复制出来
- 发给 AI，还要解释半天我的字段定义（什么是“状态”，评分是 10 分制还是 5 分制...）
- 拿到结果后再复制回 Notion

而 Notion AI 就像是一个**住在工作区里的助理**。它天生就知道你这个数据库里有哪些字段，也知道你过往的记录习惯。

### 实战一：一键统计与复盘

在 Notion AI 里，你可以直接选中一个数据库，让它帮你做分析。我试着让它对我的书影清单做个统计：

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-37-34.png" width="60%" /></div>

这种“统计 + 归纳”的场景非常适合懒人：
- **快速复盘**：今年看了多少电影？最常看什么类型？
- **个性化推荐**：从未完成清单里挑 5 个评分高的，按“轻松程度”排序。
- **内容输出**：把一年的观影记录直接生成一篇 Markdown 格式的年终总结（连草稿都不用自己打）。


    > PS：我确实每年都要写观影总结，之前每次的年度观影总结基本要写 6h 以上，这次使用 Notion AI 看看能多长时间 0_o
    > - [Yano 的 2019 观影总结](../观影/Yano%20的%202019%20观影总结.md)
    > - [Yano 的 2020 观影总结](../观影/Yano%20的%202020%20观影总结.md)
    > - [Yano 的 2021 观影总结](../观影/Yano%20的%202021%20观影总结.md)
    > - [Yano 的 2022 观影总结](../观影/Yano%20的%202022%20观影总结.md)
    > - [Yano 的 2023 观影总结](../观影/Yano%20的%202023%20观影总结.md)
    > - [Yano 的 2024 观影总结](../观影/Yano%20的%202024%20观影总结.md)

### 实战二：懒人福音，自动补全字段

最近打算看《利刃出鞘 3》，我只在数据库里建了个标题，其他啥都没填。然后直接召唤 AI，让它帮我完善信息。

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-39-35.png" width="60%" /></div>

因为它知道我还没开始看，所以评分、阅读时间这些字段它会留空；而导演、主演、海报、豆瓣链接这些公开信息，它会自动联网搜索并补齐。

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-40-45.png" width="50%" /></div>

**以前需要手动去豆瓣搜、复制、粘贴的步骤，现在一句话就搞定了。**

## 进阶玩法：给 AI 写“员工手册” 

Notion AI 的设置里有个 **Instructions** 功能，我觉得这才是长期使用的精髓。你可以把它理解为给 AI 写的“员工手册”。

比如可以专门建一个页面叫「书影清单录入规范」，写清楚：
- 评分标准是 1-10 分
- 没看过的电影评分留空
- 链接优先用豆瓣

然后把这个页面加到 Instructions 里。以后每次让 AI 干活，它都会先看一眼这个手册，输出的结果就非常稳定了。

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-43-22.png" width="60%" /></div>

顺便还能设置一下 AI 的语气和形象，挺好玩的。

<div style="margin: 30px 0;"><img src="https://yano.oss-cn-beijing.aliyuncs.com/blog/2025-12-20-15-45-24.png" width="80%" /></div>


## 碎碎念：关于限制和注意事项

**Notion AI 的本质是什么？**

> 是「嵌入在 Notion 里的通用文本 AI 助手」，并不是一个无限制的 ChatGPT。

简单说，它不是一个无限制陪聊的 ChatGPT，而是**专门帮你打理 Notion 笔记的私人秘书**。它能直接读懂你当前页面、甚至整个数据库的内容，帮你总结、润色、改写。这就比那些需要把内容“复制出去再粘贴回来”的外部 AI 强太多了。

**关于次数限制**：官方其实没给具体的数字，只说是个「合理使用机制」（Fair Use）。

## 总结

如果你也是 Notion 的重度用户，强烈建议试一下。

- **把死数据变活**：不用导出 Excel 也能做各种花式统计。
- **极致的懒人体验**：新增记录 + 补全字段 + 生成摘要，一气呵成。

即使是试用版，跑一遍自己的数据库、知识库笔记也能发现很多惊喜。安利！

# 我的公众号

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

coding 笔记、读书笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注 `^_^`

<div style="margin: 30px 0;"><img src="http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg"/></div>