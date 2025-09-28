# 2024/4/21 21:06
import cv2

# 读取图像
image_name = 'image_2_part_1'
image = cv2.imread('./cropped_parts/' + image_name + '.png')
image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

# 创建窗口并设置大小
image = cv2.resize(image, None, fx=0.56, fy=0.56)
backup_image = image.copy()  # 创建备份图像

# 显示图像
cv2.imshow('Select Rectangles', backup_image)

# 定义变量保存用户选择的矩形框列表
rectangles = []
drawing = False


# 回调函数，在窗口上绘制矩形
def draw_rectangle(event, x, y, flags, param):
    global rectangles, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        # 开始绘制矩形
        rectangles.append((x, y))
        drawing = True

    elif event == cv2.EVENT_LBUTTONUP:
        # 完成矩形绘制
        rectangles.append((x, y))
        drawing = False

        # 绘制矩形框（仅在备份图像上绘制）
        cv2.rectangle(backup_image, rectangles[-2], rectangles[-1], (0, 255, 0), 2)
        cv2.imshow('Select Rectangles', backup_image)


# 设置鼠标回调函数
cv2.setMouseCallback('Select Rectangles', draw_rectangle)

# 等待 ESC 键按下退出
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

# 保存矩形框为图片
for i in range(0, len(rectangles), 2):
    x1, y1 = rectangles[i]
    x2, y2 = rectangles[i + 1]
    cropped_image = image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
    cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite('./cropped_words/'+image_name+f'_word_{i // 2}.png', cropped_image)
    print(f'Cropped word {i // 2 + 1} saved as "cropped_word_{i // 2}.png"')

cv2.destroyAllWindows()
