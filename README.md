# LaQual: LLM应用质量评估框架

LaQual是一个专门用于评估大语言模型(LLM) App 质量的自动化框架。该框架通过标签生成、指标和评估标准生成、问题构建、应用测试和响应评估四个核心步骤，实现对LLM应用的全面质量评估。

##  项目概述

LaQual框架旨在解决LLM应用质量评估中的以下挑战：
- **标准化评估指标**：为不同类别的LLM应用生成专门的评估指标
- **自动化问题生成**：基于评估指标自动生成测试问题
- **智能应用测试**：对应用进行基础指标筛选和问题测试
- **客观响应评估**：使用LLM API对应用响应进行客观评估

##  系统架构

```
LaQual Framework
├── 标签生成 (Label Generation)
├── 应用分类分析
├── 指标库生成
│   └── 时间衰减算法
├── 问题生成 (Question Generation)
│   ├── 指标解析
│   ├── 问题构建
│   └── 质量验证
├── 应用测试 (App Testing)
│   ├── 基础指标检查
│   ├── 问题测试
│   └── 响应收集
└── 响应评估 (Response Evaluation)
    ├── 内容质量评估
    ├── 性能指标计算
    └── 综合评分
```

##  项目结构

```
LaQual/
│── label_metrics_generator.py # 标签和指标生成器
│   ├── question_generator.py     # 问题生成器
│   ├── app_tester.py            # 应用测试器
│   └── response_evaluator.py    # 响应评估器
├── main.py                      # 主程序
├── requirements.txt             # 依赖包
├── config.example.py            # 配置示例
└── README.md                    # 项目说明
```

##  快速开始

### 环境要求

- Python 3.8+
- SiliconFlow API密钥

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥

设置环境变量配置SiliconFlow API密钥：

```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

或者复制配置示例文件并修改：

```bash
cp config.example.py config.py
# 然后编辑 config.py 文件，填入您的API密钥
```

**注意**：请确保API密钥的安全性，不要在代码中硬编码密钥。

### 运行完整流程

```bash
python main.py --full --apps-file apps_by_tags.json
```

### 运行单个步骤

```bash
# 步骤1：生成标签和指标
python main.py --step 1 --apps-file apps_by_tags.json

# 步骤2：生成评估问题
python main.py --step 2

# 步骤3：应用基础指标检查
python main.py --step 3 --apps-file sample_apps.json

# 步骤4：评估响应
python main.py --step 4
```

##  核心功能

### 1. 标签和指标生成器 (Label & Metrics Generator)

- **功能**：基于应用类别和标签生成评估指标库
- **输入**：应用标签数据 (`apps_by_tags.json`)
- **输出**：标签指标数据 (`tag_metrics.json`)
- **特点**：
  - 支持多种应用类别
  - 自动指标分类
  - 时间衰减算法

### 2. 问题生成器 (Question Generator)

- **功能**：根据标签指标生成评估问题
- **输入**：标签指标数据 (`tag_metrics.json`)
- **输出**：评估问题集 (`tag_evaluation_questions.json`)
- **特点**：
  - 基于LLM API生成
  - 问题质量验证
  - 多维度问题设计

### 3. 应用测试器 (App Tester)

- **功能**：应用基础指标检查
- **输入**：应用数据
- **输出**：过滤后的应用数据 (`filtered_apps.json`)
- **特点**：
  - 基础指标过滤
  - 时间衰减算法
  - 应用类型识别

### 4. 响应评估器 (Response Evaluator)

- **功能**：评估应用响应质量
- **输入**：应用测试结果 + 标签指标
- **输出**：评估结果 (`evaluation_results.json`)
- **特点**：
  - 内容质量评估
  - 性能指标计算
  - 综合评分算法

##  评估指标

### 基础指标
- **浏览量**：应用被查看的次数
- **使用量**：应用被使用的次数
- **收藏量**：应用被收藏的次数
- **被复制**：应用被复制的次数

### 时间衰减算法
使用 `0.99^(quarters-1)` 的衰减系数，确保新老应用在公平的基础上比较。

### 评估维度
- **内容质量**：回答的准确性、完整性、相关性
- **性能表现**：响应时间、token生成速度

##  输出结果

### 评估结果格式

```json
{
  "app_info": {
    "title": "应用名称",
    "tags": ["标签1", "标签2"],
    "metrics": {...}
  },
  "evaluations": {
    "标签1": {
      "指标1": {
        "问题1": {
          "score": 4,
          "final_score": 3.8,
          "pros": ["优点1", "优点2"],
          "cons": ["不足1", "不足2"],
          "suggestions": ["建议1", "建议2"]
        }
      }
    }
  }
}
```

##  联系方式

- 项目维护者：Wang Yan
- 邮箱：wangyan@mails.cuc.edu.cn

**注意**：本项目仅供学术研究使用，请遵守相关法律法规和API使用条款。

##  致谢

感谢以下开源项目和技术：
- SiliconFlow API
- Sentence Transformers
- Python社区

---


