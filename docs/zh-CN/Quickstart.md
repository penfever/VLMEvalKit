# 快速开始

在运行评测脚本之前，你需要先**配置** VLMs，并正确设置模型路径。然后你可以使用脚本 `run.py` 进行多个VLMs和基准测试的推理和评估。

## 第0步 安装和设置必要的密钥

**安装**

```bash
git clone https://github.com/open-compass/VLMEvalKit.git
cd VLMEvalKit
pip install -e .
```

**设置密钥**

要使用 API 模型（如 GPT-4v, Gemini-Pro-V 等）进行推理，或使用 LLM API 作为**评判者或选择提取器**，你需要首先设置 API 密钥。如果你设置了密钥，VLMEvalKit 将使用一个评判 LLM 从输出中提取答案，否则它将使用**精确匹配模式**（在输出字符串中查找 "Yes", "No", "A", "B", "C"...）。**精确匹配模式只能应用于是或否任务和多项选择任务。**

- 你可以将所需的密钥放在 `$VLMEvalKit/.env` 中，或直接将它们设置为环境变量。如果你选择创建 `.env` 文件，其内容将如下所示：

  ```bash
  # .env 文件，将其放置在 $VLMEvalKit 下
  # 专有 VLMs 的 API 密钥
  # QwenVL APIs
  DASHSCOPE_API_KEY=
  # Gemini w. Google Cloud Backends
  GOOGLE_API_KEY=
  # OpenAI API
  OPENAI_API_KEY=
  OPENAI_API_BASE=
  # StepAI API
  STEPAI_API_KEY=
  # REKA API
  REKA_API_KEY=
  # GLMV API
  GLMV_API_KEY=
  # CongRong API
  CW_API_BASE=
  CW_API_KEY=
  # SenseNova API
  SENSENOVA_API_KEY=
  # Hunyuan-Vision API
  HUNYUAN_SECRET_KEY=
  HUNYUAN_SECRET_ID=
  # LMDeploy API
  LMDEPLOY_API_BASE=
  # 你可以设置一个评估时代理，评估阶段产生的 API 调用将通过这个代理进行
  EVAL_PROXY=
  ```

- 如果需要使用 API 在对应键值空白处填写上你的密钥。这些 API 密钥将在进行推理和评估时自动加载。
## 第1步 配置

**VLM 配置**：所有 VLMs 都在 `vlmeval/config.py` 中配置。对于某些 VLMs（如 MiniGPT-4、LLaVA-v1-7B），需要额外的配置（在配置文件中配置代码 / 模型权重根目录）。在评估时，你应该使用 `vlmeval/config.py` 中 `supported_VLM` 指定的模型名称来选择 VLM。确保在开始评估之前，你可以成功使用 VLM 进行推理，使用以下命令 `vlmutil check {MODEL_NAME}`。

## 第2步 评测

**新功能!!!** 我们集成了一个新的配置系统，以实现更灵活的评估设置。查看[文档](/docs/zh-CN/ConfigSystem.md)或运行`python run.py --help`了解更多详情 🔥🔥🔥

### 🔥 增强功能（DCVLR 版本）

#### 🤖 自定义模型支持

使用 `--pass-custom-model` 评估任何 HuggingFace 模型，无需手动配置：

```bash
# 评估自定义 Qwen2.5-VL 模型
python run.py --pass-custom-model Qwen/Qwen2.5-VL-7B-Instruct --data MMBench_DEV_EN

# 与现有模型结合使用
python run.py --model GPT4o --pass-custom-model microsoft/Phi-3-vision-128k-instruct --data MMBench_DEV_EN

# 多数据集自定义模型评估
python run.py --pass-custom-model liuhaotian/llava-v1.5-7b --data MMBench_DEV_EN MMMU_DEV_VAL
```

**支持的架构**：自动检测 25+ 种模型家族，包括 Qwen2-VL、Qwen2.5-VL、LLaVA、InternVL、MiniCPM、Phi、Molmo、Aria、Pixtral、SmolVLM、IDEFICS、CogVLM、DeepSeek、Llama-Vision、Gemma 等。

#### ⚡ VLLM 加速与批处理

启用高性能推理，可获得 2-4 倍加速：

```bash
# 启用 VLLM 批处理（自动检测兼容性）
python run.py --pass-custom-model Qwen/Qwen2.5-VL-7B-Instruct --data MMBench_DEV_EN --use-vllm --batch-size 4

# 与预配置模型一起使用
python run.py --model molmo-7B-D-0924 --data MMBench_DEV_EN --use-vllm --batch-size 8

# 内存受限环境
python run.py --model molmo-7B-D-0924 --data MMBench_DEV_EN --use-vllm --batch-size 2 --verbose
```

**VLLM 兼容模型**：Qwen2-VL 和 Qwen2.5-VL（所有变体）、Molmo（所有尺寸）、Llama-4、Gemma3，以及具有自动兼容性检测的自定义模型。

#### 🔧 令牌控制

全局控制所有模型的输出长度：

```bash
# 全局令牌覆盖（优先于所有模型/数据集默认值）
python run.py --model GPT4o --data MMBench_DEV_EN --max-output-tokens 2048

# 与自定义模型一起使用
python run.py --pass-custom-model Qwen/Qwen2.5-VL-7B-Instruct --data MMBench_DEV_EN --max-output-tokens 1024
```

#### 💾 高级响应保存

保存详细的评估数据用于分析：

```bash
# 保存原始模型响应（支持 Yale_physics、OlympiadBench、VMCBench_DEV）
python run.py --model GPT4o --data quantum_dataset --save-detailed-eval

# 保存 LLM 评判响应（支持 Yale_physics 数据集）
python run.py --model GPT4o --data mechanics_dataset --save-judge-responses

# 多种格式和选项
python run.py --model GPT4o --data atomic_dataset --save-detailed-eval --save-judge-responses --response-format xlsx
```

**支持的格式**：`json`（默认）、`csv`、`xlsx`

#### 📊 WandB 实验跟踪

使用 `scripts/wandb_logger.py` 进行全面的实验记录：

```bash
# 运行评估并记录到 WandB
python scripts/wandb_logger.py --run-and-log --model GPT4o --data MMBench_DEV_EN

# 自定义模型评估与 WandB
python scripts/wandb_logger.py --run-and-log --pass-custom-model Qwen/Qwen2.5-VL-7B-Instruct --data MMBench_DEV_EN

# 记录现有结果
python scripts/wandb_logger.py --log-all --work-dir ./outputs

# 包含所有功能的完整工作流程
python scripts/wandb_logger.py --run-and-log \
  --pass-custom-model oumi-ai/Molmo-7B-D-0924 \
  --data MMBench_DEV_EN MMMU_DEV_VAL \
  --use-vllm --batch-size 4 \
  --max-output-tokens 1024 \
  --save-detailed-eval \
  --project my-vlm-research
```

**WandB 功能**：自动指标提取、模型配置跟踪、性能监控、实验比较。

我们使用 `run.py` 进行评估。你可以使用 `$VLMEvalKit/run.py` 或创建脚本的软链接运行（以便在任何地方使用该脚本）：

**参数**

- `--data (list[str])`: 设置在 VLMEvalKit 中支持的数据集名称（可以在代码库首页的 README 中找到支持的数据集列表）
- `--model (list[str])`: 设置在 VLMEvalKit 中支持的 VLM 名称（在 `vlmeval/config.py` 中的 `supported_VLM` 中定义）
- `--mode (str, 默认值为 'all', 可选值为 ['all', 'infer'])`：当 mode 设置为 "all" 时，将执行推理和评估；当设置为 "infer" 时，只执行推理
- `--api-nproc (int, 默认值为 4)`: 调用 API 的线程数
- `--work-dir (str, default to '.')`: 存放测试结果的目录

**用于评测图像多模态评测集的命令**

你可以使用 `python` 或 `torchrun` 来运行脚本:

```bash
# 使用 `python` 运行时，只实例化一个 VLM，并且它可能使用多个 GPU。
# 这推荐用于评估参数量非常大的 VLMs（如 IDEFICS-80B-Instruct）。

# 在 MMBench_DEV_EN、MME 和 SEEDBench_IMG 上使用 IDEFICS-80B-Instruct 进行推理和评估
python run.py --data MMBench_DEV_EN MME SEEDBench_IMG --model idefics_80b_instruct --verbose
# 在 MMBench_DEV_EN、MME 和 SEEDBench_IMG 上使用 IDEFICS-80B-Instruct 仅进行推理
python run.py --data MMBench_DEV_EN MME SEEDBench_IMG --model idefics_80b_instruct --verbose --mode infer

# 使用 `torchrun` 运行时，每个 GPU 上实例化一个 VLM 实例。这可以加快推理速度。
# 但是，这仅适用于消耗少量 GPU 内存的 VLMs。

# 在 MMBench_DEV_EN、MME 和 SEEDBench_IMG 上使用 IDEFICS-9B-Instruct、Qwen-VL-Chat、mPLUG-Owl2。在具有 8 个 GPU 的节点上进行推理和评估。
torchrun --nproc-per-node=8 run.py --data MMBench_DEV_EN MME SEEDBench_IMG --model idefics_80b_instruct qwen_chat mPLUG-Owl2 --verbose
# 在 MME 上使用 Qwen-VL-Chat。在具有 2 个 GPU 的节点上进行推理和评估。
torchrun --nproc-per-node=2 run.py --data MME --model qwen_chat --verbose
```

**用于评测视频多模态评测集的命令**

```bash
# 使用 `python` 运行时，只实例化一个 VLM，并且它可能使用多个 GPU。
# 这推荐用于评估参数量非常大的 VLMs（如 IDEFICS-80B-Instruct）。

# 在 MMBench-Video 上评测 IDEFCIS2-8B, 视频采样 8 帧作为输入，不采用 pack 模式评测. MMBench_Video_8frame_nopack 是一个定义在 `vlmeval/dataset/video_dataset_config.py` 的数据集设定.
torchrun --nproc-per-node=8 run.py --data MMBench_Video_8frame_nopack --model idefics2_8
# 在 MMBench-Video 上评测 GPT-4o (API 模型), 视频采样每秒一帧作为输入，采用 pack 模式评测
python run.py --data MMBench_Video_1fps_pack --model GPT4o
```

评估结果将作为日志打印出来。此外，**结果文件**也会在目录 `$YOUR_WORKING_DIRECTORY/{model_name}` 中生成。以 `.csv` 结尾的文件包含评估的指标。
### 常见问题
#### 构建输入prompt：`build_prompt()`函数
如果您在评测某个benchmark时，发现模型输出的结果与预期不符，可能是因为您使用的模型没有正确构建输入prompt。

在VLMEvalkit中，每个`dataset`类都包含一个名为`build_prompt()`的函数，用于构建输入问题的格式。不同的benchmark可以选择自定义`build_prompt()`函数，也可以使用默认的实现。

例如，在处理默认的[多选题/Multi-Choice QA]([vlmeval/dataset/image_mcq.py](https://github.com/open-compass/VLMEvalKit/blob/43af13e052de6805a8b08cd04aed5e0d74f82ff5/vlmeval/dataset/image_mcq.py#L164))时，`ImageMCQDataset.build_prompt()`类会将`hint`、`question`、`options`等元素（若数据集中包含）组合成一个完整的问题格式，如下所示：
```
HINT
QUESTION
Options:
A. Option A
B. Option B
···
Please select the correct answer from the options above.
```

此外，由于不同模型对评测的需求可能有所不同，VLMEvalkit也支持在模型层面自定义对不同benchmark构建prompt的方法，即`model.build_prompt()`，具体示例可以参考[InternVL](https://github.com/open-compass/VLMEvalKit/blob/43af13e052de6805a8b08cd04aed5e0d74f82ff5/vlmeval/vlm/internvl_chat.py#L324)。

**注意：当同时定义了`model.build_prompt()`以及`dataset.build_prompt()`时，`model.build_prompt()`将优先于`dataset.build_prompt()`，即前者会覆盖后者。**

由于部分模型（如Qwen2VL，InternVL等）对于不同类型的benchmark定义了广泛的prompt构建方法，为了更灵活地适应不同的benchmark，VLMEvalkit支持在模型中自定义`model.use_custom_prompt()`函数。通过添加或者修改`use_custom_prompt()`函数，您可以决定对于哪些benchmark使用模型自定义的`use_custom_prompt()`方法，示例如下：
```
def use_custom_prompt(self, dataset: str) -> bool:
    from vlmeval.dataset import DATASET_TYPE, DATASET_MODALITY
    dataset_type = DATASET_TYPE(dataset, default=None)
    if not self._use_custom_prompt:
        return False
    if listinstr(['MMVet'], dataset):
        return True
    if dataset_type == 'MCQ':
        return True
    if DATASET_MODALITY(dataset) == 'VIDEO':
        return False
    return False
```
仅当`use_custom_prompt()`函数返回`True`时，VLMEvalkit才会对当前benchmark调用模型的`build_prompt()`函数。
通过这种方式，您可以根据具体需求灵活地控制哪些benchmark使用模型自定义的prompt构建逻辑，从而更好地适配不同模型和任务的需求。

#### 模型切分

目前 VLMEvalKit 的启动方式自动支持同机上进程间 GPU 资源的划分与模型切分。该功能在推理后端为 `lmdeploy` 或 `transformers` 时被支持，具体行为如下：

- 基于 `python` 命令启动时，模型默认分配到所有可用的 GPU 上，如想指定使用哪些 GPU，可以使用 `CUDA_VISIBLE_DEVICES` 环境变量。
- 基于 `torchrun` 命令启动时，每个模型实例会被分配到 `N_GPU // N_PROC` 个 GPU 上，`N_PROC` 为 torchrun 命令中的 `--nproc-per-node` 参数所指定的进程数。`N_GPU` 的取值为：
    - 如 `CUDA_VISIBLE_DEVICES` 环境变量未设置，`N_GPU` 为全部可用 GPU 数量。
    - 如 `CUDA_VISIBLE_DEVICES` 环境变量被设置，`N_GPU` 为 `CUDA_VISIBLE_DEVICES` 环境变量所指定的 GPU 数量，并且，仅有指定的 GPU 会被利用。

下面提供了，在一台配备 8 块 GPU 的机器上运行评测任务的具体示例：
```bash
# <!-- 起两个模型实例数据并行，每个实例用 4 GPU -->
torchrun --nproc-per-node=2 run.py --data MMBench_DEV_EN --model InternVL3-78B
# <!-- 起一个模型实例，每个实例用 8 GPU -->
python run.py --data MMBench_DEV_EN --model InternVL3-78B
# <!-- 起三个模型实例，每个实例用 2 GPU，0 号、7 号 GPU 未被使用 -->
CUDA_VISIBLE_DEVICES=1,2,3,4,5,6 torchrun --nproc-per-node=3 run.py --data MMBench_DEV_EN --model InternVL3-38B
```

注：此方式不支持 `vllm` 后端，基于 `vllm` 后端起评测任务时，请用 `python` 命令启动，默认调用所有可见的 GPU。

#### 性能差距
在不同的运行环境中，模型的性能表现可能会有所差异。因此，在评估过程中，您可能会发现自己的评测结果与VLMEvalKit官方榜单上的结果存在差距。这种差异可能与`transformers`, `cuda`, `torch`等版本的变化有关。

此外，对于异常的表现，我们建议您优先查看运行完成后的本地生成记录`{model}_{dataset}.xlsx`或者评估记录`{model}_{dataset}_{judge_model}.xlsx`，这可能会帮助您更好地理解评估结果并发现问题。



### 部署本地语言模型作为评判 / 选择提取器
上述默认设置使用 OpenAI 的 GPT 作为评判 LLM。你也可以使用 [LMDeploy](https://github.com/InternLM/lmdeploy) 部署本地评判 LLM。

首先进行安装:
```
pip install lmdeploy openai
```

然后可以通过一行代码部署本地评判 LLM。LMDeploy 将自动从 Huggingface 下载模型。假设我们使用 internlm2-chat-1_8b 作为评判，端口为 23333，密钥为 sk-123456（密钥必须以 "sk-" 开头，后跟任意数字）：
```
lmdeploy serve api_server internlm/internlm2-chat-1_8b --server-port 23333
```

使用以下 Python 代码获取由 LMDeploy 注册的模型名称：
```
from openai import OpenAI
client = OpenAI(
    api_key='sk-123456',
    base_url="http://0.0.0.0:23333/v1"
)
model_name = client.models.list().data[0].id
```

配置对应环境变量，以告诉 VLMEvalKit 如何使用本地评判 LLM。正如上面提到的，也可以在  `$VLMEvalKit/.env` 文件中设置：
```
OPENAI_API_KEY=sk-123456
OPENAI_API_BASE=http://0.0.0.0:23333/v1/chat/completions
LOCAL_LLM=<model_name you get>
```

最后，你可以运行第2步中的命令，使用本地评判 LLM 来评估你的 VLM。

**请注意：**

- 如果你希望将评判 LLM 部署在单独的一个 GPU 上，并且由于 GPU 内存有限而希望在其他 GPU 上评估你的 VLM，可以使用 `CUDA_VISIBLE_DEVICES=x` 这样的方法，例如：
```
CUDA_VISIBLE_DEVICES=0 lmdeploy serve api_server internlm/internlm2-chat-1_8b --server-port 23333
CUDA_VISIBLE_DEVICES=1,2,3 torchrun --nproc-per-node=3 run.py --data HallusionBench  --model qwen_chat --verbose
```
- 如果本地评判 LLM 在遵循指令方面不够好，评估过程可能会失败。请通过 issues 报告此类失败情况。
- 可以以不同的方式部署评判 LLM，例如使用私有 LLM（而非来自 HuggingFace）或使用量化 LLM。请参考 [LMDeploy doc](https://lmdeploy.readthedocs.io/en/latest/serving/api_server.html) 文档。也可以使用其他支持 OpenAI API 框架的方法。

### 使用 LMDeploy 加速模型推理

可参考[文档](/docs/zh-CN/EvalByLMDeploy.md)
