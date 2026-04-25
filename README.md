# 球衣款式匹配系统

## 项目简介
该系统用于从客户提供的球衣图片中匹配球衫堂(Kitstown)上的对应款式，帮助服装抄版工作。

## 功能模块
1. **爬虫模块**：爬取球衫堂的球衣图片和相关信息
2. **特征提取模块**：提取图片的颜色、形状和纹理特征
3. **匹配模块**：比对客户图片与球衫堂图片的相似度
4. **Web界面**：提供用户上传图片和查看匹配结果的界面

## 技术栈
- Python 3.8+
- Scrapy (爬虫)
- OpenCV (图像处理)
- TensorFlow/PyTorch (特征提取)
- Flask (Web界面)

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
1. 运行爬虫爬取球衫堂数据：
   ```bash
   python crawler/kitstown_spider.py
   ```

2. 启动Web服务：
   ```bash
   python app.py
   ```

3. 在浏览器中访问 http://localhost:5000 上传客户图片进行匹配
