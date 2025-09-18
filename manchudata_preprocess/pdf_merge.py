# 2024/4/11 21:38
import PyPDF2
import os

# 指定PDF文件所在目录和合并后的文件名
pdf_dir = './data/pdf/'
output_pdf = './data/merged.pdf'

# 获取PDF文件列表
pdf_files = [file for file in os.listdir(pdf_dir) if file.endswith('.pdf')]

# 创建PdfFileMerger对象
merger = PyPDF2.PdfMerger()

# 逐个合并PDF文件
for pdf_file in pdf_files:
    with open(os.path.join(pdf_dir, pdf_file), 'rb') as file:
        merger.append(file)

# 合并后保存为新的PDF文件
with open(output_pdf, 'wb') as output_file:
    merger.write(output_file)
