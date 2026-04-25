import requests
import time
from bs4 import BeautifulSoup
import re

# 定义要分析的URL
test_urls = [
    "http://120.48.37.155/wap?key=984VV4",
    "http://118.193.34.26/wap?key=MKYPO8"
]

# 分析URL的函数
def analyze_url(url):
    print(f"\n=== 分析URL: {url} ===")
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        
        # 发送请求并获取响应
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 打印响应信息
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"Cookie: {response.cookies.get_dict()}")
        
        # 分析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"\n页面标题: {soup.title.string if soup.title else '无标题'}")
        
        # 查找卡密相关内容
        print("\n页面主要内容:")
        print(soup.get_text(separator='\n', strip=True))
        
        # 检查是否有重定向
        if response.history:
            print(f"\n重定向历史:")
            for resp in response.history:
                print(f"  - {resp.status_code}: {resp.url}")
            print(f"  - 最终URL: {response.url}")
        
        # 查找可能的API或链接
        print("\n页面中的链接:")
        links = soup.find_all('a', href=True)
        for link in links:
            print(f"  - {link.text.strip()}: {link['href']}")
        
        # 查找可能的JavaScript代码
        print("\n页面中的JavaScript:")
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找可能包含URL或密钥的JavaScript代码
                js_content = script.string
                url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
                key_pattern = re.compile(r'key=([a-zA-Z0-9]+)')
                
                urls_in_js = url_pattern.findall(js_content)
                keys_in_js = key_pattern.findall(js_content)
                
                if urls_in_js:
                    print(f"  发现URL: {urls_in_js}")
                if keys_in_js:
                    print(f"  发现密钥: {keys_in_js}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 主函数
if __name__ == "__main__":
    print("开始分析卡密页面URL...")
    
    for url in test_urls:
        response = analyze_url(url)
        
        if response:
            # 尝试检查是否有稳定的域名或API
            domain = url.split('/')[2]
            path = '/'.join(url.split('/')[3:])
            
            print(f"\nURL结构分析:")
            print(f"  域名: {domain}")
            print(f"  路径: {path}")
            
            # 尝试直接访问域名根目录
            root_url = f"http://{domain}/"
            print(f"\n尝试访问根目录: {root_url}")
            try:
                root_response = requests.get(root_url, timeout=5)
                print(f"  状态码: {root_response.status_code}")
                print(f"  根目录内容: {root_response.text[:200]}...")
            except Exception as e:
                print(f"  访问错误: {e}")
    
    print("\n分析完成。根据分析结果，您可以:")
    print("1. 检查是否有稳定的主域名或API入口")
    print("2. 监控URL变化规律，定时更新抓取目标")
    print("3. 分析页面中的JavaScript，寻找动态生成URL的逻辑")
    print("4. 考虑是否有其他方式获取卡密信息（如官方API）")