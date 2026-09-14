from tkinter import TclError

from package import *#导入包集合
import read_non_default_document_function as ndf#导入文档阅读函数

#读取配置文件
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

#常量配置
DEFAULT_FONT=config["default_font"]
FONT_SIZE=config["font_size"]
SEMI_FONT_SIZE=config["semi_font_size"]
ENTRY_WIDTH=config["entry_width"]
BUTTON_WIDTH=config["button_width"]
MAX_LENGTH=config["max_length"]
DEFAULT_WIDTH=config["default_width"]
DEFAULT_HEIGHT=config["default_height"]
FILE_READ_LIMIT=config["file_read_limit"]
COUNT_DOWN_MAX=config["count_down_max"]
COUNT_DOWN_MIN=config["count_down_min"]
COUNT_DOWN_FONT_SIZE=config["count_down_font_size"]
COUNT_DOWN_WIN_REMAIN_TIME=config["count_down_win_remain_time"]
TYPING_GAP_MIN=config["typing_gap_min"]
TYPING_GAP_MAX=config["typing_gap_max"]
TRANSPARENCY=config["transparency"]
content=""


class WindowManager:

    def setup_window(self):#窗口主体搭建函数

        # Tk以及Toplevel共用置中置顶函数
        def place_window_at_centre_front(window):
            window.attributes("-topmost", True)
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

        #主窗口初始化
        window=tk.Tk()
        window.title("键盘输入模仿器")
        # window.geometry("400x50+800+350")
        window.resizable(False,False)

        upload_option_label=tk.Label(window,text="文本上传方式：",font=(DEFAULT_FONT, FONT_SIZE))
        upload_option_label.grid(row=1,column=1)
        upload_var=tk.StringVar()


        #窗口监控函数，绑定text
        #on_modified监控text字数，改变字体颜色
        #on_key监控输入以及字数，忽略指定输入并控制内容长度
        #on_ctrl_v监控粘贴操作，禁止导致超出字数限制粘贴
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


        def on_ctrl_v(text):

            def paste_handler(event):
                try:
                    clipboard_text = event.widget.clipboard_get()
                except tk.TclError:
                    return "break"

                current_text = event.widget.get("1.0", "end-1c")
                # 当前已有多少字符
                current_length = len(current_text)
                # 还能输入多少
                remaining = MAX_LENGTH - current_length
                if remaining <= 0:
                    messagebox.showwarning("字数超限",
                                           f"当前文本已经达到 {MAX_LENGTH} 字限制",
                                           parent=event.widget.winfo_toplevel())
                    return "break"
                # 剪贴板内容超过剩余空间
                if len(clipboard_text) > remaining:
                    clipboard_text = clipboard_text[:remaining]
                    messagebox.showwarning(
                        "粘贴内容过长",
                        f"剪贴板内容过长，仅粘贴前 {remaining} 个字符。\n"
                        f"最大字数限制：{MAX_LENGTH}",
                        parent=event.widget.winfo_toplevel()
                    )
                event.widget.insert(tk.INSERT, clipboard_text)
                return "break"

            text.bind("<Control-v>", paste_handler)


        #任务完成窗口退出缓冲函数，检测输入是否为空，询问用户选择
        def confirm_command(new_window, text):
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



        def manual_input():#主窗口手动输入功能
            new_window=tk.Toplevel(window)#第二级手动输入窗口初始化
            new_window.title("手动输入")
            new_window.resizable(False, False)

            remind_label=tk.Label(new_window,text="请输入文本：",font=(DEFAULT_FONT,FONT_SIZE))#提示词与字数提示设置
            remind_label.grid(row=1,column=1)
            count_label=tk.Label(new_window,text="目前字数：0/1000",font=(DEFAULT_FONT,FONT_SIZE))#创建字数提示label
            count_label.grid(row=2,column=1)

            text_var=tk.StringVar()#输入框设置
            text=tk.Text(new_window,width=DEFAULT_WIDTH,height=DEFAULT_HEIGHT,)
            text.grid(row=1,column=2)
            text.focus_set()
            text.tag_add("sel", "1.0", "1.0")

            #监控函数绑定
            on_key(text)
            on_modified(text,count_label)#传入字数提示label
            on_ctrl_v(text)

            confirm_button=tk.Button(new_window,#确认提交按钮设置
                                     text="提交",
                                     width=BUTTON_WIDTH,
                                     font=(DEFAULT_FONT, FONT_SIZE),
                                     command=lambda:confirm_command(new_window,text))#确认提交函数绑定缓冲函数
            confirm_button.grid(row=2,column=2)

            place_window_at_centre_front(new_window)#第二级窗口置中置顶



        def open_file_explorer():#主窗口读取文档功能

            new_window=tk.Toplevel(window)#第二级文档读取窗口初始化
            new_window.resizable(False, False)


            def read_particular_file():#阅读文档格式判断分类以及读取操作函数
                while True:#保持错误操作后资源管理器开启
                    path = filedialog.askopenfilename(title="请选择要打开的文件")
                    if not path:
                        new_window.destroy()
                        return None
                    file_extension=os.path.splitext(path)[1].lower()
                    if file_extension in (".txt", ".md", ".log", ".py", ".csv"):#默认文档读取
                        with open(path, "r", encoding="utf-8", errors="replace") as file:
                            return file.read(FILE_READ_LIMIT)


                    #非默认文档阅读详见read_non_default_document_function.py
                    elif file_extension == ".pdf":#pdf读取
                        try:
                            ndf.read_pdf_limited_with_fitz(path, limit=None)

                            return ndf.read_pdf_limited_with_fitz(path, FILE_READ_LIMIT)

                        except Exception as e:
                            messagebox.showwarning("错误", f"读取 PDF 失败：{e}", parent=window)
                            return None

                    elif file_extension==".docx":#docx读取

                        ndf.read_docx_text_from_xml(path, limit=None)

                        return ndf.read_docx_text_from_xml(path,FILE_READ_LIMIT)

                    else:#排除不支持格式文件，进行下一轮循环
                        messagebox.showwarning("错误","不支持该格式文件",parent=new_window)
                        continue

            global content
            content=read_particular_file()#全局内容变量赋值

            showcase_label=tk.Label(new_window,font=(DEFAULT_FONT,FONT_SIZE))#字数提示label创建
            showcase_label.grid(row=2,column=1)
            remind_label=tk.Label(new_window,text="文本预览:\n(图片可能导致读取错误)",font=(DEFAULT_FONT,FONT_SIZE))#提示词
            remind_label.grid(row=1,column=1)
            showcase_text=tk.Text(new_window,width=DEFAULT_WIDTH,height=DEFAULT_HEIGHT,state="normal")#输入框
            showcase_text.grid(row=1,column=2)

            confirm_button=tk.Button(new_window,#确认按钮设置
                                     text="确认",
                                     width=BUTTON_WIDTH,
                                     font=(DEFAULT_FONT, FONT_SIZE),
                                     command=lambda:confirm_command(new_window,showcase_text))#确认提交
            confirm_button.grid(row=2,column=2)

            place_window_at_centre_front(new_window)#第二级窗口置中置顶



            #请空原有内容，展示新读取内容函数
            def showcase_file_content(text,content):
                text.delete("1.0","end")
                text.insert("1.0",content)

            #监控函数绑定
            on_key(showcase_text)
            on_modified(showcase_text,showcase_label)#传入字数提示label
            on_ctrl_v(showcase_text)

            showcase_file_content(showcase_text,content)#展示读取内容



        def input_operating_window():#最终输出设置窗口，两种输入功能共用
            new_window=tk.Toplevel(window)#第二级输出设置窗口初始化
            new_window.resizable(False,False)
            new_window.title("输入操作窗口")

            countdown_duration=tk.IntVar(value=COUNT_DOWN_MIN)#倒计时时长与输入时间间隔Var设置
            typing_gap=tk.DoubleVar(value=TYPING_GAP_MAX)
            countdown_label=tk.Label(new_window,text=f"倒计时时长（秒）：",font=(DEFAULT_FONT,FONT_SIZE))
            countdown_label.grid(row=1,column=1)
            countdown_entry=tk.Entry(new_window, textvariable=countdown_duration, width=ENTRY_WIDTH, font=(DEFAULT_FONT, FONT_SIZE) )
            countdown_entry.grid(row=1,column=2)
            typing_gap_label = tk.Label(new_window, text=f"输入时间间隔（秒）：", font=(DEFAULT_FONT, FONT_SIZE))
            typing_gap_label.grid(row=2, column=1)
            typing_gap_entry = tk.Entry(new_window, textvariable=typing_gap, width=ENTRY_WIDTH,font=(DEFAULT_FONT, FONT_SIZE))
            typing_gap_entry.grid(row=2, column=2)

            remind_label=countdown_label=tk.Label(new_window,#提示词设置
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

            def check_duration_and_gap():#倒计时时长与输入时间间隔Var检查

                def is_empty():#输入判空函数
                    try:
                        countdown_duration.get()
                        typing_gap.get()
                        return False
                    except tk.TclError :
                        return True

                #输入判断分类
                if is_empty():
                    messagebox.showwarning("错误","输入为空",parent=new_window)
                elif not isinstance(countdown_duration.get(),int):
                    messagebox.showwarning("错误", "时长非正整数", parent=new_window)
                elif typing_gap.get()<0:
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


                    def floating_countdown():#倒计时窗口
                        root = tk.Toplevel(window)
                        # root.overrideredirect(True)  # 去掉标题栏和边框
                        root.attributes("-topmost", True)  # 总在最前
                        root.attributes("-alpha", TRANSPARENCY)  # 半透明
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

                        def tick():#倒计时操作与检测函数
                            nonlocal seconds
                            if seconds > 1:
                                seconds-=1
                                rest_time_label.config(text=f"剩余时间\n{seconds}s")
                                root.after(1000, tick)
                            else:
                                rest_time_label.config(text="时间到")
                                root.after(COUNT_DOWN_WIN_REMAIN_TIME,root.destroy)

                        root.after(1000, tick)#进入定时执行

                    floating_countdown()#设置提交后开始倒计时

                    def new_thread():#文本输出独立进程执行
                        time.sleep(countdown_duration.get())
                        pyautogui.write(content,interval=typing_gap.get())#开始输出文本
                        messagebox.showinfo("成功","文本输入完成",parent=window)

                    t1=threading.Thread(target=new_thread,daemon=True)
                    t1.start()

            confirm_button = tk.Button(new_window,#输出设置窗口确定按钮设置
                                       text="确认",
                                       width=BUTTON_WIDTH,
                                       font=(DEFAULT_FONT, FONT_SIZE),
                                       command=check_duration_and_gap)  # 确认输出
            confirm_button.grid(row=3, column=2)

            place_window_at_centre_front(new_window)#第二级窗口置中置顶



        #主窗口功能选择按钮设置
        button_1=tk.Button(window,text="手动输入",width=BUTTON_WIDTH,font=(DEFAULT_FONT, FONT_SIZE),command=manual_input)
        button_1.grid(row=1,column=2)
        button_2=tk.Button(window,text="选择文档",width=BUTTON_WIDTH,font=(DEFAULT_FONT, FONT_SIZE),command=open_file_explorer)
        button_2.grid(row=1,column=3)

        place_window_at_centre_front(window)#主窗口居中置顶
        window.mainloop()#开始主窗口循环


def main():#程序入口
    solution=WindowManager()
    solution.setup_window()

if __name__=="__main__":
    main()