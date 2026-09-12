import time
import tkinter as tk
import os
import zipfile
import fitz
import xml.etree.ElementTree as ET
import threading
from tkinter.ttk import Combobox
from tkinter import ttk, messagebox, filedialog, IntVar

import pyautogui
from docx import Document
from pypdf import PdfReader



DEFAULT_FONT="consolas"
FONT_SIZE=15
SEMI_FONT_SIZE=10
ENTRY_WIDTH=4
BUTTON_WIDTH=10
MAX_LENGTH=1000
DEFAULT_WIDTH=100
DEFAULT_HEIGHT=10
FILE_READ_LIMIT=1000
COUNT_DOWN_MAX=3600
COUNT_DOWN_MIN=3
COUNT_DOWN_FONT_SIZE=30
COUNT_DOWN_WIN_REMAIN_TIME=3
TYPING_GAP_MIN=0.01
TYPING_GAP_MAX=1
content=""



def setup_window():

    def place_window_at_centre(window):
        window.update_idletasks()
        scr_half_height = window.maxsize()[1] // 2
        scr_half_width = window.maxsize()[0] // 2
        win_height=height=window.winfo_height()
        win_width=width=window.winfo_width()
        win_half_height=win_height//2
        win_half_width=win_width//2
        x_coor = scr_half_width - win_half_width
        y_coor = scr_half_height - win_half_height
        window.geometry(f"{win_width}x{win_height}+{x_coor}+{y_coor}")

    window=tk.Tk()
    window.title("键盘输入模仿器")
    # window.geometry("400x50+800+350")
    window.resizable(False,False)

    upload_option_label=tk.Label(window,text="文本上传方式：",font=(DEFAULT_FONT, FONT_SIZE))
    upload_option_label.grid(row=1,column=1)
    upload_var=tk.StringVar()


    def on_modified(text,label):

        def show_count(event):
            content = text.get("1.0", "end-1c")
            if len(content)==MAX_LENGTH:
                label.config(text=f"目前字数:{MAX_LENGTH}/{MAX_LENGTH}",fg="red")
            else:
                label.config(text=f"目前字数:{len(content)}/{MAX_LENGTH}",fg="black")
            text.edit_modified(False)

        text.bind("<<Modified>>",show_count)

    def on_key(text):

        def key_monitor(event):
            current = text.get("1.0", "end-1c")
            if event.keysym in ("BackSpace", "Delete",
                                "Left", "Right", "Up", "Down",
                                "Home", "End", "Prior", "Next",
                                "Shift_L", "Shift_R", "Control_L", "Control_R"):
                return None
            elif len(current) >= MAX_LENGTH:
                return "break"
            return None

        text.bind("<Key>", key_monitor)

    def confirm_command(new_window,text):
        text_str = text.get("1.0", "end-1c")
        if len(text_str) == 0:
            messagebox.showwarning("错误", "未填写文本", parent=new_window)
        else:
            choice = messagebox.showinfo("选项", "是否确认提交", parent=new_window)
            if choice:
                global content
                content = text_str
                new_window.destroy()
                input_operating_window()


    def manual_input():
        new_window=tk.Toplevel(window)
        new_window.title("手动输入")
        new_window.resizable(False, False)

        remind_label=tk.Label(new_window,text="请输入文本：",font=(DEFAULT_FONT,FONT_SIZE))
        remind_label.grid(row=1,column=1)
        count_label=tk.Label(new_window,text="目前字数：0/1000",font=(DEFAULT_FONT,FONT_SIZE))
        count_label.grid(row=2,column=1)

        text_var=tk.StringVar()
        text=tk.Text(new_window,width=DEFAULT_WIDTH,height=DEFAULT_HEIGHT,)
        text.grid(row=1,column=2)

        on_key(text)
        on_modified(text,count_label)

        confirm_button=tk.Button(new_window,
                                 text="提交",
                                 width=BUTTON_WIDTH,
                                 font=(DEFAULT_FONT, FONT_SIZE),
                                 command=lambda:confirm_command(new_window,text))#确认提交
        confirm_button.grid(row=2,column=2)


    def open_file_explorer():

        new_window=tk.Toplevel(window)
        new_window.resizable(False, False)

        def read_particular_file():
            while True:
                path = filedialog.askopenfilename(title="请选择要打开的文件")
                if not path:
                    new_window.destroy()
                    return None
                file_extension=os.path.splitext(path)[1].lower()
                if file_extension in (".txt", ".md", ".log", ".py", ".csv"):
                    with open(path, "r", encoding="utf-8", errors="replace") as file:
                        return file.read(FILE_READ_LIMIT)


                elif file_extension == ".pdf":
                    try:

                        def read_pdf_limited_with_fitz(path, limit=None):
                            doc = fitz.open(path)
                            parts = []
                            total = 0
                            for page in doc:
                                text = page.get_text("text")
                                remaining = limit - total if limit else None
                                if remaining is not None and remaining <= 0:
                                    break
                                if remaining is not None and len(text) > remaining:
                                    parts.append(text[:remaining])
                                    break
                                parts.append(text)
                                total += len(text)
                            doc.close()
                            result = "\n".join(parts)
                            return result[:limit] if limit else result  # ← 统一截断

                        return read_pdf_limited_with_fitz(path, FILE_READ_LIMIT)

                    except Exception as e:
                        messagebox.showwarning("错误", f"读取 PDF 失败：{e}", parent=window)
                        return None

                elif file_extension==".docx":

                    def read_docx_text_from_xml(path, limit=None):
                        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        with zipfile.ZipFile(path) as docx_zip:
                            with docx_zip.open('word/document.xml') as xml_file:
                                context = ET.iterparse(xml_file, events=('start', 'end'))
                                _, root = next(context)  # 获取根元素

                                text_parts = []
                                total_len = 0

                                for event, elem in context:
                                    if event == 'end' and elem.tag.endswith('}t'):
                                        if elem.text:
                                            text_parts.append(elem.text)
                                            total_len += len(elem.text)
                                            if limit and total_len >= limit:
                                                break
                                        elem.clear()

                                full_text = ''.join(text_parts)
                                return full_text[:limit] if limit else full_text

                    return read_docx_text_from_xml(path,FILE_READ_LIMIT)


                else:
                    messagebox.showwarning("错误","不支持该格式文件",parent=new_window)
                    continue

        global content
        content=read_particular_file()

        showcase_label=tk.Label(new_window,font=(DEFAULT_FONT,FONT_SIZE))
        showcase_label.grid(row=2,column=1)
        remind_label=tk.Label(new_window,text="文本预览:\n(图片可能导致读取错误)",font=(DEFAULT_FONT,FONT_SIZE))
        remind_label.grid(row=1,column=1)
        showcase_text=tk.Text(new_window,width=DEFAULT_WIDTH,height=DEFAULT_HEIGHT,state="normal")
        showcase_text.grid(row=1,column=2)

        confirm_button=tk.Button(new_window,
                                 text="确认",
                                 width=BUTTON_WIDTH,
                                 font=(DEFAULT_FONT, FONT_SIZE),
                                 command=lambda:confirm_command(new_window,showcase_text))#确认提交
        confirm_button.grid(row=2,column=2)



        def showcase_file_content(text,content):
            text.delete("1.0","end")
            text.insert("1.0",content)

        on_key(showcase_text)
        on_modified(showcase_text,showcase_label)

        showcase_file_content(showcase_text,content)


    def input_operating_window():
        new_window=tk.Toplevel(window)
        new_window.resizable(False,False)
        new_window.title("输入操作窗口")

        countdown_duration=tk.IntVar(value=COUNT_DOWN_MIN)
        typing_gap=tk.IntVar(value=TYPING_GAP_MAX)
        countdown_label=tk.Label(new_window,text=f"倒计时时长（秒）：",font=(DEFAULT_FONT,FONT_SIZE))
        countdown_label.grid(row=1,column=1)
        countdown_entry=tk.Entry(new_window, textvariable=countdown_duration, width=ENTRY_WIDTH, font=(DEFAULT_FONT, FONT_SIZE) )
        countdown_entry.grid(row=1,column=2)
        typing_gap_label = tk.Label(new_window, text=f"输入速度（秒）：", font=(DEFAULT_FONT, FONT_SIZE))
        typing_gap_label.grid(row=2, column=1)
        typing_gap_entry = tk.Entry(new_window, textvariable=typing_gap, width=ENTRY_WIDTH,font=(DEFAULT_FONT, FONT_SIZE))
        typing_gap_entry.grid(row=2, column=2)

        remind_label=countdown_label=tk.Label(new_window,
                                              text=f"倒计时时长应为正整数\n"
                                                   f"不得超过{COUNT_DOWN_MAX}秒\n"
                                                   f"不少于{COUNT_DOWN_MIN}秒\n"
                                                   f"输入时间间隔应为正\n"
                                                   f"不大于{TYPING_GAP_MAX}秒\n"
                                                   f"不小于{TYPING_GAP_MIN}秒\n"
                                                   f"倒计时结束后将开始输出文本\n"
                                                   f"请确认后迅速选中指定的输入框",
                                              font=(DEFAULT_FONT,SEMI_FONT_SIZE))
        remind_label.grid(row=3,column=1)

        def check_duration_and_gap():
            if not isinstance(countdown_duration.get(),int):
                messagebox.showwarning("错误", "时长非正整数", parent=new_window)
            if typing_gap.get()<0:
                messagebox.showwarning("错误", "输入时间间隔非正数", parent=new_window)
            elif countdown_duration.get()>COUNT_DOWN_MAX:
                messagebox.showwarning("错误","时长超出限制",parent=new_window)
            elif countdown_duration.get()<COUNT_DOWN_MIN:
                messagebox.showwarning("错误","时长小于最小值",parent=new_window)
            elif typing_gap.get()>TYPING_GAP_MAX:
                messagebox.showwarning("错误","输入时间间隔超出限制",parent=new_window)
            elif typing_gap.get()<TYPING_GAP_MIN:
                messagebox.showwarning("错误","输入时间间隔小于最小值",parent=new_window)
            else:
                choice=messagebox.askyesno("设置成功","是否开始输出",parent=new_window)
                if choice:
                    new_window.destroy()
                else:
                    return


                def floating_countdown():
                    root = tk.Toplevel(window)
                    # root.overrideredirect(True)  # 去掉标题栏和边框
                    root.attributes("-topmost", True)  # 总在最前
                    root.attributes("-alpha", 0.85)  # 半透明
                    root.resizable(False,False)
                    sw = root.winfo_screenwidth()
                    sh = root.winfo_screenheight()
                    w, h = 200, 160
                    root.geometry(f"{w}x{h}+{sw - w - 20}+{sh - h - 60}")# 放到屏幕右下角

                    rest_time_label = tk.Label(root,
                                     text=f"剩余时间\n{countdown_duration.get()}s",
                                     font=(DEFAULT_FONT, COUNT_DOWN_FONT_SIZE, "bold"),
                                     fg="white", bg="black")
                    rest_time_label.pack(fill="both", expand=True)#占满窗口

                    seconds = countdown_duration.get()

                    def tick():
                        nonlocal seconds
                        if seconds > 1:
                            seconds-=1
                            rest_time_label.config(text=f"剩余时间\n{seconds}s")
                            root.after(1000, tick)
                        else:
                            rest_time_label.config(text="时间到")
                            root.after(3000,root.destroy)

                    root.after(1000, tick)

                floating_countdown()

                def new_thread():
                    time.sleep(countdown_duration.get())
                    pyautogui.write(content,interval=typing_gap.get())#开始输出文本
                    messagebox.showinfo("成功","文本输入完成",parent=window)

                t1=threading.Thread(target=new_thread,daemon=True)
                t1.start()

        confirm_button = tk.Button(new_window,
                                   text="确认",
                                   width=BUTTON_WIDTH,
                                   font=(DEFAULT_FONT, FONT_SIZE),
                                   command=check_duration_and_gap)  # 确认输出
        confirm_button.grid(row=3, column=2)



    button_1=tk.Button(window,text="手动输入",width=BUTTON_WIDTH,font=(DEFAULT_FONT, FONT_SIZE),command=manual_input)
    button_1.grid(row=1,column=2)
    button_2=tk.Button(window,text="选择文档",width=BUTTON_WIDTH,font=(DEFAULT_FONT, FONT_SIZE),command=open_file_explorer)
    button_2.grid(row=1,column=3)

    place_window_at_centre(window)#窗口居中
    window.mainloop()


def main():
    setup_window()

if __name__=="__main__":
    main()