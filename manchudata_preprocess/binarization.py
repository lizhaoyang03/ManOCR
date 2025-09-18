import cv2
import os
import time

time_start = time.time()

cropped_dir = "./data/cropped_parts/"
path_last = './data/bin_png/'
# path_gray = './data/gray/'

cropped_files = [file for file in os.listdir(cropped_dir) if file.endswith('.png')]

for i in range(len(cropped_files)):
    print(f"正在二值化第{i}张图像")
    img = cv2.imread(os.path.join(cropped_dir, cropped_files[i]))

    # 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite(os.path.join(path_gray, cropped_files[i]), gray)

    # 二值化
    r, b = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imwrite(os.path.join(path_last, cropped_files[i]), b)

time_end = time.time()
print('totally cost', time_end - time_start, 'seconds')

