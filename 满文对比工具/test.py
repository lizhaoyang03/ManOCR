import os
import re

def rename_images_by_txt(base_dir):
    """
    根据项目根目录下的page_x.txt文件内容，重命名对应page_x文件夹中的图片。

    Args:
        base_dir (str): 项目的根目录路径。
    """
    # 遍历根目录下的所有文件和文件夹
    for entry in os.listdir(base_dir):
        # 匹配所有 page_x.txt 文件
        if re.match(r'page_(\d+)\.txt', entry):
            page_number = re.match(r'page_(\d+)\.txt', entry).group(1)

            txt_path = os.path.join(base_dir, entry)
            image_folder_path = os.path.join(base_dir, f'page_{page_number}')

            # 确保对应的图片文件夹存在
            if not os.path.exists(image_folder_path):
                print(f"警告: 文件夹 '{image_folder_path}' 不存在，跳过处理 page_{page_number}.txt。")
                continue

            print(f"正在处理页码为 {page_number} 的文件...")

            recognition_results = {}
            try:
                # 读取txt文件内容，存储编号和识别结果
                with open(txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # 提取页码、编号和识别结果
                        parts = line.strip().split(',')
                        if len(parts) == 3:
                            number = parts[1].split('：')[1].strip()
                            result = parts[2].split('：')[1].strip()
                            recognition_results[number] = result
            except FileNotFoundError:
                print(f"错误: 找不到文件 '{txt_path}'。")
                continue

            # 遍历图片文件夹，重命名图片
            for image_file in os.listdir(image_folder_path):
                # 检查文件名是否为纯数字加.png，例如 '1.png'
                if re.match(r'(\d+)\.png', image_file):
                    file_number = re.match(r'(\d+)\.png', image_file).group(1)

                    if file_number in recognition_results:
                        transcription = recognition_results[file_number]

                        # 构建新的文件名：a_0_c_x_y_b.png
                        # a是编号（补0），c是页码，b是识别结果，x和y是占位符
                        # 将编号转换为两位数格式（个位数前面补0）
                        file_number_padded = f"{int(file_number):02d}"
                        new_name = f"{file_number_padded}_0_{page_number}_x_y_{transcription}.png"

                        old_path = os.path.join(image_folder_path, image_file)
                        new_path = os.path.join(image_folder_path, new_name)

                        # 重命名文件
                        try:
                            os.rename(old_path, new_path)
                            print(f"已将 '{old_path}' 重命名为 '{new_path}'")
                        except FileExistsError:
                            print(f"重命名文件 '{old_path}' 时出错: 目标文件名 '{new_name}' 已存在。")
                        except Exception as e:
                            print(f"重命名文件 '{old_path}' 时出错: {e}")
                    else:
                        print(f"警告: 找不到编号为 '{file_number}' 的图片在txt文件中的对应识别结果。")

# 使用示例
# 请根据你的实际路径修改
#project_root = 'my_data/'

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 基于脚本目录构建数据目录路径
project_root = os.path.join(script_dir, 'my_data')

rename_images_by_txt(project_root)