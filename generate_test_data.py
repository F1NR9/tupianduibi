import cv2
import numpy as np
import os
import json

# 创建测试数据
def generate_test_data():
    # 球队列表
    teams = ["巴塞罗那", "皇家马德里", "曼联", "利物浦", "拜仁慕尼黑"]
    
    # 球衣类型
    categories = ["主场", "客场", "第三球衣"]
    
    # 年份
    years = ["2022-23", "2023-24", "2024-25"]
    
    # 颜色方案
    color_schemes = [
        [(0, 0, 255), (255, 255, 255)],  # 红蓝
        [(255, 255, 255), (255, 0, 0)],  # 白红
        [(255, 0, 0), (255, 255, 255)],  # 红白
        [(0, 100, 0), (255, 255, 255)],  # 绿白
        [(0, 0, 0), (255, 255, 255)]     # 黑白
    ]
    
    # 创建目录
    image_dir = os.path.join(os.getcwd(), 'data', 'images')
    meta_dir = os.path.join(os.getcwd(), 'data', 'metadata')
    
    # 生成测试数据
    for team in teams:
        for category in categories:
            for year in years:
                # 选择颜色方案
                color_idx = (teams.index(team) * len(categories) + categories.index(category)) % len(color_schemes)
                color1, color2 = color_schemes[color_idx]
                
                # 生成图片
                for i in range(2):  # 每个款式生成2张图片
                    # 创建图片
                    img = np.zeros((512, 512, 3), dtype=np.uint8)
                    
                    # 绘制条纹
                    if i == 0:
                        # 水平条纹
                        for j in range(0, 512, 64):
                            if j // 64 % 2 == 0:
                                img[j:j+64, :] = color1
                            else:
                                img[j:j+64, :] = color2
                    else:
                        # 垂直条纹
                        for j in range(0, 512, 64):
                            if j // 64 % 2 == 0:
                                img[:, j:j+64] = color1
                            else:
                                img[:, j:j+64] = color2
                    
                    # 添加队徽（简单圆形）
                    cv2.circle(img, (256, 150), 50, (255, 255, 255), -1)
                    cv2.circle(img, (256, 150), 40, color1, -1)
                    
                    # 保存图片
                    safe_team = team.replace('/', '_').replace('\\', '_')
                    safe_category = category.replace('/', '_').replace('\\', '_')
                    image_name = f"{safe_team}_{year}_{safe_category}_{i}.jpg"
                    image_path = os.path.join(image_dir, image_name)
                    cv2.imwrite(image_path, img)
                    print(f"生成图片: {image_path}")
                    
                    # 生成元数据
                    metadata = {
                        'team_name': team,
                        'category': category,
                        'year': year,
                        'detail_link': f"https://www.kitstown.com/team/{team}/{year}/{category}",
                        'image_links': [f"/images/{image_name}"]
                    }
                    
                    # 保存元数据
                    meta_file = os.path.join(meta_dir, f"{safe_team}_{year}_{safe_category}.json")
                    with open(meta_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    print(f"生成元数据: {meta_file}")

if __name__ == "__main__":
    generate_test_data()
