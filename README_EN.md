# LaQual: A Novel Framework for Automated Evaluation of LLM App Quality

LaQual is a specialized automated framework for evaluating the quality of Large Language Model (LLM) apps. The framework achieves comprehensive quality evaluation of LLM apps through 5 core functions: label generation, metric generation, static indicator evaluation, evaluation task generation, and response quality evaluation.

## Project Overview

The LaQual framework aims to address the following challenges in LLM app quality evaluation:
- **Standardized Evaluation Metrics**: Generate specialized evaluation metrics for LLM apps in different application scenarios
- **Automated task Generation**: Automatically generate test questions based on evaluation metrics
- **Intelligent App Testing**: Perform static indicator screening for apps
- **Objective Response Evaluation**: Use LLM API to evaluate app responses objectively

## System Architecture

```
LaQual Framework
├── Label Generation
│   ├── App Description Analysis
│   ├── Label Generation
│   └── Similarity Verification
├── Metric Generation
│   ├── Label Analysis
│   └── Metric & Evaluation Standard Generation
├── Static Indicator Evaluation
│   ├── App Type Identification
│   ├── Static Indicator Evaluation
│   ├── Time Decay Algorithm
│   └── Filter Non-compliant Apps
├── Evaluation Task Generation
│   ├── Metric Parsing
│   ├── Task Construction
│   └── Quality Verification
└── Response Evaluation
    ├── Content Quality Evaluation
    ├── Response performance evaluation
    └── Comprehensive Scoring
```

## Project Structure

```
LaQual/
├── core/                          # Core modules
│   ├── label_generation.py         # Label generation
│   ├── Metric_generation.py        # Metric generation
│   ├── Static_indicator_evaluation.py # Static indicator evaluation
│   ├── Evaluation_task_generation.py # Application test question generation
│   └── Response_quality_evaluation.py # Response evaluation
├── main.py                      # Main program
├── requirements.txt             # Dependencies
├── config.example.py            # Configuration example
└── README.md                    # Project documentation
```

## Quick Start

### Requirements

- Python 3.8+
- SiliconFlow API key

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Set environment variable to configure SiliconFlow API key:

```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

Or copy the configuration example file and modify it:

```bash
cp config.example.py config.py
# Then edit the config.py file and enter your API key
```

**Note**: Please ensure the security of your API key and do not hardcode keys in the code.

## Core Functions

### 1. Label Generation

- **Function**: Generate labels based on LLM App descriptions
- **Input**: App data
- **Output**: Generated labels
- **Features**:
  - LLM API-based generation
  - Similarity verification
  - Semantic analysis

### 2. Metric Generation

- **Function**: Generate evaluation metrics based on app labels
- **Input**: App label 
- **Output**: Label metric 
- **Features**:
  - Support for multiple LLM App categories
  - Automatic metric classification
  - Standardized evaluation

### 3. Static Indicator Evaluation

- **Function**: Apply static indicator checks for apps
- **Input**: App data
- **Output**: Filtered app data
- **Features**:
  - Static indicator filtering
  - Time decay algorithm
  - App type identification

### 4. Evaluation Task Generation

- **Function**: Generate evaluation tasks based on metrics
- **Input**: Label and metric data
- **Output**: Evaluation tasks
- **Features**:
  - LLM API-based generation
  - task quality verification
  - Multi-dimensional Task design

### 5. Response Quality Evaluation

- **Function**: Evaluate app response quality
- **Input**: App test results + label metrics
- **Output**: Evaluation results
- **Features**:
  - Content quality assessment
  - Response performance evaluation
  - Comprehensive scoring algorithm

## Evaluation Metrics

### Basic Metrics
- **Views**: Number of times the app was viewed
- **Interactions**: Number of times the app was used
- **Favorites**: Number of times the app was favorited
- **Copies**: Number of times the app was copied

### Time Decay Algorithm
Uses a decay coefficient of `0.99^(quarters-1)` to ensure fair comparison between new and old applications.

## Output Results

### Evaluation Result Format

```json
{
  "app_info": {
    "title": "App Name",
    "label": ["label"],
    "metrics": {...}
  },
  "evaluations": {
    "Tag1": {
      "Metric1": {
        "Question1": {
          "score": 4,
          "pros": ["Advantage1", "Advantage2"],
          "cons": ["Disadvantage1", "Disadvantage2"],
          "suggestions": ["Suggestion1", "Suggestion2"]
        }
      }
    }
  }
}
```

## Contact Information

- Project Maintainer: Wang Yan
- Project Link: [https://github.com/wangyanainn-ainn/LaQual]

**Note**: This project is for academic research purposes only. Please comply with relevant laws and regulations and API usage terms.

## Acknowledgments

Thanks to the following open-source projects and technologies:
- SiliconFlow API
- Sentence Transformers
- Python Community

---

