import os
import numpy as np
import faiss
from feature_extractor import FeatureExtractor

class Matcher:
    def __init__(self):
        self.extractor = FeatureExtractor()
        self.index = None
        self.image_paths = []
    
    def build_index(self, image_dir):
        """构建特征索引"""
        print("开始收集图片路径...")
        # 收集所有图片路径
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.endswith('.jpg') or file.endswith('.png'):
                    # 确保路径使用正确的编码
                    try:
                        image_path = os.path.join(root, file)
                        # 测试是否能读取文件
                        if os.path.exists(image_path):
                            self.image_paths.append(image_path)
                    except Exception as e:
                        print(f"处理文件路径失败: {file}, 错误: {e}")
        
        print(f"收集到 {len(self.image_paths)} 张图片")
        
        # 提取特征
        features = []
        valid_image_paths = []
        
        print("开始提取特征...")
        for i, image_path in enumerate(self.image_paths):
            try:
                print(f"提取第 {i+1}/{len(self.image_paths)} 张图片的特征: {image_path}")
                feature = self.extractor.extract_features(image_path)
                if feature is not None:
                    features.append(feature)
                    valid_image_paths.append(image_path)
                    print(f"成功提取特征: {image_path}")
                else:
                    print(f"特征提取失败: {image_path}")
            except Exception as e:
                print(f"提取特征失败: {image_path}, 错误: {e}")
        
        # 更新有效图片路径
        self.image_paths = valid_image_paths
        
        # 构建FAISS索引
        if features:
            print(f"提取到 {len(features)} 个有效特征")
            features = np.array(features, dtype=np.float32)
            print(f"特征向量形状: {features.shape}")
            self.index = faiss.IndexFlatL2(features.shape[1])
            self.index.add(features)
            print(f"索引构建完成，包含 {len(features)} 张图片")
        else:
            print("没有提取到有效特征")
    
    def match(self, query_image_path, top_k=5):
        """匹配图片"""
        if self.index is None:
            print("索引未构建")
            return []
        
        # 提取查询图片特征
        print(f"提取查询图片特征: {query_image_path}")
        query_feature = self.extractor.extract_features(query_image_path)
        if query_feature is None:
            print("查询图片特征提取失败")
            return []
        
        # 搜索相似图片
        print("开始搜索相似图片...")
        query_feature = np.array([query_feature], dtype=np.float32)
        distances, indices = self.index.search(query_feature, top_k)
        
        # 整理匹配结果
        results = []
        for i in range(top_k):
            if indices[0][i] < len(self.image_paths):
                results.append({
                    'image_path': self.image_paths[indices[0][i]],
                    'distance': distances[0][i]
                })
        
        print(f"匹配完成，找到 {len(results)} 个结果")
        return results

if __name__ == "__main__":
    matcher = Matcher()
    # 构建索引
    matcher.build_index('data/images')
    
    # 测试匹配
    test_image = "test.jpg"
    results = matcher.match(test_image)
    
    print("匹配结果:")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['image_path']} (距离: {result['distance']:.4f})")
