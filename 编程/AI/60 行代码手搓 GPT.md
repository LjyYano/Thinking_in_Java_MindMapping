# 准备工作

首先将项目克隆到本地：

```SHELL
git clone https://github.com/jaymody/picoGPT
cd picoGPT
```

安装依赖：

```SHELL
pip install -r requirements.txt
```

我使用的是 Apple Silicon 芯片（M1/M2）的 macOS 系统，需要更改 requirements.txt 文件。

<details>
<summary><h4 style="display: inline-block; margin: 0;">在 M1/M2 Mac 上安装 TensorFlow 的常见问题及解决方案</h4></summary>

### 问题背景
在 Apple Silicon 芯片（M1/M2）的 macOS 系统上安装 TensorFlow 时，常遇到以下问题：

```bash
ERROR: Could not find a version that satisfies the requirement tensorflow-macos==2.11.0
ERROR: No matching distribution found for tensorflow-macos==2.11.0
```

### 问题分析

#### 1. TensorFlow 版本兼容性问题
- **原因**：TensorFlow 2.11 及更早版本不支持 Python 3.11+
- **表现**：`ERROR: No matching distribution found`
- **解决方案**：升级到支持 Apple Silicon 的版本

#### 2. numpy 版本冲突
- **原因**：旧版 numpy 与 Python 3.11+ 不兼容
- **表现**：`Ignored versions that require a different python version`
- **解决方案**：使用兼容版本 `numpy==1.26.0`

#### 3. 依赖包名称错误
- **原因**：`FuzzyTM` 的正确 PyPI 包名是 `fuzzytm`
- **表现**：`ERROR: No matching distribution found for fuzzy-tm`
- **解决方案**：修正包名拼写

#### 4. Keras 版本冲突
- **原因**：TensorFlow 2.x 自带 Keras 2.x，与独立安装的 Keras 3.x 冲突
- **表现**：`gensim 4.3.0 requires FuzzyTM>=0.4.0`
- **解决方案**：移除显式的 Keras 安装

### 最终解决方案

#### requirements.txt 配置
```python
numpy==1.26.0
regex==2023.10.3
requests==2.31.0
tqdm==4.66.1
fire==0.5.0
tensorflow-macos==2.16.1  # 支持 Apple Silicon 的最新稳定版
tensorflow-metal==1.1.0   # GPU 加速插件
fuzzytm>=0.4.0            # 注意正确包名（全小写）
```

#### 安装步骤
```bash
# 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate

# 升级 pip 并安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```
</details>

<details>
<summary><h4 style="display: inline-block; margin: 0;">PyCharm 配置</h4></summary>

<div align="center">
    <img src="http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-01-27-08-55-39.png?x-oss-process=image/resize,w_800" alt="PyCharm 配置">
    <p>项目设置 Python 解释器</p>
</div>

<div align="center" >
    <img src="http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-01-27-09-00-48.png?x-oss-process=image/resize,w_800" alt="PyCharm 配置">
    <p>Jupyter Notebook 设置 Python 解释器</p>
</div>

</details>