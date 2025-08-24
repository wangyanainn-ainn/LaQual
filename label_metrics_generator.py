"""
LaQual - Label & Metrics Generator
功能：基于应用类别和标签生成评估指标库
作者：wang yan
日期：2025-01-27
"""

import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import requests
import time
import sys
from sentence_transformers import SentenceTransformer, util
import torch
import re

SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY') or 'your_api_key_here'
SILICONFLOW_API_URL = os.getenv('SILICONFLOW_API_URL') or 'https://api.siliconflow.cn/v1/chat/completions'

class LabelMetricsGenerator:
    def __init__(self):
        self.data = None
        self.tags = defaultdict(lambda: {
            "apps": [],
            "count": 0
        })
        # API配置
        self.api_url = SILICONFLOW_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
        }
        
        # 加载相似度模型
        print("正在加载中文相似度模型...")
        try:
            # 设置本地缓存目录
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # 使用专门的中文预训练模型
            self.similarity_model = SentenceTransformer(
                'shibing624/text2vec-base-chinese',
                cache_folder=cache_dir,
                local_files_only=True  # 只使用本地文件
            )
            print("中文相似度模型加载成功（使用本地缓存）")
        except Exception as e:
            print(f"本地模型加载失败: {str(e)}")
            try:
                # 如果本地加载失败，尝试在线下载
                print("尝试在线下载中文模型...")
                self.similarity_model = SentenceTransformer(
                    'shibing624/text2vec-base-chinese',
                    cache_folder=cache_dir
                )
                print("中文相似度模型下载并加载成功")
            except Exception as e:
                print(f"模型加载失败: {str(e)}")
                print("将跳过相似度验证")
                self.similarity_model = None
        
    def generate_metrics_prompt_for_tag(self, tag: str) -> str:
        # 对于相似的标签，使用相同的标签名来生成指标
        original_tag = tag
            
        return f"""作为LLM应用质量评估专家，请为"{original_tag}"标签的应用生成3个评估指标。

一、基础要求:
1.  **独特性与相关性 :**
    *   指标必须能精准反映该标签应用的独特价值主张。
    *   指标必须与"{original_tag}"这个核心标签高度相关。
2.  **可量化与可操作性 :**
    *   指标必须可以被量化评估（最终输出为1-5分）。
    *   其对应的评分标准，必须描述**具体、可观察**的内容特征或行为，而非模糊、抽象的概念，以便于评估人员进行客观判断。
3.  **维度区分度 :**
    *   生成的3个指标应从**不同**的角度对应用进行评估，确保它们之间存在明确的区分度，避免语义上的重复或高度重叠。

二、评估范围的核心约束：
    *   **主观与内容导向:** 指标必须**完全**基于对生成文本内容的**主观质量评估**。
    *   **禁止外部依赖:** 严禁生成任何需要外部数据、系统性能监控（如响应速度）、用户行为统计（如点击率）或长期观察才能得出的客观指标。
    *   **纯文本评估:** 评估必须完全基于文本内容，避免涉及对图像、视频、音频等多模态元素的评估。

三、评分标准的具体要求:
    *   每一个指标都必须包含一套清晰、明确的五级评分标准。
    *   评分标准必须是可操作的，便于人类评估员进行客观、一致的判断。

请按以下JSON格式返回：
{{
    "指标1": {{
        "描述": "指标描述",
        "评分标准": [
            "5分标准描述",
            "4分标准描述",
            "3分标准描述",
            "2分标准描述",
            "1分标准描述"
        ]
    }},
    "指标2": {{
        // 同上
    }},
    "指标3": {{
        // 同上
    }}
}}"""

    def call_api_for_metrics_for_tag(self, tag: str) -> Dict:
        """调用API为指定标签生成指标"""
        prompt = self.generate_metrics_prompt_for_tag(tag)
        
        data = {
            "model": "Qwen/QwQ-32B",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 512
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 尝试解析JSON
            try:
                # 提取JSON部分
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_content = content[json_start:json_end]
                    metrics = json.loads(json_content)
                    return metrics
                else:
                    print(f"无法找到JSON内容: {content}")
                    return {}
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {str(e)}")
                print(f"原始内容: {content}")
                return {}
                
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            return {}

    def generate_metrics_for_all_tags(self, output_file: str = None):
        """为所有标签生成指标"""
        if not self.data:
            print("请先加载数据")
            return
        
        all_tags_analysis = self.analyze_all_tags()
        all_metrics = {}
        
        for tag_info in all_tags_analysis["all_tags"]:
            tag = tag_info["标签名称"]
            print(f"正在为标签 '{tag}' 生成指标...")
            
            metrics = self.call_api_for_metrics_for_tag(tag)
            if metrics:
                all_metrics[tag] = metrics
                print(f"✅ 成功为标签 '{tag}' 生成指标")
            else:
                print(f"❌ 为标签 '{tag}' 生成指标失败")
            
            # 添加延迟避免API限制
            time.sleep(1)
        
        # 保存结果
        if output_file is None:
            output_file = "../data/tag_metrics.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_metrics, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 所有指标已保存到: {output_file}")
        return all_metrics

def main():
    """主函数"""
    generator = LabelMetricsGenerator()
    
    # 加载数据
    data_file = "../data/apps_by_tags.json"
    if not generator.load_data(data_file):
        print("数据加载失败，程序退出")
        return
    
    # 生成指标
    generator.generate_metrics_for_all_tags()

if __name__ == "__main__":
    main()
