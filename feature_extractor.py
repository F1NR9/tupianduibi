import cv2
import numpy as np
from sklearn.preprocessing import normalize

class FeatureExtractor:
    def __init__(self):
        pass
    
    def extract_color_features(self, image):
        """提取颜色特征"""
        # 转换为HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 计算颜色直方图
        hist_h = cv2.calcHist([hsv], [0], None, [8], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [8], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [8], [0, 256])
        
        # 归一化
        hist_h = cv2.normalize(hist_h, hist_h).flatten()
        hist_s = cv2.normalize(hist_s, hist_s).flatten()
        hist_v = cv2.normalize(hist_v, hist_v).flatten()
        
        # 合并特征
        color_features = np.concatenate([hist_h, hist_s, hist_v])
        return color_features
    
    def extract_shape_features(self, image):
        """提取形状特征"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 100, 200)
        
        # 计算边缘直方图
        edge_hist = cv2.calcHist([edges], [0], None, [16], [0, 256])
        edge_hist = cv2.normalize(edge_hist, edge_hist).flatten()
        
        return edge_hist
    
    def extract_texture_features(self, image):
        """提取纹理特征"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算LBP特征
        lbp = self._compute_lbp(gray)
        lbp_hist = cv2.calcHist([lbp], [0], None, [256], [0, 256])
        lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()
        
        return lbp_hist
    
    def _compute_lbp(self, image):
        """计算局部二值模式(LBP)"""
        height, width = image.shape
        lbp = np.zeros((height, width), dtype=np.uint8)
        
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = image[i, j]
                code = 0
                code |= (image[i-1, j-1] > center) << 7
                code |= (image[i-1, j] > center) << 6
                code |= (image[i-1, j+1] > center) << 5
                code |= (image[i, j+1] > center) << 4
                code |= (image[i+1, j+1] > center) << 3
                code |= (image[i+1, j] > center) << 2
                code |= (image[i+1, j-1] > center) << 1
                code |= (image[i, j-1] > center) << 0
                lbp[i, j] = code
        
        return lbp
    
    def extract_features(self, image_path):
        """提取完整特征"""
        # 读取图片（支持中文路径）
        try:
            # 使用np.fromfile读取文件内容
            img_data = np.fromfile(image_path, dtype=np.uint8)
            # 使用cv2.imdecode解码图片
            image = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            if image is None:
                return None
        except Exception as e:
            print(f"读取图片失败: {image_path}, 错误: {e}")
            return None
        
        # 调整图片大小
        image = cv2.resize(image, (256, 256))
        
        # 提取各特征
        color_features = self.extract_color_features(image)
        shape_features = self.extract_shape_features(image)
        texture_features = self.extract_texture_features(image)
        
        # 合并特征
        features = np.concatenate([color_features, shape_features, texture_features])
        
        # 归一化
        features = normalize([features])[0]
        
        return features

if __name__ == "__main__":
    extractor = FeatureExtractor()
    # 测试特征提取
    test_image = "data/images/test.jpg"
    features = extractor.extract_features(test_image)
    print(f"特征向量长度: {len(features)}")
    print(f"特征向量: {features[:10]}...")
