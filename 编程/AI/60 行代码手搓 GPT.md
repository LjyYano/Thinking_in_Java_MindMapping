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
fuzzytm>=0.4.0
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

```Python
# 在 Notebook 中执行查看当前内核
import sys
print(sys.executable)  # 应显示 conda 环境路径
```

</details>

项目介绍，一共有 3 个文件：
1. encoder.py：包含了 OpenAI 的 BPE 分词器的代码，这是直接从 gpt-2 仓库拿过来的
2. utils.py：包含下载并加载 GPT-2 模型的权重，分词器和超参数
3. gpt2.py：包含了实际 GPT 模型以及生成的代码，这个代码可以作为 python 脚本直接运行

下载必要的模型和分词器文件到 models/124M，并且加载 encoder, hparams, params。
```Python
from utils import load_encoder_hparams_and_params
encoder, hparams, params = load_encoder_hparams_and_params("124M", "models")
```
## 编码器
```Python
from encoder import get_encoder

# 设置模型目录
models_dir = "models"  # 你的模型目录路径
model_name = "124M"    # 模型名称，比如 "124M"

# 获取编码器实例
encoder = get_encoder(model_name, models_dir)
```

使用的是 GPT-2 的 BPE 分词器：

```Python
# 编码文本
ids = encoder.encode("Not all heroes wear capes.")
print(ids)
```

输出：
```
[3673, 477, 10281, 5806, 1451, 274, 13]
```

运行：
```Python
# 解码回文本
text = encoder.decode(ids)
print(text)
```

输出：
```
Not all heroes wear capes.
```

分词器的词汇表(存储于encoder.decoder)，我们可以看看实际的token到底长啥样：

```Python
[encoder.decoder[i] for i in ids]
```

输出：
```
['Not', 'Ġall', 'Ġheroes', 'Ġwear', 'Ġcap', 'es', '.']
```

有的时候我们的token是单词（比如：Not），有的时候虽然也是单词，但是可能会有一个空格在它前面（比如Ġall, Ġ代表一个空格），有时候是一个单词的一部分（比如：capes被分隔为Ġcap和es），还有可能它就是标点符号（比如：.）。

词汇表：models/124M/encoder.json
字节对组合：models/124M/vocab.bpe

## 超参数

```Python
hparams = {
    "n_vocab": 50257,
    "n_ctx": 1024,
    "n_embd": 768,
    "n_head": 12,
    "n_layer": 12,
}
```
以下是 GPT-2 模型核心超参数的详细解释：
1. **n_vocab**（50257）：词汇表大小，表示模型可以识别的唯一 token 数量（包含 50257 个 BPE 分词单元和特殊控制字符）
2. **n_ctx**（1024）：上下文窗口长度，决定模型单次能处理的最大 token 序列长度（相当于约 700 个英文单词的文本容量）
3. **n_embd**（768）：嵌入维度，每个 token 被转换为 768 维的稠密向量表示（向量空间中的语义编码）
4. **n_head**（12）：多头注意力机制中的并行头数量，12 个头可并行捕捉不同维度的语义关联（768/12=64 每个头处理 64 维特征）
5. **n_layer**（12）：Transformer 解码器层数，12 层堆叠结构实现深层特征提取（每层包含自注意力 + 前馈神经网络）

这些参数共同构成 GPT-2 的基础架构：

12层 x (12头注意力 + 768维FFN) @ 1024上下文窗口，模型总参数量为 124M（1.24 亿）。参数间的比例关系（如 n_embd/n_head=64）是经过大量实验验证的优化配置。

## 参数

params是一个嵌套的json字典，该字典具有模型训练好的权重。

```Python
import numpy as np
def shape_tree(d):
    if isinstance(d, np.ndarray):
        return list(d.shape)
    elif isinstance(d, list):
        return [shape_tree(v) for v in d]
    elif isinstance(d, dict):
        return {k: shape_tree(v) for k, v in d.items()}
    else:
        ValueError("uh oh")

print(shape_tree(params))
```

<details>
<summary>输出结果</summary>

```json
{
  "blocks":[
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    },
    {
      "attn":{
        "c_attn":{
          "b":[
            2304
          ],
          "w":[
            768,
            2304
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            768,
            768
          ]
        }
      },
      "ln_1":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "ln_2":{
        "b":[
          768
        ],
        "g":[
          768
        ]
      },
      "mlp":{
        "c_fc":{
          "b":[
            3072
          ],
          "w":[
            768,
            3072
          ]
        },
        "c_proj":{
          "b":[
            768
          ],
          "w":[
            3072,
            768
          ]
        }
      }
    }
  ],
  "ln_f":{
    "b":[
      768
    ],
    "g":[
      768
    ]
  },
  "wpe":[
    1024,
    768
  ],
  "wte":[
    50257,
    768
  ]
}
```
</details>

# GPT 架构

GPT 的架构是基于 [transformer](https://arxiv.org/pdf/1706.03762) 的：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-01-27-10-31-36.png)

但它仅仅使用了解码器层（图中的右边部分）：

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-01-27-10-32-00.png)

注意，因为我们已经搞定了编码器，所以中间的 **cross-attention** 层也被移除了。

从宏观的角度来看，GPT 架构有三个部分组成：

- 文本 + 位置**嵌入**(positional **embeddings**)
- 基于transformer的**解码器层**(**decoder stack**)
- **投影为词汇表**(**projection to vocab**)的步骤