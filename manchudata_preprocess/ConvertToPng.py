# 2024/3/28 15:11
import fitz  # PyMuPDF


def save_page_as_image(page, page_number, image_path, scale):
    # 获取页面的像素尺寸
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))

    # 保存为PNG文件
    pix.save(image_path)

    print(f"Page {page_number} saved as {image_path}")


# 打开PDF文件
pdf_path = "./data/merged.pdf"
pdf_document = fitz.open(pdf_path)

scale = 4

# 遍历每一页，将其转换为图像
for page_number in range(len(pdf_document)):
    page = pdf_document.load_page(page_number)

    # 保存为PNG文件
    image_path = f"./data/png/page_{page_number + 1}.png"
    save_page_as_image(page, page_number+1, image_path, scale)

# 关闭PDF文件
pdf_document.close()

print("PDF转换为图片完成")
