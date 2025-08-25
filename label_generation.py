"""
LaQual - Label Generation
功能：基于应用信息生成标签
作者：Wang Yan
日期：2025-01-27
"""

import json
import os
import time
import requests
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
from sentence_transformers import SentenceTransformer, util
import torch
import re

# SiliconFlow API配置
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY') or 'your_api_key_here'
SILICONFLOW_API_URL = os.getenv('SILICONFLOW_API_URL') or 'https://api.siliconflow.cn/v1/chat/completions'

class LabelGeneration:
    def __init__(self):
        """初始化标签生成器"""
        self.data = None
        self.api_url = SILICONFLOW_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
        }
        
        # 加载相似度模型
        print("正在加载中文相似度模型...")
        try:
            # 设置本地缓存目录
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")
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

    def load_apps_data(self, file_path: str) -> bool:
        """加载应用数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                print(f"成功加载应用数据文件: {file_path}")
                return True
        except Exception as e:
            print(f"加载应用数据文件失败: {str(e)}")
            return False

    def verify_tag_similarity(self, tag: str, descriptions: List[str]) -> bool:
        """使用中文预训练模型验证标签与描述的语义相似度"""
        if self.similarity_model is None:
            print("相似度模型未加载，跳过相似度验证")
            return True
            
        try:
            # 预处理标签和描述
            def preprocess_text(text):
                # 移除标点符号
                text = re.sub(r'[^\w\s]', '', text)
                # 移除多余空格
                text = ' '.join(text.split())
                return text
            
            tag = preprocess_text(tag)
            processed_descriptions = [preprocess_text(desc) for desc in descriptions]
            
            # 编码标签
            tag_embedding = self.similarity_model.encode(tag, convert_to_tensor=True)
            
            # 计算与每个描述的相似度
            similarities = []
            for desc in processed_descriptions:
                # 将长描述分段，每段最多100个字符
                desc_chunks = [desc[i:i+100] for i in range(0, len(desc), 100)]
                chunk_similarities = []
                
                for chunk in desc_chunks:
                    chunk_embedding = self.similarity_model.encode(chunk, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(tag_embedding, chunk_embedding)
                    chunk_similarities.append(similarity.item())
                
                # 取每个描述中最高的相似度
                max_chunk_similarity = max(chunk_similarities)
                similarities.append(max_chunk_similarity)
            
            # 计算平均相似度
            avg_similarity = sum(similarities) / len(similarities)
            print(f"标签相似度: {avg_similarity:.3f}")
            
            # 计算最大相似度
            max_similarity = max(similarities)
            print(f"最大相似度: {max_similarity:.3f}")
            
            # 输出相似度最高的描述
            max_similarity_index = similarities.index(max_similarity)
            print(f"相似度最高的描述: {descriptions[max_similarity_index][:100]}...")
            
            # 如果平均相似度超过0.7或最大相似度超过0.7，就认为标签合适
            return avg_similarity >= 0.7 or max_similarity >= 0.7
        except Exception as e:
            print(f"相似度计算失败: {str(e)}")
            return True  # 如果相似度计算失败，默认通过验证

    def generate_tag_from_descriptions(self, descriptions: List[str]) -> str:
        """根据应用描述生成一个概括这些应用核心价值的标签"""
        prompt = f"""作为LLM应用分类专家，请分析以下应用描述，提取核心实体并生成一个最能够突出这些应用核心价值和特色的标签。

应用描述：
{json.dumps(descriptions, ensure_ascii=False, indent=2)}

分析步骤：
1. 提取核心实体：
   - 专业领域（如：医疗、法律、教育等）
   - 核心功能（如：诊断、咨询、辅导等）
   - 应用场景（如：在线问诊、法律咨询、在线教育等）

2. 生成标签要求：
   - 必须准确反映这些应用的核心价值和特色
   - 应保留完整的专业领域和核心功能词汇，确保术语的准确性和专业性，不要过度简化
   - 标签简洁明了，长度控制在6-9个字
   - 优先使用完整的中文专业术语，不要过度简化
   - 确保标签具有足够的特异性，避免过于宽泛的概括

3. 禁止词列表：
   - 标签中绝对不能出现以下词汇：["工具", "助手", "服务", "平台", "系统"]

4. 示例：
- 如果描述包含"心理辅导"，应生成"心理辅导"而不是"辅导"
- 如果描述包含"法律咨询"，应生成"法律咨询"而不是"咨询"
- 如果描述包含"医疗诊断"，应生成"医疗诊断"而不是"诊断"

请直接返回标签名称，不要包含任何其他内容。"""

        attempt = 1
        while True:  # 无限循环，直到生成满足要求的标签
            try:
                print(f"\n正在尝试第 {attempt} 次生成标签...")
                print("开始调用API...")
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "Qwen/QwQ-32B",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "max_tokens": 50,
                        "temperature": 0.3,
                        "top_p": 0.7,
                        "top_k": 20,
                        "n": 1,
                        "response_format": {"type": "text"}
                    },
                    timeout=120
                )
                print("API调用完成，开始解析响应...")
                response.raise_for_status()
                tag = response.json()['choices'][0]['message']['content'].strip()
                tag = tag.splitlines()[0].strip()  # 只取第一行作为标签
                print(f"生成的标签: {tag}")
                
                print("开始验证标签相似度...")
                # 验证标签相似度
                if self.verify_tag_similarity(tag, descriptions):
                    print(f"\n✅ 成功生成标签: {tag}")
                    return tag
                else:
                    print(f"\n⚠️ 标签相似度不足，将重新生成...")
                
            except requests.exceptions.Timeout:
                print(f"\n❌ 第 {attempt} 次尝试超时")
                print("超时发生在:")
                import traceback
                print(traceback.format_exc())
            except requests.exceptions.RequestException as e:
                print(f"\n❌ 第 {attempt} 次尝试失败: {str(e)}")
            except Exception as e:
                print(f"\n❌ 第 {attempt} 次尝试出错: {str(e)}")
                print("错误发生在:")
                import traceback
                print(traceback.format_exc())
            
            # 指数退避重试
            retry_delay = min(2 ** (attempt - 1), 30)
            print(f"\n⏳ {retry_delay}秒后进行第{attempt + 1}次尝试...")
            time.sleep(retry_delay)
            attempt += 1

    def generate_label_for_apps(self, apps_data: Dict) -> Dict:
        """根据应用数据生成标签"""
        try:
            # 处理不同格式的输入数据
            descriptions = []
            if isinstance(apps_data, list):
                # 如果是描述数组
                descriptions = apps_data
            elif isinstance(apps_data, dict) and "apps" in apps_data:
                # 如果是包含apps字段的对象
                descriptions = [app.get('description', '') for app in apps_data.get('apps', [])]
            else:
                print("输入数据格式不正确")
                return None

            if not descriptions:
                print("未找到应用描述")
                return None

            # 生成标签
            tag = self.generate_tag_from_descriptions(descriptions)
            if not tag:
                print("生成标签失败")
                return None

            # 构建结果
            result = {
                "标签": tag,
                "应用数量": len(descriptions),
                "应用描述": descriptions
            }

            return result

        except Exception as e:
            print(f"处理应用数据时出错: {str(e)}")
            return None



def main():
    """主函数"""
    generator = LabelGeneration()
    
    # 加载应用数据
    apps_file = "../sample_apps.json"
    if not generator.load_apps_data(apps_file):
        print("❌ 应用数据加载失败")
        return
    
    # 生成标签
    result = generator.generate_label_for_apps(generator.data)
    
    if result:
        print(f"\n✅ 标签生成完成")
        print(f"生成的标签: {result['标签']}")
        print(f"应用数量: {result['应用数量']}")
        
        # 保存结果
        output_file = "generated_label.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 标签已保存到: {output_file}")
        except Exception as e:
            print(f"保存结果失败: {str(e)}")
    else:
        print("❌ 标签生成失败")

if __name__ == "__main__":
    main()
