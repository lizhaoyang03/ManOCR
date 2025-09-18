import cv2
import os

png_dir = './data/png/'
png_files = [file for file in os.listdir(png_dir) if file.endswith('.png')]

j = 0
for i in range(1, len(png_files)+1):
    path = "./data/png/page_" + str(i) + ".png"
    print(f"正在切割第{i}面")

    # 读取图像
    image = cv2.imread(path)

    # 获取图像的高度和宽度
    height, width = image.shape[:2]

    # 定义要保留的图像区域的边界，每个版面切割为两张图像，分别设置两张图像的区域
    # 上边界
    top_boundary1 = 1250
    top_boundary2 = 1220
    # 下边界
    bottom_boundary1 = height - 780
    bottom_boundary2 = height - 780
    # 左右边界
    left_boundary1 = 1150
    right_boundary1 = int(width / 2 - 500)
    left_boundary2 = int(width / 2 + 490)
    right_boundary2 = width - 1150

    # 裁剪图像
    cropped_image1 = image[top_boundary1:bottom_boundary1, left_boundary1:right_boundary1]
    cropped_image2 = image[top_boundary2:bottom_boundary2, left_boundary2:right_boundary2]

    # 保存裁剪后的图像
    j = j + 1
    cv2.imwrite('./data/cropped_png/image_'+str(j)+'.png', cropped_image1)
    j = j + 1
    cv2.imwrite('./data/cropped_png/image_'+str(j)+'.png', cropped_image2)
