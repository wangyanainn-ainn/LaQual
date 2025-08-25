"""
LaQual - Response_quality_evaluation
功能：评估应用响应质量
作者：wang yan
日期：2025-01-27
"""

import json
import os
from typing import List, Dict, Any
import requests
from datetime import datetime
import time
import re

# API配置
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY') or 'your_api_key_here'
SILICONFLOW_API_URL = os.getenv('SILICONFLOW_API_URL') or 'https://api.siliconflow.cn/v1/chat/completions'

class ResponseEvaluator:
    def __init__(self):
        """初始化评估器"""
        self.api_key = SILICONFLOW_API_KEY
        self.api_url = SILICONFLOW_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 性能评估阈值
        self.performance_thresholds = {
            "total_seconds": {
                "excellent": 30,  # 30秒以内
                "good": 60,      # 60秒以内
                "fair": 90,      # 90秒以内
                "poor": 120      # 120秒以内
            },
            "token_rate": {
                "excellent": 5.0,  # 5 tokens/秒以上
                "good": 3.0,      # 3 tokens/秒以上
                "fair": 2.0,      # 2 tokens/秒以上
                "poor": 1.0       # 1 token/秒以上
            }
        }
        
        # 评分权重
        self.weights = {
            "content_score": 0.8,    # 内容评分权重
            "performance_score": 0.2  # 性能评分权重
        }

    def evaluate_response(self, question: str, response: str, scoring_criteria: List[str]) -> Dict[str, Any]:
        """使用LLM API评估单个响应的质量"""
        prompt = f"""请根据以下评分标准对回答进行详细评估：

问题：{question}

回答：{response}

评分标准：
{chr(10).join(scoring_criteria)}

请按照以下格式输出评估结果：
分数：[1-5之间的数字]
优点：
- [列出回答的优点，至少2点]
不足：
- [列出回答的不足，至少2点]
改进建议：
- [给出具体的改进建议，至少2点]

请确保评估客观、专业，并严格遵循评分标准。"""

        max_retries = 20  # 增加最大重试次数，确保多次评估直至成功
        retry_delay = 5
        timeout = 60  # 增加超时时间到60秒

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": "Qwen/QwQ-32B",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的评估专家，负责评估AI助手的回答质量。请根据评分标准给出1-5分的评分，并提供详细的评估理由和改进建议。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "max_tokens": 5000,
                    "temperature": 0,
                    "top_p": 0.7,
                    "top_k": 50,
                    "frequency_penalty": 0.5,
                    "n": 1,
                    "response_format": {"type": "text"}
                }
                
                print(f"正在尝试第 {attempt + 1} 次评估...")
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
            
                if response.status_code == 400:
                    print("API请求格式错误，请检查请求参数")
                    print(f"错误详情: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return {"score": 0, "evaluation": "评估失败"}
                elif response.status_code == 401:
                    print("API密钥无效或未授权")
                    return {"score": 0, "evaluation": "评估失败"}
                elif response.status_code == 429:
                    print("API调用频率超限，请稍后重试")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * 2)  # 对于频率限制，等待更长时间
                        continue
                    return {"score": 0, "evaluation": "评估失败"}
                elif response.status_code != 200:
                    print(f"API调用失败，状态码: {response.status_code}")
                    print(f"错误详情: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return {"score": 0, "evaluation": "评估失败"}
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' not in result or not result['choices']:
                    print("API返回数据格式错误")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return {"score": 0, "evaluation": "评估失败"}
                    
                evaluation_text = result['choices'][0]['message']['content'].strip()
                
                # 验证响应是否完整
                if len(evaluation_text) < 50 or "分数：" not in evaluation_text:
                    print("响应内容不完整，正在重试...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return {"score": 0, "evaluation": "评估失败：响应不完整"}
                
                # 提取分数
                score_match = re.search(r'分数：(\d+(?:\.\d+)?)', evaluation_text)
                if score_match:
                    score = float(score_match.group(1))
                    score = min(max(score, 1), 5)  # 确保分数在1-5之间
                    return {
                        "score": score,
                        "evaluation": evaluation_text
                    }
                else:
                    print("未能从响应中提取分数")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return {"score": 0, "evaluation": "评估失败"}
                    
            except requests.exceptions.Timeout:
                print(f"请求超时（{timeout}秒），正在重试...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {"score": 0, "evaluation": "评估超时"}
            except requests.exceptions.RequestException as e:
                print(f"API请求错误: {str(e)}")
                if hasattr(e.response, 'text'):
                    print(f"错误详情: {e.response.text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {"score": 0, "evaluation": "评估失败"}
            except Exception as e:
                print(f"评估出错: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {"score": 0, "evaluation": "评估失败"}
        
        return {"score": 0, "evaluation": "评估失败，已达到最大重试次数"}

    def evaluate_performance(self, metrics: Dict) -> Dict:
        """只评估响应效率（tokens_per_second），并返回三项性能指标"""
        try:
            total_time = metrics.get("total_time", 0)
            token_count = metrics.get("token_count", 0)
            tokens_per_second = metrics.get("tokens_per_second", 0)

            # 响应效率评分分档（可后续调整）
            if tokens_per_second >= 25:
                eff_score = 5
            elif tokens_per_second >= 20:
                eff_score = 4
            elif tokens_per_second >= 15:
                eff_score = 3
            elif tokens_per_second >= 10:
                eff_score = 2
            else:
                eff_score = 1

            return {
                "total_time": total_time,
                "token_count": token_count,
                "tokens_per_second": tokens_per_second,
                "eff_score": eff_score
            }
        except Exception as e:
            print(f"性能评估出错: {str(e)}")
            return {
                "total_time": 0,
                "token_count": 0,
                "tokens_per_second": 0,
                "eff_score": 1
            }

    def evaluate_batch(self, test_results_file: str, metrics_file: str, output_file: str):
        """批量评估测试结果"""
        # 加载测试结果
        try:
            with open(test_results_file, 'r', encoding='utf-8') as f:
                test_results = json.load(f)
        except Exception as e:
            print(f"加载测试结果失败: {str(e)}")
            return
        
        # 加载指标数据
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
        except Exception as e:
            print(f"加载指标数据失败: {str(e)}")
            return
        
        app_evaluations = []
        
        for app_result in test_results:
            app_info = app_result.get('app_info', {})
            responses = app_result.get('responses', {})
            
            app_name = app_info.get('title', 'Unknown')
            app_url = app_info.get('url', '')
            
            print(f"\n正在评估应用: {app_name}")
            
            evaluation_details = []
            total_content_score = 0
            total_performance_score = 0
            evaluation_count = 0
            
            for tag, tag_responses in responses.items():
                if tag not in metrics_data:
                    continue
                
                tag_metrics = metrics_data[tag]
                
                for metric_name, metric_responses in tag_responses.items():
                    if metric_name not in tag_metrics:
                        continue
                    
                    metric_criteria = tag_metrics[metric_name].get('评分标准', [])
                    metric_description = tag_metrics[metric_name].get('描述', '')
                    
                    for question_name, question_data in metric_responses.items():
                        question = question_data.get('question', '')
                        response = question_data.get('response', '')
                        metrics = question_data.get('metrics', {})
                        
                        print(f"评估标签 '{tag}' 指标 '{metric_name}' 问题 '{question_name}'")
                        
                        # 评估响应内容
                        content_evaluation = self.evaluate_response(question, response, metric_criteria)
                        content_score = content_evaluation.get('score', 3)
                        
                        # 评估性能
                        performance_metrics = self.evaluate_performance(metrics)
                        performance_score = performance_metrics.get('eff_score', 1)
                        
                        # 计算综合评分
                        final_score = (
                            content_score * self.weights['content_score'] +
                            performance_score * self.weights['performance_score']
                        )
                        
                        evaluation_detail = {
                            "metric": metric_name,
                            "description": metric_description,
                            "scoring_criteria": metric_criteria,
                            "question": question,
                            "response": response,
                            "content_score": content_score,
                            "performance_score": performance_score,
                            "final_score": round(final_score, 2),
                            "content_evaluation": content_evaluation.get('evaluation', ''),
                            "performance_metrics": performance_metrics
                        }
                        
                        evaluation_details.append(evaluation_detail)
                        total_content_score += content_score
                        total_performance_score += performance_score
                        evaluation_count += 1
            
            if evaluation_count > 0:
                avg_content_score = total_content_score / evaluation_count
                avg_performance_score = total_performance_score / evaluation_count
                total_score = (
                    avg_content_score * self.weights['content_score'] +
                    avg_performance_score * self.weights['performance_score']
                )
            else:
                avg_content_score = 0
                avg_performance_score = 0
                total_score = 0
            
            app_evaluation = {
                "app_name": app_name,
                "app_url": app_url,
                "total_score": round(total_score, 2),
                "content_score": round(avg_content_score, 2),
                "performance_score": round(avg_performance_score, 2),
                "evaluation_details": evaluation_details
            }
            
            app_evaluations.append(app_evaluation)
        
        # 保存评估结果
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(app_evaluations, f, ensure_ascii=False, indent=2)
        
        # 生成详细报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"evaluation_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("应用响应质量评估报告\n")
            f.write("=" * 60 + "\n\n")
            
            for i, eval_data in enumerate(app_evaluations, 1):
                f.write(f"应用 {i}: {eval_data['app_name']}\n")
                f.write(f"URL: {eval_data['app_url']}\n")
                f.write(f"总分: {eval_data['total_score']}\n")
                f.write(f"内容评分: {eval_data['content_score']}\n")
                f.write(f"性能评分: {eval_data['performance_score']}\n")
                f.write("-" * 50 + "\n")
                
                for detail in eval_data["evaluation_details"]:
                    f.write(f"\n{detail['metric']}:\n")
                    f.write(f"内容评分: {detail['content_score']}分\n")
                    f.write(f"性能评分: {detail['performance_score']}分\n")
                    f.write(f"问题: {detail['question']}\n")
                    f.write("\n性能指标:\n")
                    f.write(f"响应总时间: {detail['performance_metrics']['total_time']:.2f}秒\n")
                    f.write(f"Token总数: {detail['performance_metrics']['token_count']}\n")
                    f.write(f"响应效率: {detail['performance_metrics']['tokens_per_second']:.2f} tokens/秒\n")
                    f.write(f"效率评分: {detail['performance_metrics']['eff_score']}分\n")
                    f.write("\n内容评估:\n")
                    f.write(f"{detail['content_evaluation']}\n")
                    f.write("-" * 50 + "\n")
                
                f.write("\n" + "=" * 50 + "\n\n")

        print(f"\n评估报告已生成: {report_file}")
        print(f"✅ 评估完成，结果已保存到: {output_file}")
        return app_evaluations

def main():
    """主函数"""
    evaluator = ResponseEvaluator()
    
    # 文件路径
    test_results_file = "../results/app_test_results.json"
    metrics_file = "../data/tag_metrics.json"
    output_file = "../results/evaluation_results.json"
    
    # 批量评估
    evaluator.evaluate_batch(test_results_file, metrics_file, output_file)

if __name__ == "__main__":
    main()
