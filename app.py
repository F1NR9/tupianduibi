from flask import Flask, request, render_template, send_file
import os
import tempfile
import threading
from matcher import Matcher

print("开始初始化应用...")

app = Flask(__name__)

print("初始化匹配器...")
# 初始化匹配器
matcher = Matcher()

# 标志变量，表示索引是否构建完成
index_built = False

print("定义路由...")

@app.route('/')
def index():
    print("访问首页")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    print("接收上传文件")
    if 'file' not in request.files:
        print("没有文件上传")
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        print("没有选择文件")
        return "No file selected", 400
    
    # 检查索引是否构建完成
    if not index_built:
        print("索引尚未构建完成，请稍后再试")
        return "索引尚未构建完成，请稍后再试", 503
    
    # 保存上传的文件
    print(f"保存文件: {file.filename}")
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp:
        file.save(temp)
        temp_path = temp.name
    
    # 匹配图片
    print(f"开始匹配: {temp_path}")
    results = matcher.match(temp_path, top_k=5)
    
    # 删除临时文件
    os.unlink(temp_path)
    print(f"删除临时文件: {temp_path}")
    
    # 整理结果
    matches = []
    for result in results:
        # 提取图片信息
        image_path = result['image_path']
        distance = result['distance']
        
        # 生成图片相对路径（只包含文件名）
        image_filename = os.path.basename(image_path)
        
        matches.append({
            'image_url': f'/images/{image_filename}',
            'image_name': image_filename,
            'distance': distance
        })
    
    print(f"匹配完成，找到 {len(matches)} 个结果")
    return render_template('results.html', matches=matches)

@app.route('/images/<path:filename>')
def serve_image(filename):
    print(f"提供图片: {filename}")
    # 确保路径正确
    image_path = os.path.join('data', 'images', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        print(f"图片不存在: {image_path}")
        return "Image not found", 404

def build_index():
    """在后台线程中构建索引"""
    global index_built
    print("开始构建索引...")
    # 构建索引
    image_dir = os.path.join(os.getcwd(), 'data', 'images')
    print(f"图片目录: {image_dir}")
    if os.path.exists(image_dir):
        print(f"目录存在，开始构建索引")
        matcher.build_index(image_dir)
        index_built = True
        print("索引构建完成")
    else:
        print(f"目录不存在: {image_dir}")

if __name__ == '__main__':
    print("创建templates目录...")
    # 创建templates目录
    templates_dir = os.path.join(os.getcwd(), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    print("创建index.html模板...")
    # 创建index.html模板
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>球衣款式匹配系统</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0;
            padding: 10px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .upload-form {
            margin: 20px 0;
            padding: 20px;
            border: 2px dashed #ddd;
            border-radius: 10px;
            text-align: center;
        }
        input[type="file"] {
            margin: 15px 0;
            width: 100%;
            padding: 10px;
            font-size: 16px;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        .status {
            text-align: center;
            margin: 15px 0;
            padding: 15px;
            background-color: #f0f0f0;
            border-radius: 8px;
            font-size: 16px;
        }
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 20px;
            }
            .upload-form {
                padding: 15px;
            }
            input[type="submit"] {
                padding: 12px 20px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>球衣款式匹配系统</h1>
        <div class="status" id="status">系统初始化中，请稍候...</div>
        <div class="upload-form">
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label for="file" style="font-size: 16px; font-weight: bold;">上传球衣图片：</label>
                <input type="file" id="file" name="file" accept="image/*" required>
                <input type="submit" value="开始匹配">
            </form>
        </div>
    </div>
    <script>
        // 定期检查系统状态
        setInterval(function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ready') {
                        document.getElementById('status').textContent = '系统已就绪，可以上传图片';
                        document.getElementById('status').style.backgroundColor = '#d4edda';
                        document.getElementById('status').style.color = '#155724';
                    }
                })
                .catch(error => console.error('Error:', error));
        }, 2000);
    </script>
</body>
</html>
''')
    
    print("创建results.html模板...")
    # 创建results.html模板
    with open(os.path.join(templates_dir, 'results.html'), 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>匹配结果</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0;
            padding: 10px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .matches {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .match-item {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            background-color: #f9f9f9;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .match-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .match-item img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .image-name {
            margin-top: 10px;
            font-size: 14px;
            color: #333;
            word-wrap: break-word;
            min-height: 40px;
        }
        .distance {
            margin-top: 8px;
            font-size: 16px;
            font-weight: bold;
            color: #4CAF50;
        }
        .back-link {
            display: block;
            text-align: center;
            margin: 25px 0;
            padding: 12px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .back-link:hover {
            background-color: #45a049;
        }
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 20px;
            }
            .matches {
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 15px;
            }
            .match-item {
                padding: 10px;
            }
            .image-name {
                font-size: 12px;
                min-height: 30px;
            }
            .distance {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>匹配结果</h1>
        <div class="matches">
            {% for match in matches %}
            <div class="match-item">
                <img src="{{ match.image_url }}" alt="匹配结果">
                <div class="image-name">{{ match.image_name }}</div>
                <div class="distance">相似度: {{ (1 - match.distance) * 100 | round(2) }}%</div>
            </div>
            {% endfor %}
        </div>
        <a href="/" class="back-link">返回上传页面</a>
    </div>
</body>
</html>
''')
    
    # 添加状态检查路由
    @app.route('/status')
    def status():
        return {'status': 'ready' if index_built else 'initializing'}
    
    # 在后台线程中构建索引
    print("启动后台线程构建索引...")
    index_thread = threading.Thread(target=build_index)
    index_thread.daemon = True
    index_thread.start()
    
    print("启动Flask服务...")
    app.run(debug=True)
