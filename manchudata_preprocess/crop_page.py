# 2024/4/12 19:26
from PIL import Image
import os

png_dir = './data/cropped_png/'
png_files = [file for file in os.listdir(png_dir) if file.endswith('.png')]
for j in range(1, len(png_files)+1):
    # 打开图像文件
    print(f"正在切割第{j}面")
    image_path = "./data/cropped_png/image_" + str(j) + ".png"
    image = Image.open(image_path)

    # 获取图像的宽度和高度
    width, height = image.size

    # 计算每个部分的宽度
    part_width = width // 10

    # 切分图像并保存每个部分
    for i in range(10):
        left = i * part_width
        upper = 0
        right = (i + 1) * part_width
        lower = height
        # 裁剪图像的矩形区域
        cropped_image = image.crop((left, upper, right, lower))
        # 保存裁剪后的图像
        cropped_image.save(f'./data/cropped_parts/image_{j}_part_{i}.png')

