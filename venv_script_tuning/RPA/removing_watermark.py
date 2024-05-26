path = str(input("해당하는 파일을 경로 복사하여 붙여넣기 해주세요. \n"))

title = str(input("책 제목을 아래에 적어주세요. \n"))

start_page = int(input("시작하는 페이지를 아래에 적어주세요.\n \
                       ex) 7 \n"))

contents = str(input("목차를 작성해주세요.\
                     \n 하나를 다 적었다면 $를 적고\
                     바로 다음 것을 적어주세요.\n \
                     ex) 두 개의 달$어려운 고난$지식의밤$사람의 두 눈 \n"))

# 목차.
contents = contents.split(sep='$').append(title)

enter_condition = str(input("Enter가 필요한 조건 중, 기본적인 조건이 아닌 것을\
                            알려주세요. 없다면 없음이라고 입력해주세요. \n \
                            ex) 열림원 메멘토모리의\
                            '질문'이라는 부분으로 Enter가 필요한 경우: \n \
                            질문 "))
# 워터마크 제거.
watermark = str(input('워터마크가 있다면 작성해주세요: '))

# on-off 기능.
english_remove_by_font = str(input("설명하는 영어를 지우고 싶다면 '예'를 입력하세요: "))

# 기준이 되는 layout 페이지. 우측 아래에 페이지가 존재하여야 함. 들여쓰기 없고, 
layout_page = int(input("기준이 될 페이지를 설정해주세요."))

# font-based text 분류.
font_based_text = str(input("폰트 사이즈 기반 텍스트를 분류하시겠어요? '예', '아니오'로 답변해주세요 "))

print('분류할 필요가 없다면 \'필요 없음\'이라고 적어주세요. ')
categorize_by_fontsize = []

custom_fontsize_book_layout = ['장 제목','소제목','각주','내주', '일반']
if font_based_text == '예':
    for item in custom_fontsize_book_layout:
        book_fontsize = int(input(f'{item} 폰트 사이즈: '))
        if book_fontsize == '필요없음':
            book_fontsize = None
        categorize_by_fontsize.append(book_fontsize)

# 그림이나 표 인식 필요.

# add to text a '\n' or remove it if the conditions are good.
def categorizing_by_font(text: str, fontsize: float) -> str:
    pass

# 언어모델에 돌리는 걸 아래에서 하면 모든 귀찮은게 해결되겟는데?
    

import time

t1 = time.time()



# 없음이면 false 처리.
if enter_condition == '없음':
    enter_condition = False
if watermark == '없음':
    watermark = ''
if english_remove_by_font == '예':
    english_remove_by_font = True
else:
    english_remove_by_font = False


# user_input = input(prompt="파일 이름을 적어주세요!")

import pdfplumber
import re
from pykospacing import Spacing

rule_csv_path = "rules/test.csv"

# ok. applied completed.
spacing = Spacing()
# spacing.set_rules_by_csv(rule_csv_path, "단어")
# 이 기능은 조금 조심해서 써야 할듯. '번 져'가 되는 경우가 있음. 몇 번 져도 등...

# 우선, 워터마크 지우기 기능 필요. "무단복제 및 유출금지"


def setLayout(page: list) -> tuple:
    with pdfplumber.open(path, pages = [layout_page, layout_page+1], laparams=None) as pdf:   
        x0 = 100000 # max position.
        top = 100000 # max position.
        x1 = 0
        bottom = 0

        for page in pdf.pages:
            for word in page.extract_words():
                if word['x0'] < x0:
                    x0 = word['x0'] 
                if word['top'] < top:
                    top = word['top']
                if word['x1'] > x1:
                    x1 = word['x1']
                if word['bottom'] > bottom:
                    bottom = word['bottom']
        
        return (x0 , top - 10, x1, bottom - 10)

def needEnter(word):
    # 여기서부터 작성 시작.

    # 'ldquot라고'가 있으면 enter x.

    lsquot = '\u2018'
    rsquot = '\u2019' # 이거랑 
    ldquot = '\u201C'
    ldquot = '\u201D' # 이게 중요하네.
    # "— "는 파이썬에서 "\u2014 "
    pattern = r'[.!?][\u201D\u2019]'
    if re.search(pattern, word):
        return True
    else:
        return False

# 이게 한 문장에서만 적용되는게 아니라 여러 문장이 있는 글에서도 적용되게 해달라고 하자.
# 메멘토모리에서 문제발생.
def process_words(words_in_range):
    n_pattern = r'[.!?][\u201D\u2019]'
    f_pattern = r'[\u201D\u2019]'
    quotes_indices = []
    for idx, word in enumerate(words_in_range):
        if '\u2018' in word or '\u201C' in word:
            # 어차피 무조건 [0]에 위치하기에 그냥 idx만 append.
            sum_count = word.count('\u2018')+word.count('\u201C')
            [quotes_indices.append(idx) for i in range(sum_count)]
        # 만약 match되면, 그리고 quotes_indices이면
        if re.search(f_pattern, word):
           if re.search(n_pattern, word) and quotes_indices:
                # 해당하는 곳 앞에 '\n'를 넣어줌.
                words_in_range[quotes_indices[0]] = '\n' + words_in_range[quotes_indices[0]]
                # 맨 처음 들어온 것을 지움. queue로도 구현 가능할듯.
                quotes_indices.pop(0)
           else:
                # 그냥 강조 부분이라면 삭제함. 뒤에서부터 삭제해야 함.
                quotes_indices.pop()   
    return words_in_range

def eliminate_space(words_in_range):
    temp = []
    pattern = r'[.!?]'
    for idx, item in enumerate(words_in_range):

        # if temp.append()

        if item.find('*') > -1:
            if re.search(pattern, words_in_range[idx-1]) is not None:
                temp.append(' '+item.replace('*',''))
            else:
                # 바로 뒤 단어를 파악하며 spacing으로 검사하고 대체함.
                s = item.replace('*', '')
                l_item = temp.pop()
                if not l_item: # 빈 string이면.
                    l_item = temp.pop()
                if s.find('\n') != -1:
                    s = spacing(l_item+ s) + '\n'    
                else:
                    s = spacing(l_item+ s)
                
                temp.append(' '+s)
        
        # space만 넣고 반환.
        else:
            temp.append(' '+ item) 

    return temp





# path = r"C:\Users\82104\PythonWorkspace\script_tuning_project\pdf\열림원_메멘토 모리.pdf"
path = r"pdf\원고_매우예민한사람들을위한상담소.pdf"

contents = ['데미안', '두 개의 세계']

page_range = range(start_page, 60
)


# 다음 코드로 텍스트를 모두 뽑아왔음. 이제 적절한 가공을 거치자.
# needEnter 부분 가공 시작.

# 데미안 기준.
# x0: 104 x1 = 360
# top: 79 bottom: 527 (페이지 부분) bottom-글자: 490
# upright랑 direction. 
# 메멘토모리 기준.

line_height_threshold = 25  # 줄 바꿈을 삽입할 최소 간격

words_in_range = []
last_y1= None
last_x1=None
last_word=''

'''
워터마크 제거하기: 
word를 print하여 워터마크가 특정 위치이고, (불가능)
어떤 글자인지 파악하여 제거할 수도 있다. (불가능)
워터마크가 하나로 합쳐져 있는 형태임. PDF 폰트를 확인하여 수정하는 방법 고려.
extra_attrs=[]를 확인하자...

정 안되면 char별로 인식하여 합치는 방식으로 해야할 수도 있음. 
이럼 새로 짜야지..

'''

# word에서 ' 혹은 "을 감지하면
# line을 생성하고, 만약 정규식 패턴이 감지가 된다면.
# 앞에 \n, 뒤에 \n를 생성하면 된다. 


leftmost, topmost, rightmost, bottommost = (setLayout(layout_page))



with pdfplumber.open(path, pages = page_range, laparams=None) as pdf:   
    
    page_shifted = False
    for page in pdf.pages:
        page = page.crop((leftmost, topmost, rightmost, bottommost))
        if len(page.extract_words()) < 20: # 챕터를 나타내는 등 짧은 페이지 넘기는 용도.
            continue
        
        # initialization
        x0, y0, x1, y1 = (0,0,0,0)
        for word in page.extract_words(use_text_flow=True, extra_attrs=['size', 'fontname', 'stroking_color', 'non_stroking_color']):
            # font-size problem: floating points...
            # print(word)
            x0, y0, x1, y1 = map(float, (word['x0'], word['top'], word['x1'], word['bottom']))
            # 이건 페이지 넘어가면서 새로운 주제일 때.
            # .으로 끝나고, 페이지 끝날 때의 y좌표가 가장 아래가 아니면. 
            if page_shifted is True:
                page_shifted = False
                if last_word.count('.') > 0 and last_y1 < (bottommost - 55)  :
                    words_in_range.append('\n'+word['text'])
                    last_x1 = x1
                    last_y1 = y1
                    continue
            #  가장 아래면 x1이 가장 오른쪽에 가깝지 않으면.
                else:
                    if last_word.count('.') > 0 and last_x1 <= rightmost and last_x1 > rightmost - 20 :
                        words_in_range.append('\n'+word['text'])
                        last_x1 = x1
                        last_y1 = y1
                        continue

            # 다음 문장으로 넘어가는 부분은 무조건 붙이기. 그리고 append은 false로.
            # 단, 전 text에 .이 있으면 넘어감... 여기서 바로 spacing을 해버리자.
            if word['non_stroking_color'] != (0,0,0,1):
                print(word['text'], word['non_stroking_color'])
            # 색 있으면 non-stroking_color: [1]임.
            # 검은색이면 non-stroking_color: (0,0,0,1)임
            # 하얀색이면 non-stroking_color: (0,0,0,0)임


            if last_x1 is not None and last_x1 - x0 > 200:
            
                # word['text'] = spacing()
                word['text'] = '*'+ word['text']

            # 이전 단어와의 수직 간격이 충분히 크면 줄 바꿈을 추가
            if last_y1 is not None and y0 - last_y1 > line_height_threshold:
                word['text'] = '\n'+ word['text']

            # 수직 간격이 없어도, .이 없이 들여쓰기가 되면 소제목으로 간주.

            # 단, 폰트가 소제목이라면 아니다!

            # 엔터 필요한 조건이면 엔터 추가.
            if needEnter(word['text']):
                word['text'] = word['text']+'\n'
            words_in_range.append(word['text'])
            last_x1 = x1
            last_y1 = y1
            last_word = word['text']
        
        # 페이지 전환.
        page_shifted = True

        # 워터마크 제거.
        if watermark:
            for i in range(len(watermark)):
                if watermark[0] == words_in_range[-1][-1]:
                    words_in_range[-1] = words_in_range[-1][0:-1]
                    if words_in_range[-1][0] == '*':
                        words_in_range[-1] = words_in_range[-1][1:]
                else:
                    words_in_range.pop()
                

processed_list = process_words(words_in_range)
processed_list = eliminate_space(processed_list)
processed_list[0] = processed_list[0][1:]

# PyKoSpacing 적용해보기. 띄어쓰기가 되어있지 않은 애들에게 적용. 이상한 띄어쓰기에는 적용 안됨.
# processed_string = ''.join(processed_list)
# processed_string = spacing(processed_string)


with open('HSP_testing.txt', 'w', encoding='utf-8') as f:
    f.write(''.join(processed_list))

t2 = time.time()


print(f"소요시간: {t2-t1: .2f}초.")
# 데미안 completed.

 # 다음 문장으로 넘어가는 부분은 무조건 붙이기. 그리고 append은 false로.
            # 단, 전 text에 .이 있으면 넘어감... 여기서 바로 spacing을 해버리자.




# testing.


# if last_x1 is not None and last_x1 - x0 > 200:
#     word['text'] = spacing()
#     word['text'] = '*'+ word['text']


# def space_making(word: str)  -> str:
    
#     word = spacing(word + words_in_range.pop())