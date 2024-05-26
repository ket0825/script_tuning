# tkinter
import tkinter.messagebox as msgbox
import time
import tkinter.ttk as ttk
from tkinter import *

root = Tk()

root.title("GUI 타이틀")
root.geometry("640x480")
# root.geometry("640x480+100+300") # 가로*세로 + x좌표 + y좌표.

# root.resizable(False, False) # 창크기 변경 불가.

#### 위젯 (버튼, 텍스트박스 등등)
## 버튼
# btn1 = Button(root, text="버튼1")
# btn1.pack() # 이걸 실제로 해야 생김.

# btn2 = Button(root, padx=5, pady=10, text="버튼2") # padding x, y임.
# btn2.pack() # 이걸 실제로 해야 생김.

# btn3 = Button(root, text="버튼3", height=20, width=20) # width height은 고정 크기임.
# btn3.pack() # 이걸 실제로 해야 생김.

# def btcmd():
#     print('버튼 클릭됨')

# btn4 = Button(root, text="버튼4", fg='yellow', bg='red', command=btcmd) # 색상
# btn4.pack() # 이걸 실제로 해야 생김.

# photo = PhotoImage(file='파일경로')

# btn5 = Button(root, image=photo) # 이미지
# btn5.pack() # 이걸 실제로 해야 생김.

## 레이블: 그냥 글씨

# label1 = Label(root, text="label1")
# label1.pack()

# def change():
#     label1.config(text="또 만나요") # config로 재정의 가능.

#     # 이미지 변경을 위한 것이라면 전역 변수로 함수에서 선언해야 함.

# btn = Button(root, text="클릭", command=change)
# btn.pack()

# photo도 가능

## Text 위젯: 여러 줄
# txt = Text(root, width=30, height=5)
# txt.pack()

# txt.insert(END, "insert the text")

# ## Entry: 한 줄.
# e = Entry(root, width=30)
# e.pack()

# def btncmd():
#     print(txt.get("1.0", END)) #1.0 => 라인 1부터 0번째 col부터.
#     print(e.get())

#     txt.delete("1.0", END)
#     e.delete(0, END)
    

# btn1 = Button(root, text="click", command=btncmd)
# btn1.pack()



## 리스트 박스
# listbox = Listbox(root, selectmode='extended', height=3) # 여러 개, single은 하나만. # height에 따라 보이는 수가 다름.
# listbox.insert(0,'a')
# listbox.insert(1,'b')
# listbox.insert(3,'c')
# listbox.insert(END,'d')
# listbox.insert(END,'e')
# listbox.insert(END,'f')
# listbox.pack()

# def btcmd():
#     # listbox.delete(0) # 맨 앞 항목 삭제.
#     # print(f"listbox.size(): {listbox.size()}") # listbox 갯수 확인
#     # 
#     print(f"listbox.get(0,2): {listbox.get(0,2)}") # 값 얻기. 총 3개
 
#     print(f"listbox.curselection():{listbox.curselection()}") # 위치 반환.
#     # 

# btn = Button(root, text="button1", command=btcmd)
# btn.pack()


## 체크박스
# chkvar = IntVar()
# chkbox = Checkbutton(root, text="today not seen", variable=chkvar)

# # chkbox.select() # 자동 체크
# # chkbox.deselect()


# chkbox.pack()

# chkbox2 = Checkbutton(root, text="qhwl dksgrl")

# def btcmd():
#     print(chkvar.get()) # 0 혹은 1

# btn = Button(root, text="button1", command=btcmd)
# btn.pack()

## 라디오 버튼: 택 1

# Label(root, text="selecet menu").pack()

# burger_var = IntVar()

# btn_burger1 = Radiobutton(root, text="normal", value=1, variable=burger_var)
# btn_burger1.select()
# btn_burger2 = Radiobutton(root, text="normal2", value=2,variable=burger_var)
# btn_burger3 = Radiobutton(root, text="normal3",value=3, variable=burger_var)

# btn_burger1.pack()
# btn_burger2.pack()
# btn_burger3.pack()

# Label(root, text="select drink").pack()

# drink_var = IntVar()

# btn_drink1 = Radiobutton(root, text="normal", value=1, variable=drink_var)
# btn_drink1.select()
# btn_drink2 = Radiobutton(root, text="normal2", value=2,variable=drink_var)
# btn_drink3 = Radiobutton(root, text="normal3",value=3, variable=drink_var)

# btn_drink1.pack()
# btn_drink2.pack()
# btn_drink3.pack()

# def btcmd():
#     print(burger_var.get())

# btn = Button(root, text="button1", command=btcmd)
# btn.pack()


## 콤보박스

# values = [str(i+1)+"일" for i in range(31)]
# combobox = ttk.Combobox(root, height=5, values=values,state="readonly") # state 없으면 수정 가능.
# combobox.pack()
# combobox.set("카드 결제일") # 최초 목록 제목 설정
# combobox.current(0)


# def btcmd():
#     pass

# btn = Button(root, text="button1", command=btcmd)
# btn.pack()


## progress bar.


# progress_bar = ttk.Progressbar(root, maximum=100, mode='indeterminate') # indeterminate는 언제 끝날지 모름...
# progress_bar = ttk.Progressbar(root, maximum=100, mode='determinate')
# progress_bar.start(10) # 10ms마다 움직임.
# progress_bar.pack()


# def btcmd():
#     progress_bar.stop() # 중지

# btn = Button(root, text="button1", command=btcmd)
# btn.pack()

# p_var2 = DoubleVar()
# progress_bar2 = ttk.Progressbar(root, maximum=100, length=150, variable=p_var2)
# progress_bar2.pack()

# def btcmd2():
#     for i in range(101):
#         time.sleep(0.01) # 0.01초 대기
#         p_var2.set(i) # set으로 설정.
#         progress_bar2.update() # ui 업데이트

# btn = Button(root, text="button1", command=btcmd2)
# btn.pack()


## 메뉴바

# menu = Menu(root)

# def create_new_file():
#     print("new file created!")

# menu_file = Menu(menu, tearoff=0)
# menu_file.add_command(label="New File", command=create_new_file)
# menu_file.add_command(label="New Window")
# menu_file.add_separator() # 구분자
# menu_file.add_command(label="Open file")
# menu_file.add_separator() # 구분자
# menu_file.add_command(label="Save all", state='disable') # 비활성화
# menu_file.add_command(label="Exit", command=root.quit) # 비활성화

# menu.add_cascade(label="File", menu=menu_file) # 제일 앞부분.

# # 빈 값.
# menu.add_cascade(label="Edit", ) # 제일 앞부분.


# # menu에 radiobutton 추가. (택 1)
# menu_lang = Menu(menu, tearoff=0)
# menu_lang.add_radiobutton(label='1')
# menu_lang.add_radiobutton(label='2')
# menu_lang.add_radiobutton(label='3')
# menu_lang.add_radiobutton(label='4')

# menu.add_cascade(label='language', menu=menu_lang)


# # View menu (체크박스)

# menu_view = Menu(menu, tearoff=0)
# menu_view.add_checkbutton(label="check1")
# menu_view.add_checkbutton(label="check2")
# menu.add_cascade(label="View",menu=menu_view)


# root.config(menu=menu)


## 메세지 박스: 에러 등 상태 표시. 분기 처리 가능

# def info():
#     msgbox.showinfo("알림", "정상 완료.")

# def warning():
#     msgbox.showwarning("경고", "매진")

# def error():
#     msgbox.showerror("에러", "에러가 발생했습니다.")

# def okcancel():
#     msgbox.askokcancel("확인 / 취소", "확인하기 및 취소하기")

# def retrycancel():
#     msgbox.askretrycancel("다시시도 / 취소", "다시시도 및 취소하기")

# def yesno():
#     msgbox.askyesno("예 / 아니오", "역방향입니다.")
    
# def yesnocancel():
#     response = msgbox.askyesnocancel(title=None, message="조심하세요.")
#     # 네: 저장 후 종료
#     # 아니오: 저장하지 않고 종료
#     # 취소: 프로그램 종료 자체를 취소.
#     print("응답: ", response)
#     if response == 1:
#         print("예")
#     elif response == 0:
#         print("No")
#     elif response == None:
#         print("취소")

# Button(root, text="button1", command=info).pack()
# Button(root, text="button2", command=warning).pack()
# Button(root, text="button3", command=error).pack()
# Button(root, text="button4", command=okcancel).pack()
# Button(root, text="button5", command=retrycancel).pack()
# Button(root, text="button6", command=yesno).pack()
# Button(root, text="button7", command=yesnocancel).pack()


## 프레임: 위젯을 안에 넣을 수 있음.

# Label(root, text="메뉴를 선택해주세요").pack(side="top")
# Button(root, text="선택하기").pack(side="bottom")

# frame_burger = Frame(root, relief="solid", bd=1)
# frame_burger.pack(side='left', fill='both', expand=True)


# def btcmd():
#     pass

# Button(frame_burger, text="button1", command=btcmd).pack() # 프레임이면 root가 아님.
# Button(frame_burger, text="button2", command=btcmd).pack()
# Button(frame_burger, text="button3", command=btcmd).pack()

# frame_drink = LabelFrame(root, text="음료", relief="solid", bd=1)
# frame_drink.pack(side='right', fill='both', expand=True)

# Button(frame_drink, text="coke").pack()
# Button(frame_drink, text="cider").pack()


## 스크롤 바.

# frame = Frame(root)
# frame.pack()

# scrollbar = Scrollbar(frame)
# scrollbar.pack(side='right', fill='y')

# listbox = Listbox(frame, selectmode='extended', height=10, yscrollcommand=scrollbar.set) # set를 해줘야 함.

# for i in range(1, 32):
#     listbox.insert(END, str(i)+"일")

# listbox.pack()

# scrollbar.config(command=listbox.yview) # listbox와 매핑.


## 그리드

# btn_f16 = Button(root, text="F16", width=5, height=2)
# btn_f17 = Button(root, text="F17", width=5, height=2)
# btn_f18 = Button(root, text="F18", width=5, height=2)
# btn_f19 = Button(root, text="F19", width=5, height=2)

# btn_f16.grid(row= 0, column=0, sticky=N+E+W+S, padx=3, pady=3) # 빈 공간을 N E W S 방향으로 확장
# btn_f17.grid(row= 0, column=1, sticky=N+E+W+S, padx=3, pady=3)
# btn_f18.grid(row= 0, column=2, sticky=N+E+W+S, padx=3, pady=3)
# btn_f19.grid(row= 0, column=3, sticky=N+E+W+S, padx=3, pady=3)

# btn_clear = Button(root, text="clear", width=5, height=2)
# btn_equal = Button(root, text="=", width=5, height=2)
# btn_divide = Button(root, text="/", width=5, height=2)
# btn_multiple = Button(root, text="*", width=5, height=2)

# btn_clear.grid(row= 1, column=0, sticky=N+E+W+S, padx=3, pady=3)
# btn_equal.grid(row= 1, column=1, sticky=N+E+W+S, padx=3, pady=3)
# btn_divide.grid(row= 1, column=2, sticky=N+E+W+S, padx=3, pady=3)
# btn_multiple.grid(row= 1, column=3, sticky=N+E+W+S, padx=3, pady=3)

# btn_7 = Button(root, text="7", width=5, height=2)
# btn_8 = Button(root, text="8", width=5, height=2)
# btn_9 = Button(root, text="9", width=5, height=2)
# btn_sub = Button(root, text="-", width=5, height=2)

# btn_7.grid(row= 2, column=0, sticky=N+E+W+S, padx=3, pady=3)
# btn_8.grid(row= 2, column=1, sticky=N+E+W+S, padx=3, pady=3)
# btn_9.grid(row= 2, column=2, sticky=N+E+W+S, padx=3, pady=3)
# btn_sub.grid(row= 2, column=3, sticky=N+E+W+S, padx=3, pady=3)

# btn_4 = Button(root, text="4", width=5, height=2)
# btn_5 = Button(root, text="5", width=5, height=2)
# btn_6 = Button(root, text="6", width=5, height=2)
# btn_plus = Button(root, text="+", width=5, height=2)

# btn_4.grid(row= 3, column=0, sticky=N+E+W+S, padx=3, pady=3)
# btn_5.grid(row= 3, column=1, sticky=N+E+W+S, padx=3, pady=3)
# btn_6.grid(row= 3, column=2, sticky=N+E+W+S, padx=3, pady=3)
# btn_plus.grid(row= 3, column=3, sticky=N+E+W+S, padx=3, pady=3)

# btn_1 = Button(root, text="1", width=5, height=2)
# btn_2 = Button(root, text="2", width=5, height=2)
# btn_3 = Button(root, text="3", width=5, height=2)
# btn_enter = Button(root, text="enter", width=5, height=2) # 새로로 합쳐짐

# btn_1.grid(row= 4, column=0, sticky=N+E+W+S, padx=3, pady=3)
# btn_2.grid(row= 4, column=1, sticky=N+E+W+S, padx=3, pady=3)
# btn_3.grid(row= 4, column=2, sticky=N+E+W+S, padx=3, pady=3)
# btn_enter.grid(row= 4, column=3, rowspan=2, sticky=N+E+W+S, padx=3, pady=3) # 현재 위치에서 아래쪽으로 확장

# btn_0 = Button(root, text="0", width=5, height=2)
# btn_point = Button(root, text=".", width=5, height=2)

# btn_0.grid(row= 5, column=0, columnspan=2, sticky=N+E+W+S, padx=3, pady=3) # 현재 위치에서 오른쪽으로 확장
# btn_point.grid(row= 5, column=2, sticky=N+E+W+S, padx=3, pady=3)


root.mainloop()

