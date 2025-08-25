"""
LaQual - Evaluation_task_generation
功能：根据标签指标生成评估问题
作者：wang yan
日期：2025-01-27
"""

import json
import os
import requests
import time
import sys
from typing import Dict, List, Any

# SiliconFlow API配置
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY') or 'your_api_key_here'
SILICONFLOW_API_URL = os.getenv('SILICONFLOW_API_URL') or 'https://api.siliconflow.cn/v1/chat/completions'

class QuestionGenerator:
    def __init__(self):
        self.api_key = SILICONFLOW_API_KEY
        self.api_url = SILICONFLOW_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ensure_output_dir(self, output_dir: str):
        """确保输出目录存在"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")

    def load_metrics(self, file_path: str) -> Dict[str, Any]:
        """加载指标数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取指标文件时出错: {str(e)}")
            return {}

    def call_siliconflow_api(self, prompt: str) -> str:
        """调用SiliconFlow API生成问题"""
        data = {
            "model": "Qwen/QwQ-32B",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的AI应用评估专家，擅长生成评估问题。请根据给定的指标信息，生成完整、专业、具体、可操作的评估问题。你的问题应该：\n1. 专业性强\n2. 具体可操作\n3. 逻辑清晰\n4. 便于评估\n5. 符合评分标准\n6. 确保生成完整的问题，不要被截断"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "max_tokens": 4000,  # 增加token限制，确保能生成完整的问题
            "temperature": 0.4,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }
        
        try:
            print("正在调用SiliconFlow API...")
            response = requests.post(self.api_url, headers=self.headers, json=data)
            
            if response.status_code == 400:
                print("API请求格式错误，请检查请求参数")
                print(f"错误详情: {response.text}")
                return None
            elif response.status_code == 401:
                print("API密钥无效或未授权")
                return None
            elif response.status_code == 429:
                print("API调用频率超限，请稍后重试")
                return None
            elif response.status_code != 200:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"错误详情: {response.text}")
                return None
                
            response.raise_for_status()
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                print("API返回数据格式错误")
                return None
                
            content = result['choices'][0]['message']['content']
            
            # 验证生成的内容是否完整
            if content and len(content) > 0:
                # 检查是否以完整句子结束
                if not any(content.endswith(end) for end in ['。', '！', '？', '.', '!', '?']):
                    print("警告：生成的内容可能不完整，尝试重新生成")
                    return None
                    
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"API请求异常: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"API响应解析错误: {str(e)}")
            return None
        except Exception as e:
            print(f"调用API时发生未知错误: {str(e)}")
            return None

    def generate_question(self, category: str, metric_name: str, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据指标生成一个具体、可操作的问题"""
        description = metric_data.get("描述", "")
        scoring_criteria = metric_data.get("评分标准", [])
        
        prompt = f"""你是一个专业的AI应用评估专家。请根据以下信息，生成一个具体、可操作的评估问题。

评估对象：{category}领域的{metric_name}
指标描述：{description}

请生成一个自然的问题，要求：
1. 问题要模拟真实用户对该应用进行交互时的提问
2. 问题要包含完整的上下文信息
3. 问题要具体可操作
4. 问题中不要包含任何评估目的或指标说明
5. 问题要符合该领域的常见用户需求
6. 问题要有一定的挑战性和复杂度
7. 问题必须包含具体的内容或示例，不能只说"以下内容"或"以下段落"
8. 确保生成完整的问题，不要被截断
9. 问题必须以完整的句子结束，使用适当的标点符号

参考示例：
- 学术写作：请帮我写一篇关于气候变化对农业影响的论文摘要，要求包含研究背景、方法和主要发现。
- 语言学习：请用英语写一封商务邮件，内容是向客户解释项目延期一周的原因，语气要专业且诚恳。
- 写作辅助：请帮我写一篇产品使用说明，介绍一款新型智能家居设备的主要功能和使用方法。
- 幽默：请写一个关于职场新人的幽默段子，要体现办公室日常生活的趣味性。

请按照上述示例的风格，生成一个自然的问题。注意：
1. 问题的内容要具体
2. 确保问题完整且可操作
3. 不要使用"请分析"、"请检查"、"请评价"等词汇
4. 问题必须以完整的句子结束，使用适当的标点符号

请严格按照如下格式输出：
问题：[问题内容]
"""

        max_retries = 10
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                print(f"\n正在尝试第 {attempt + 1} 次生成问题...")
                ai_response = self.call_siliconflow_api(prompt)
                if not ai_response:
                    print(f"第 {attempt + 1} 次API调用失败，准备重试...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)
                    continue

                # 解析问题
                lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
                question = next((line.replace('问题：', '').replace('问题:', '').strip() for line in lines if line.startswith('问题')), '')

                if not question:
                    print(f"第 {attempt + 1} 次生成的问题格式不完整，准备重试...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)
                    continue

                if len(question) < 10:
                    print(f"第 {attempt + 1} 次生成的问题过于简单，准备重试...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)
                    continue
                    
                # 验证问题是否完整
                if not any(question.endswith(end) for end in ['。', '！', '？', '.', '!', '?']):
                    print(f"第 {attempt + 1} 次生成的问题可能不完整，准备重试...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)
                    continue

                print(f"\n✅ 成功生成问题！")
                print(f"问题: {question}")

                return {
                    "category": category,
                    "metric_name": metric_name,
                    "description": description,
                    "question": question,
                    "scoring_criteria": scoring_criteria
                }

            except Exception as e:
                print(f"第 {attempt + 1} 次生成失败: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
                continue

        raise Exception(f"在 {max_retries} 次尝试后仍未能生成满意的问题")

    def process_metrics(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理指标数据并生成问题"""
        processed_metrics = []
        
        # 获取标签和评估指标
        tag = metrics_data.get("标签", "")
        evaluation_metrics = metrics_data.get("评估指标", {})
        
        print(f"\n{'='*50}")
        print(f"正在处理标签: {tag}")
        print(f"{'='*50}")
        
        for metric_name, metric_data in evaluation_metrics.items():
            try:
                print(f"处理指标: {metric_name}")
                
                # 生成问题（会一直重试直到成功）
                question_data = self.generate_question(tag, metric_name, metric_data)
                
                # 添加基本信息
                question_data["basic_info"] = {
                    "tag": tag,
                    "application_count": metrics_data.get("应用数量", 0),
                    "application_descriptions": metrics_data.get("应用描述", [])
                }
                
                processed_metrics.append(question_data)
                print(f"✅ 已完成指标: {metric_name}")
                
            except Exception as e:
                print(f"\n❌ 处理指标 {metric_name} 时出错: {str(e)}")
                print("跳过当前指标，继续处理下一个...")
                continue
        
        return processed_metrics

    def save_to_json(self, data: List[Dict[str, Any]], filename: str):
        """保存结果到JSON文件"""
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(filename)
            self.ensure_output_dir(output_dir)
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {filename}")
        except Exception as e:
            print(f"保存文件时出错: {str(e)}")

    def generate_questions_for_all_tags(self, input_file: str, output_file: str):
        """为所有标签生成问题"""
        # 加载指标数据
        print(f"正在加载指标数据: {input_file}")
        metrics_data = self.load_metrics(input_file)
        
        if not metrics_data:
            print("未能加载指标数据，程序退出")
            return None
        
        # 处理指标数据
        print("正在处理指标数据并生成问题...")
        processed_metrics = self.process_metrics(metrics_data)
        
        # 保存结果
        print("正在保存结果...")
        self.save_to_json(processed_metrics, output_file)
        
        print(f"处理完成，共生成 {len(processed_metrics)} 个问题")
        print(f"结果文件位置: {output_file}")
        
        return processed_metrics

def main():
    """主函数"""
    generator = QuestionGenerator()
    
    # 文件路径
    input_file = "../data/tag_metrics.json"
    output_file = "../data/output/tag_evaluation_questions.json"
    
    # 生成问题
    generator.generate_questions_for_all_tags(input_file, output_file)

if __name__ == "__main__":
    main()
