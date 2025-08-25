# LaQual: LLM应用质量评估框架

LaQual是一个专门用于评估大语言模型(LLM) App 质量的自动化框架。该框架通过标签生成、指标生成、静态指标评估、评估问题构建、响应评估5个核心功能，实现对LLM应用的全面质量评估。

##  项目概述

LaQual框架旨在解决LLM应用质量评估中的以下挑战：
- **标准化评估指标**：为不同应用场景的LLM应用生成专门的评估指标
- **自动化问题生成**：基于评估指标自动生成测试问题
- **智能应用测试**：对应用进行静态指标筛选
- **客观响应评估**：使用LLM API对应用响应进行客观评估

##  系统架构

```
LaQual Framework
├── 标签生成 (Label Generation)
│   ├── 应用描述分析
│   ├── 标签生成
│   └── 相似度验证
├── 指标生成 (Metric Generation)
│   ├── 标签分析
│   └── 指标、评估标准生成
├── 静态指标评估 (Static Indicator evaluation)
│   ├── 应用类型识别
│   ├── 静态指标评估
│   ├── 时间衰减算法
│   └── 过滤不达标应用
├── 问题生成 (Question Generation)
│   ├── 指标解析
│   ├── 问题构建
│   └── 质量验证
└── 响应评估 (Response Evaluation)
    ├── 内容质量评估
    ├── 性能指标计算
    └── 综合评分
```

##  项目结构

```
LaQual/
├── core/                          # 核心模块
│   ├── label_generation.py         # 标签生成
│   ├── Metric_generation.py        # 指标生成
│   ├── Static_indicator_evaluation.py # 静态指标评估
│   ├── Evaluation_task_generation.py # 应用测试问题生成
│   └── Response_quality_evaluation.py # 响应评估
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

##  核心功能

### 1. 标签生成 (Label Generation)

- **功能**：基于应用描述生成标签
- **输入**：应用数据
- **输出**：生成的标签
- **特点**：
  - 基于LLM API生成
  - 相似度验证
  - 语义分析

### 2. 指标生成 (Metric Generation)

- **功能**：基于应用标签生成评估指标
- **输入**：应用标签数据 
- **输出**：标签指标数据
- **特点**：
  - 支持多种应用类别
  - 自动指标分类
  - 标准化评估

### 3. 静态指标评估 (Static Indicator Evaluation)

- **功能**：应用静态指标检查
- **输入**：应用数据
- **输出**：过滤后的应用数据 
- **特点**：
  - 静态指标过滤
  - 时间衰减算法
  - 应用类型识别

### 4. 评估问题生成 (Evaluation task Generation)

- **功能**：根据标签指标生成评估问题
- **输入**：标签|、指标数据 
- **输出**：评估问题 
- **特点**：
  - 基于LLM API生成
  - 问题质量验证
  - 多维度问题设计


### 5. 响应质量评估 (Response Quality Evaluation)

- **功能**：评估应用响应质量
- **输入**：应用测试结果 + 标签指标
- **输出**：评估结果
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
- 项目链接：[GitHub链接]

**注意**：本项目仅供学术研究使用，请遵守相关法律法规和API使用条款。

##  致谢

感谢以下开源项目和技术：
- SiliconFlow API
- Sentence Transformers
- Python社区

---

