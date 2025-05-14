"""API客户端模块，用于处理与后端服务的通信"""

import os
import json
import base64
import logging
import mimetypes
import requests
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from src.utils.config_loader import config_loader

# 配置日志
logger = logging.getLogger(__name__)

# 确保mimetypes已初始化
mimetypes.init()

# 添加一些常见的图片类型映射（如果系统中没有）
if '.png' not in mimetypes.types_map:
    mimetypes.add_type('image/png', '.png')
if '.jpg' not in mimetypes.types_map and '.jpeg' not in mimetypes.types_map:
    mimetypes.add_type('image/jpeg', '.jpg')
    mimetypes.add_type('image/jpeg', '.jpeg')
if '.bmp' not in mimetypes.types_map:
    mimetypes.add_type('image/bmp', '.bmp')

class APIConfig:
    """API配置类，负责从配置加载器获取API配置"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIConfig, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置"""
        # 从环境变量获取
        self.base_url = os.environ.get('RF4_API_BASE_URL')
        
        # 如果环境变量没有配置，从配置加载器获取
        if not self.base_url:
            self.base_url = config_loader.get('api_base_url')
        
        # 如果仍然未配置，使用默认值
        if not self.base_url:
            self.base_url = "http://localhost:5000/api"
            logger.warning(f"未找到API基础URL配置，使用默认值: {self.base_url}")
        
        # 加载API端点配置
        self.endpoints = config_loader.get('api_endpoints', {})
        if not self.endpoints:
            # 默认端点配置
            self.endpoints = {
                "process_image": {
                    "path": "process_image",
                    "method": "POST",
                    "description": "处理图像识别鱼类"
                },
                # 其他端点配置可在这里添加...
            }
            logger.warning(f"未找到API端点配置，使用默认值")
    
    def get_base_url(self) -> str:
        """获取API基础URL"""
        return self.base_url
    
    def set_base_url(self, url: str) -> None:
        """设置API基础URL"""
        self.base_url = url
        # 更新配置
        config_loader.set('api_base_url', url)
        config_loader.save_config()
    
    def get_endpoint(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定名称的API端点配置"""
        return self.endpoints.get(name)
    
    def set_endpoint(self, name: str, config: Dict[str, Any]) -> None:
        """设置API端点配置"""
        if self.endpoints is None:
            self.endpoints = {}
        self.endpoints[name] = config
        # 更新配置
        config_loader.set('api_endpoints', self.endpoints)
        config_loader.save_config()

class APIException(Exception):
    """API异常类"""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class BaseAPIClient:
    """API客户端基类"""
    
    def __init__(self):
        self.config = APIConfig()
        self.base_url = self.config.get_base_url()
        self.session = requests.Session()
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理API响应"""
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"API响应错误: {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = f"API错误: {error_data['error']}"
            except:
                pass
            
            logger.error(error_msg)
            raise APIException(error_msg, response.status_code)
    
    def _get_endpoint_url(self, endpoint_name: str) -> str:
        """获取完整的端点URL"""
        endpoint_config = self.config.get_endpoint(endpoint_name)
        if not endpoint_config:
            raise APIException(f"未找到端点配置: {endpoint_name}")
        
        endpoint_path = endpoint_config.get("path", endpoint_name)
        return self.base_url + endpoint_path
    
    def get(self, endpoint_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送GET请求"""
        url = self._get_endpoint_url(endpoint_name)
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def post(self, endpoint_name: str, data: Optional[Dict[str, Any]] = None, 
             json_data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送POST请求"""
        url = self._get_endpoint_url(endpoint_name)
        print(url)
        logger.debug(f"发送POST请求: {url}, 数据: {data}, JSON数据: {json_data}, 文件: {files}")
        response = self.session.post(url, data=data, json=json_data, files=files)
        return self._handle_response(response)

class RF4APIClient(BaseAPIClient):
    """俄罗斯钓鱼4 API客户端"""
    
    def get_file_mime_type(self, file_path: str) -> str:
        """获取文件的MIME类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的MIME类型
        """
        # 使用文件扩展名猜测MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # 如果无法猜测，使用默认值
        if mime_type is None:
            mime_type = 'application/octet-stream'
            
            # 对于特定的图片扩展名，设置对应的MIME类型
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.bmp':
                mime_type = 'image/bmp'
            elif ext == '.gif':
                mime_type = 'image/gif'
            elif ext == '.tiff' or ext == '.tif':
                mime_type = 'image/tiff'
                
        return mime_type
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """处理图像识别鱼类
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含处理结果的字典
        """
        file_obj = None
        try:
            # 获取文件的MIME类型
            mime_type = self.get_file_mime_type(image_path)
            logger.debug(f"上传图片 {image_path} MIME类型: {mime_type}")
            
            # 打开文件
            file_obj = open(image_path, 'rb')
            
            # 使用multipart/form-data直接上传文件
            files = {
                'image': (os.path.basename(image_path), file_obj, mime_type)
            }
            
            # 发送到后端API
            return self.post("process_image", files=files)
                
        except Exception as e:
            logger.error(f"处理图片失败: {str(e)}")
            raise APIException(f"处理图片失败: {str(e)}")
        finally:
            # 确保资源正确关闭
            if file_obj is not None and not file_obj.closed:
                file_obj.close()
    
    # def get_fish_database(self) -> List[Dict[str, Any]]:
    #     """获取鱼类数据库
        
    #     Returns:
    #         包含所有鱼类信息的列表
    #     """
    #     try:
    #         return self.get("fish_database")
    #     except Exception as e:
    #         logger.error(f"获取鱼类数据库失败: {str(e)}")
    #         raise APIException(f"获取鱼类数据库失败: {str(e)}")
    
    # def get_lake_info(self, lake_id: Union[int, str]) -> Dict[str, Any]:
    #     """获取湖泊信息
        
    #     Args:
    #         lake_id: 湖泊ID
            
    #     Returns:
    #         包含湖泊信息的字典
    #     """
    #     try:
    #         return self.get("lake_info", params={"lake_id": lake_id})
    #     except Exception as e:
    #         logger.error(f"获取湖泊信息失败: {str(e)}")
    #         raise APIException(f"获取湖泊信息失败: {str(e)}")
    
    def upload_custom_image(self, image_path: str, image_type: str) -> Dict[str, Any]:
        """上传自定义图像
        
        Args:
            image_path: 图像文件路径
            image_type: 图像类型
            
        Returns:
            上传结果
        """
        file_obj = None
        try:
            # 获取文件的MIME类型
            mime_type = self.get_file_mime_type(image_path)
            logger.debug(f"上传自定义图片 {image_path} MIME类型: {mime_type}")
            
            # 打开文件
            file_obj = open(image_path, 'rb')
            
            files = {
                'image': (os.path.basename(image_path), file_obj, mime_type)
            }
            data = {"type": image_type}
            
            return self.post("upload_image", data=data, files=files)
            
        except Exception as e:
            logger.error(f"上传图片失败: {str(e)}")
            raise APIException(f"上传图片失败: {str(e)}")
        finally:
            # 确保资源正确关闭
            if file_obj is not None and not file_obj.closed:
                file_obj.close()

# 为方便使用，创建默认实例
rf4_api = RF4APIClient() 