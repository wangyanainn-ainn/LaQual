"""
LaQual - App Tester
功能：应用基础指标检查
作者：Wang Yan
日期：2025-01-27
"""

import json
import os
import time
import re
from datetime import datetime
from typing import Dict, List, Any

def safe_int_conversion(value):
    """安全地将值转换为整数"""
    try:
        if value is None:
            return 0
        if isinstance(value, str):
            # 移除可能的非数字字符，保留数字、小数点和负号
            cleaned = re.sub(r'[^0-9.-]', '', value)
            if not cleaned or cleaned == '.' or cleaned == '-':
                return 0
            # 尝试转换为浮点数再转为整数
            return int(float(cleaned))
        elif isinstance(value, (int, float)):
            return int(value)
        else:
            return 0
    except (ValueError, TypeError, AttributeError):
        return 0

def calculate_quarters_fixed(publish_time):
    """计算发布时间到现在的季度数"""
    try:
        # 处理不同的日期格式
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d"
        ]
        
        publish_date = None
        for fmt in date_formats:
            try:
                publish_date = datetime.strptime(publish_time, fmt)
                break
            except ValueError:
                continue
        
        if publish_date is None:
            print(f"无法解析发布时间: {publish_time}")
            return 1.0
            
        current_date = datetime.now()
        months_diff = (current_date.year - publish_date.year) * 12 + current_date.month - publish_date.month
        quarters = max(1.0, months_diff / 3.0)
        return quarters
    except Exception as e:
        print(f"计算季度数时出错: {str(e)}")
        return 1.0

def calculate_time_decay(quarters):
    """计算时间衰减系数"""
    return 0.99 ** (quarters - 1)

def calculate_standardized_metric(raw_value, quarters):
    """计算标准化指标值"""
    decay_factor = calculate_time_decay(quarters)
    return (raw_value / quarters) * decay_factor

def check_basic_metrics(static_metrics: Dict) -> bool:
    """
    基础指标检查函数
    """
    try:
        # 1. 获取发布时间并计算季度数
        publish_time = static_metrics.get('发布时间', '')
        if not publish_time:
            print("警告：未找到发布时间，使用默认值")
            quarters = 1.0
        else:
            quarters = calculate_quarters_fixed(publish_time)
        
        # 2. 识别应用类型
        app_type = "通用型"  # 默认类型
        tool_type = ""
        
        # 获取标签（从static_metrics中获取）
        tag = ""
        if "标签" in static_metrics:
            tag_value = static_metrics["标签"]
            if isinstance(tag_value, list) and tag_value:
                tag = str(tag_value[0]).lower()
            elif isinstance(tag_value, str):
                tag = tag_value.lower()
            else:
                tag = str(tag_value).lower()
        
        print(f"应用标签: {tag}")

        # 根据标签关键词识别类型
        if any(keyword in tag for keyword in ["医疗", "健康", "疾病", "诊断", "治疗", "心理"]):
            app_type = "专业问答型"
            tool_type = "医疗健康"
        elif any(keyword in tag for keyword in ["法律", "法规", "合同", "诉讼"]):
            app_type = "专业问答型"
            tool_type = "法律咨询"
        elif any(keyword in tag for keyword in ["金融", "理财", "投资", "股票"]):
            app_type = "专业问答型"
            tool_type = "金融理财"
        elif any(keyword in tag for keyword in ["教育", "培训", "课程", "数学", "语文", "生物", "物理", "化学", "历史", "地理", "政治"]):
            app_type = "专业问答型"
            tool_type = "教育培训"
        elif any(keyword in tag for keyword in ["翻译", "单词", "互译", "语法", "语言", "中文", "英语", "日语", "德语", "韩语", "法语", "俄语", "意大利语"]):
            app_type = "专业问答型"
            tool_type = "语言学习"
        elif any(keyword in tag for keyword in ["咨询", "顾问", "专家"]):
            app_type = "专业问答型"
            tool_type = "专业咨询"
        elif any(keyword in tag for keyword in ["代码", "编程", "开发", "调试", "算法", "前端", "后端", "python", "java", "javascript", "matlab"]):
            app_type = "工具型"
            tool_type = "开发工具"
        elif any(keyword in tag for keyword in ["室内设计", "品牌设计"]):
            app_type = "工具型"
            tool_type = "设计工具"
        elif any(keyword in tag for keyword in ["规划", "规划师", "规划设计"]):
            app_type = "工具型"
            tool_type = "规划工具"
        elif any(keyword in tag for keyword in ["数据分析", "统计分析", "数据预测"]):
            app_type = "工具型"
            tool_type = "分析工具"
            
        print(f"应用类型识别: {app_type}" + (f" ({tool_type})" if tool_type else ""))

        # 3. 根据应用类型设置不同的阈值
        type_thresholds = {
            "工具型": {
                '浏览量': 20,
                '使用量': 20,
                '收藏量': 20,
                '被复制': 20,
                '模型配置': 1,
                '知识库数量': 0,
                '组件数量': 2
            },
            "专业问答型": {
                '浏览量': 20,
                '使用量': 20,
                '收藏量': 20,
                '被复制': 20,
                '模型配置': 1,
                '知识库数量': 1,
                '组件数量': 0
            },
            "通用型": {
                '浏览量': 20,
                '使用量': 20,
                '收藏量': 20,
                '被复制': 20,
                '模型配置': 1,
                '知识库数量': 0,
                '组件数量': 0
            }
        }

        # 4. 获取当前应用类型的阈值
        thresholds = type_thresholds[app_type]
        
        # 5. 分别计算基础指标和其他指标的通过情况
        basic_metrics_passed = 0  # 基础指标（浏览量、使用量、收藏量、被复制量）
        other_metrics_passed = 0  # 其他指标（模型配置、知识库数量、组件数量）
        
        # 基础指标列表
        basic_metrics = ['浏览量', '使用量', '收藏量', '被复制']
        
        for metric, threshold in thresholds.items():
            if metric in static_metrics:
                try:
                    if metric == '模型配置':
                        model_config = static_metrics[metric]
                        if isinstance(model_config, list):
                            value = len(model_config)
                        elif isinstance(model_config, str):
                            value = 1 if model_config.strip() else 0
                        else:
                            value = int(model_config) if model_config else 0
                    elif metric == '组件数量':
                        # 检查组件相关指标
                        components = 0
                        if '组件' in static_metrics:
                            comp_data = static_metrics['组件']
                            if isinstance(comp_data, list):
                                components = len(comp_data)
                            else:
                                components = safe_int_conversion(comp_data)
                        elif '组件数量' in static_metrics:
                            components = safe_int_conversion(static_metrics['组件数量'])
                        value = components
                    elif metric == '知识库数量':
                        # 使用知识库数量替代私有配置数量
                        value = safe_int_conversion(static_metrics.get('知识库数量', 0))
                    else:
                        # 对静态指标进行时间加权并加入时间衰减
                        raw_value = safe_int_conversion(static_metrics[metric])
                        weighted_value = raw_value / quarters
                        value = calculate_standardized_metric(raw_value, quarters)
                        print(f"原始{metric}: {raw_value}, 季度加权: {weighted_value:.1f}, 衰减后: {value:.1f}")
                    
                    if value >= threshold:
                        if metric in basic_metrics:
                            basic_metrics_passed += 1
                            print(f"✓ {metric}: {value:.1f} (阈值: {threshold}) [基础指标]")
                        else:
                            other_metrics_passed += 1
                            print(f"✓ {metric}: {value:.1f} (阈值: {threshold}) [其他指标]")
                    else:
                        print(f"✗ {metric}: {value:.1f} (阈值: {threshold})")
                        
                except Exception as e:
                    print(f"处理指标 {metric} 时出错: {str(e)}")
                    continue
        
        # 6. 根据应用类型设置不同的通过条件
        basic_metrics_required = 1  # 基础指标需要满足1个
        
        # 其他指标需要全部满足（3个）
        other_metrics_required = 3
        
        # 总指标需要满足4个（1个基础指标 + 3个其他指标）
        total_metrics_required = 4
        
        # 判断是否通过基础过滤
        basic_passed = basic_metrics_passed >= basic_metrics_required
        other_passed = other_metrics_passed >= other_metrics_required
        is_passed = basic_passed and other_passed
        
        # 打印评分详情
        print("\n应用评分详情:")
        print(f"应用类型: {app_type}" + (f" ({tool_type})" if tool_type else ""))
        print(f"基础指标通过数: {basic_metrics_passed}/4 (需要: {basic_metrics_required}个)")
        print(f"基础指标通过: {'是' if basic_passed else '否'}")
        print(f"其他指标通过数: {other_metrics_passed} (需要: {other_metrics_required}个)")
        print(f"其他指标通过: {'是' if other_passed else '否'}")
        print(f"总体通过: {'是' if is_passed else '否'}")
        
        # 1. 必须满足模型配置
        if '模型配置' not in static_metrics or not static_metrics['模型配置'] or len(static_metrics['模型配置']) < thresholds['模型配置']:
            print("✗ 模型配置不满足要求")
            return False
        else:
            print(f"✓ 模型配置满足要求: {len(static_metrics['模型配置'])}")

        # 2. 工具型必须满足组件数量
        if app_type == "工具型":
            components = 0
            if '组件' in static_metrics:
                components = len(static_metrics['组件']) if isinstance(static_metrics['组件'], list) else 0
            elif '组件数量' in static_metrics:
                components = safe_int_conversion(static_metrics['组件数量'])
            if components < thresholds['组件数量']:
                print("✗ 工具型应用组件数量不满足要求")
                return False
            else:
                print(f"✓ 工具型应用组件数量满足要求: {components}")

        # 3. 专业问答型必须满足知识库数量
        if app_type == "专业问答型":
            kb_count = safe_int_conversion(static_metrics.get('知识库数量', 0))
            if kb_count < thresholds['知识库数量']:
                print("✗ 专业问答型应用知识库数量不满足要求")
                return False
            else:
                print(f"✓ 专业问答型应用知识库数量满足要求: {kb_count}")

        # 4. 其他基础指标可以按原有方式判断
        return is_passed
        
    except Exception as e:
        print(f"指标检查过程中出现未知错误: {str(e)}")
        return False

class AppTester:
    def __init__(self):
        """初始化应用测试器"""
        pass

    def load_apps_data(self, file_path: str) -> List[Dict]:
        """加载应用数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载应用数据失败: {str(e)}")
            return []

    def check_app_metrics(self, app_data: Dict) -> bool:
        """检查单个应用的基础指标"""
        return check_basic_metrics(app_data)

    def filter_apps_by_metrics(self, apps_data: List[Dict]) -> List[Dict]:
        """根据基础指标过滤应用"""
        filtered_apps = []
        
        for app in apps_data:
            print(f"\n检查应用: {app.get('title', 'Unknown')}")
            if self.check_app_metrics(app):
                filtered_apps.append(app)
                print(f"✅ 应用通过基础指标检查")
            else:
                print(f"❌ 应用未通过基础指标检查")
        
        return filtered_apps

    def save_filtered_apps(self, filtered_apps: List[Dict], output_file: str):
        """保存过滤后的应用数据"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_apps, f, ensure_ascii=False, indent=2)
            print(f"✅ 过滤后的应用数据已保存到: {output_file}")
        except Exception as e:
            print(f"保存过滤后的应用数据失败: {str(e)}")

    def process_apps_batch(self, apps_file: str, output_file: str):
        """批量处理应用数据"""
        # 加载应用数据
        apps_data = self.load_apps_data(apps_file)
        if not apps_data:
            print("应用数据加载失败")
            return
        
        print(f"加载了 {len(apps_data)} 个应用")
        
        # 过滤应用
        filtered_apps = self.filter_apps_by_metrics(apps_data)
        
        print(f"\n过滤结果:")
        print(f"原始应用数量: {len(apps_data)}")
        print(f"通过过滤的应用数量: {len(filtered_apps)}")
        print(f"过滤率: {len(filtered_apps)/len(apps_data)*100:.1f}%")
        
        # 保存结果
        self.save_filtered_apps(filtered_apps, output_file)
        
        return filtered_apps

def main():
    """主函数"""
    tester = AppTester()
    
    # 文件路径
    apps_file = "sample_apps.json"
    output_file = "filtered_apps.json"
    
    # 批量处理
    tester.process_apps_batch(apps_file, output_file)

if __name__ == "__main__":
    main()
