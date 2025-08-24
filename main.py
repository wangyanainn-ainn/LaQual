"""
LaQual - Main Program
作者：Wang yan
日期：2025-01-27
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# 添加core目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from label_metrics_generator import LabelMetricsGenerator
from question_generator import QuestionGenerator
from app_tester import AppTester
from response_evaluator import ResponseEvaluator

class LaQualFramework:
    def __init__(self):
        """初始化LaQual框架"""
        self.config = {
            "data_dir": ".",
            "results_dir": ".",
            "output_dir": "."
        }
        
        # 确保目录存在
        for dir_path in self.config.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # 初始化各个组件
        self.label_metrics_generator = LabelMetricsGenerator()
        self.question_generator = QuestionGenerator()
        self.app_tester = AppTester()
        self.response_evaluator = ResponseEvaluator()

    def step1_generate_label_metrics(self, apps_file: str = None) -> str:
        """步骤1：生成标签和指标"""
        print("=" * 60)
        print("步骤1：生成标签和指标")
        print("=" * 60)
        
        if apps_file is None:
            apps_file = "apps_by_tags.json"
        
        # 检查输入文件是否存在
        if not os.path.exists(apps_file):
            print(f"❌ 输入文件不存在: {apps_file}")
            print("请确保提供了正确的应用数据文件")
            return None
        
        # 生成标签和指标
        output_file = "tag_metrics.json"
        metrics = self.label_metrics_generator.generate_metrics_for_all_tags(output_file)
        
        if metrics:
            print(f"✅ 标签和指标生成完成，共生成 {len(metrics)} 个标签的指标")
            return output_file
        else:
            print("❌ 标签和指标生成失败")
            return None

    def step2_generate_questions(self, metrics_file: str = None) -> str:
        """步骤2：生成评估问题"""
        print("=" * 60)
        print("步骤2：生成评估问题")
        print("=" * 60)
        
        if metrics_file is None:
            metrics_file = "tag_metrics.json"
        
        # 检查输入文件是否存在
        if not os.path.exists(metrics_file):
            print(f"❌ 指标文件不存在: {metrics_file}")
            print("请先运行步骤1生成标签指标")
            return None
        
        # 生成问题
        output_file = "tag_evaluation_questions.json"
        questions = self.question_generator.generate_questions_for_all_tags(metrics_file, output_file)
        
        if questions:
            print(f"✅ 评估问题生成完成，共生成 {len(questions)} 个标签的问题")
            return output_file
        else:
            print("❌ 评估问题生成失败")
            return None

    def step3_test_apps(self, apps_file: str = None) -> str:
        """步骤3：应用基础指标检查"""
        print("=" * 60)
        print("步骤3：应用基础指标检查")
        print("=" * 60)
        
        if apps_file is None:
            apps_file = "sample_apps.json"
        
        # 检查输入文件是否存在
        if not os.path.exists(apps_file):
            print(f"❌ 应用数据文件不存在: {apps_file}")
            print("请提供应用数据文件")
            return None
        
        # 检查应用基础指标
        output_file = "filtered_apps.json"
        results = self.app_tester.process_apps_batch(apps_file, output_file)
        
        if results:
            print(f"✅ 应用基础指标检查完成，共检查 {len(results)} 个应用")
            return output_file
        else:
            print("❌ 应用基础指标检查失败")
            return None

    def step4_evaluate_responses(self, test_results_file: str = None, metrics_file: str = None) -> str:
        """步骤4：评估响应"""
        print("=" * 60)
        print("步骤4：评估响应")
        print("=" * 60)
        
        if test_results_file is None:
            test_results_file = "app_test_results.json"
        
        if metrics_file is None:
            metrics_file = "tag_metrics.json"
        
        # 检查输入文件是否存在
        if not os.path.exists(test_results_file):
            print(f"❌ 测试结果文件不存在: {test_results_file}")
            print("请先运行步骤3测试应用")
            return None
        
        if not os.path.exists(metrics_file):
            print(f"❌ 指标文件不存在: {metrics_file}")
            print("请先运行步骤1生成标签指标")
            return None
        
        # 评估响应
        output_file = "evaluation_results.json"
        results = self.response_evaluator.evaluate_batch(test_results_file, metrics_file, output_file)
        
        if results:
            print(f"✅ 响应评估完成，共评估 {len(results)} 个应用")
            return output_file
        else:
            print("❌ 响应评估失败")
            return None

    def run_full_pipeline(self, apps_file: str = None):
        """运行完整的评估流程"""
        print("🚀 开始LaQual完整评估流程")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # 步骤1：生成标签和指标
        metrics_file = self.step1_generate_label_metrics(apps_file)
        if not metrics_file:
            print("❌ 流程在第1步失败")
            return False
        
        # 步骤2：生成评估问题
        questions_file = self.step2_generate_questions(metrics_file)
        if not questions_file:
            print("❌ 流程在第2步失败")
            return False
        
        # 步骤3：应用基础指标检查
        filtered_apps_file = self.step3_test_apps(apps_file)
        if not filtered_apps_file:
            print("❌ 流程在第3步失败")
            return False
        
        # 步骤4：评估响应
        evaluation_file = self.step4_evaluate_responses(filtered_apps_file, metrics_file)
        if not evaluation_file:
            print("❌ 流程在第4步失败")
            return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 60)
        print("🎉 LaQual评估流程完成！")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration:.2f} 秒")
        print(f"最终结果文件: {evaluation_file}")
        print("=" * 60)
        
        return True

    def run_single_step(self, step: int, **kwargs):
        """运行单个步骤"""
        if step == 1:
            return self.step1_generate_label_metrics(**kwargs)
        elif step == 2:
            return self.step2_generate_questions(**kwargs)
        elif step == 3:
            return self.step3_test_apps(**kwargs)
        elif step == 4:
            return self.step4_evaluate_responses(**kwargs)
        else:
            print(f"❌ 无效的步骤号: {step}")
            return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LaQual框架 - LLM应用质量评估')
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4], 
                       help='运行单个步骤 (1: 生成标签和指标, 2: 生成问题, 3: 应用基础指标检查, 4: 评估响应)')
    parser.add_argument('--apps-file', type=str, help='应用数据文件路径 (默认: apps_by_tags.json)')
    parser.add_argument('--full', action='store_true', help='运行完整流程')
    
    args = parser.parse_args()
    
    # 初始化框架
    framework = LaQualFramework()
    
    if args.full:
        # 运行完整流程
        framework.run_full_pipeline(args.apps_file)
    elif args.step:
        # 运行单个步骤
        kwargs = {}
        if args.apps_file:
            kwargs['apps_file'] = args.apps_file
        
        result = framework.run_single_step(args.step, **kwargs)
        if result:
            print(f"✅ 步骤 {args.step} 完成，输出文件: {result}")
        else:
            print(f"❌ 步骤 {args.step} 失败")
    else:
        # 默认运行完整流程
        print("未指定参数，运行完整流程...")
        framework.run_full_pipeline(args.apps_file)

if __name__ == "__main__":
    main()
