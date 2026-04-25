import requests
import time
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText

# 配置参数
CHECK_INTERVAL = 300  # 检查间隔（秒）
LOG_FILE = "url_monitor.log"

# 卡密页面的初始URL
initial_urls = [
    "http://120.48.37.155/wap?key=984VV4",
    "http://118.193.34.26/wap?key=MKYPO8"
]

# 配置邮件通知（可选）
EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_password",
    "receiver_email": "your_email@gmail.com"
}

# 日志记录函数
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

# 发送邮件通知
def send_email(subject, body):
    if not EMAIL_CONFIG["enabled"]:
        return
    
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_CONFIG["sender_email"]
        msg["To"] = EMAIL_CONFIG["receiver_email"]
        
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        server.send_message(msg)
        server.quit()
        log_message("邮件通知已发送")
    except Exception as e:
        log_message(f"发送邮件失败: {e}")

# 解析卡密信息
def parse_camiy_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    
    # 查找手机号
    phone_pattern = re.compile(r"手机号(\d{11})")
    phone_match = phone_pattern.search(text)
    phone = phone_match.group(1) if phone_match else "未找到"
    
    # 查找验证码
    code_pattern = re.compile(r"验证码(\d{6})")
    code_match = code_pattern.search(text)
    code = code_match.group(1) if code_match else "未找到"
    
    return {
        "phone": phone,
        "code": code,
        "has_camiy": phone != "未找到" and code != "未找到"
    }

# 检查URL是否有效并获取卡密
def check_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        camiy_info = parse_camiy_info(response.text)
        
        if camiy_info["has_camiy"]:
            log_message(f"URL {url} 有效，卡密信息: 手机号={camiy_info['phone']}, 验证码={camiy_info['code']}")
            return True, camiy_info, response
        else:
            log_message(f"URL {url} 访问成功，但未找到卡密信息")
            return False, camiy_info, response
            
    except Exception as e:
        log_message(f"检查URL {url} 失败: {e}")
        return False, None, None

# 尝试找到稳定的URL模式
def find_stable_url_pattern(known_urls):
    log_message("尝试分析URL模式...")
    
    # 分析已知URL的结构
    url_parts = []
    for url in known_urls:
        if not url.startswith("http"):
            continue
        
        parts = url.split("/")
        if len(parts) >= 3:
            domain = parts[2]
            path = "/".join(parts[3:])
            url_parts.append((domain, path))
    
    if not url_parts:
        return None
    
    # 检查是否有共同的路径模式
    paths = [path for _, path in url_parts]
    if all(path == paths[0] for path in paths):
        log_message(f"发现共同路径模式: {paths[0]}")
        return paths[0]
    
    return None

# 主监控函数
def monitor_urls():
    log_message("=== 卡密页面监控程序启动 ===")
    
    # 分析已知URL模式
    stable_path = find_stable_url_pattern(initial_urls)
    
    # 监控循环
    while True:
        # 检查初始URL
        for url in initial_urls:
            success, camiy_info, response = check_url(url)
            
            if success:
                # 发送卡密信息通知
                send_email(
                    "卡密信息更新",
                    f"找到新的卡密信息:\n手机号: {camiy_info['phone']}\n验证码: {camiy_info['code']}\n来源URL: {url}"
                )
        
        # 如果发现稳定路径，尝试探索其他可能的域名
        if stable_path:
            # 这里可以添加自定义的域名列表或自动发现逻辑
            # 示例：尝试常见的IP范围
            test_domains = [
                "120.48.37.155",
                "118.193.34.26",
                # 可以添加更多可能的域名或IP
            ]
            
            for domain in test_domains:
                test_url = f"http://{domain}/{stable_path}"
                if test_url not in initial_urls:
                    success, camiy_info, response = check_url(test_url)
                    if success:
                        initial_urls.append(test_url)
        
        # 等待下一次检查
        log_message(f"等待 {CHECK_INTERVAL} 秒后进行下一次检查...")
        time.sleep(CHECK_INTERVAL)

# 手动检查函数
def manual_check():
    log_message("=== 手动检查卡密信息 ===")
    
    for url in initial_urls:
        success, camiy_info, response = check_url(url)
        if success:
            print(f"\n找到卡密信息：")
            print(f"URL: {url}")
            print(f"手机号: {camiy_info['phone']}")
            print(f"验证码: {camiy_info['code']}")

# 主程序入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_check()
    else:
        monitor_urls()