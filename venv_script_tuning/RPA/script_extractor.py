import time
t1 = time.time()

import os
import pdfplumber
import re
from pykospacing import Spacing
from typing import List 
from kiwipiepy import Kiwi
import csv


def _replace_to_single_double_quote(text: str) -> str:
    """
    (와 )도 SSO, SSC로 분류되는데, 이건 사람이 직접 다 확인하고, 제거해야 한다.
    특수문자 보관함:
    ●
    """    
    # 왜 안됨? .replace("ʼ", "'")\ 여기 여는 작은따옴표 추가 필요.
    text = text.replace("\u201C", "'")\
                .replace("·", ", ")\
                .replace("–", "-")\
                .replace("－", "-")\
                .replace("｜", "|")\
               .replace("㈜ ", "주식회사 ")\
               .replace("∼", "~")\
               .replace("\u201D", "'")\
               .replace("\u2018", "'")\
               .replace("\u2019", "'")\
               .replace("\u201D", "'")\
               .replace("․", ".")\
               .replace('「', "'")\
               .replace('」', "'")\
               .replace('『', "'")\
               .replace("』", "'")\
               .replace("〈", "'")\
               .replace("〉","'") \
               .replace("・ ", ", ") \
               .replace(" ・", ", ") \
               .replace("・", ", ") \
               .replace("～", "~")\
               .replace("＇", "'")\
               .replace("×", "x")\
                .replace("‟", "'")\
                .replace("`", "'")\
                .replace("´", "'")\
                .replace("ʼ", "'")\
                .replace("‘", "'")\
                .replace("’", "'")\
                .replace("‚", "'")\
                .replace("‛", "'")\
                .replace("“", "'")\
                .replace("”", "'")\
                .replace("„", "'")\
                .replace("′", "'")\
                .replace("″", "'")\
                .replace("‵", "'")\
                .replace("‶", "'")\
                .replace("❛", "'")\
                .replace("❜", "'")\
                .replace("❝", "'")\
                .replace("❞", "'")\
                .replace("❟", "'")\
                .replace("❠", "'")\
                .replace("⹂", "'")\
                .replace("〃", "'")\
                .replace("〝", "'")\
                .replace("〞", "'")\
                .replace("〟", "'")\
                .replace("＂", "'")\
                .replace("＇", "'") \
                .replace("  ", " ")\
               .replace("	", " ")
    
    return text



def convert_fontcolor_to_tuple(fontcolor: any) -> tuple: # Union[tuple(int, ...), List[int]]
    # black
    if fontcolor == (0,0,0,1):
        return (1,0,0)
    
    # white
    if fontcolor == (0,0,0,0):
        return (0,1,0)

    # others
    return (0,0,1)


class ScriptExtractor:
    '''
    #### class variable: share all things inside the ScriptExtractor class for a book. 
    document: to handle .docx extension.
    spacing: whether is neccessary for space or not, checking the space
    must be needed between the first word of newline 
    and last word of prev line.
    title: title of book.
    categorize_by_fontsize: classify the words whether insert newline or not.
    contents: contain contents in this book.
    layout_page: set standard for determining the coordinates of page.
    watermark: if there is watermark, it should be eliminated.
    remove_english_footnote: remove english footnote for korean book.
    remove_english_intext_citation: remove english intext citation for korean book.
    ------
    '''    
    path = ''
    title = ''    
    watermark = False
    output_path = ""
    even_layout_location = {'leftmost': 10000, 
                        'topmost':10000, 
                        'rightmost':0, 
                        'bottommost':0,
                        }
    odd_layout_location = {'leftmost': 10000, 
                        'topmost':10000, 
                        'rightmost':0, 
                        'bottommost':0,
                        }
    kiwi = Kiwi(model_type='sbg')
    NEWLINE_SPACE = 25 # Could be Hypertuned(얘는 커도 괜찮을꺼임.)
    PARAGRAPH_SPACE = 5 # Could be Hypertuned
    LINE_HEIGHT_THRESHOLD = 25 # Could be Hypertuned
    filtered_chars = set()
    spacing = None
    allow_hanja = None
    ACCESS_PTRN = None
   
    # @property
    # def get_categorize_by_font(self):
    #      return self.__class__.categorize_by_font

    @classmethod
    def set_option(cls, path:str, output_path:str,  LINE_HEIGHT_THRESHOLD=15,
                    PARAGRAPH_SPACE = 5,
                    NEWLINE_SPACE=25,
                    allow_hanja=False,
                    watermark=False, # not supported.
                    ) -> None:
        try:        
            cls.output_path = output_path
            cls.path = path
            cls.watermark = watermark
            cls.LINE_HEIGHT_THRESHOLD = LINE_HEIGHT_THRESHOLD
            cls.PARAGRAPH_SPACE = PARAGRAPH_SPACE
            cls.NEWLINE_SPACE = NEWLINE_SPACE
            cls.allow_hanja = allow_hanja
            
            # 한영프독스페인
            spanish_specific = r"\u00C1\u00E1\u00C9\u00E9\u00CD\u00ED\u00D3\u00F3\u00DA\u00FA\u00D1\u00F1\u00DC\u00FC\u00A1\u00BF"
            french_specific = r"\u00C0-\u017F"
            german_specific = r"\u00C4\u00E4\u00D6\u00F6\u00DC\u00FC\u00DF"
            
            if allow_hanja:
                cls.ACCESS_PTRN = re.compile("[" + r"^가-힣ㄱ-ㅎㅏ-ㅣ0-9a-zA-Z一-龥\s'\"@_#$\^&*\(\)\-=+<>\/\|}{~:…℃±·°※￦\[\]÷\\;," + spanish_specific + french_specific + german_specific + "]")                
            else:
                cls.ACCESS_PTRN = re.compile("[" + r"^가-힣ㄱ-ㅎㅏ-ㅣ0-9a-zA-Z\s'\"@_#$\^&*\(\)\-=+<>\/\|}{~:…℃±·°※￦\[\]÷\\;," + spanish_specific + french_specific + german_specific + "]")                

                
            custom_layout_by_font_list = []
            #TODO: 폰트 기반 분류 작업들...
            # user_font_input = str(input("더 입력하시겠습니까? 그러시려면 전과 같이 입력해주세요. \n \
            #                                 아니라면 '끝'이라고 입력해주세요: "))
            # while user_font_input != "끝":
            #     user_font = user_font_input.replace(' ', '').split(',')
            #     user_font[1] = round(float(user_font[1]),1)
            
            #     if user_font[2] == '검':
            #         user_font[2] = (1,0,0)
            #     elif user_font[2] == '흰':
            #         user_font[2] = (0,1,0)
            #     else:
            #         user_font[2] = (0,0,1)
                
            #     custom_layout_by_font_list.append(user_font)
            #     user_font_input = str(input("더 입력하시겠습니까? 그러시려면 전과 같이 입력해주세요. \n \
            #                                 아니라면 '끝'이라고 입력해주세요."))
                
            # # custom_layout_by_font_list: [['본문', 11, (0,0,1)], ]
            # cls.categorize_by_font = {(i[1],i[2]):i[0] for i in custom_layout_by_font_list}
            # # {"11, (1,0,0)": "본문"}
        except Exception as E:
            raise E

    def __init__(self, pages:List[int], excluded_lines_count_odd=1, 
                 excluded_lines_count_even=1,
                  layout_pages=None) -> None:
        self.pages = pages
        self.last_word = {
                        'x0': None, 
                        'top':None, 
                        'x1':None, 
                        'bottom':None,
                        'text':''
                        }
        self.even_layout_location = {
                        'leftmost': 10000, 
                        'topmost':10000, 
                        'rightmost':0, 
                        'bottommost':0,
                        }
        self.odd_layout_location = {
                        'leftmost': 10000, 
                        'topmost':10000, 
                        'rightmost':0, 
                        'bottommost':0,
                        }
        self.image_page = []
        self.images = {}
        self.excluded_lines_count_even = excluded_lines_count_even
        self.excluded_lines_count_odd = excluded_lines_count_odd
        self.layout_pages = layout_pages
        self.max_freq_font_size = 0

    # @classmethod
    # Input: 모든 줄글.
    # Output: 모든 줄글에 레이블링한 것이 결과가 된다.
    # make model로 모델을 만들고, 이걸 cls.method나 variable로 저장.
    # 이후, 이걸 self.page_range에 맞게 한번에 대입하도록 만듦.
    # def classify_word_by_font(
    #     cls, 
    #     word:str, 
    #     fontsize: float,
    #     x0: float,
    #     top: float,
    #     fontcolor: any # tuple(int,...) | List[int]
    #     ) -> str: # tuple(int) | List[int]

    #     # 서문은 어떻게...?
    #     pages = range(int(input("목차를 제외하고 페이지 시작을 입력해주세요.")), int(input("끝 페이지를 입력해주세요"))+1)
    #     with pdfplumber.open(cls.path, pages=pages, laparams=None) as pdf:  
    #         page_shifted = False
            
    #         leftmost, topmost, rightmost, bottommost = [i for i in cls.layout_location.values()]



    #         for idx, page in enumerate(pdf.pages):
    #             page = page.crop((leftmost, topmost, rightmost, bottommost))             

    #             for word in page.extract_words(use_text_flow=cls.watermark,
    #                                             extra_attrs=['size', 'fontname', 'stroking_color', 'non_stroking_color']):
    #                 pass
        
    def _only_accessed_char(self, text:str) -> str:
        substrated_text = self.__class__.ACCESS_PTRN.sub("", text)
        if substrated_text != text and self.__class__.ACCESS_PTRN.search(text).group() not in self.__class__.filtered_chars:
            filtered_char = self.__class__.ACCESS_PTRN.search(text).group()
            self.__class__.filtered_chars.add(filtered_char)
            f = open("문제될만한 글자들.txt", "a", encoding='utf-8-sig')        
            f.write(filtered_char+"\n")
            f.close()

        return substrated_text.strip()

    def set_new_layout(self):
        try:
            """
            Set the page layout by odd and even
            without page_num or upper decoration.
            """
            print("레이아웃 설정")
            layout_t1 = time.time()
            
            layout_pages = None
            if self.layout_pages:
                layout_pages = self.layout_pages
            else:
                layout_pages = self.pages

            with pdfplumber.open(self.__class__.path, pages=layout_pages, laparams=None) as pdf:   
                # 마지막 line이 몇 개인지 사용자 입력, 테스트 등으로 파악해두는게 필요할듯.
                even_standard_page = ""
                odd_standard_page = ""
                for page in pdf.pages:
                    page_lines = page.extract_words(keep_blank_chars=True)
                    page_x0, page_top, page_x1, page_bottom = page.bbox
                    
                    prev_even = self.even_layout_location.copy()
                    prev_odd = self.odd_layout_location.copy()
                    for idx, line_dict in enumerate(page_lines):
                        if (
                            line_dict['bottom'] > page_bottom
                            or line_dict['x1'] > page_x1
                            or line_dict['top'] < page_top
                            or line_dict['x0'] < page_x0
                            ):
                            continue    # 아예 미반영.

                        if page.page_number % 2 == 0:
                            if len(page_lines) - self.excluded_lines_count_even <= idx:
                                break
                            # 마지막 line이 몇 개인지
                            self.even_layout_location['leftmost'] = min(self.even_layout_location['leftmost'], line_dict['x0'])
                            self.even_layout_location['topmost'] = min(self.even_layout_location['topmost'], line_dict['top']) 
                            self.even_layout_location['rightmost'] = max(self.even_layout_location['rightmost'], line_dict['x1']) 
                            self.even_layout_location['bottommost'] = max(self.even_layout_location['bottommost'], line_dict['bottom'])
                            for prev_val, cur in zip(prev_even.values(), self.even_layout_location.values()):
                                if prev_val != cur:
                                    even_standard_page = str(page.page_number)
                                    

                        else:
                            if len(page_lines) - self.excluded_lines_count_odd <= idx:
                                break

                            self.odd_layout_location['leftmost'] = min(self.odd_layout_location['leftmost'], line_dict['x0'])
                            self.odd_layout_location['topmost'] = min(self.odd_layout_location['topmost'], line_dict['top']) 
                            self.odd_layout_location['rightmost'] = max(self.odd_layout_location['rightmost'], line_dict['x1']) 
                            self.odd_layout_location['bottommost'] = max(self.odd_layout_location['bottommost'], line_dict['bottom'])                        
                            for prev_val, cur in zip(prev_odd.values(), self.odd_layout_location.values()):
                                if prev_val != cur:
                                    odd_standard_page = str(page.page_number)


                if self.even_layout_location['bottommost'] == 0:
                    self.even_layout_location = None
                if self.odd_layout_location['bottommost'] == 0:
                    self.odd_layout_location = None
                
            layout_t2 = time.time()       
            try:
                output_dir = self.__class__.output_path + f"/{self.__class__.path[self.__class__.path.rfind('/')+1:].replace('.pdf','')}_레이아웃/"
                os.mkdir(output_dir)
            except:
                pass
            f = open(f"{output_dir}레이아웃_기준_{layout_pages[0]}_{layout_pages[-1]}.txt", 'w', encoding='utf-8-sig')
            f.write(f"홀수 기준 페이지: {odd_standard_page}\n")
            f.write(f"짝수 기준 페이지: {even_standard_page}\n")
            f.close()

            print(f"레이아웃 설정 완료. 시간:{(layout_t2 - layout_t1):.2f}초")
            print(f"레이아웃: 짝수 페이지: {self.even_layout_location}, \n 홀수 페이지: {self.odd_layout_location}")
        except Exception as E:
            raise E


    def layout_checker(self, layout_filename):
        try:
            try:
                output_dir = self.__class__.output_path + f"/{self.__class__.path[self.__class__.path.rfind('/')+1:].replace('.pdf','')}_레이아웃/"
                os.mkdir(output_dir)
                print(f"시작: {layout_filename}")
            except:
                print(f"건너뛰기: {layout_filename}")
                pass

            # txt_filepath = self.__class__.output_path + f"{title}/"+ title + '_' + str(self.pages[0]) +'-' + str(self.pages[-1])+ "_레이아웃_외부텍스트" +'.txt'
            txt_filepath = output_dir + layout_filename
            
            with pdfplumber.open(self.__class__.path, pages=self.pages, laparams=None) as pdf, \
                open(txt_filepath, 'w', encoding='utf-8-sig') as ofile \
                : 
                ofile.write(f"제외된 홀수 페이지 줄 수: {self.excluded_lines_count_odd}\t")
                ofile.write(f"제외된 짝수 페이지 줄 수: {self.excluded_lines_count_even}\n")
                

                for page_order, page in enumerate(pdf.pages):
                    # 홀수, 짝수 페이지 별로 layout 설정.
                    leftmost, topmost, rightmost, bottommost = (0, 0, 0, 0)
                    if page.page_number % 2 == 0 and self.even_layout_location != None:
                        leftmost, topmost, rightmost, bottommost = [i for i in self.even_layout_location.values()]
                    elif page.page_number % 2 == 1 and self.odd_layout_location != None:
                        leftmost, topmost, rightmost, bottommost = [i for i in self.odd_layout_location.values()]

                    if (leftmost, topmost, rightmost, bottommost) != (0,0,0,0):
                        page = page.outside_bbox((leftmost, topmost, rightmost, bottommost))
                    else:
                        pass # 그냥 crop을 하지 않아야 하는 케이스
                    # for line in page.extract_words(keep_blank_chars=True):
                    ofile.write('\n'.join((f"페이지: {page.page_number}쪽, 텍스트: {line['text']}"for line in page.extract_words(keep_blank_chars=True))))
                    ofile.write('\n')

            print("layout_checker done!")
        except Exception as e:
            raise e
            
    def fontsize_counter(self):
        with pdfplumber.open(self.__class__.path, pages=self.pages, laparams=None) as pdf \
            :  
            # pre: set_new_layout() 이전에 되어 있어야 함.

            font_size_counter = {} 
            for page_order, page in enumerate(pdf.pages):
                # 홀수, 짝수 페이지 별로 layout 설정.
                leftmost, topmost, rightmost, bottommost = (0, 0, 0, 0)
                if page.page_number % 2 == 0 and self.even_layout_location != None:
                    leftmost, topmost, rightmost, bottommost = [i for i in self.even_layout_location.values()]
                elif page.page_number % 2 == 1 and self.odd_layout_location != None:
                    leftmost, topmost, rightmost, bottommost = [i for i in self.odd_layout_location.values()]

                if (leftmost, topmost, rightmost, bottommost) != (0,0,0,0):
                    page = page.crop((leftmost, topmost, rightmost, bottommost))
                else:
                    pass # 그냥 crop을 하지 않아야 하는 케이스

                page_words = page.extract_words(extra_attrs=["size"])
                for idx, word_dict in enumerate(page_words):
                    word_text = _replace_to_single_double_quote(word_dict['text']) # 그리고 나서 line별로 다 replace로 바꾸고,                    #TODO: 숫자가 있고, 뒤에 글자(한글, 영어, 특수문자 존재 시 붙여쓰기 만들기)
                    word_text = self._only_accessed_char(word_text)
                    word_dict['text'] = word_text
                    if font_size_counter.get(round(word_dict['size'])):
                        font_size_counter[round(word_dict['size'])] += 1
                    else:
                        font_size_counter[round(word_dict['size'])] = 1

            max_key = max(font_size_counter, key=font_size_counter.get)

            self.max_freq_font_size = max_key
            print(f"가장 많이 나온 폰트 사이즈: {max_key}")


    def read_pdf_v2(self,
                    title:str,
                    read_line_with_word=True, 
                    check_overwritten_word=True, 
                    extract_image=True,
                    text_flow=True,
                    robust_spacing=False,
                    check_space_with_ko_eng=True,
                    check_space_with_num_char=True,
                    )-> None:
        
        try:
            if robust_spacing:
                self.__class__.spacing = Spacing()            
            # 한자모드

            #TODO: sample 페이지로 layout 설정하는 과정 무조건 필요!
            # 홀수, 짝수 페이지로 layout 설정하고,
            # 그리고 나서 line별로 다 replace로 바꾸고,
            # line 별 x와 y있고, 맨 마지막이 .!?이라면 여기까지 glue 써주고 txt에 써주고.
            # 만약 line 별 x가 연속적으로 최대값 전 즈음이면 그냥 붙여준 다음 .붙여주기도 하고.
            # (보통 소주제 같은 것들)
            # line에서 x가 맨 끝이 아닌데 .이 있으면 또 . 넣어주고.
            # 만약 line에서 y가 큰 간격이라면 사이에 엔터 넣어주고.
            # 만약 문단 변화가 있는 곳에서 엔터를 넣는 옵션을 준다면 거기서 엔터를 또 넣어주고.
            try:
                os.mkdir(self.__class__.output_path + f"/{title}/")
                print(f"시작: {title}")
            except:
                print(f"건너뛰기: {title}")
                pass
            
            if check_space_with_ko_eng:
                NO_SPACE_WITH_KO_ENG_PTRN =  re.compile(r"[가-힣0-9]+[A-Za-z]+")
            if check_space_with_num_char:
                EXIST_SPACE_WITH_NUM_CHAR_PTRN =  re.compile(r"[0-9]+\s+[가-힣A-Za-z]+")

            SPECIAL_CHAR_PTRN = re.compile(r'[ㄱ-ㅎㅏ-ㅣ@_#$\^&*\(\)\-=+<>\/\|}{~:…℃±·°※￦\[\]÷\\;]')
            
            warning_line_file_path = self.__class__.output_path + f"/{title}/"+ title+ '_' + str(self.pages[0]) +'-' + str(self.pages[-1])+'_확인 필요 단어.csv'
            txt_filepath = self.__class__.output_path + f"/{title}/"+ title+ '_' + str(self.pages[0]) +'-' + str(self.pages[-1])+ "_pdf에서 텍스트" +'.txt'
            print(txt_filepath)

        
            with pdfplumber.open(self.__class__.path, pages=self.pages, laparams=None) as pdf, \
                open(txt_filepath, 'w', encoding='utf-8-sig') as ofile, \
                open(warning_line_file_path, 'a', encoding='utf-8-sig', newline='') as csvf \
                :  
                # pre: set_new_layout() 이전에 되어 있어야 함.

                font_prop = {} 
                lines = []
                file_wrote_flag = False
                sent = ""
                prev_line = None
                diff_size_words_list = []
                csv_writing = False
                file_exists = os.path.isfile(warning_line_file_path) and os.path.getsize(warning_line_file_path) > 0
                csv_writer = csv.writer(csvf)

                for page_order, page in enumerate(pdf.pages):
                    # 홀수, 짝수 페이지 별로 layout 설정.
                    leftmost, topmost, rightmost, bottommost = (0, 0, 0, 0)
                    if page.page_number % 2 == 0 and self.even_layout_location != None:
                        leftmost, topmost, rightmost, bottommost = [i for i in self.even_layout_location.values()]
                    elif page.page_number % 2 == 1 and self.odd_layout_location != None:
                        leftmost, topmost, rightmost, bottommost = [i for i in self.odd_layout_location.values()]

                    if (leftmost, topmost, rightmost, bottommost) != (0,0,0,0):
                        page = page.crop((leftmost, topmost, rightmost, bottommost))
                    else:
                        pass # 그냥 crop을 하지 않아야 하는 케이스
                    # if page.annots:
                    #     print('annots가 있는 페이지',page.page_number)
                    # # print(page)
                    
                    # check table, image, etc ... instance
                    if (
                        len(page.edges) >= 4 # 곡선, 선, 사각형 등 다 포함. 이것도 수정할 수 있는 부분으로...?
                        or page.images
                        ):
                        print(page.page_number)
                        self.image_page.append(str(page.page_number))
                        if extract_image:
                            try:
                                os.mkdir(self.__class__.output_path + f"/{title}/확인할 페이지 이미지")
                            except:
                                pass
                            im_path = self.__class__.output_path + f"/{title}/"+f"확인할 페이지 이미지/{page.page_number}.png"
                            page.to_image(resolution=128).save(im_path, format="PNG") # 약 6초 걸림.

                    # TODO:페이지 폰트 사이즈 중 가장 큰 경우 제외한 나머지만 모두 추출.
                    # 가다가 flag 켜지면 끝날 때까지 계속 그 사이즈일 때까지 기억하고 csv에 저장. 그 이후 다시 최다 빈도 문자가 나오면 다시 꺼짐.                    
                    for word_dict in page.extract_words(extra_attrs=['size']):
                        if self.max_freq_font_size == round(word_dict['size']):
                            if csv_writing: # write not a main text.
                                if not file_exists:
                                    header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                                    csv_writer.writerow(header)
                                    file_exists = True
                                problematic_line_text = ' '.join(diff_size_words_list)
                                csv_writer.writerow([problematic_line_text, problematic_line_text, f"{page.page_number}페이지", "글자 사이즈 변화 주의"])
                                csv_writing = False
                                diff_size_words_list.clear()
                            else: # just a main text.
                                pass

                        else: # not a main text.
                            diff_size_words_list.append(word_dict['text'])
                            csv_writing = True

                    if read_line_with_word:
                        page_lines = page.extract_words(keep_blank_chars=True, use_text_flow=text_flow)            
                    else:
                        page_lines = page.extract_text_lines(layout=False)
                    for idx, line_dict in enumerate(page_lines):
                        # if "당신은" in line_dict['text'] and "감정사슬에" in line_dict['text'] and "묶인" in line_dict['text']:
                        #     print(line_dict['text'])

                        # 문제 생길만한 케이스 처리.
                        exist_bottom_or_top_gap_and_near_x_pos = (check_overwritten_word 
                                                                    and prev_line
                                                                    and (abs(prev_line['bottom'] - line_dict['bottom']) < 1 
                                                                        or abs(prev_line['top'] - line_dict['top'])< 1) # 차이가 1 이하면 검사.  2에서 변경함.
                                                                    and abs(line_dict['x0'] - prev_line['x1']) < 1  # 겹치거나 너무 가까우면.
                                                                    )                    
                        if exist_bottom_or_top_gap_and_near_x_pos:
                            if not file_exists:
                                header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                                csv_writer.writerow(header)
                                file_exists = True
                            csv_writer.writerow([line_text, line_text, f"{page.page_number}페이지 {idx+1}번째 줄 부근", "줄 겹침 주의"])

                        line_text = _replace_to_single_double_quote(line_dict['text']) # 그리고 나서 line별로 다 replace로 바꾸고,                    #TODO: 숫자가 있고, 뒤에 글자(한글, 영어, 특수문자 존재 시 붙여쓰기 만들기)
                        line_text = self._only_accessed_char(line_text)
                        line_dict['text'] = line_text
                        
                        if line_text == "정을 넣어 보자. 마음에 달라붙는 쫄깃한 화법은 표현력(연기력)이 핵심이다.":
                            print(f"line_text: {line_text}")

                        # 텍스트 처리 이후 에러 확인 절차.
                        if check_space_with_ko_eng and NO_SPACE_WITH_KO_ENG_PTRN.search(line_text):
                            if not file_exists:
                                header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                                csv_writer.writerow(header)
                                file_exists = True
                            problematic_line_text = NO_SPACE_WITH_KO_ENG_PTRN.search(line_text).group()
                            csv_writer.writerow([line_text, problematic_line_text, f"{page.page_number}페이지 {idx+1}번째 줄 부근", "한영 띄어쓰기 오류 주의"])

                        if check_space_with_num_char and EXIST_SPACE_WITH_NUM_CHAR_PTRN.search(line_text):
                            if not file_exists:
                                header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                                csv_writer.writerow(header)
                                file_exists = True
                            problematic_line_text = EXIST_SPACE_WITH_NUM_CHAR_PTRN.search(line_text).group()
                            csv_writer.writerow([line_text, problematic_line_text, f"{page.page_number}페이지 {idx+1}번째 줄 부근", "숫자 포함 띄어쓰기 오류 주의"])

                        if SPECIAL_CHAR_PTRN.search(line_text):
                            if not file_exists:
                                header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                                csv_writer.writerow(header)
                                file_exists = True
                            problematic_line_text = SPECIAL_CHAR_PTRN.search(line_text).group()
                            csv_writer.writerow([line_text, problematic_line_text, f"{page.page_number}페이지 {idx+1}번째 줄 부근", "특수문자 혹은 한글 자음 풀어쓰기."])

                                
                        is_over_line_height_threshold = (prev_line and line_dict['top'] - prev_line['bottom'] > self.__class__.LINE_HEIGHT_THRESHOLD)
                        is_final_page_line = (len(pdf.pages)-1 == page_order and len(page_lines)-1 == idx)
                        prev_line_is_last_line = (idx == 0  # prev_page's last line
                                                and prev_line
                                                and prev_line['bottom'] < bottommost - self.__class__.PARAGRAPH_SPACE) # 1. y 끝까지 오지 않은 경우. (이미 glue 되어 있음. 엔터)
                                

                        if (file_wrote_flag 
                            or is_final_page_line # 마지막 페이지의 마지막 부분.
                            or is_over_line_height_threshold
                            ):
                            if is_final_page_line:
                                lines.append(line_text) # 추가하고 glue 처리.

                            if robust_spacing:
                                for line in lines:
                                    if sent == "":
                                        sent = line
                                        continue
                                    sent = sent[0:sent.rfind(' ')+1] \
                                            + self.__class__.spacing(sent[sent.rfind(' ')+1:] + line[:line.find(" ")])\
                                            + line[line.find(" "):]                                   
                            else:    
                                sent = self.__class__.kiwi.glue(lines) # glue를 여기에서만 진행시키기.
                            if is_over_line_height_threshold:
                                sent += '\n'
                            if prev_line_is_last_line:
                                sent += "\n"
                                file_wrote_flag = True
                            
                            #TODO: 이거 지워볼까.
                            sent = sent + ' ' if (sent[-1] != " " and sent[-1] != "\n" ) else sent
                            
                            ofile.write(sent)
                            sent = ""
                            file_wrote_flag = False
                            lines.clear()   

                        if not line_text:
                            continue                   
                        
                        lines.append(line_text)
                        
                        #TODO: 따옴표까지도 따로 분리하는 옵션은 이후 추가 예정.
                        end_punctuation_mark = (len(line_text) >= 2
                                            and (line_text[-1] in ".!?"
                                            or line_text[-2] in ".!?"))
                        
                        x1_pos_is_newline = line_dict['x1'] < rightmost - self.__class__.NEWLINE_SPACE

                        if end_punctuation_mark:                    
                            file_wrote_flag = True                
                        elif x1_pos_is_newline:
                            file_wrote_flag = True
                    
                        prev_line = line_dict


                if diff_size_words_list: # if diff_size words remain,
                        if not file_exists:
                            header = ["문제될 수 있는 줄", "문제될 문자", "위치", "이유"]
                            csv_writer.writerow(header)
                            file_exists = True
                        problematic_line_text = ' '.join(diff_size_words_list)
                        csv_writer.writerow([problematic_line_text, problematic_line_text, f"{page.page_number}페이지 {idx+1}번째 줄 부근", "글자 사이즈 변화 주의"])
                        csv_writing = False
                        diff_size_words_list.clear()

            print("pdf reading done.")
            
        except Exception as E:
            raise E


    def write_reference_page(self, title):
        try:
            file_path = self.__class__.output_path + f"/{title}/"+title+ '_' + str(self.pages[0]) +'-' + str(self.pages[-1])+"_정보.txt"
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(f"책 제목: {title} \n")
                f.write(f"변환 페이지: {self.pages[0]}부터 {self.pages[-1]} \n")
                f.write("확인 요망 페이지:\n" + '\n'.join(self.image_page))
        except Exception as E:
            raise E

            
if __name__ == "__main__":   
     
    book_dict = {
        "pdf/가짜노동_본문.pdf": {'title': "가짜노동_본문_테스트.pdf", "layout_page":[18,19], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,390], },
    "pdf/과학드림의무섭게빠져드는과학책.pdf": {'title': "과학드림의무섭게빠져드는과학책_테스트.pdf", "layout_page":[7,8], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,322]},
    "pdf/관계를 읽는 시간.pdf": {'title': "관계를 읽는 시간_테스트_glue.pdf", "layout_page":[13,14], "excluded_lines_count": {'odd':2, 'even':2 }, "pages": [7,322]},
    "pdf/괜찮은 어른이 되고 싶어서.pdf": {'title': "괜찮은 어른이 되고 싶어서_테스트.pdf", "layout_page":[9,10], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [8,254]},
    "pdf/글로지은집.pdf": {'title': "글로지은집_테스트.pdf", "layout_page":[10, 11], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [6,387]},
    "pdf/꼴찌 마녀 밀드레드 8 (가제).pdf": {'title': "꼴찌 마녀 밀드레드 8 (가제)_테스트.pdf", "layout_page":[266,267], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [9, 268]},
    "pdf/나는 오늘부터 부자가 되기로 결심했다 _본문-확인용2.pdf": {'title': "나는 오늘부터 부자가 되기로 결심했다 _본문-확인용2_테스트.pdf", "layout_page":[7,8], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,240]},
    "pdf/늦기 전에 공부정서를 키워야 합니다.pdf": {'title': "늦기 전에 공부정서를 키워야 합니다_테스트.pdf", "layout_page":[30, 33], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [7,247]},
    # "pdf/다정한 말_본문.pdf": {'title': "다정한 말_본문_테스트.pdf", "layout_page":[9, 10], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,328]}, # 얘는 아예 사진임. 그래서 불가능.
    "pdf/당신도 느리게 나이 들 수 있습니다.pdf": {'title': "당신도 느리게 나이 들 수 있습니다_테스트.pdf", "layout_page":[11, 12], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [10,270]},
    "pdf/랩걸 Lab Girl.pdf": {'title': "랩걸 Lab Girl_테스트.pdf", "layout_page":[10, 19], "excluded_lines_count": {'odd':2, 'even':2 }, "pages": [7,409]},
    "pdf/마음은 단단하게 인생은 유연하게.pdf": {'title': "마음은 단단하게 인생은 유연하게_테스트2.pdf", "layout_page":[10, 11], "excluded_lines_count": {'odd':2, 'even':2 }, "pages": [27,241]},
    "pdf/마음을 치료하는 당신만의 물망초 식당.pdf": {'title': "마음을 치료하는 당신만의 물망초 식당_테스트.pdf", "layout_page":[38, 39], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,167]},
    "pdf/말주변이 없어도 똑 부러지게 말하는 법_내지_ci.pdf": {'title': "말주변이 없어도 똑 부러지게 말하는 법_내지_ci_테스트.pdf", "layout_page":[28,41], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,222]},
    "pdf/매우 예민한 사람들을 위한 상담소.pdf": {'title': "매우 예민한 사람들을 위한 상담소_테스트.pdf", "layout_page":[47,48], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,411]},
    "pdf/메멘토 모리.pdf": {'title': "메멘토 모리_테스트.pdf", "layout_page":[25,26], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [7,243]},
    "pdf/몬스터 차일드.pdf": {'title': "몬스터 차일드_테스트.pdf", "layout_page":[16,17], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [7,211]},
    "pdf/무조건 합격하는 암기의 기술.pdf": {'title': "무조건 합격하는 암기의 기술_테스트.pdf", "layout_page":[295,332], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [7,361]},
    "pdf/미래의 나를 구하러 갑니다.pdf": {'title': "미래의 나를 구하러 갑니다_테스트.pdf", "layout_page":[209,210], "excluded_lines_count": {'odd':2, 'even':2 }, "pages": [7,213]},
    "pdf/부동산 유치원_본문_2쇄-수정(교정용s) (1).pdf": {'title': "부동산 유치원_본문_2쇄-수정(교정용s) (1)_테스트.pdf", "layout_page":[26,35], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,240]},
    "pdf/빤쓰왕과 사악한 황제_20220920 (1).pdf": {'title': "빤쓰왕과 사악한 황제_20220920 (1)_테스트.pdf", "layout_page":[36,33], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [13,213]},
    "pdf/삼개주막 기담회 3.pdf": {'title': "삼개주막 기담회 3_테스트.pdf", "layout_page":[10,11], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [7,376]},
    "pdf/아이 마음에 상처 주지 않는 습관.pdf": {'title': "아이 마음에 상처 주지 않는 습관_테스트.pdf", "layout_page":[7,18], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,318]},
    "pdf/안녕나의순정 본문_저해상.pdf": {'title': "안녕나의순정 본문_저해상_테스트.pdf", "layout_page":[26,23], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [3,41]},
    # "pdf/어른의 문장력_내지(2도) 인쇄용수정.pdf": {'title': "어른의 문장력_내지(2도) 인쇄용수정_테스트.pdf", "layout_page":[8,213], "excluded_lines_count": {'odd':2, 'even':2 }, "pages": [4,227]},
    "pdf/어린이의말.pdf": {'title': "어린이의말_테스트.pdf", "layout_page":[136,129], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [4,146]},
    "pdf/영어책한권외워봤니.pdf": {'title': "영어책한권외워봤니_테스트.pdf", "layout_page":[9,292], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [8,295]},
    # "pdf/오이대왕.pdf": {'title': "오이대왕_테스트.pdf", "layout_page":[183,172], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,185]},
    "pdf/우리 가족은 꽤나 진지합니다.pdf": {'title': "우리 가족은 꽤나 진지합니다_테스트.pdf", "layout_page":[16,25], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,102]},
    "pdf/유리고코로.pdf": {'title': "유리고코로_테스트.pdf", "layout_page":[8,11], "excluded_lines_count": {'odd':1, 'even':1 }, "pages": [5,329]},
    }

    for path, info in book_dict.items():
        # if path != "pdf/오이대왕.pdf":
        #     print(path)
        #     continue
        extractor = ScriptExtractor(
                                    list(range(info['pages'][0], info['pages'][1])), 
                                    excluded_lines_count_odd=info['excluded_lines_count']['odd'], 
                                    excluded_lines_count_even=info['excluded_lines_count']['even'],
                                    layout_pages=None
                                    )
        extractor.set_option(path, output_path="C:/Users/82104/Desktop/", LINE_HEIGHT_THRESHOLD=15, PARAGRAPH_SPACE=5, NEWLINE_SPACE=25)
        extractor.set_new_layout()
        extractor.layout_checker()
        extractor.read_pdf_v2(
                            title=info['title'],
                            read_line_with_word=True,
                            check_overwritten_word=True, extract_image=False, text_flow=True,
                            robust_spacing=False, 
                            check_space_with_ko_eng=True,
                            check_space_with_num_char=True
                            ) # 사용자 입력
        extractor.write_reference_page()
    
    # 마음은 단단하게 # 마음을 치료하는... 이거 2페이지당임... # 몬스터차일드 확인 필요 (소설)
    # 2페이지당인거 확인하기...
    # 미래의 나를... # 빤스왕과... # 안녕 나의 순정...
    # 레이아웃에서 쪽수 없는 경우도 커버하도록 하기. (홀수,짝수 다르게.)


    # path = r"pdf\과학드림의무섭게빠져드는과학책.pdf"    # 사용자 입력
    # # path = r"pdf\sample.pdf"        
    # pages = list(range(int(input('시작 페이지를 입력해주세요: ')), int(input('끝 페이지를 입력해주세요: '))+1)) # 사용자 입력
    # extractor = ScriptExtractor(pages)
    # extractor.set_option(path, output_path="C:/Users/82104/Desktop/", title='과학드림의무섭게빠져드는과학책_테스트', layout_page=24,  excluded_lines_count=1) # 여기가 사용자가 입력해야 함.
    # # extractor.set_layout()
    # # extractor.read_pdf(double_quote_to_single_quote=True) # 이 부분도 사용자 입력 필요.
    # extractor.set_new_layout()
    # extractor.read_pdf_v2(read_line_with_word=True, check_overwritten_word=True, extract_image=True) # 사용자 입력
    # extractor.write_reference_page()
    # # extractor.write_script_by_notepad()
    # # extractor.write_script_by_docx()


t2 = time.time()

print(f"소요시간: {t2-t1:.2f}초.")



# 네이버 백과사전 api로 하는 것은 외래어와 한자어 구분이 안될 수도 있기에 제외...

# from kiwipiepy import Kiwi

# kiwi = Kiwi(model_type='sbg')
# example_text = [
#                 # '이 책을 공동 집필한 우리 두 사람은 덴마크의 뉴스 프로그램 〈데드라인〉에 출연했다.',
#                 # '우리는 만나서 그동안 각자 봐온 것과 해온 일에 대해 오래 대화했고, 롤란드 파울센의 책, 『공허 노동, Empty Labor 』이 드디어 출판되었을 때 왜 더 큰 반향을 일으키지 않았을까 의아해했다.',
#                 # '그는 더 큰 정치적・경제적・사회적 미래 문제를 다루는 자리에 연사로 초청되었는데, 여기서 제시된 케인스의 전망은 오늘날 우리에게 라이트 못지않은 잘못된 예측으로 보인다.',
#                 # '(인생의 모든 단계에서) 보통 사람이 느리고 편한 속도에 맞춰 일하려는 경향이 있다는 데는 의문의 여지가 없다.',
#                 # "지금 우리 시대는 스탠리 큐브릭의 〈 2001 : 스페이스 오디세이〉 영화 속 설정 연도에서 20년이 훌쩍 지났지만, 감독의 상상이 실현되려면 아직 멀었다는 걸 생각하면 당황스러울 지경이다.",
#                 # "“예, 알겠습니다. 예….”"
#                 ]
# for i in example_text: # SSO (인용부호 열림), SSC (인용부호 닫힘)으로 바뀜.
#     return_text =  kiwi.tokenize(i)
#     print(f"return_text: {return_text}")


# TODO: sample 페이지로 layout 설정하는 과정 무조건 필요!


# TODO: 가로로 2장 있는 것까지 고려...?

