import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
import shutil
import re

class ImageCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片检查工具")
        self.root.geometry("1200x800")
        
        # 配置变量
        self.target_folder = "my_data"  # 可配置的目标文件夹名
        
        # 数据变量
        self.current_page = None
        self.current_image_index = 0
        self.image_files = []
        self.processed_dir = None
        
        # 创建界面
        self.create_widgets()
        
        # 初始化
        self.load_page_folders()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 页面选择区域
        page_frame = ttk.LabelFrame(main_frame, text="选择页面", padding="5")
        page_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(page_frame, text="页面:").grid(row=0, column=0, padx=(0, 5))
        self.page_var = tk.StringVar()
        self.page_combo = ttk.Combobox(page_frame, textvariable=self.page_var, state="readonly", width=20)
        self.page_combo.grid(row=0, column=1, padx=(0, 10))
        self.page_combo.bind('<<ComboboxSelected>>', self.on_page_selected)
        
        # 图片显示区域
        # 左侧：待检查图片
        left_frame = ttk.LabelFrame(main_frame, text="待检查图片", padding="5")
        left_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.left_canvas = tk.Canvas(left_frame, bg="white", width=500, height=400)
        self.left_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 右侧：正确图片
        right_frame = ttk.LabelFrame(main_frame, text="正确图片", padding="5")
        right_frame.grid(row=1, column=2, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.right_canvas = tk.Canvas(right_frame, bg="white", width=500, height=400)
        self.right_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 控制区域
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 输入框区域
        input_frame = ttk.Frame(control_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 正确与否
        ttk.Label(input_frame, text="正确与否:").grid(row=0, column=0, padx=(0, 5), pady=5)
        self.correct_var = tk.StringVar()
        self.correct_entry = ttk.Entry(input_frame, textvariable=self.correct_var, width=10)
        self.correct_entry.grid(row=0, column=1, padx=(0, 20), pady=5)
        
        # 列号
        ttk.Label(input_frame, text="列号:").grid(row=0, column=2, padx=(0, 5), pady=5)
        self.col_var = tk.StringVar()
        self.col_entry = ttk.Entry(input_frame, textvariable=self.col_var, width=10)
        self.col_entry.grid(row=0, column=3, padx=(0, 20), pady=5)
        
        # 行号
        ttk.Label(input_frame, text="行号:").grid(row=0, column=4, padx=(0, 5), pady=5)
        self.row_var = tk.StringVar()
        self.row_entry = ttk.Entry(input_frame, textvariable=self.row_var, width=10)
        self.row_entry.grid(row=0, column=5, padx=(0, 20), pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.confirm_btn = ttk.Button(button_frame, text="确认", command=self.confirm_action)
        self.confirm_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.remove_btn = ttk.Button(button_frame, text="移除", command=self.remove_action)
        self.remove_btn.grid(row=0, column=1, padx=(10, 0))
        
        # 状态信息
        self.status_var = tk.StringVar(value="请选择页面")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # 进度信息
        self.progress_var = tk.StringVar(value="")
        progress_label = ttk.Label(control_frame, textvariable=self.progress_var, foreground="green")
        progress_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
    def load_page_folders(self):
        """加载页面文件夹列表"""
        current_dir = Path.cwd()
        target_dir = current_dir /"满文对比工具"/self.target_folder
        
        if not target_dir.exists():
            messagebox.showerror("错误", f"目标文件夹 {target_dir} 不存在")
            return
        
        # 查找所有以page_开头的文件夹
        page_folders = []
        for item in target_dir.iterdir():
            if item.is_dir() and item.name.startswith('page_'):
                page_folders.append(item.name)
        
        if not page_folders:
            messagebox.showwarning("警告", "未找到任何page_文件夹")
            return
        
        # 更新下拉框
        self.page_combo['values'] = sorted(page_folders)
        if page_folders:
            self.page_combo.set(page_folders[0])
            self.on_page_selected()
    
    def on_page_selected(self, event=None):
        """页面选择事件"""
        self.current_page = self.page_var.get()
        if not self.current_page:
            return
        
        # 加载图片文件列表
        current_dir = Path.cwd()
        target_dir = current_dir /"满文对比工具"/ self.target_folder
        page_dir = target_dir / self.current_page
        
        if not page_dir.exists():
            messagebox.showerror("错误", f"页面文件夹 {page_dir} 不存在")
            return
        
        # 获取PNG文件列表
        self.image_files = list(page_dir.glob("*.png"))
        self.image_files.sort()
        
        # 创建处理后的文件夹
        self.processed_dir = target_dir / f"processed_{self.current_page}"
        self.processed_dir.mkdir(exist_ok=True)
        
        # 重置索引
        self.current_image_index = 0
        
        # 显示第一张图片
        if self.image_files:
            self.show_current_image()
        else:
            messagebox.showinfo("信息", f"页面 {self.current_page} 中没有找到PNG文件")
    
    def show_current_image(self):
        """显示当前图片"""
        if not self.image_files or self.current_image_index >= len(self.image_files):
            self.status_var.set("所有图片处理完成")
            return
        
        # 获取当前图片文件
        current_file = self.image_files[self.current_image_index]
        
        # 显示待检查图片
        self.display_image(current_file, self.left_canvas)
        
        # 尝试显示对应的正确图片
        self.show_correct_image(current_file)
        
        # 更新状态
        self.status_var.set(f"当前处理: {current_file.name}")
        self.progress_var.set(f"进度: {self.current_image_index + 1}/{len(self.image_files)}")
        
        # 解析文件名并填充输入框
        self.parse_filename(current_file.name)
    
    def show_correct_image(self, source_file):
        """显示对应的正确图片"""
        # 解析源文件名获取编号和字母
        number, letters = self.extract_info_from_filename(source_file.name)
        if number is None or letters is None:
            self.right_canvas.delete("all")
            self.right_canvas.create_text(250, 200, text="无法解析文件名", fill="red")
            return
        
        # 查找对应的正确图片
        current_dir = Path.cwd()
        target_dir = current_dir /"满文对比工具"/ self.target_folder
        generated_dir = target_dir / "generated_images" / self.current_page
        
        # 将编号转换为两位数格式（个位数前面补0）
        number_padded = f"{number:02d}"
        correct_image_path = generated_dir / f"{number_padded}_{letters}.png"
        
        if correct_image_path.exists():
            self.display_image(correct_image_path, self.right_canvas)
        else:
            self.right_canvas.delete("all")
            self.right_canvas.create_text(250, 200, text="未找到对应图片", fill="orange")
    
    def display_image(self, image_path, canvas):
        """在画布上显示图片"""
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 计算缩放比例
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1:  # 画布还未初始化
                canvas_width, canvas_height = 500, 400
            
            # 计算缩放比例
            img_width, img_height = image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
            
            # 缩放图片
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 清空画布并显示图片
            canvas.delete("all")
            canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor="center")
            
            # 保持引用防止垃圾回收
            canvas.image = photo
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(250, 200, text=f"图片加载失败: {e}", fill="red")
    
    def extract_info_from_filename(self, filename):
        """从文件名中提取编号和字母串"""
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
    
    def parse_filename(self, filename):
        """解析文件名并填充输入框"""
        # 移除文件扩展名
        name_without_ext = os.path.splitext(filename)[0]
        
        # 尝试匹配格式: 数字_数字_数字_x_y_字母串
        pattern = r'^(\d+)_(\d+)_(\d+)_x_y_(.+)$'
        match = re.match(pattern, name_without_ext)
        
        if match:
            # 填充输入框
            self.correct_var.set(match.group(2))  # 第二个数字
            self.col_var.set(match.group(3))      # 第三个数字
            self.row_var.set("")                  # 行号留空
        else:
            # 尝试匹配其他格式
            pattern2 = r'^(\d+)_(\d+)_(\d+)_(\d+)_(.+)$'
            match2 = re.match(pattern2, name_without_ext)
            if match2:
                self.correct_var.set(match2.group(2))  # 第二个数字
                self.col_var.set(match2.group(3))      # 第三个数字
                self.row_var.set(match2.group(4))      # 第四个数字
            else:
                # 清空输入框
                self.correct_var.set("")
                self.col_var.set("")
                self.row_var.set("")
    
    def confirm_action(self):
        """确认按钮动作"""
        if not self.image_files or self.current_image_index >= len(self.image_files):
            return
        
        # 获取当前文件
        current_file = self.image_files[self.current_image_index]
        
        # 获取输入值
        correct = self.correct_var.get().strip()
        col = self.col_var.get().strip()
        row = self.row_var.get().strip()
        
        # 验证输入
        if not correct or not col:
            messagebox.showwarning("警告", "请填写正确与否和列号")
            return
        
        # 解析原文件名
        number, letters = self.extract_info_from_filename(current_file.name)
        if number is None or letters is None:
            messagebox.showerror("错误", "无法解析原文件名")
            return
        
        # 构建新文件名（删除最前面的序号）
        if row:
            new_filename = f"{correct}_{col}_{row}_{letters}.png"
        else:
            new_filename = f"{correct}_{col}_x_y_{letters}.png"
        
        # 复制文件到处理后的文件夹
        new_file_path = self.processed_dir / new_filename
        try:
            shutil.copy2(current_file, new_file_path)
            messagebox.showinfo("成功", f"文件已保存为: {new_filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
            return
        
        # 移动到下一张图片
        self.next_image()
    
    def remove_action(self):
        """移除按钮动作"""
        # 直接移动到下一张图片，不保存文件
        self.next_image()
    
    def next_image(self):
        """移动到下一张图片"""
        self.current_image_index += 1
        if self.current_image_index < len(self.image_files):
            self.show_current_image()
        else:
            # 所有图片处理完成
            self.status_var.set("所有图片处理完成")
            self.progress_var.set(f"进度: {len(self.image_files)}/{len(self.image_files)}")
            self.left_canvas.delete("all")
            self.right_canvas.delete("all")
            self.left_canvas.create_text(250, 200, text="处理完成", fill="green", font=("Arial", 20))
            self.right_canvas.create_text(250, 200, text="处理完成", fill="green", font=("Arial", 20))
            
            # 显示完成消息
            messagebox.showinfo("完成", f"页面 {self.current_page} 的所有图片处理完成！\n处理后的文件保存在: {self.processed_dir}")
    
    def set_target_folder(self, folder_name):
        """设置目标文件夹名称"""
        self.target_folder = folder_name
        # 重新加载页面文件夹
        self.load_page_folders()

def main():
    root = tk.Tk()
    app = ImageCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 