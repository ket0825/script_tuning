import tkinter.messagebox as msgbox
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
# import tkinter.font as tkFont
import asyncio
import os
from typing import List
import threading
import traceback

from RPA.script_extractor import ScriptExtractor


root = Tk()
# resolution
# resol_width = 900
# resol_height = 700

# default_font = tkFont.nametofont("TkDefaultFont")

# 기본 글꼴 설정 복사하여 'bold' 스타일 추가
# bold_font = tkFont.Font(font=default_font, weight="bold")
# underline_font = tkFont.Font(font=default_font, underline=True)

root.title("PDF 스크립트 변환기")
root.geometry("1000x800")
root.resizable(False, True)

# 파일 추가
def browse_pdf_path():
    folder_selected = filedialog.askopenfilename(
                                        title="변환하려는 PDF를 선택하세요",
                                        filetypes=(("pdf 파일", "*.pdf"), ("모든 파일", "*.*")), 
                                        )
    
    if folder_selected == "": # 사용자가 취소를 누를 때임.
        return
    print(allow_hanja.get())
    # 기존 경로들 모두 삭제.
    pdf_path_tab1.delete(0, END)
    pdf_path_tab2.delete(0, END)

    pdf_path_tab1.insert(0, folder_selected)
    pdf_path_tab2.insert(0, folder_selected)


def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때임.
        return
    
    pdf_dest_path_tab1.delete(0, END)    # 기존 경로들 모두 삭제.
    pdf_dest_path_tab2.delete(0, END)    # 기존 경로들 모두 삭제.

    pdf_dest_path_tab1.insert(0, folder_selected)
    pdf_dest_path_tab2.insert(0, folder_selected)
    

def check_layout():
    if not pdf_path_tab1.get():
        msgbox.showerror("에러", "선택된 파일이 없습니다.")
        return
    
    if not pdf_dest_path_tab1.get():
        msgbox.showerror("에러", "저장되는 경로를 설정해주세요.")
        return
    
    pages = []
    
    try:
        pages_str = e_layout_check_page.get().split(",")
        pages = list(range(int(pages_str[0].strip()), int(pages_str[1].strip())+1))
    except Exception as e:
        msgbox.showerror("에러", "문제가 발생했습니다.\n레이아웃 확인 페이지를 다시 체크해주세요.")
        return

    layout_pages = []
    try:
        option = int(check_option_var.get())
        if option == 1:
            option_input_str = e_layout_check_option1.get().split(",")
            layout_pages = list(range(int(option_input_str[0].strip()), int(option_input_str[1].strip())+1))
        elif option == 2:
            option_input_str = e_layout_check_option2.get().split(",")
            layout_pages = list(int(option_input_str[0].strip()), int(option_input_str[1].strip()))
    except Exception as e:
        msgbox.showerror("에러", "문제가 발생했습니다.\n레이아웃 확인 옵션을 다시 체크해주세요.")
        return
    
    excluded_lines_count_odd = int(combo_odd_excluded_line_option.get())
    excluded_lines_count_even = int(combo_even_excluded_line_option.get())
    
    try:
        extractor = ScriptExtractor(
                pages=pages,
                excluded_lines_count_odd=excluded_lines_count_odd,
                excluded_lines_count_even=excluded_lines_count_even,
                layout_pages=layout_pages
        )
        # 단 하나의 파일만 넣을 수 있게 해야 할듯.
        pdf_file_path = pdf_path_tab1.get()
        output_dirname = pdf_dest_path_tab1.get()
        if len(layout_pages) > 2:
            start_page = str(layout_pages[0])
            end_page = str(layout_pages[-1])
            output_path = output_dirname
            layout_filename = pdf_file_path[pdf_file_path.rfind("/")+1:].replace(".pdf", "") + "_레아이웃_범위_"+ start_page + "_" + end_page + ".txt"
        else:
            start_page = str(layout_pages[0])
            end_page = str(layout_pages[1])
            output_path = output_dirname
            layout_filename = pdf_file_path[pdf_file_path.rfind("/")+1:].replace(".pdf", "") + "_레아이웃_단일_"+ start_page + "_" + end_page + ".txt"
            # output_path = output_dirname + pdf_file_path[pdf_file_path.rfind("/"):].replace(".pdf", "") + "_레아이웃_단일"+ start_page + "_" + end_page

        extractor.set_option(pdf_file_path, 
                             output_path=output_path, 
                             LINE_HEIGHT_THRESHOLD=15, 
                             PARAGRAPH_SPACE=5, 
                             NEWLINE_SPACE=20,
                             )        
        extractor.set_new_layout()
        extractor.layout_checker(layout_filename)        
        msgbox.showinfo("변환 완료", "정상적으로 변환이 완료되었습니다.\n반드시 파일을 확인해주세요.")
        
        ### tab2의 페이지, 레이아웃 확인 옵션, 제외되는 줄 수 설정 보존.        
        e_convert_page = Entry(frame_convert_page)
        e_convert_page.insert(0, e_layout_check_page.get())

        option = int(check_option_var.get())
        if option == 1:
            btn_layout_option1.select()
            e_layout_option1.insert(0, e_layout_check_option1.get())
        elif option == 2:
            btn_layout_option2.select()
            e_layout_option2.insert(0, e_layout_check_option2.get())
        
        combo_odd_excluded_line_option_tab2.current(excluded_lines_count_odd)
        combo_even_excluded_line_option_tab2.current(excluded_lines_count_even)

        
    except Exception as e:
        error_msg = traceback.format_exc()
        msgbox.showerror("에러", "문제가 발생했습니다.\nPDF 파일과 저장경로를 다시 확인해주세요.\n에러내용: "+ error_msg)
        return


def convert_pdf_to_script():
    if not pdf_path_tab1.get():
        msgbox.showerror("에러", "선택된 파일이 없습니다.")
        return
    
    if not pdf_dest_path_tab1.get():
        msgbox.showerror("에러", "저장되는 경로를 설정해주세요.")
        return

    pages = []
    try:
        pages_str = e_convert_page.get().split(",")
        pages = list(range(int(pages_str[0].strip()), int(pages_str[1].strip())+1))
    except Exception as e:
        msgbox.showerror("에러", "문제가 발생했습니다.\n변환 페이지를 다시 체크해주세요.")
        return

    layout_pages = []
    try:
        option = int(check_option_var.get())
        if option == 1:
            option_input_str = e_layout_option1.get().split(",")
            layout_pages = list(range(int(option_input_str[0].strip()), int(option_input_str[1].strip())+1))
        elif option == 2:
            option_input_str = e_layout_option2.get().split(",")
            layout_pages = list(int(option_input_str[0].strip()), int(option_input_str[1].strip()))
    except Exception as e:
        msgbox.showerror("에러", "문제가 발생했습니다.\n레이아웃 옵션을 다시 체크해주세요.")
        return
   
    excluded_lines_count_odd = int(combo_odd_excluded_line_option_tab2.get())
    excluded_lines_count_even = int(combo_even_excluded_line_option_tab2.get()) 

    try:
        extractor = ScriptExtractor(
                pages=pages,
                excluded_lines_count_odd=excluded_lines_count_odd,
                excluded_lines_count_even=excluded_lines_count_even,
                layout_pages=layout_pages
        )
        # 단 하나의 파일만 넣을 수 있게 해야 할듯.
        pdf_file_path = pdf_path_tab2.get()
        output_dirname = pdf_dest_path_tab2.get()
        if len(layout_pages) > 2:
            start_page = str(layout_pages[0])
            end_page = str(layout_pages[-1])
            output_path = output_dirname
            # layout_filename = pdf_file_path[pdf_file_path.rfind("/")+1:].replace(".pdf", "") + "_레아이웃_범위_"+ start_page + "_" + end_page + ".txt"
        else:
            start_page = str(layout_pages[0])
            end_page = str(layout_pages[1])
            output_path = output_dirname
            # layout_filename = pdf_file_path[pdf_file_path.rfind("/")+1:].replace(".pdf", "") + "_레아이웃_단일_"+ start_page + "_" + end_page + ".txt"
            # output_path = output_dirname + pdf_file_path[pdf_file_path.rfind("/"):].replace(".pdf", "") + "_레아이웃_단일"+ start_page + "_" + end_page

        extractor.set_option(pdf_file_path, 
                             output_path=output_path, 
                             LINE_HEIGHT_THRESHOLD=int(e_line_height_threshold.get()), 
                             PARAGRAPH_SPACE=int(e_paragraph_space.get()), 
                             NEWLINE_SPACE=int(e_newline_space.get()),
                             allow_hanja=allow_hanja.get()
                             )        
        extractor.set_new_layout()
        extractor.fontsize_counter()
        extractor.read_pdf_v2(
                            title=e_txt_title.get(),
                            read_line_with_word=read_line_with_word.get(),
                            check_overwritten_word=check_overwritten_word.get(),
                            extract_image=extract_image.get(),
                            robust_spacing=robust_spacing.get(),
                            text_flow=text_flow.get(),
                            check_space_with_ko_eng=check_space_with_ko_eng.get(),
                            check_space_with_num_char=check_space_with_num_char.get(),
                            )
        
        extractor.write_reference_page(title=e_txt_title.get())
        
        msgbox.showinfo("변환 완료", "정상적으로 변환이 완료되었습니다.\n반드시 파일을 확인해주세요.")
        
    except Exception as e:
        error_msg = traceback.format_exc()
        msgbox.showerror("에러", "문제가 발생했습니다.\nPDF 파일과 저장경로를 다시 확인해주세요.\n에러내용: "+ error_msg)
        return


def browse_dest_path_tab2():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때임.
        return
    
    pdf_dest_path_tab2.delete(0, END)    # 기존 경로들 모두 삭제.
    pdf_dest_path_tab2.insert(0, folder_selected)


def create_tab_content(frame, text):
    label = Label(frame, text=text, font=("Helvetica", 20, "bold"))
    label.pack(pady=5, fill=X)


# 1. text_to_csv 진행하기.
    
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True, fill="both")

# 첫번째 탭.
frame_tab1 = Frame(notebook, bd=0)
frame_tab1.pack(fill=BOTH, expand=True)
create_tab_content(frame_tab1, "레이아웃 확인")

# tab1용.
def on_mousewheel_tab1(e):
    canvas_tab1.yview_scroll(int(-1*(e.delta/120)), UNITS)

# Canvas의 scrollregion 설정
def configure_scrollregion(event):
    canvas_tab1.configure(scrollregion=canvas_tab1.bbox("all"))

def bind_mousewheel_on_tab1(widget):
    widget.bind("<MouseWheel>", on_mousewheel_tab1)
    for child in widget.winfo_children():
        bind_mousewheel_on_tab1(child)

# SCROLLABLE TAB1
scrollbar_tab1 = Scrollbar(frame_tab1, orient=VERTICAL)
scrollbar_tab1.pack(side="right", fill="y")

canvas_tab1 = Canvas(frame_tab1, yscrollcommand=scrollbar_tab1.set)
canvas_tab1.pack(side=LEFT, fill=BOTH, expand=True)
# canvas_tab1.bind("<MouseWheel>", on_mousewheel_tab2)

scrollbar_tab1.config(command=canvas_tab1.yview)

# Canvas에 스크롤 가능한 Frame 추가
scrollable_frame_tab1 = Frame(canvas_tab1)
canvas_tab1.create_window((0, 0), window=scrollable_frame_tab1, anchor="nw")
scrollable_frame_tab1.bind("<Configure>", configure_scrollregion)


## Entry로 선택하는 경로들 설정.
frame_pdf_path_tab1 = LabelFrame(scrollable_frame_tab1, text="PDF경로")
frame_pdf_path_tab1.pack(pady=5, expand=True, fill=X)

pdf_path_tab1 = Entry(frame_pdf_path_tab1)
pdf_path_tab1.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_pdf_path_tab1 = Button(frame_pdf_path_tab1, text='찾아보기', pady=3, width=10, command=browse_pdf_path)
btn_pdf_path_tab1.pack(side=RIGHT)

# 저장되는 경로.
frame_path_tab1 = LabelFrame(scrollable_frame_tab1, text="저장경로")
frame_path_tab1.pack(pady=5, expand=True, fill=X)


pdf_dest_path_tab1 = Entry(frame_path_tab1)
pdf_dest_path_tab1.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_dest_path_tab1 = Button(frame_path_tab1, text='찾아보기', pady=3, width=10, command=browse_dest_path)
btn_dest_path_tab1.pack(side=RIGHT)


# layout checker 옵션들
## Combo 두 개


# 페이지 및 목차 등: combobox
# 홀수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.
# 짝수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.


# 레이아웃 체크 옵션: 라디오 및 입력창.
# 스피드: 칸 두 개, or 홀 짝 페이지들. (단 홀 짝 모두 하나씩은 있어야 함.)
# 정확성: 페이지 입력: 칸 2개. (자율 입력)
frame_layout_check_page = LabelFrame(scrollable_frame_tab1 ,text='레이아웃 확인 페이지')
frame_layout_check_page.pack(pady=5, expand=True, fill=X)

lbl_layout_check_page = Label(frame_layout_check_page, 
                              text="레이아웃을 설정하여 확인할 페이지를 쉼표를 이용하여 입력하세요. 예) 19, 300 >> 19~300",
                              font=("TkDefaultFont", 10, 'bold'),
                            )
lbl_layout_check_page.pack(expand=True, fill=X, pady=5)

# ~에서 ~까지
lbl_layout_at = Label(frame_layout_check_page, text="페이지:")
lbl_layout_at.pack(side=LEFT, ipady=4, padx=5, pady=5)

e_layout_check_page = Entry(frame_layout_check_page)
e_layout_check_page.pack(side=LEFT, ipady=4, padx=5, pady=5)


frame_layout_check_option = LabelFrame(scrollable_frame_tab1 ,text='레이아웃 확인 옵션')
frame_layout_check_option.pack(pady=5, expand=True, fill=X)

lbl_layout_check_option = Label(frame_layout_check_option,
                                font=("TkDefaultFont", 10, 'bold'),
                                text='홀수, 짝수 페이지가 하나 이상 있어야 합니다. 입력 칸에 쉼표로 구분하여 넣어주세요. 예) 19,24', 
                                # font=bold_font,
                                )
lbl_layout_check_option.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

check_option_var = IntVar()

# entry는 grid 사용.
btn_layout_check_option1 = Radiobutton(frame_layout_check_option, 
                                       text="(추천) 정확도 위주 (레이아웃을 범위로 확인합니다. 예) 19,300 >> 19~300페이지 확인)", 
                                       font=("TkDefaultFont", 10, 'underline'),
                                    #    font=underline_font,
                                       value=1, 
                                       variable=check_option_var,
                                       )
btn_layout_check_option1.select()
btn_layout_check_option1.grid(row=1, column=0, sticky=W, padx=5, pady=5)
# btn_layout_check_option1.pack(side=TOP, anchor=W)
e_layout_check_option1 = Entry(frame_layout_check_option,)
e_layout_check_option1.grid(row=1, column=1, sticky=W, padx=5, pady=5)
# e1.pack(side=TOP, anchor=E)

btn_layout_check_option2 = Radiobutton(frame_layout_check_option, 
                                       text="스피드 위주 (레이아웃을 두 페이지로 확인합니다. 예: 19,20)", 
                                    #    font=underline_font,
                                       value=2, 
                                       variable=check_option_var,
                                       )
btn_layout_check_option2.grid(row=2, column=0, sticky=W, padx=5, pady=5)
e_layout_check_option2 = Entry(frame_layout_check_option,)
e_layout_check_option2.grid(row=2, column=1, sticky=W, padx=5, pady=5)


frame_layout_checker_tab1 = LabelFrame(scrollable_frame_tab1, text="제외되는 줄 수 설정")
frame_layout_checker_tab1.pack(pady=5, expand=True, fill=X)

## 콤보1: 홀수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.
lbl_odd_excluded_line_count = Label(frame_layout_checker_tab1, text="홀수 페이지 제외 줄 수", width=18)
lbl_odd_excluded_line_count.grid(row=0, column=0, sticky=W, padx=5, pady=5)
odd_excluded_line_option = [str(i) for i in range(5)]
combo_odd_excluded_line_option = ttk.Combobox(frame_layout_checker_tab1, state="readonly", values=odd_excluded_line_option, width=2)
combo_odd_excluded_line_option.current(1)
combo_odd_excluded_line_option.grid(row=0, column=1,  padx=5, pady=5)

## 콤보2: 짝수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.
lbl_even_excluded_line_count = Label(frame_layout_checker_tab1, text="짝수 페이지 제외 줄 수", width=18)
lbl_even_excluded_line_count.grid(row=0, column=2, padx=5, pady=5)
even_excluded_line_option = [str(i) for i in range(10)]
combo_even_excluded_line_option = ttk.Combobox(frame_layout_checker_tab1, state="readonly", values=even_excluded_line_option, width=2)
combo_even_excluded_line_option.current(1)
combo_even_excluded_line_option.grid(row=0, column=3,  padx=5, pady=5)


#TODO: 이후 추가 예정.
## 콤보 3: 30분 단위로 끊어주기.
# lbl_warning_cases =  Label(frame_layout_checker_tab1, text="경고 무시하기", width=10)
# lbl_warning_cases.pack(side=LEFT, padx=5)
# ignore_warning_case = ["아니오", "예"]
# combo_warning_case = ttk.Combobox(frame_layout_checker_tab1, state="readonly", values=ignore_warning_case)
# combo_warning_case.current(0)
# combo_warning_case.pack(side=LEFT)

## 변환 버튼
frame_layout_checker_button = Frame(scrollable_frame_tab1)
frame_layout_checker_button.pack(pady=5, fill=X)
   
layout_checker_btn =  Button(frame_layout_checker_button, text="레이아웃 확인하기", font=("TkDefaultFont", 11, 'bold'), command=check_layout, padx=15, pady=5)
layout_checker_btn.pack(side=RIGHT)


bind_mousewheel_on_tab1(canvas_tab1)


"""
tab2: PDF 스크립트 변환.
"""

# mouse wheel과의 연동준비
def on_mousewheel_tab2(e):
    canvas_tab2.yview_scroll(int(-1*(e.delta/120)), UNITS)

# Canvas의 scrollregion 설정
def configure_scrollregion(event):
    canvas_tab2.configure(scrollregion=canvas_tab2.bbox("all"))

def bind_mousewheel_on_tab2(widget):
    widget.bind("<MouseWheel>", on_mousewheel_tab2)
    for child in widget.winfo_children():
        bind_mousewheel_on_tab2(child)



# 2. 레이아웃 확인 후 값들 유지.
frame_tab2 = Frame(notebook, bd=0)
frame_tab2.pack(fill='both', expand=True)
create_tab_content(frame_tab2, "PDF 스크립트 변환")

# SCROLLABLE TAB2
scrollbar_tab2 = Scrollbar(frame_tab2, orient=VERTICAL)
scrollbar_tab2.pack(side="right", fill="y")

canvas_tab2 = Canvas(frame_tab2, yscrollcommand=scrollbar_tab2.set)
canvas_tab2.pack(side=LEFT, fill=BOTH, expand=True)
# canvas_tab2.bind("<MouseWheel>", on_mousewheel_tab2)

scrollbar_tab2.config(command=canvas_tab2.yview)

# Canvas에 스크롤 가능한 Frame 추가
scrollable_frame_tab2 = Frame(canvas_tab2)
canvas_tab2.create_window((0, 0), window=scrollable_frame_tab2, anchor="nw")
scrollable_frame_tab2.bind("<Configure>", configure_scrollregion)


## Entry로 선택하는 경로들 설정.
frame_pdf_path_tab2 = LabelFrame(scrollable_frame_tab2, text="PDF경로")
frame_pdf_path_tab2.pack(pady=5, expand=True, fill=X)

pdf_path_tab2 = Entry(frame_pdf_path_tab2,)
pdf_path_tab2.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_pdf_path_tab2 = Button(frame_pdf_path_tab2, text='찾아보기', pady=3, width=10, command=browse_pdf_path)
btn_pdf_path_tab2.pack(side=RIGHT)

# 저장되는 경로.
frame_path_tab2 = LabelFrame(scrollable_frame_tab2, text="저장경로")
frame_path_tab2.pack(pady=5, expand=True, fill=X)

pdf_dest_path_tab2 = Entry(frame_path_tab2)
pdf_dest_path_tab2.pack(side=LEFT, fill=X, expand=True, ipady=4, ipadx=10)

btn_dest_path_tab2 = Button(frame_path_tab2, text='찾아보기', pady=3, width=10, command=browse_dest_path)
btn_dest_path_tab2.pack(side=RIGHT)


# layout checker 옵션들
## Combo 두 개


# 페이지 및 목차 등: combobox
# 홀수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.
# 짝수 페이지 제외 줄 수: 기본 1. 0-9까지 선택.



# def __init__(self, pages:List[int], excluded_lines_count_odd=1, excluded_lines_count_even=1, robust_spacing=False, layout_pages=None) -> None:

# def read_pdf_v2(self, 
#                 read_line_with_word=True, 
#                 check_overwritten_word=True, 
#                 extract_image=True,
#                 text_flow=True,
#                 check_space_with_ko_eng=True,
#                 check_space_with_num_char=True
#                 )-> None:


# 레이아웃 체크 옵션: 라디오 및 입력창.
# 스피드: 칸 두 개, or 홀 짝 페이지들. (단 홀 짝 모두 하나씩은 있어야 함.)
# 정확성: 페이지 입력: 칸 2개. (자율 입력)
frame_pdf_script_convert = LabelFrame(scrollable_frame_tab2 ,text='PDF 스크립트 변환 옵션')
frame_pdf_script_convert.pack(pady=5, expand=True, fill=X)

lbl_pdf_script_convert_explanation = Label(frame_pdf_script_convert, 
                              text="옵션을 설정하세요.",
                              font=("TkDefaultFont", 10, 'bold'),
                            )
lbl_pdf_script_convert_explanation.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

read_line_with_word = IntVar()
check_overwritten_word = IntVar()
extract_image = IntVar()
text_flow = IntVar()
check_space_with_ko_eng = IntVar()
check_space_with_num_char = IntVar()
robust_spacing = IntVar()
allow_hanja = IntVar()

lbl_txt_title = Label(frame_pdf_script_convert, text="책 제목을 입력하세요: ")
lbl_txt_title.grid(row=1, column=0, sticky=W, padx=5, pady=5)
e_txt_title = Entry(frame_pdf_script_convert)
e_txt_title.grid(row=1, column=1, sticky=W, padx=5, pady=5)

# LINE_HEIGHT_THRESHOLD=15, 
# PARAGRAPH_SPACE=5, 
# NEWLINE_SPACE=20

lbl_line_height_threshold = Label(frame_pdf_script_convert, text="문단 사이가 x 포인트만큼 간격이 있다면 줄바꿈 삽입.")
lbl_line_height_threshold.grid(row=2, column=0, sticky=W, padx=5, pady=5)
e_line_height_threshold = Entry(frame_pdf_script_convert)
e_line_height_threshold.insert(0, "15")
e_line_height_threshold.grid(row=2, column=1, sticky=W, padx=5, pady=5)

lbl_paragraph_space = Label(frame_pdf_script_convert, text="챕터 등이 끝나서 레이아웃 기준으로 아래에 x 포인트만큼 공백이 있다면 줄바꿈 삽입.")
lbl_paragraph_space.grid(row=3, column=0, sticky=W, padx=5, pady=5)
e_paragraph_space = Entry(frame_pdf_script_convert)
e_paragraph_space.insert(0, "5")
e_paragraph_space.grid(row=3, column=1, sticky=W, padx=5, pady=5)

lbl_newline_space = Label(frame_pdf_script_convert, text="문단이 끝나거나 표 내부 문장이 종료되면 거기까지 띄어쓰기 교정함. 레이아웃 기준 문장의 종료를 판단하기 위하여 우측부터 x만큼의 공백 포인트.")
lbl_newline_space.grid(row=4, column=0, sticky=W, padx=5, pady=5)
e_newline_space = Entry(frame_pdf_script_convert)
e_newline_space.insert(0, "20")
e_newline_space.grid(row=4, column=1, sticky=W, padx=5, pady=5)

chkbox_read_line_with_word = Checkbutton(frame_pdf_script_convert, text="단어 기준 한 줄로 추출하기", variable=read_line_with_word)
chkbox_read_line_with_word.select()
chkbox_read_line_with_word.grid(row=5, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_check_overwritten_word = Checkbutton(frame_pdf_script_convert, text="pdf 내에서 겹칠 정도로 가까운 글자 체크", variable=check_overwritten_word)
chkbox_check_overwritten_word.select()
chkbox_check_overwritten_word.grid(row=6, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_extract_image = Checkbutton(frame_pdf_script_convert, text="그림, 표 등이 존재하는 페이지를 이미지로 저장 (시간 오래 걸림)", variable=extract_image)
chkbox_check_overwritten_word.deselect()
chkbox_extract_image.grid(row=7, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_text_flow = Checkbutton(frame_pdf_script_convert, text="위에서 아래 대신, 커서 흐름대로 변환 (필요한 경우가 존재함)", variable=text_flow)
chkbox_text_flow.deselect()
chkbox_text_flow.grid(row=8, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_check_space_with_ko_eng = Checkbutton(frame_pdf_script_convert, text="한글 단어와 영어 단어 순으로 나오는 것 공백 체크", variable=check_space_with_ko_eng)
chkbox_check_space_with_ko_eng.select()
chkbox_check_space_with_ko_eng.grid(row=9, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_check_space_with_num_char = Checkbutton(frame_pdf_script_convert, text="숫자와 글자 사이에 공백 체크", variable=check_space_with_num_char)
chkbox_check_space_with_num_char.select()
chkbox_check_space_with_num_char.grid(row=10, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_robust_spacing = Checkbutton(frame_pdf_script_convert, text="pdf 띄어쓰기 교정 모델 (사용 시 시간 많이 걸림)", variable=robust_spacing)
chkbox_robust_spacing.deselect()
chkbox_robust_spacing.grid(row=11, column=0, columnspan=2, sticky=W, padx=5, pady=5)

chkbox_allow_hanja = Checkbutton(frame_pdf_script_convert, text="한자 허용하기 (허용하지 않으면 자동으로 빠짐)", variable=allow_hanja)
chkbox_allow_hanja.deselect()
chkbox_allow_hanja.grid(row=12, column=0, columnspan=2, sticky=W, padx=5, pady=5)



### 아래는 모두 레이아웃 확인 탭과 연계.
frame_convert_page = LabelFrame(scrollable_frame_tab2 ,text='변환 페이지')
frame_convert_page.pack(pady=5, expand=True, fill=X)

lbl_convert_page = Label(frame_convert_page, 
                              text="변환할 페이지를 쉼표를 이용하여 입력하세요. 예) 19, 300 >> 19~300",
                              font=("TkDefaultFont", 10, 'bold'),
                            )
lbl_convert_page.pack(expand=True, fill=X, pady=5)
# ~에서 ~까지
lbl_convert_at = Label(frame_convert_page, text="페이지:")
lbl_convert_at.pack(side=LEFT, ipady=4, padx=5, pady=5)

e_convert_page = Entry(frame_convert_page)
e_convert_page.pack(side=LEFT, ipady=4, padx=5, pady=5)

 
frame_layout_option = LabelFrame(scrollable_frame_tab2 ,text='레이아웃 옵션')
frame_layout_option.pack(pady=5, expand=True, fill=X)

lbl_layout_option = Label(frame_layout_option,
                                font=("TkDefaultFont", 10, 'bold'),
                                text='홀수, 짝수 페이지가 하나 이상 있어야 합니다. 입력 칸에 쉼표로 구분하여 넣어주세요. 예) 19,24', 
                                # font=bold_font,
                                )
lbl_layout_option.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

layout_option_var = IntVar()

# entry는 grid 사용.
btn_layout_option1 = Radiobutton(frame_layout_option, 
                                       text="(추천) 정확도 위주 (레이아웃을 범위로 확인합니다. 예) 19,300 >> 19~300페이지 확인)", 
                                       font=("TkDefaultFont", 10, 'underline'),
                                    #    font=underline_font,
                                       value=1, 
                                       variable=layout_option_var,
                                       )
btn_layout_option1.select()
btn_layout_option1.grid(row=1, column=0, sticky=W, padx=5, pady=5)
# btn_layout_check_option1.pack(side=TOP, anchor=W)
e_layout_option1 = Entry(frame_layout_option,)
e_layout_option1.grid(row=1, column=1, sticky=W, padx=5, pady=5)
# e1.pack(side=TOP, anchor=E)

btn_layout_option2 = Radiobutton(frame_layout_option, 
                                       text="스피드 위주 (레이아웃을 두 페이지로 확인합니다. 예: 19,20)", 
                                       value=2, 
                                       variable=layout_option_var,
                                       )
btn_layout_option2.grid(row=2, column=0, sticky=W, padx=5, pady=5)
e_layout_option2 = Entry(frame_layout_option,)
e_layout_option2.grid(row=2, column=1, sticky=W, padx=5, pady=5)


## 제외되는 줄 수 설정 계승:
frame_layout_excluded_line_count_tab2 = LabelFrame(scrollable_frame_tab2, text="제외되는 줄 수 설정")
frame_layout_excluded_line_count_tab2.pack(pady=5, expand=True, fill=X)

## 콤보1: 홀수 페이지 제외 줄 수: 기본 1. 0-4까지 선택.
lbl_odd_excluded_line_count_tab2 = Label(frame_layout_excluded_line_count_tab2, text="홀수 페이지 제외 줄 수", width=18)
lbl_odd_excluded_line_count_tab2.grid(row=0, column=0, sticky=W, padx=5, pady=5)
odd_excluded_line_option_tab2 = [str(i) for i in range(5)]
combo_odd_excluded_line_option_tab2 = ttk.Combobox(frame_layout_excluded_line_count_tab2, state="readonly", values=odd_excluded_line_option_tab2, width=2)
combo_odd_excluded_line_option_tab2.current(1)
combo_odd_excluded_line_option_tab2.grid(row=0, column=1,  padx=5, pady=5)

## 콤보2: 짝수 페이지 제외 줄 수: 기본 1. 0-4까지 선택.
lbl_even_excluded_line_count_tab2 = Label(frame_layout_excluded_line_count_tab2, text="짝수 페이지 제외 줄 수", width=18)
lbl_even_excluded_line_count_tab2.grid(row=0, column=2, padx=5, pady=5)
even_excluded_line_option_tab2 = [str(i) for i in range(10)]
combo_even_excluded_line_option_tab2 = ttk.Combobox(frame_layout_excluded_line_count_tab2, state="readonly", values=even_excluded_line_option_tab2, width=2)
combo_even_excluded_line_option_tab2.current(1)
combo_even_excluded_line_option_tab2.grid(row=0, column=3,  padx=5, pady=5)


#TODO: 이후 추가 예정.
## 콤보 3: 30분 단위로 끊어주기.
# lbl_warning_cases =  Label(frame_layout_checker_tab1, text="경고 무시하기", width=10)
# lbl_warning_cases.pack(side=LEFT, padx=5)
# ignore_warning_case = ["아니오", "예"]
# combo_warning_case = ttk.Combobox(frame_layout_checker_tab1, state="readonly", values=ignore_warning_case)
# combo_warning_case.current(0)
# combo_warning_case.pack(side=LEFT)

## 변환 버튼
frame_convert_button = Frame(scrollable_frame_tab2)
frame_convert_button.pack(pady=5, fill=X)
   
comma_btn = Button(frame_convert_button, text="변환하기", font=("TkDefaultFont", 11, 'bold'), command=convert_pdf_to_script, padx=15, pady=5,)
comma_btn.pack(side=RIGHT)

notebook.add(frame_tab1, text="레이아웃 확인")
notebook.add(frame_tab2, text='PDF 스크립트 변환')

bind_mousewheel_on_tab2(canvas_tab2)


root.mainloop()

#TODO: 초기 directory 설정 원상태로 두기.
