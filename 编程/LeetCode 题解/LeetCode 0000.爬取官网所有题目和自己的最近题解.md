# 公众号

coding 笔记、点滴记录，以后的文章也会同步到公众号（Coding Insight）中，大家关注^_^

我的博客地址：[博客主页](https://yano-nankai.notion.site/yano-nankai/Yano-Space-ff42bde7acd1467eb3ae63dc0d4a9f8c)。

![](http://yano.oss-cn-beijing.aliyuncs.com/2019-07-29-qrcode_for_gh_a26ce4572791_258.jpg)

# 前言

最近想将自己 LeetCode 账号的题目，按照题号顺序将题解整理到 GitHub 上，但是现在 LeetCode 有 1500 道题目（其实我也就做了400+），手动工作量太大，研究了一下午写了爬虫程序，结尾附源码。

# 目标

- 爬取所有算法的题目，按照{题号}-{题目名称}生成文件名
- 对于每道题目，获取最近一次提交的Java题解
- 如果题解中引入了 HashMap 等类，需要给出 import，即生成的Java文件能编译通过
- 在 Java 文件中，通过注释的方式，给出这道题的官网链接，方便刷题

# 获取题解目录

首先打开官网：https://leetcode-cn.com/problemset/algorithms/

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-130355.png)

打开控制台，细心能发现题解的链接：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-130615.png)

可以看到这个接口每道题目都有，不过是倒叙排列，题号最大的在最上面。这里比较重要的有下面几个参数：

- question_id：题号
- question__title：英文标题，空格分隔
- question__title_slug：slug 形式的标题（在获取自己提交的最近题解时会用到）

数据类定义如下：

```java
@Data
public class TitleVo {

    private String user_name;
    private String category_slug;
    private List<StatStatusPairsBean> stat_status_pairs;

    @Data
    public static class StatStatusPairsBean {

        private StatBean stat;
        private boolean paid_only;
        private boolean is_favor;
        private int frequency;
        private int progress;

        @Data
        public static class StatBean {

            private int question_id;
            private String question__title;
            private String question__title_slug;
            private boolean question__hide;
            private String frontend_question_id;
        }

    }
}
```

这个接口不需要登录态，仅一个 get 请求就能够获取所有题目。使用Java爬取代码如下：

```java
OkHttpClient client = new OkHttpClient();
Request request = new Request.Builder()
        .url("https://leetcode-cn.com/api/problems/algorithms/").method("GET", null)
        .build();
Response response = client.newCall(request).execute();
String body = response.body().string();
TitleVo titleVo = JSON.parseObject(body, TitleVo.class);
```

## 生成文件名称

为了以后方便查找和复习，希望将文件命名成 `L0010_Regular_Expression_Matching` 这样的格式，注意题目的 title 可能包含 `-`、空格、英文括号等，需要特殊处理，否则是不合法的 Java 文件名称（有几个类似于 「L1000056_拿硬币」 的竞赛题目，没有英文，暂不处理）。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-131136.png)

代码如下：

```java
// 1. 生成 title
String title = "L" + String.format("%04d", bean.getStat().getQuestion_id())
        + "_"
        + bean.getStat().getQuestion__title().replaceAll(" ", "_")
                .replaceAll("\\(", "").replaceAll("\\)", "")
                .replaceAll("-", "_").replaceAll(",", "");
```

# 填入「最近提交代码」

以第一题为例，点击代码编辑区域上访的 {}，获取最近一次提交的代码。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-131602.png)

在控制台能够看到 https://leetcode-cn.com/submissions/latest/?qid=1&lang=java 接口，即为自己提交的代码。

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-131725.png)

这个接口需要登录态，使用代码请求的时候需要带上 cookie，下面的代码 cookie 为空，在使用的时候需要填入自己的 cookie。注意有些题目爬取获取不到最近提交的代码，比如我在测试时前20题的第6题和第13题一直获取不到题解，或者400道之后的题目我都没有提交过题目，所以需要直接获取原题目代码。原题目代码的类是 `QuestionVo`，不详细叙述，直接贴代码。

```java
private String getRecentSubmitCode(int qid, String titleSlug) {
    OkHttpClient client = new OkHttpClient();
    Request request = new Request.Builder()
            .url(String.format("https://leetcode-cn.com/submissions/latest/?qid=%d&lang=java",
                    qid))
            .method("GET", null)
            .addHeader("Cookie", "")
            .build();
    try {
        Response response = client.newCall(request).execute();
        CodeVo codeVo = JSON.parseObject(response.body().string(), CodeVo.class);
        if (codeVo != null && StringUtils.isNotEmpty(codeVo.getCode())) {
            return codeVo.getCode();
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
    QuestionVo questionVo = getQuestionVo(titleSlug);
    if (questionVo != null) {
        QuestionVo.DataBean.QuestionBean.CodeSnippetsBean javaCode = questionVo.getData()
                .getQuestion().getCodeSnippets().stream()
                .filter(q -> Objects.equals(q.getLang(), "Java")).findFirst().orElse(null);
        return javaCode.getCode();
    }
    return "";
}
```

CodeVo 类：

```java
@Data
public class CodeVo {

    private String code;
}
```

QuestionVo 类（在 CodeVo 为空时使用）：

```java
@Data
public class QuestionVo {

    @SerializedName("data")
    private DataBean data;

    public static class DataBean {

        @SerializedName("question")
        private QuestionBean question;

        public QuestionBean getQuestion() {
            return question;
        }

        public void setQuestion(QuestionBean question) {
            this.question = question;
        }

        @Data
        public static class QuestionBean {

            @SerializedName("questionId")
            private String questionId;
            private String questionFrontendId;
            private int boundTopicId;
            private String title;
            private String titleSlug;
            private String content;
            private String translatedTitle;
            private String translatedContent;
            private Object isLiked;
            private String stats;
            private SolutionBean solution;
            private String status;
            private String metaData;
            private boolean judgerAvailable;
            private String judgeType;
            private boolean enableRunCode;
            private String envInfo;
            private String dailyRecordStatus;
            private String style;
            private String __typename;
            private List<TopicTagsBean> topicTags;
            private List<CodeSnippetsBean> codeSnippets;

            @Data
            public static class SolutionBean {

                private String id;
                private boolean canSeeDetail;
                private String __typename;

            }

            @Data
            public static class TopicTagsBean {

                private String name;
                private String slug;
                private String translatedName;
                private String __typename;

            }

            @Data
            public static class CodeSnippetsBean {

                private String lang;
                private String langSlug;
                private String code;
                private String __typename;

            }
        }
    }
}
```

# 处理 import

总结了下基本就是 HashMap、Arrays 之类的 JDK 基础类，在上面获取到的题解代码中如果存在某些关键字，就直接在题解代码最上面加入对应的 import。代码如下：

```java
private StringBuilder getImports(TitleVo.StatStatusPairsBean bean, String recentSubmitCode) {
    StringBuilder importSb = new StringBuilder();
    if (recentSubmitCode.contains("HashMap")) {
        importSb.append("import java.util.HashMap;\n");
    }
    if (recentSubmitCode.contains("Map<")) {
        importSb.append("import java.util.Map;\n");
    }
    if (recentSubmitCode.contains("ListNode")) {
        importSb.append("import common.ListNode;\n");
    }
    if (recentSubmitCode.contains("Node")) {
        importSb.append("import common.Node;\n");
    }
    if (recentSubmitCode.contains("Arrays")) {
        importSb.append("import java.util.Arrays;\n");
    }
    if (recentSubmitCode.contains("List<")) {
        importSb.append("import java.util.List;\n");
    }
    if (recentSubmitCode.contains("ArrayList")) {
        importSb.append("import java.util.ArrayList;\n");
    }
    if (recentSubmitCode.contains("HashSet")) {
        importSb.append("import java.util.HashSet;\n");
    }
    if (recentSubmitCode.contains("Set<")) {
        importSb.append("import java.util.Set;\n");
    }
    if (recentSubmitCode.contains("Stack<")) {
        importSb.append("import java.util.Stack;\n");
    }
    if (recentSubmitCode.contains("TreeNode")) {
        importSb.append("import common.TreeNode;\n");
    }

    importSb.append(String.format("\n// https://leetcode-cn.com/problems/%s/\n",
            bean.getStat().getQuestion__title_slug()));

    return importSb;
}
```

# 生成 Java 文件

使用的是 `org.apache.commons.io.FileUtils`，将上述代码转换并写入文件即可。

```java
FileUtils.writeByteArrayToFile(new File("./" + title + ".java"),
        recentSubmitCode.getBytes());
```

# 整体代码

```java
@Test
public void test() throws IOException {
    OkHttpClient client = new OkHttpClient();
    Request request = new Request.Builder()
            .url("https://leetcode-cn.com/api/problems/algorithms/").method("GET", null)
            .build();
    Response response = client.newCall(request).execute();
    String body = response.body().string();
    TitleVo titleVo = JSON.parseObject(body, TitleVo.class);

    titleVo.getStat_status_pairs().stream()
            .filter(bean -> bean.getStat().getQuestion_id() < 1500)
            .forEach(bean -> {
                try {
                    // 1. 生成 title
                    String title = "L" + String.format("%04d", bean.getStat().getQuestion_id())
                            + "_"
                            + bean.getStat().getQuestion__title().replaceAll(" ", "_")
                                    .replaceAll("\\(", "").replaceAll("\\)", "")
                                    .replaceAll("-", "_").replaceAll(",", "");
                    System.out.println(title);

                    // 2. 填入代码
                    String recentSubmitCode = getRecentSubmitCode(
                            bean.getStat().getQuestion_id(),
                            bean.getStat().getQuestion__title_slug());
                    if (StringUtils.isNotEmpty(recentSubmitCode)) {
                        recentSubmitCode = recentSubmitCode.replaceFirst("class Solution",
                                "class " + title);
                        // System.out.println(recentSubmitCode);
                    }

                    // 3. 若存在 Arrays、TreeNode 等类，增加 import
                    recentSubmitCode = getImports(bean, recentSubmitCode) + recentSubmitCode;

                    // 4. 生成 java 文件
                    FileUtils.writeByteArrayToFile(new File("./" + title + ".java"),
                            recentSubmitCode.getBytes());

                    TimeUnit.MILLISECONDS.sleep(100);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });

}
```

最终生成的文件如下，同时增加了题目的中文官网链接，方便刷题、测试：

![](http://yano.oss-cn-beijing.aliyuncs.com/2020-08-19-132656.png)

# 说明

- 试了几次，1500道题目每题间隔 100 ms爬取并无异常，看来LeetCode 中国官网还没有封禁策略
- 特意花了60多块钱开了会员，但是通过分析来看，会员题目也是可以看到的（逃）
- 代码最终上传在了：https://github.com/LjyYano/LeetCode/tree/master/leetcode/src/main/java
- 时间仓促，爬虫代码写得不规范，但是达到目的了~