@echo off

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 运行爬虫
echo 运行爬虫爬取球衫堂数据...
python crawler/kitstown_spider.py

REM 启动Web服务
echo 启动Web服务...
python app.py
