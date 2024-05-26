### text_to_csv should be used.

from typing import List
import re
import csv
import random


X_path = [
    "data/training_text_transcripted.txt",
    "data/training_text.txt"
    ]

Y_path = [
    "data/training_text_transcripted_after.txt",
    "data/training_text_after.txt"
]

training_csv = 'data/csv/training_data_no_dq.csv'
test_csv = 'data/csv/test_data_no_dq.csv'
training_key = 'data/csv/training_key_no_dq.csv'
test_key = 'data/csv/test_key_no_dq.csv'

not_kor_en_num_special_char = re.compile(r"[^A-Za-z0-9가-힣\{\}\[\]\/?.,;:|…*~!^\-_+<>@\#$%&\\\=\'\"\s]")
# ( )와 같은 괄호도 문제 유발함.
# kor_en_num_ptn = re.compile(r"[A-Za-z0-9가-힣]")

# def split_sentences(text):
#     sentences = []
#     start = 0
#     in_quotes = False

#     for i, char in enumerate(text):
#         # 인용 부호 상태를 토글합니다.
#         if char in "\"'":
#             in_quotes = not in_quotes

#         # 인용 부호 외부에서 문장의 끝을 찾습니다.
#         if not in_quotes and char in ".!?" and (i + 1 == len(text) or text[i + 1].isspace()):
#             sentences.append(text[start:i + 1].strip())
#             start = i + 1

#     if start < len(text):
#         sentences.append(text[start:].strip())

#     return sentences

# def split_sentences(text):
#     sentences = []
#     start = 0
#     in_quotes = False

#     for i, char in enumerate(text):
#         # 인용 부호 상태를 토글합니다.
#         if char in "\"'":
#             in_quotes = not in_quotes
#             # 인용 부호가 닫히고 새로운 문장이 시작되는 경우를 처리합니다.
#             if not in_quotes and i + 1 < len(text) and text[i + 1].isspace():
#                 sentences.append(text[start:i + 1].strip())
#                 start = i + 1
#                 continue

#         # 인용 부호 외부에서 문장의 끝을 찾습니다.
#         if not in_quotes and char in ".!?" and (i + 1 == len(text) or text[i + 1].isspace()):
#             sentences.append(text[start:i + 1].strip())
#             start = i + 1

#     if start < len(text):
#         sentences.append(text[start:].strip())

#     return sentences


def split_sent(text):
    split_flag = False
    split_idx = 0
    sents = []
    start = 0
    for idx, ch in enumerate(text):

        if split_flag and split_idx + 2 < idx:
            split_flag = False
            split_idx = 0

        if ch in ('.','!','?'):
            split_flag = True
            split_idx = idx
            continue

        if split_flag and ch == ' ':
            split_flag = False
            sents.append(text[start:idx])
            start = idx + 1

    sents.append(text[start:])

    return sents




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


def split_sentences(text):
    sentences = []
    start = 0
    in_quotes = False
    quote_end = False

    for i, char in enumerate(text):
        # 인용 부호 상태를 토글합니다.
        if char in "\"'":
            in_quotes = not in_quotes
            if not in_quotes:
                quote_end = True
            continue

        # 인용 부호가 닫힌 후 첫 번째 구두점을 찾습니다.
        if quote_end and char in ".!?":
            quote_end = False


        # 인용 부호 외부에서 문장의 끝을 찾습니다.
        if not in_quotes and not quote_end and char in ".!?" and (i + 1 == len(text) or text[i + 1].isspace()):
            sentences.append(text[start:i + 1].strip())
            start = i + 1

    if start < len(text):
        sentences.append(text[start:].strip())

    return sentences


def check_right_sent(sentence: str) -> str:
    if sentence.find("  ") != -1:
        print(f"[WARNING] 띄어쓰기 두 칸. \n \
              문제되는 문장: {sentence}")
        return "[WARNING] 띄어쓰기 두 칸"
    elif (sentence.find(",") != -1 and sentence.find(", ") == -1):
        print(f"[WARNING] 쉼표 주의. \n \
              문제되는 문장: {sentence}")
        return "[WARNING] 쉼표 주의"
    elif sentence.find("' ") != -1 :
        print(f"[WARNING] 작은따옴표 주의. 문제되는 문장: {sentence} \n" ,
              "해당되는 부분:", sentence.find("' "))
        return "[WARNING] 작은따옴표 주의"
    elif sentence.find('" ' ) != -1 :
        print(f"[WARNING] 큰따옴표 주의. \n \
              문제되는 문장: {sentence} \n",
            "해당되는 부분:", sentence.find('" '))
        return "[WARNING] 큰따옴표 주의"
    elif not_kor_en_num_special_char.search(sentence) != None:
        print(f"[WARNING] 특수문자 주의. \n \
              문제되는 문장: {sentence} \n", 
            f"해당되는 부분: {not_kor_en_num_special_char.search(sentence)}")        
        return "[WARNING] 특수문자 주의"

    return "SUCCESS"


def check_similar_sentence(x_sent, y_sent, similarity_check_criterion):
    if similarity_check_criterion == '1단계':
        parsed_x_sent = x_sent.replace(",", "").replace(" ","")
        parsed_y_sent = y_sent.replace(",", "").replace(" ","")
    elif similarity_check_criterion == '2단계':
        parsed_x_sent = x_sent.replace(",", "")
        parsed_y_sent = y_sent.replace(",", "")
    similarity_counter = 0

    if len(parsed_x_sent) == len(parsed_y_sent):
        for x_char, y_char in zip(parsed_x_sent, parsed_y_sent):
            if x_char != y_char:
                # similarity_counter+=1
                print(f"[ERROR] 다른 문장:\n \
                       x_sent: {x_sent} \n",
                      f"y_sent: {y_sent}")
                return False
            else:
                continue
    else:
        print(f"[ERROR] 다른 문장: \n \
              x_sent: {x_sent} \n",
              f"y_sent: {y_sent}")
        return False
    
    # if len(x_sent) != similarity_counter:
    #     print(f"다른 문장: x_sent: {x_sent} \n",
    #           f"y_sent: {y_sent}")
    #     return False
    
    return True


def training_text_to_csv_shuffle(X_path: List[str],  Y_path: List[str], training_csv_filename, test_csv_filename):
    add_dq = input("큰따옴표를 붙여 쉼표를 유지하는 방식을 유지하고 싶다면 해당 옵션에서 '예'라고 말해주세요. ")
    if add_dq == "예":
        add_dq = True
    else:
        add_dq = False

    ignore_warning_case = input("WARNING을 무시한다면 '무시하기'라고 입력하세요. ")
    if ignore_warning_case == "무시하기":
        ignore_warning_case =True
    else:
        ignore_warning_case = False

    similarity_check_criterion = input("유사도 단계를 '1단계', '2단계' 중 하나로 선택해주세요. ")
    csv_data_index = list(dict())
    index=0
    for x_path, y_path  in zip(X_path, Y_path):
        with open(x_path, 'r', encoding='utf-8') as xfile, open(y_path, 'r', encoding='utf-8') as yfile:
            for x_lines, y_lines in zip(xfile.readlines(), yfile.readlines()):
                x_sentences = split_sentences(x_lines.rstrip())
                y_sentences = split_sentences(y_lines.rstrip())
                for x_sent, y_sent in zip(x_sentences, y_sentences):
                    if not check_similar_sentence(x_sent, y_sent, similarity_check_criterion):
                        continue

                    if not ignore_warning_case:
                        if check_right_sent(x_sent) == "SUCCESS" and check_right_sent(y_sent) == "SUCCESS":
                            if add_dq:
                                if x_sent.find(",") != -1 and y_sent.find(",") != -1:
                                    csv_datum = {
                                    'Text': '"'+x_sent+'"',
                                    'Completion': '"'+y_sent+'"',
                                    'index': index
                                }
                                elif x_sent.find(",") != -1 and y_sent.find(",") == -1:
                                    csv_datum = {
                                        'Text': '"'+x_sent+'"',
                                        'Completion': y_sent,
                                        'index': index
                                    }
                                elif x_sent.find(",") == -1 and y_sent.find(",") != -1:
                                    csv_datum = {
                                        'Text': x_sent,
                                        'Completion': '"'+y_sent+'"',
                                        'index': index
                                    }
                                else:
                                    csv_datum = {
                                        'Text': x_sent,
                                        'Completion': y_sent,
                                        'index': index
                                    }
                            else:
                                csv_datum = {
                                        'Text': x_sent,
                                        'Completion': y_sent,
                                        'index': index
                                    }
                            csv_data_index.append(csv_datum)
                            index+=1

                    # Warning case ignore.
                    if ignore_warning_case:
                        if add_dq:
                            if x_sent.find(",") != -1 and y_sent.find(",") != -1:
                                csv_datum = {
                                'Text': '"'+x_sent+'"',
                                'Completion': '"'+y_sent+'"',
                                'index': index
                            }
                            elif x_sent.find(",") != -1 and y_sent.find(",") == -1:
                                csv_datum = {
                                    'Text': '"'+x_sent+'"',
                                    'Completion': y_sent,
                                    'index': index
                                }
                            elif x_sent.find(",") == -1 and y_sent.find(",") != -1:
                                csv_datum = {
                                    'Text': x_sent,
                                    'Completion': '"'+y_sent+'"',
                                    'index': index
                                }
                            else:
                                csv_datum = {
                                    'Text': x_sent,
                                    'Completion': y_sent,
                                    'index': index
                                }
                        else:
                            csv_datum = {
                                    'Text': x_sent,
                                    'Completion': y_sent,
                                    'index': index
                                }
                        csv_data_index.append(csv_datum)
                        index+=1

    random.shuffle(csv_data_index)


    # Writing to a CSV file
    split_ratio = 0.9
    training_count = round(index * split_ratio)

    csv_index = [[d['index']] for d in csv_data_index]
    csv_data = [{"Text": d["Text"], "Completion": d["Completion"],} for d in csv_data_index]

    with open(training_csv_filename, mode='w', newline='', encoding='utf-8') as training_file, \
        open(test_csv_filename, mode='w', newline='', encoding='utf-8') as test_file, \
        open(training_key, mode='w', newline='', encoding='utf-8') as training_key_file, \
        open(test_key, mode='w', newline='', encoding='utf-8') as test_key_file\
        :

        # Create a DictWriter object
        training_writer = csv.DictWriter(training_file, fieldnames=csv_data[0].keys())
        test_writer = csv.DictWriter(test_file, fieldnames=csv_data[0].keys())
        training_key_writer = csv.writer(training_key_file)
        test_key_writer = csv.writer(test_key_file)
        
        # Write the header (column names)
        training_writer.writeheader()
        test_writer.writeheader()
        
        # Write the rows
        for idx, row in enumerate(csv_data):
            if idx < training_count:
                training_writer.writerow(row)
            else:
                test_writer.writerow(row)
        
        # Write the index
        for idx, key in enumerate(csv_index):
            if idx < training_count:
                training_key_writer.writerow(key)
            else:
                test_key_writer.writerow(key)


def training_text_to_csv(X_path: List[str],  Y_path: List[str], training_csv_filename:str, test_csv_filename:str):
    add_dq = input("큰따옴표를 붙여 쉼표를 유지하는 방식을 유지하고 싶다면 해당 옵션에서 '예'라고 말해주세요. ")
    if add_dq == "예":
        add_dq = True
    else:
        add_dq = False

    ignore_warning_case = input("WARNING을 무시한다면 '무시하기'라고 입력하세요. ")
    if ignore_warning_case == "무시하기":
        ignore_warning_case =True
    else:
        ignore_warning_case = False

    similarity_check_criterion = input("유사도 단계를 '1단계', '2단계' 중 하나로 선택해주세요. ")

    x_warning_sentences = []
    y_warning_sentences = []
    csv_data = list(dict())
    # SPLIT_SENTENCE_PATTERN = re.compile('(?<=[(.\'|!\'|?\'|.|!|?)])\s+')
    SPACE_PTRN = re.compile('\s+')
    SEARCH_PTRN = re.compile('[.!?]')
    
    # def find_patterns_and_split(text):
    #     parts = []
    #     start = 0

    #     SEARCH_PTRN.search(text[start:])
    #     while True:
    #         # 패턴 검색
    #         match = SEARCH_PTRN.search(text[start:])
    #         ptrn_pos = match.start()
    #             SPACE_PTRN.search(text[ptrn_pos+1:])


    #         match = SPLIT_SENTENCE_PTRN.search(text[start:])
    #         if not match:
    #             # 더 이상 패턴이 없으면 남은 부분을 추가하고 종료
    #             parts.append(text[start:])
    #             break

    #         # 패턴이 발견된 위치
    #         end = start + match.start()

    #         # 현재 위치부터 패턴 시작 위치까지의 부분을 추가
    #         parts.append(text[start:end])

    #         # 다음 검색을 위해 시작 위치 업데이트
    #         start = end + len(match.group())

    #     return parts
    
    def find_patterns_and_split(text):
        parts = []
        start = 0        
        flag = False
        flag_idx = None
        for idx, ch in enumerate(text):
            if flag and ch == " ":
                parts.append(text[start:idx+1])
                flag = False
                start = idx + 1
                continue

            if ch in ['.', '!', '?']:
                flag = True
                flag_idx = idx

            if flag_idx and (flag_idx == idx+2)and flag:
                flag = False
           
        parts.append(text[start:])
            
        return parts

    # def recursive_split(text, maxsplit=1):
    #     # 탈출
    #     if not SPLIT_SENTENCE_PATTERN.search(text, maxsplit):
    #         return text
    #     else:
    #         back_part = text[SPLIT_SENTENCE_PATTERN.search(text, maxsplit).pos + 1:]
    #         split_sents = recursive_split(back_part)
    #     # 분할 수행
    #     parts = SPLIT_SENTENCE_PATTERN.split(text, maxsplit)
    #     parts[0] # 보존.
    #     parts[-1]
        
    #     # 추가 분할이 필요한지 확인
    #     for i, part in enumerate(parts):
    #         if SPLIT_SENTENCE_PATTERN.search(part):
    #             # 재귀적으로 분할 수행
    #             parts[i:i + 1] = recursive_split(part, maxsplit)
        
    #     return parts
    

    for x_path, y_path  in zip(X_path, Y_path):
        with open(x_path, 'r', encoding='utf-8') as xfile, \
            open(y_path, 'r', encoding='utf-8') as yfile:
            for x_lines, y_lines in zip(xfile.readlines(), yfile.readlines()):
                # 후에 sentence 나누는 기준을 다르게 해야 할수도 있음. "\n"로 바꾼다던지...                               
                # x_sentences = list(map(_replace_to_single_double_quote, split_sentences(x_lines)))
                # y_sentences = list(map(_replace_to_single_double_quote, split_sentences(y_lines)))
                x_sentences = list(map(_replace_to_single_double_quote, re.split('(?<=[.!?])(?:[\'\"]?)(\s+)', x_lines.rstrip())))
                y_sentences = list(map(_replace_to_single_double_quote, re.split('(?<=[.!?])(?:[\'\"]?)(\s+)', y_lines.rstrip())))

                # x_sentences = list(map(_replace_to_single_double_quote, find_patterns_and_split(x_lines.rstrip())))
                # y_sentences = list(map(_replace_to_single_double_quote, find_patterns_and_split(y_lines.rstrip())))
                
                for x_sent, y_sent in zip(x_sentences, y_sentences):
                    if (not x_sent) or (not y_sent): # 공백이면 안넣기.
                        continue

                    if not check_similar_sentence(x_sent, y_sent, similarity_check_criterion):
                        x_warning_sentences.append(x_sent)
                        y_warning_sentences.append(y_sent)
                        continue
                    
                    x_quote_count = x_sent.count("'") + x_sent.count('"')
                    if x_quote_count % 2 != 0:
                        print(f"[WARNING] 따옴표 닫힘 문장 존재. \n \
                              확인해야 할 문장: {x_sent}")
                        x_warning_sentences.append(x_sent)
                    y_quote_count = y_sent.count("'") + y_sent.count('"')
                    if y_quote_count % 2 != 0:
                        print(f"[WARNING] 따옴표 닫힘 문장 존재. \n \
                              확인해야 할 문장: {y_sent}")
                        y_warning_sentences.append(y_sent)


                    if not ignore_warning_case:
                        if check_right_sent(x_sent) == "SUCCESS" and check_right_sent(y_sent) == "SUCCESS":
                            if add_dq:
                                if x_sent.find(",") != -1 and y_sent.find(",") != -1:
                                    csv_datum = {
                                    'Text': '"'+x_sent+'"',
                                    'Completion': '"'+y_sent+'"',
                                    }
                                elif x_sent.find(",") != -1 and y_sent.find(",") == -1:
                                    csv_datum = {
                                        'Text': '"'+x_sent+'"',
                                        'Completion': y_sent,
                                    }
                                elif x_sent.find(",") == -1 and y_sent.find(",") != -1:
                                    csv_datum = {
                                        'Text': x_sent,
                                        'Completion': '"'+y_sent+'"',
                                    }
                                else:
                                    csv_datum = {
                                        'Text': x_sent,
                                        'Completion': y_sent,
                                    }
                            else:
                                csv_datum = {
                                        'Text': x_sent,
                                        'Completion': y_sent,
                                    }
                            csv_data.append(csv_datum)
                        
                        else:
                            x_warning_sentences.append(x_sent)
                            y_warning_sentences.append(y_sent)


                    # Warning case ignore.
                    if ignore_warning_case:
                        if add_dq:
                            if x_sent.find(",") != -1 and y_sent.find(",") != -1:
                                csv_datum = {
                                'Text': '"'+x_sent+'"',
                                'Completion': '"'+y_sent+'"',
                                }
                            elif x_sent.find(",") != -1 and y_sent.find(",") == -1:
                                csv_datum = {
                                    'Text': '"'+x_sent+'"',
                                    'Completion': y_sent,
                                }
                            elif x_sent.find(",") == -1 and y_sent.find(",") != -1:
                                csv_datum = {
                                    'Text': x_sent,
                                    'Completion': '"'+y_sent+'"',
                                }
                            else:
                                csv_datum = {
                                    'Text': x_sent,
                                    'Completion': y_sent,
                                }
                        else:
                            csv_datum = {
                                    'Text': x_sent,
                                    'Completion': y_sent,
                                }
                        csv_data.append(csv_datum)

    # Writing to a CSV file
    split_ratio = 0.9
    training_count = round(len(csv_data) * split_ratio)

    with open(training_csv_filename, mode='w', newline='', encoding='utf-8') as training_file, \
        open(test_csv_filename, mode='w', newline='', encoding='utf-8') as test_file, \
        open(training_csv_filename.replace(".csv","_warning_sentences.csv"), mode='w', newline='', encoding='utf-8') as training_warning_file,\
        open(test_csv_filename.replace(".csv","_warning_sentences.csv"), mode='w', newline='', encoding='utf-8') as test_warning_file \
        :

        # Create a DictWriter object
        training_writer = csv.DictWriter(training_file, fieldnames=csv_data[0].keys())
        test_writer = csv.DictWriter(test_file, fieldnames=csv_data[0].keys())

        # Write the header (column names)
        training_writer.writeheader()
        test_writer.writeheader()
        
        # Write the rows
        for idx, row in enumerate(csv_data):
            if idx < training_count:
                training_writer.writerow(row)
            else:
                test_writer.writerow(row)

        # Warning files.
        
        training_warning_file_writer = csv.writer(training_warning_file)
        test_warning_file_writer = csv.writer(test_warning_file)
        
        training_warning_file_writer.writerow(["문제될 문장들"])
        test_warning_file_writer.writerow(["문제될 문장들"])
            
        for row in x_warning_sentences:
            training_warning_file_writer.writerow([row])
            
        for row in y_warning_sentences:
            test_warning_file_writer.writerow([row])

    print("COMPLETE TASK: training_text_to_csv")


def training_text_to_csv_chunk(X_path: List[str],  Y_path: List[str], training_csv_filename:str, test_csv_filename:str, split_ratio=0.9):

    ignore_warning_case = input("WARNING을 무시한다면 '무시하기'라고 입력하세요. ")
    if ignore_warning_case == "무시하기":
        ignore_warning_case =True
    else:
        ignore_warning_case = False

    similarity_check_criterion = input("유사도 단계를 '1단계', '2단계' 중 하나로 선택해주세요. ")

    x_warning_sentences = []
    y_warning_sentences = []
    csv_data = list(dict())
    for x_path, y_path  in zip(X_path, Y_path):
        with open(x_path, 'r', encoding='utf-8') as xfile, open(y_path, 'r', encoding='utf-8') as yfile:
            for x_lines, y_lines in zip(xfile.readlines(), yfile.readlines()):
                # 후에 sentence 나누는 기준을 다르게 해야 할수도 있음. "\n"로 바꾼다던지...
                x_sentences = split_sentences(x_lines)
                y_sentences = split_sentences(y_lines)
                sent_len_buffer = 0
                sent_len_buffer_limit = 150
                sent_buffer_x = ""
                sent_buffer_y = ""

                for x_sent, y_sent in zip(x_sentences, y_sentences):
                    # 맨 끝 줄바꿈 시 나오는 공백 처리.
                    if x_sent == '' and y_sent == '':
                        recent_csv_datum = csv_data.pop()
                        recent_csv_datum['Text'] = recent_csv_datum['Text']+"\n"
                        recent_csv_datum['Completion'] = recent_csv_datum['Completion']+"\n"
                        csv_data.append(recent_csv_datum)
                        continue

                    if not check_similar_sentence(x_sent, y_sent, similarity_check_criterion):
                        x_warning_sentences.append(x_sent)
                        y_warning_sentences.append(y_sent)
                        continue
                    
                    x_quote_count = x_sent.count("'") + x_sent.count('"')
                    if x_quote_count % 2 != 0:
                        print(f"[WARNING] 따옴표 닫힘 문장 존재. \n \
                              확인해야 할 문장: {x_quote_count}")
                        x_warning_sentences.append(x_quote_count)

                    y_quote_count = y_sent.count("'") + y_sent.count('"')
                    if y_quote_count % 2 != 0:
                        print(f"[WARNING] 따옴표 닫힘 문장 존재. \n \
                              확인해야 할 문장: {y_quote_count}")
                        y_warning_sentences.append(y_quote_count)

                    cur_sent_x = x_sent
                    cur_sent_y = y_sent
                    # check sent if there is an punctuation.
                    if not ignore_warning_case:
                        if check_right_sent(x_sent) == "SUCCESS" and check_right_sent(y_sent) == "SUCCESS":
                            if cur_sent_x.find(".") < 1 and cur_sent_x.find("!") < 1 and cur_sent_x.find("?") < 1:
                                if cur_sent_x.find("\n"):
                                    sent_buffer_x += cur_sent_x[:cur_sent_x.find("\n")]+ ".\n "
                                else:
                                    sent_buffer_x += cur_sent_x + ". "
                                if cur_sent_y.find("\n"):
                                    sent_buffer_y += cur_sent_y[:cur_sent_y.find("\n")]+ ".\n "
                                else:
                                    sent_buffer_y += cur_sent_y + ". "
                            else:
                                sent_buffer_x += cur_sent_x + " "
                                sent_buffer_y += cur_sent_y + " "
                            
                            sent_len_buffer += len(cur_sent_x) # x 기준임.
                        else:
                            x_warning_sentences.append(x_sent)
                            y_warning_sentences.append(y_sent)
                        
                        if sent_len_buffer > sent_len_buffer_limit or cur_sent_x[-1] == "\n":
                            sent_buffer_x = sent_buffer_x[:-1]
                            sent_buffer_y = sent_buffer_y[:-1]
                            csv_datum = {
                                    'Text': sent_buffer_x,
                                    'Completion': sent_buffer_y,
                                    }
                            csv_data.append(csv_datum)
                            sent_buffer_x = ""
                            sent_buffer_y = ""
                            sent_len_buffer = 0
                        
                    # Ignore warning case.
                    elif ignore_warning_case:
                        if cur_sent_x.find(".") < 1 and cur_sent_x.find("!") < 1 and cur_sent_x.find("?") < 1:
                            if cur_sent_x.find("\n"):
                                sent_buffer_x += cur_sent_x[:cur_sent_x.find("\n")]+ ".\n "
                            else:
                                sent_buffer_x += cur_sent_x + ". "
                            if cur_sent_y.find("\n"):
                                sent_buffer_y += cur_sent_y[:cur_sent_y.find("\n")]+ ".\n "
                            else:
                                sent_buffer_y += cur_sent_y + ". "
                        else:
                            sent_buffer_x += cur_sent_x + " "
                            sent_buffer_y += cur_sent_y + " "
                        
                        sent_len_buffer += len(cur_sent_x) # x 기준임.

                        if sent_len_buffer > sent_len_buffer_limit or cur_sent_x[-1] == "\n":
                            sent_buffer_x = sent_buffer_x[:-1]
                            sent_buffer_y = sent_buffer_y[:-1]
                            csv_datum = {
                                    'Text': sent_buffer_x,
                                    'Completion': sent_buffer_y,
                                    }
                            csv_data.append(csv_datum)
                            sent_buffer_x = ""
                            sent_buffer_y = ""
                            sent_len_buffer = 0

    # Writing to a CSV file
    training_count = round(len(csv_data) * split_ratio)

    with open(training_csv_filename, mode='w', newline='', encoding='utf-8') as training_file, \
        open(test_csv_filename, mode='w', newline='', encoding='utf-8') as test_file, \
        open(training_csv_filename.replace(".csv","_warning_sentences_x.csv"), mode='w', newline='', encoding='utf-8') as training_warning_file,\
        open(test_csv_filename.replace(".csv","_warning_sentences_y.csv"), mode='w', newline='', encoding='utf-8') as test_warning_file \
        :

        # Create a DictWriter object
        training_writer = csv.DictWriter(training_file, fieldnames=csv_data[0].keys())
        test_writer = csv.DictWriter(test_file, fieldnames=csv_data[0].keys())

        # Write the header (column names)
        training_writer.writeheader()
        test_writer.writeheader()
        
        # Write the rows
        for idx, row in enumerate(csv_data):
            if idx < training_count:
                training_writer.writerow(row)
            else:
                test_writer.writerow(row)

        # Warning files.
        
        training_warning_file_writer = csv.writer(training_warning_file)
        test_warning_file_writer = csv.writer(test_warning_file)
        
        training_warning_file_writer.writerow(["문제될 문장들"])
        test_warning_file_writer.writerow(["문제될 문장들"])
            
        for row in x_warning_sentences:
            training_warning_file_writer.writerow([row])
            
        for row in y_warning_sentences:
            test_warning_file_writer.writerow([row])

    print("COMPLETE TASK: training_text_to_csv")

def text_to_csv(text_path_list: List[str], csv_filename_list: List[str], ignore_warning_case=False):    
    #  similarity_check_criterion = input("유사도 단계를 '1단계', '2단계' 중 하나로 선택해주세요. ")
    
    for filename, csv_filename in zip(text_path_list, csv_filename_list):
        csv_data = list(dict())
        # Read txtfile.
        with open(filename, 'r', encoding='utf-8') as f:
            for lines in f.readlines():
                # 후에 sentence 나누는 기준을 다르게 해야 할수도 있음. "\n"로 바꾼다던지...
                # sentences = re.split('(?<=[(.\")(!\")(?\")(.\')(!\')(?\').!?])\s+', lines.rstrip())
                # x_sentences = list(map(_replace_to_single_double_quote, re.split('(?<=[.!?])[\u201D\u2019\"\']?\s+', x_lines.rstrip())))
                sentences = list(map(_replace_to_single_double_quote, re.split('(?<=[.!?])(?:[\'\"]?)(\s+)', lines.rstrip())))
                sentences = list(map(_replace_to_single_double_quote, split_sent(lines.rstrip())))

                # sentences = re.split('(?<=[.!?])[\u201D\u2019\"\']?\s+', lines.rstrip())

                for sent in sentences:
                    quote_count = sent.count("'") + sent.count('"')
                    if quote_count % 2 != 0:
                        csv_datum = [sent, "[WARNING] 따옴표 오류 문장 존재"]

                    if not ignore_warning_case and check_right_sent(sent) == "SUCCESS":    
                        csv_datum = [sent]
                    # Ignore warning case.
                    elif ignore_warning_case:
                        csv_datum = [sent]
                    else:                        
                        csv_datum = [sent, check_right_sent(sent)]

                    csv_data.append(csv_datum)
            
        # Writing to a CSV file                            
        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as csvf:
            csv_writer = csv.writer(csvf)
            
            # 일종의 header.
            csv_writer.writerow(['텍스트', '문제 사유'])

            # Write the rows
            for row in csv_data:
                csv_writer.writerow(row)            

            csv_writer.writerow(["<|endoftext|>"])                
              
    print("COMPLETE TASK: text_to_csv")

if __name__ == "__main__":
    # X_path = [
    # r"./data/training_text_transcripted.txt",
    # r"./data/training_text.txt"
    # ]
    # Y_path = [
    #     r"./data/training_text_transcripted_after.txt",
    #     r"./data/training_text_after.txt"
    # ]
    # training_csv = r'./data/csv/training_data_without_quotes.csv'
    # test_csv = r'./data/csv/test_data_without_quotes.csv'
    # training_text_to_csv(X_path, Y_path, training_csv, test_csv)

    # training_csv = 'data/csv/training_data_no_dq.csv'
    # test_csv = 'data/csv/test_data_no_dq.csv'
    # training_text_to_csv(X_path, Y_path, training_csv, test_csv)
    # training_text_to_csv_chunk(X_path, Y_path, training_csv, test_csv, split_ratio=0.9)

    text_path_list = [ "data/training_text_transcripted.txt","data/training_text.txt"]
    csv_filename_list = ['data/csv/regex_test.csv', 'data/csv/regex_test2.csv']
    # # text_to_csv(text_path_list=text_path_list, csv_filename_list=csv_filename_list)
    text_to_csv(text_path_list=text_path_list, csv_filename_list=csv_filename_list, ignore_warning_case=True)


