import tkinter as tk
import tkinter.messagebox as messagebox
import platform
window = tk.Tk()
window.title('Swan - Default Mode')
window.geometry('800x500')

menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# file menu
# file_menu = tk.Menu(menu_bar, tearoff=0)
# menu_bar.add_cascade(label='文件', menu=file_menu)
# file_menu.add_command(label='打开 (Open)')
# file_menu.add_separator()
# file_menu.add_command(label='关闭 (Close)')

# setting menu
setting_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='设置', menu=setting_menu)
setting_menu.add_command(label='程序设置 (Ctrl + E)')
setting_menu.add_command(label='账号设置 (Ctrl + R)')


def show_about():
    
    message = f"""
    Swan (天鹅)
    为了完成这该死的论文开发的程序，能够方便的爬取网络文本。
    作者: Elias
    版本号: 1.0.0
    操作系统: %s
    Python版本: %s (%s)
    编译日期: 2024.11.16
    """ % (platform.platform(), platform.python_version(), platform.python_compiler())
    messagebox.showinfo(title='Swan', message=message)

# about menu
menu_bar.add_command(label='关于', command=show_about)

# run
window.mainloop()