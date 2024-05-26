# 하기 전 word로 변환
# ❹: 이 문자를 통으로 바꿔줍니다.
# 메모장으로 변환할 부분만 처음부터 끝까지 복붙.

# input: "파일이름.txt" 입력.

# 책 제목과 목차 입력.
'''
파일 이름을 적어주세요: "파일입력.txt"

책 제목: "데미안"
시작하는 페이지 번호: 
목차 입력하기: 
0. 서문
1. 데미안
2. 허스트
3. 새로운 달
4. 눈 세모나게 떠
5. 눈 네모나게 떠
6. 저 맘에 안들죠?
'''

# 인용어구 제거하는 법 알아야 함...

# 기본: 한글, “ ”, ‘’, (안에 있는 것 또한 제거. optional), —내부 설명— 도 삭제...
# 한자도 싹 다 삭제 필요.
# 문장부호 !?. 빼고 다 제거. 

# 패턴1: “가 있으면 새로운 슬라이드를 제작해야 한다. (대화 부분) => “앞에 엔터 삽입. 뒤에 “가 나오면 끝. Enter. (예외 case, “ 뒤에 직접 인용어구 ex) 
# “ ”난 최고가 되겠어!”라고 그걸 어떻게 말해?”라고 하는 경우

#패턴2: ‘블라블라블라 이후 문장마침표.!?‘ 가 같이 존재하면 새로운 슬라이드를 제작해야 한다.
# (독백 부분) => 엔터 삽입.  \n ‘ 블라블라블라 . or ! or ? 그리고 ‘ \n


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


# 없음이면 false 처리.
if enter_condition == '없음':
    enter_condition = False


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


def readPdfByPosition():
    pass



def isInContents(page, line) -> bool:
    '''''''''''''''
    function description: return bool.
    if line has a page and contents name, it will be removed.
    '''''''''''''''
    # line 안에서 page도 포착하면
    # line 안에서 contents와 title을 포착해보기. 만약 존재한다면
    # True 반환.

    #   \t\n도 존재함..

    # 숫자이니 이렇게 만듦.
    page = str(page)

    if (line == page+'\n'):
        return True

    if page in line: 
        for content in contents:
            if content in line:
                return True
            else:
                continue
    else:
        return False
    


def isOnlyEnter(line) -> bool:
    '''''''''''''''
    function description: return bool.
    if line has only enter, it will be replaced with spacebar.
    '''''''''''''''

    # 문장종결표현 혹은 다른 것들이 있으면 enter가 없음.

    if line == "\n":
        return True
    else:
        return False

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
            quotes_indices.append(idx)
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
                # 바로 뒤 문맥을 파악하며 spacing으로 검사하고 대체함.
                s = item.replace('*', '')
                s = spacing(temp.pop() + s)
                temp.append(' '+s)

        else:
            temp.append(' '+ item) 

    return temp

def replaceChar(line):
    # '\u3000'을 ' '로 대체.

    line.replace('\n', ' ')
    pass
    return line
outfile = ''

print(path)

'''
여기 부분은 지워야 함.
'''

# 워터마크 관련.


# path = r"C:\Users\82104\PythonWorkspace\script_tuning_project\pdf\열림원_메멘토 모리.pdf"
path = r"pdf\열림원_메멘토 모리.pdf"

contents = ['데미안', '두 개의 세계']


page_range = range(start_page, 32)


# 다음 코드로 텍스트를 모두 뽑아왔음. 이제 적절한 가공을 거치자.
# needEnter 부분 가공 시작.

# 데미안 기준.
# x0: 104 x1 = 360
# top: 79 bottom: 527 (페이지 부분) bottom-글자: 490
# upright랑 direction. 
# 메멘토모리 기준.

x_min, x_max = 60, 380 # 왼쪽부터 오른쪽으로. 그리고 비율인듯.
y_min, y_max = 60, 510 # 위부터 아래로 내려감.
line_height_threshold = 15  # 줄 바꿈을 삽입할 최소 간격

words_in_range = []
last_y1= None
last_x1=None

'''
워터마크 제거하기: 
word를 print하여 워터마크가 특정 위치이고,
어떤 글자인지 파악하여 제거할 수도 있다.
print(word) 해보기.
'''


# word에서 ' 혹은 "을 감지하면
# line을 생성하고, 만약 정규식 패턴이 감지가 된다면.
# 앞에 \n, 뒤에 \n를 생성하면 된다. 

with pdfplumber.open(path, pages = page_range, laparams=None) as pdf:
    
    for page in pdf.pages:
        page.crop((x_min, y_min, x_max, y_max))
        if len(page.extract_words()) < 20: # 챕터를 나타내는 등 짧은 페이지 넘기는 용도.
            continue
        for word in page.extract_words():
            x0, y0, x1, y1 = map(float, (word['x0'], word['top'], word['x1'], word['bottom']))
            # 코드 가독성을 위하여 이 부분 crop으로 대체 생각하기.
            if x_min <= x0 and x1 <= x_max and y_min <= y0 and y1 <= y_max:
                print(word)
                
                # 다음 문장으로 넘어가는 부분은 무조건 붙이기. 그리고 append은 false로.
                if last_x1 is not None and last_x1 - x0 > 200:
                    word['text'] = '*'+ word['text']

                # 이전 단어와의 수직 간격이 충분히 크면 줄 바꿈을 추가
                if last_y1 is not None and y0 - last_y1 > line_height_threshold:
                    word['text'] = '\n'+ word['text']

                if needEnter(word['text']):
                    word['text'] = word['text']+'\n'
                words_in_range.append(word['text'])
                last_x1 = x1
                last_y1 = y1
                appending = True
                # print(word)

processed_list = process_words(words_in_range)
processed_list = eliminate_space(processed_list)
processed_list[0] = processed_list[0][1:]

# PyKoSpacing 적용해보기. 띄어쓰기가 되어있지 않은 애들에게 적용. 이상한 띄어쓰기에는 적용 안됨.
# processed_string = ''.join(processed_list)
# processed_string = spacing(processed_string)



with open('memento-mori.txt', 'w', encoding='utf-8') as f:
    f.write(''.join(processed_list))
    
# 데미안 completed.