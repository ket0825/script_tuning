import tkinter.messagebox as msgbox
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
import asyncio
import os
from typing import List
import threading

from clova_studio.text_to_csv import text_to_csv 
from clova_studio.post_clova_text import async_main

root = Tk()
# resolution
# resol_width = 900
# resol_height = 700

root.title("쉼표 찍어주기 프로젝트")

# root.geometry(f"{resol_width}x{resol_height}+100+0")

# 파일 추가
def add_text_path():
    text_file_path = filedialog.askopenfilenames( # 여러 파일을 받게 해줄 수 있음.
                                        title="변환하려는 텍스트들을 선택하세요",
                                        filetypes=(("txt 파일", "*.txt"), ("모든 파일", "*.*")), 
                                        initialdir=r"C:\Users\82104\Python_workspace\script_tuning\comma\data" # 이후에 바꿀 예정.
                                        ) 
    existing_files = list_file.get(0, END)

    for file in text_file_path: # 튜플임.
        if file not in existing_files:
            list_file.insert(END, file)


def del_text_path():
    for index in reversed(list_file.curselection()): # 이렇게 하는 이유: reverse로 해야 for 문으로 삭제할 때 문제가 생기지 않음.
        list_file.delete(index)


def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때임.
        return
    
    txt_dest_path.delete(0, END)    # 기존 경로들 모두 삭제.
    txt_dest_path.insert(0, folder_selected)
    

def start_converting():
    warning_case_bool = False if combo_warning_case.get() == "아니오" else True

    if not list_file.get(0,END):
        msgbox.showerror("에러", "선택된 파일이 없습니다.")
        return
    
    if not txt_dest_path.get():
        msgbox.showerror("에러", "저장되는 경로를 설정해주세요.")
        return

    if combo_line_option.get() == "한 줄씩 변환":
        text_file_path = list(list_file.get(0,END))
        output_dirname = txt_dest_path.get()
        csv_filename_list = [output_dirname+filename[filename.rfind("/"):].replace(".txt", "") + "_확인요망.csv"  for filename in text_file_path]
        text_to_csv(text_file_path, csv_filename_list=csv_filename_list, ignore_warning_case=warning_case_bool) # 경로 설정하는 부분 필요함.
        msgbox.showinfo("변환 완료", "정상적으로 변환이 완료되었습니다.\n반드시 파일을 확인해주세요.")
    #TODO: chunk upload
    elif combo_line_option.get() == "여러 줄씩 변환 (이후 추가 예정)":
        # 현재는 training file chunk 변환만 존재함. 이후에 적용되면 금방 만듦.
        msgbox.showerror("에러", "아직 지원하지 않습니다.")
        pass


def get_file_kb_size(file_path_list:List[str]):
    """ 파일의 크기를 kb 단위로 반환 """
    sizes = 0
    for file_path in file_path_list:
        try:            
            size = os.path.getsize(file_path)
            sizes += size
        except OSError as e:
            print(f"Error: {e}")

    kb_size = sizes / (1024 * 1024)   
    return kb_size


def estimate_time(file_path_list):
    if list_file_csv:
        eta = 0
        for file_path in file_path_list:
            size = os.path.getsize(file_path)
            kb_size = size / 1024
            eta += 8.64 * kb_size
        return int(eta)
    


def start_timer(file_path_list):
    global remaining_time
    remaining_time = estimate_time(file_path_list)  # 예를 들어, 10초로 시작
    update_timer()


def update_timer():
    global remaining_time
    if remaining_time > 0:
        remaining_time -= 1
        timer_label.config(text=f"예상 남은 시간: {remaining_time}초")
        root.after(1000, update_timer)
    else:
        timer_label.config(text="작업 중...")


def check_async_task_complete():
    if future.done():
        msgbox.showinfo("변환 완료", "정상적으로 변환이 완료되었습니다.\n 파일을 확인해주세요.")
        timer_label.config(text="작업이 완료되었습니다!")
    else:
        root.after(1000, check_async_task_complete)  # 1000ms 후에 다시 확인


def start_async_task_comma():
    if not list_file_csv.get(0,END):
        msgbox.showerror("에러", "선택된 파일이 없습니다.")
        return
    
    if not txt_dest_path_tab2.get():
        msgbox.showerror("에러", "저장되는 경로를 설정해주세요.")
        return

    csv_file_paths = list(list_file_csv.get(0,END))
    output_dirname = txt_dest_path_tab2.get()
    output_txt_list = [output_dirname+filename[filename.rfind("/"):].replace(".csv", "") + "_처리완료.txt"  for filename in csv_file_paths]
    global future
    future = asyncio.run_coroutine_threadsafe(async_main(csv_file_paths, output_txt_list), loop)
    
    # 테스트용 async.
    # future = asyncio.run_coroutine_threadsafe(async_test(), loop) 
    start_timer(csv_file_paths)
    # 시간 업데이트.
    root.after(1000, check_async_task_complete)


def start_async_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
    

def add_csv_path():
    csv_file_path = filedialog.askopenfilenames( # 여러 파일을 받게 해줄 수 있음.
                                        title="변환하려는 텍스트들을 선택하세요",
                                        filetypes=(("csv 파일", "*.csv"), ("모든 파일", "*.*")), 
                                        initialdir=r"C:\Users\82104\Python_workspace\script_tuning\comma\data" # 이후에 바꿀 예정.
                                        ) 
    existing_files = list_file_csv.get(0, END)

    for file in csv_file_path: # 튜플임.
        if file not in existing_files:
            list_file_csv.insert(END, file)

    timer_label.config(text=f"예상 시간: {estimate_time(csv_file_path)}초")


def del_csv_path():
    for index in reversed(list_file_csv.curselection()): # 이렇게 하는 이유: reverse로 해야 for 문으로 삭제할 때 문제가 생기지 않음.
        list_file_csv.delete(index)
    
    if list_file_csv.get(0, END):
        timer_label.config(text=f"예상 시간: {estimate_time(list_file_csv.get(0, END))}초")
    else:
        timer_label.config(text=f"예상 시간: 0초")


def browse_dest_path_tab2():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때임.
        return
    
    txt_dest_path_tab2.delete(0, END)    # 기존 경로들 모두 삭제.
    txt_dest_path_tab2.insert(0, folder_selected)


def create_tab_content(frame, text):
    label = Label(frame, text=text, font=("Helvetica", 20, "bold"))
    label.pack(pady=5, fill=X)


# 1. text_to_csv 진행하기.
    
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# 첫번째 탭.
frame_tab1 = Frame(notebook, bd=0)
frame_tab1.pack(fill=BOTH, expand=True)
create_tab_content(frame_tab1, "텍스트를 csv로 변환")


## 상단 버튼들
btn_file_frame = Frame(frame_tab1, bd=0)
btn_file_frame.pack(pady=5, fill=X)

btn_add_file = Button(btn_file_frame, text="텍스트추가", padx=5, pady=5, width=10, command=add_text_path)
btn_del_file = Button(btn_file_frame, text="선택삭제", padx=5, pady=5, width=10, command=del_text_path)

btn_add_file.pack(side=LEFT, padx=5)
btn_del_file.pack(side=RIGHT, padx=5)

## 리스트 박스로 선택하는 경로들 설정.

list_frame = Frame(frame_tab1)
list_frame.pack(pady=5, fill=BOTH)

list_frame_scrollbar = Scrollbar(list_frame)
list_frame_scrollbar.pack(side=RIGHT, fill=Y)

list_file = Listbox(list_frame, selectmode=EXTENDED, height=20, yscrollcommand=list_frame_scrollbar.set)
list_file.pack(side=LEFT, fill=BOTH, expand=True)
list_frame_scrollbar.config(command=list_file.yview)

# 저장되는 경로.
path_frame = LabelFrame(frame_tab1, text="저장경로")
path_frame.pack(pady=5, expand=True, fill=X)


txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_dest_path = Button(path_frame, text='찾아보기', pady=3, width=10, command=browse_dest_path)
btn_dest_path.pack(side=RIGHT)



# text to csv 옵션들
## Combo 두 개
frame_txt2csv_option = LabelFrame(frame_tab1, text="스크립트 옵션")
frame_txt2csv_option.pack(pady=5, expand=True, fill=X)

## 콤보 1: 줄 변환 옵션
lbl_line =  Label(frame_txt2csv_option, text="줄 변환 옵션", width=10)
lbl_line.pack(side=LEFT, padx=5)
line_option = ["한 줄씩 변환", "여러 줄씩 변환 (이후 추가 예정)"]
combo_line_option = ttk.Combobox(frame_txt2csv_option, state="readonly", values=line_option)
combo_line_option.current(0)
combo_line_option.pack(side=LEFT)

## 콤보 2: 경고 케이스 옵션.
lbl_warning_cases =  Label(frame_txt2csv_option, text="경고 무시하기", width=10)
lbl_warning_cases.pack(side=LEFT, padx=5)
ignore_warning_case = ["아니오", "예"]
combo_warning_case = ttk.Combobox(frame_txt2csv_option, state="readonly", values=ignore_warning_case)
combo_warning_case.current(0)
combo_warning_case.pack(side=LEFT)

#TODO: 이후 추가 예정.
## 콤보 3: 30분 단위로 끊어주기.
# lbl_warning_cases =  Label(frame_txt2csv_option, text="경고 무시하기", width=10)
# lbl_warning_cases.pack(side=LEFT, padx=5)
# ignore_warning_case = ["아니오", "예"]
# combo_warning_case = ttk.Combobox(frame_txt2csv_option, state="readonly", values=ignore_warning_case)
# combo_warning_case.current(0)
# combo_warning_case.pack(side=LEFT)

## 변환 버튼
frame_convert_button = Frame(frame_tab1)
frame_convert_button.pack(pady=5, fill=X)
   

cvrt_btn =  Button(frame_convert_button, text="변환하기", command=start_converting, padx=15, pady=5)
cvrt_btn.pack(side=RIGHT)

# 2. 확인 이후에는 clova 돌리기.
frame_tab2 = Frame(notebook, bd=0)
frame_tab2.pack(fill='both', expand=True)
create_tab_content(frame_tab2, "쉼표 찍기")


## 상단 버튼들
btn_file_frame_tab2 = Frame(frame_tab2, bd=0)
btn_file_frame_tab2.pack(pady=5, fill=X)

btn_add_file_tab2 = Button(btn_file_frame_tab2, text="CSV 추가", padx=5, pady=5, width=10, command=add_csv_path)
btn_del_file_tab2 = Button(btn_file_frame_tab2, text="선택삭제", padx=5, pady=5, width=10, command=del_csv_path)

btn_add_file_tab2.pack(side=LEFT, padx=5)
btn_del_file_tab2.pack(side=RIGHT, padx=5)

## 리스트 박스로 선택하는 경로들 설정.

list_frame_csv = Frame(frame_tab2)
list_frame_csv.pack(pady=5, fill=BOTH)

list_frame_csv_scrollbar = Scrollbar(list_frame_csv)
list_frame_csv_scrollbar.pack(side=RIGHT, fill=Y)

list_file_csv = Listbox(list_frame_csv, selectmode=EXTENDED, height=20, yscrollcommand=list_frame_csv_scrollbar.set)
list_file_csv.pack(side=LEFT, fill=BOTH, expand=True)
list_frame_csv_scrollbar.config(command=list_file_csv.yview)

# 저장되는 경로.
path_frame_tab2 = LabelFrame(frame_tab2, text="저장경로")
path_frame_tab2.pack(pady=5, expand=True, fill=X)

txt_dest_path_tab2 = Entry(path_frame_tab2)
txt_dest_path_tab2.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_dest_path_tab2 = Button(path_frame_tab2, text='찾아보기', pady=3, width=10, command=browse_dest_path_tab2)
btn_dest_path_tab2.pack(side=RIGHT)


# text to csv 옵션들
## Combo 두 개
# frame_txt2csv_option = LabelFrame(frame_tab2, text="스크립트 옵션")
# frame_txt2csv_option.pack(pady=5, expand=True, fill=X)

# ## 콤보 1: 줄 변환 옵션
# lbl_line =  Label(frame_txt2csv_option, text="줄 변환 옵션", width=10)
# lbl_line.pack(side=LEFT, padx=5)
# line_option = ["한 줄씩 변환", "여러 줄씩 변환 (이후 추가 예정)"]
# combo_line_option = ttk.Combobox(frame_txt2csv_option, state="readonly", values=line_option)
# combo_line_option.current(0)
# combo_line_option.pack(side=LEFT)

# ## 콤보 2: 경고 케이스 옵션.
# lbl_warning_cases =  Label(frame_txt2csv_option, text="경고 무시하기", width=10)
# lbl_warning_cases.pack(side=LEFT, padx=5)
# ignore_warning_case = ["아니오", "예"]
# combo_warning_case = ttk.Combobox(frame_txt2csv_option, state="readonly", values=ignore_warning_case)
# combo_warning_case.current(0)
# combo_warning_case.pack(side=LEFT)

## 예상 시간 라벨
timer_label = Label(frame_tab2, text=f"예상 시간: {estimate_time(list(list_file_csv.get(0,END)))}초")
timer_label.pack()

## 변환 버튼
frame_comma_button = Frame(frame_tab2)
frame_comma_button.pack(pady=5, fill=X)
   

comma_btn = Button(frame_comma_button, text="쉼표찍기", command=start_async_task_comma, padx=15, pady=5)
comma_btn.pack(side=RIGHT)

notebook.add(frame_tab1, text="텍스트를 csv로 변환")
notebook.add(frame_tab2, text='쉼표 찍기')

threading.Thread(target=start_async_loop, daemon=True).start()

root.mainloop()

#TODO: 초기 directory 설정 원상태로 두기.
