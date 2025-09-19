import os
import re
import requests
from pathlib import Path
import time
import random

def extract_info_from_filename(filename):
    """
    从文件名中提取编号和字母串
    例如: "12_0_106_x_y_donjiha.png" -> (12, "donjiha")
    """
    # 移除文件扩展名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 使用正则表达式匹配文件名格式
    # 匹配格式: 数字_数字_数字_x_y_字母串
    pattern = r'^(\d+)_\d+_\d+_x_y_(.+)$'
    match = re.match(pattern, name_without_ext)
    
    if match:
        number = int(match.group(1))  # 第一个数字作为编号
        letters = match.group(2)      # 最后的字母串
        return number, letters
    else:
        # 尝试匹配其他格式，如 "0_106_1_1_mergen.png"
        pattern2 = r'^(\d+)_\d+_\d+_\d+_(.+)$'
        match2 = re.match(pattern2, name_without_ext)
        if match2:
            number = int(match2.group(1))
            letters = match2.group(2)
            return number, letters
        else:
            return None, None

def download_image_from_api(letters, max_retries=3):
    """
    从API下载图片，支持重试机制，模拟真实浏览器行为
    """
    url = f"http://anakv.anakv.com/msc.php?input={letters}&font=1wpc=5&fontsize=25&cspace=10&fcolor=Black&bcolor=White"
    
    # 模拟真实浏览器的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://anakv.anakv.com/',
    }
    
    # 创建会话对象，保持连接
    session = requests.Session()
    session.headers.update(headers)
    
    for attempt in range(max_retries):
        try:
            # 增加超时时间，并添加重试延迟
            if attempt > 0:
                print(f"  重试第 {attempt} 次...")
                time.sleep(3 * attempt)  # 递增延迟
            
            # 首先访问主页，建立会话
            if attempt == 0:
                try:
                    session.get('http://anakv.anakv.com/', timeout=30)
                    time.sleep(1)  # 短暂延迟
                except:
                    pass  # 忽略主页访问失败
            
            response = session.get(url, timeout=60)  # 增加超时时间到60秒
            response.raise_for_status()
            
            # 检查响应内容是否为图片
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type or len(response.content) > 1000:  # 图片通常大于1KB
                return response.content
            else:
                print(f"  响应内容不是图片: {content_type}")
                return None
            
        except requests.exceptions.Timeout:
            print(f"  请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print(f"下载图片失败: 多次超时")
                return None
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 504:
                print(f"  504网关超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    print(f"下载图片失败: 504网关超时")
                    return None
            elif e.response.status_code == 403:
                print(f"  403禁止访问 (尝试 {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    print(f"下载图片失败: 被服务器拒绝访问")
                    return None
            else:
                print(f"下载图片失败: HTTP错误 {e.response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"下载图片失败: {e}")
            return None
    
    return None

def process_page_folders():
    """
    处理所有以page_开头的文件夹
    """
    # 获取当前工作目录
    current_dir = Path.cwd()
    
    # 指定目标文件夹路径
    target_dir = current_dir /"满文对比工具"/"my_data"
    
    # 检查目标文件夹是否存在
    if not target_dir.exists():
        print(f"错误: 目标文件夹 {target_dir} 不存在")
        return
    
    # 查找所有以page_开头的文件夹
    page_folders = []
    for item in target_dir.iterdir():
        if item.is_dir() and item.name.startswith('page_'):
            page_folders.append(item)
    
    print(f"找到 {len(page_folders)} 个page_文件夹")
    
    # 创建输出目录
    output_dir = target_dir / "generated_images"
    output_dir.mkdir(exist_ok=True)
    
    total_processed = 0
    total_success = 0
    
    for page_folder in page_folders:
        print(f"\n处理文件夹: {page_folder.name}")
        
        # 为每个page文件夹创建对应的输出子文件夹
        page_output_dir = output_dir / page_folder.name
        page_output_dir.mkdir(exist_ok=True)
        print(f"创建输出子文件夹: {page_output_dir}")
        
        # 遍历文件夹中的所有PNG文件
        png_files = list(page_folder.glob("*.png"))
        
        for png_file in png_files:
            total_processed += 1
            filename = png_file.name
            
            # 提取编号和字母串
            number, letters = extract_info_from_filename(filename)
            
            if number is None or letters is None:
                print(f"跳过文件 {filename}: 无法解析文件名格式")
                continue
            
            print(f"处理: {filename} -> 编号: {number}, 字母: {letters}")
            
            # 检查文件是否已经存在（在对应的page子文件夹中）
            # 将编号转换为两位数格式（个位数前面补0）
            number_padded = f"{number:02d}"
            output_filename = f"{number_padded}_{letters}.png"
            output_path = page_output_dir / output_filename
            
            if output_path.exists():
                print(f"  文件已存在，跳过: {output_filename}")
                total_success += 1
                continue
            
            # 从API下载图片
            image_content = download_image_from_api(letters)
            
            if image_content:
                # 保存图片到对应的page子文件夹
                try:
                    with open(output_path, 'wb') as f:
                        f.write(image_content)
                    print(f"  保存成功: {page_folder.name}/{output_filename}")
                    total_success += 1
                except Exception as e:
                    print(f"  保存失败 {output_filename}: {e}")
            else:
                print(f"  下载失败: {letters}")
            
            # 添加随机延迟避免请求过于频繁
            # delay = random.uniform(2.0, 5.0)  # 随机延迟2-5秒
            # time.sleep(delay)
    
    print(f"\n处理完成!")
    print(f"总处理文件数: {total_processed}")
    print(f"成功下载数: {total_success}")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    print("开始处理图片文件...")
    process_page_folders()
