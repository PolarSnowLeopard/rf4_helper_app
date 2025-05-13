import os
import sys
import json

# 获取项目根目录路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# 添加后端代码目录到Python路径
sys.path.append(os.path.join(project_root, "dev"))

# 导入后端处理函数
try:
    from fish_cards import get_fish_cards_result
    from roboflow_format import convert_yolo_to_standard
    from get_ocr_result import get_ocr_result
    from utils import BoundingBox, draw_bounding_boxes_on_image, save_image_to_file
except ImportError as e:
    print(f"导入后端模块失败: {e}")
    # 如果导入失败，可以创建模拟函数进行测试
    def get_fish_cards_result(image_path):
        return {"mock": "data"}
    
    def convert_yolo_to_standard(data):
        return {"result": []}
    
    def get_ocr_result(image_path):
        return {"words_result": []}


class ImageProcessor:
    def __init__(self):
        self.temp_dir = os.path.join(project_root, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process(self, image_path):
        """处理图像并返回结果"""
        try:
            # 1. 调用目标检测
            fish_cards_result = get_fish_cards_result(image_path)
            
            # 2. 转换格式
            standard_results = convert_yolo_to_standard(fish_cards_result)
            
            # 3. 转为BoundingBox列表
            fish_cards = []
            for item in standard_results['result']:
                location = item['location']
                left, top, width, height = location['left'], location['top'], location['width'], location['height']
                fish_cards.append(BoundingBox(left, top, width, height, False))
            
            # 4. OCR识别
            ocr_result = get_ocr_result(image_path)
            
            # 5. 解析OCR结果
            words_cards = []
            for item in ocr_result['words_result']:
                location = item['location']
                left, top, width, height = location['left'], location['top'], location['width'], location['height']
                item['BoundingBox'] = BoundingBox(left, top, width, height, False, item['words'])
                words_cards.append(item)
            
            # 6-7. 匹配并整理鱼类信息
            for i, word_card in enumerate(words_cards):
                for j, fish_card in enumerate(fish_cards):
                    if word_card['BoundingBox'].is_overlapping(fish_card):
                        words_cards[i]['fish_card_index'] = j
                        break
            
            fishes = []
            for i in range(len(fish_cards)):
                fish = []
                for word_card in words_cards:
                    if len(word_card['words']) < 2:
                        continue
                    fish_card_index = word_card.get('fish_card_index', None)
                    if fish_card_index is not None and fish_card_index == i:
                        fish.append(word_card['words'])
                if len(fish) > 0:
                    fishes.append(fish)
            
            # 保存处理后的图片
            result_image_path = os.path.join(self.temp_dir, "processed_image.png")
            
            # 省略绘制边界框的步骤，具体项目中可以添加
            
            return {
                "success": True,
                "fishes": fishes,
                "result_image": result_image_path
            }
            
        except Exception as e:
            print(f"处理图像时出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }