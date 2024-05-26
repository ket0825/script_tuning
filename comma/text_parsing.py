# import math
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from kiwipiepy import Kiwi, Match
import re
from typing import List, Tuple
import itertools
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
# from itertools import groupby
# from scipy.stats import truncnorm


# def gaussian(x, mean=15, sig=4):
#     return (1 / math.sqrt(2*math.pi*sig**2)) * math.exp(-(x-mean)**2 / (2*sig**2))   


# 여러 텍스트 조각을 합치되, 문맥을 고려해 적절한 공백을 사이에 삽입.
# 특히, OCR, PDF에 유용.
# (kiwi.glue([
#     "그러나  알고보니 그 봉",
#     "지 안에 있던 것은 바로",
#     "레몬이었던 것이다."]))

# kiwi.join()
# print(kiwi.split_into_sents(msg, return_tokens=True))

# def _distance_score(mean, std, _input):
#     a, b = (7, 25) # lower limit, upper limit
#     mean, std = (16, 5) # 이걸 추정시켜야 할듯.
#     rv = truncnorm(a, b, loc=mean, scale=std)
#     distance_score = rv.pdf(_input)
#     return distance_score

#     # 쉼표와 쉼표 사이의 거리 점수.
#     # 패턴을 만족시키는 타입 종류.
#     # 파일을 읽어서 가중치를 학습시키기.

#  법칙:서술어 부분만 자간좁히기, <VX> 보조용언, <VV> 동사, <VA> 형용사: 바로 앞에 자간 좁히기.
#       단, 종결어미<EF>, 연결어미<EC>인 경우만. 뒤에 어미까지 확인하여 서술어인지 아니면 다른 문장성분으로 쓰이는지 확인 필요.
#           <VCP>긍정지시사(서술격 조사) ex) 학생이다. <VCN>부정지시사 => <V.> ex) 아닌.

#  의존명사 자간좁히기, <NNB> 앞에 공백 제거.
#  기호(?, !)다음에 연결형 단어는 자간좁히기(! 라고) <JKQ> 인용격조사 앞에 공백 제거.

#  소유격 조사 자간좁히기, <JKG> 뒤에 공백 제거.
#  접속부사 자간좁히기, <MAJ> 뒤에 공백 제거.
#  보조사: 명사, 대명사, 수사, 부사, 어미 뒤에 붙음. (신경 x)

kiwi=Kiwi(model_type='sbg')

# 해당 패턴 바로 뒤에 쉼표인지 확인해야 함. 재조정 필요.
# ec_vx는 걸러내기 위한 패턴.
ec_vx = re.compile(r'^EC(?= +?)VX{1}') 
# ec_v는 조금 더 여러 개로 나눠야 함.
# ec_jx(여기까지 캡쳐)_com_..._v
# ec(여기까지 캡쳐)_com_..._v
ec_jx_comma_v = re.compile(r'^EC(\s+JX)*(?= +(MAG |MAJ |N(.{1,2}?) +JKB )*(VV |VA )+(.{3,9}))(?!ETN )')
# ex) EC JX JX NNG 
ec_comma_v = re.compile(r'^EC(?= +?(MAG |MAJ |N(.{1,2}?) +JKB )*(VV |VA )(.{3,9}))(?!ETN)')
# 그 외 패턴.
ec = re.compile(r'^EC')
jks = re.compile(r'^JKS') # 보완 필요.
jkq = re.compile(r'^JKQ') # 보완 필요.
jx = re.compile(r'(?<=(N..)) ?JX')
sp = re.compile(r'^SP')
ef = re.compile(r'^EF')
jkb = re.compile(r'^JKB')
# 체언과 조사 관형사, 관형어 조합. 
# lookahead만 하면 뒤에서 걸러진 것들이기에 괜찮음.
# 조사가 많이 없이 긴 명사,
n_m_n_m = re.compile(r'(N.{1,2} (JKG |JKO )?|V.{1,2} (EP )*(ET.) |MM |MAG ){2,}(?=(MAG )?(V.{1,2} (EP )*(ET. )|MM )?(N.{1,2}) (JKQ|JKB|JKS|JX))') # pattern.end에서부터 매칭함...
# TODO: 너무 긴 명사구에서 마지막 부분 전에 띄어줌. 대신 지금 다음 띄어쓰기까지 나옴...

ef = re.compile(r'EF(?! [.!?])')
# negative lookbehind할 필요 없음. 위에 if 문에서 이미 다 걸러짐.

# 부사 파생 접미사는 높이, 멀리 등이고, 
# 부사격 조사는 ~께서, ~에서 등.

# 보완 필요.
# 두 경우 모두.
# 갈등을 유발할 때  
# 겨울철 우울증의 경우 사람들은
# 의사들은 강한 바나나 알러지 원숭이의 매우 큰 머리털의 경우 사람들이

# 뒷 문장 패턴까지 모두 검색해야 함...

# NN

def _tags_parsing(tokens: List) -> List:
    token_list = []
    token_tuple = None
    for token in tokens:
        # 명사 => XPN + NNG => NNG
        # NNG + XSN => NNG
        if not token_list:
            token_list.append((token.form, token.tag, token.start, token.len))
            continue
        
        token_tuple = (token.form, token.tag, token.start, token.end)
        
        if (token.tag == "NNG" 
            and token_list[-1][1] == 'XPN'             
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "NNG", prev_token[2], token.end)

        elif (token.tag == "XSN"       
            and token_list[-1][1] == 'NNG'             
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "NNG", prev_token[2], token.end)
            
            # tokens_tags
            # 요란/XR 히/XSM -> 요란히/MAG
            # 사랑/NNG 하/XSV 다/EF -> 사랑하/VV 다/E (동사 찾을 때 XSV도 찾아야함.)
            # 매콤/XR 하/XSA 다/EF -> 매콤하/VA 다/EF (형용사 찾을 때 XSA도 같이 찾아야 함.)
        elif (token.tag == "XSN"       
            and token_list[-1][1] == 'XR'             
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "NNG", prev_token[2], token.end)
        
        elif (token.tag == "XSV"       
            and (token_list[-1][1] == 'XR'
                or  token_list[-1][1] == 'NNG')            
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "VV", prev_token[2], token.end)
        
        elif (token.tag == "XSA"       
            and (token_list[-1][1] == 'XR'
                 or token_list[-1][1] == 'NNG')
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "VA", prev_token[2], token.end)
        
        elif (token.tag == "XSM"       
            and token_list[-1][1] == 'XR'             
            ):
            prev_token = token_list.pop()
            token_tuple = (prev_token[0]+token.form, "MAG", prev_token[2], token.end)
        
        # 조건에 맞지 않으면 그냥 return.
        token_list.append(token_tuple)

    return token_list

def num_to_korean(num: int) -> str:
    num_dict = {0: "영", 1: "일", 2: "이", 3: "삼", 4: "사", 5: "오", 6: "육", 7: "칠", 8: "팔", 9: "구"}
    unit_dict = {0: "", 1: "십", 2: "백", 3: "천", 4: "만", 5: "십", 6: "백", 7: "천", 8: "억", 9: "조"}
    num_str = str(num)
    num_str_len = len(num_str)
    korean = ""
    for idx, digit_char in enumerate(num_str):
        digit = int(digit_char)
        if digit != 0:
            korean += num_dict[digit]
            korean += unit_dict[num_str_len-idx-1]
    return korean

def morph_length_calculator(prev_morph, cur_morph):
    # 영어면 2글자.
    if cur_morph[1] == 'SL':
        return 2
    elif cur_morph[1] == 'SN':
        return len(num_to_korean(int(cur_morph[0])))
    elif prev_morph == None or prev_morph[3] != cur_morph[3]:
        return (cur_morph[3] - cur_morph[2])
    return 0

def _insert_comma(morphs: List[Tuple[str, str, int, int]]) -> None:
    comma_candidate = []
    prev_morph = None
    morphs_len = len(morphs)
    for i, morph in enumerate(morphs):
        comma_type = "word"
        # 앞으로 10개 형태소를 살펴봄.
        # 뒤로 10개 형태소를 살펴봄.
        prev_morphs = morphs[max(0,i-10): min(i+1, morphs_len)] # 현재 단어까지 반영.
        next_morphs = morphs[i:min(i + 10, len(morphs))]
        # 타입 확인
        tags_string = ' '.join([tag for _, tag, _, _ in next_morphs])
        prev_tags_string = ' '.join([tag for _, tag, _, _ in prev_morphs])
        # 용언 + 연결어미 + 보조용언 사이 index를 찾으면 0점.
        if ec_vx.search(tags_string):
            comma_type = "ec_vx" # comma_type = "ec_vx": 얘는 잡지 않음!
            end_index = ec_vx.search(tags_string).end()
        # 연결어미 + (부사어 or 보조사) + 용언
        elif ec_jx_comma_v.search(tags_string):
            comma_type = "ec_jx_comma_v"
            end_index = ec_jx_comma_v.search(tags_string).end()
        # 연결어미 + (부사어 or 보조사) + 용언
        elif ec_comma_v.search(tags_string):
            comma_type = "ec_comma_v"
            end_index = ec_jx_comma_v.search(tags_string).end()
        # 그 외 연결어미 존재 패턴.
        elif ec.search(tags_string):
            comma_type = "ec"
            end_index = ec.search(tags_string).end()
        # 주격 조사
        elif jks.search(tags_string):
            comma_type = "jks"
            end_index = jks.search(tags_string).end()
        # 인용격 조사
        elif jkq.search(tags_string):
            comma_type = 'jkq'
            end_index = jkq.search(tags_string).end()
        # 보조사
        elif jx.search(prev_tags_string):
            comma_type = 'jx'
            end_index = jx.search(tags_string).end()
        # 명사, 형용사, 부사 등으로만 이어진 긴 부분.
        elif n_m_n_m.search(prev_tags_string): 
            comma_type = 'n_m_n_m' # 명사, 형용사, 부사 등 여러 것 혼재.
            end_index = n_m_n_m.search(tags_string).end()
        elif jkb.search(tags_string):
            comma_type = 'jkb'
            end_index = jkb.search(tags_string).end()
        elif sp.search(tags_string):
            comma_type = 'sp'  # 이 부분 문제 생길수도..
            end_index = sp.search(tags_string).end()
        elif ef.search(tags_string):
            comma_type = 'ef'  # 이 부분도 문제 생길수도..
            end_index = ef.search(tags_string).end()
        morphs[end_index][3]
        morph_length = morph_length_calculator(prev_morph, morph) # 후에 길이 계산 체크 필요. (받침 등 형태소 타입 때문에...)
        comma_candidate.append((comma_type, morph_length)) # generator 안되면...
        #  yield (comma_type, morph_length, i)
        
        prev_morph = morph
        # 후에 타입 별 분류 가능.

        # 다음 쉬어가는 구간도 따로 넣어야 하긴 할텐데...
    

    return comma_candidate


def comma_type_one_hot_encode(comma_type):
    comma_candidate_type = {
        "ec_jx_comma_v": 0,
        "ec_comma_v": 0,
        "ec": 0,
        "jks": 0,
        'jkq': 0,
        'jx': 0,
        'n_m_n_m': 0,
        'jkb': 0,
        'sp': 0,
        'ef': 0 
    }
    if comma_type in comma_candidate_type:
        comma_candidate_type[comma_candidate_type] = 1
        return list(comma_candidate_type.values())


def _data_preprocessing(comma_candidate: List[Tuple[str, int]], comma_indices=False # 요건 나중에 추가할 때...?
                        ) -> Tuple:
    '''
    문장 당 preprocessing 작업임.
    딱 쉼표 후보군들만 추리는 과정임. 일반 word는 다 제외됨.        
    '''

    # type, token length, index -> return index list to insert comma.
    # 1. 먼저, sp와 ef를 기준으로 list를 나눔.
    # groups = groupby(comma_candidate, key=lambda x: x[0]!= "ef")  
    # key 결과로 true or false가 바뀌는 지점까지 group화.
    # ef_list = [list(group) for k, group in groups if k] # 그 key값이 true라면 list에 넣음.

    
    # input: ([0,0,0,0,1],10,40,50),([0,0,0,0,1], 6, 34, 50)
    #   -> subsentence 패턴, 전까지 길이, 남은 길이, 전체 길이.
    # output: [1, 0, 0, 1, 0] -> 해당 위치에서 쉼표 들어갈지 말지.
    # 다음 패턴이 나오는 길이...

    # sp나 ef가 나오기 전까지 list로 묶여 있음.

    X = []
    Y = []
    NO_COMMA = ('word', 'ec_vx') # 수정을 나중에 할 수도 있음.
    indices = [] # comma가 어디에 있는지 표기해줌.
    sent_len = sum(item[1] for item in comma_candidate) # 길이들의 합임.
    rest_sent_len = sent_len
    distance = 0
    is_comma = False
    for i, comma_token in enumerate(comma_candidate):
        if is_comma and comma_token[0] == 'sp':
            Y.append(1)
            indices.append(i) # comm
            is_comma = False
            continue
        if is_comma and comma_token[0] != 'sp':
            Y.append(0)
            is_comma = False
            continue             

        distance += comma_token[1] # morph length

        if comma_token[0] in NO_COMMA:
            continue
        
        rest_sent_len -= distance
        comma_type_encoded = comma_type_one_hot_encode(comma_token[0]) # one-hot-encoded.
        X.append([comma_type_encoded, distance, rest_sent_len, sent_len])
        is_comma = True           
        distance = 0
    
    if comma_indices == False:
        return (X, Y)
    
    return indices



# def sentence_parsing(sentence: str) -> str:
#     parsed_tokens = _tags_parsing(kiwi.tokenize(sentence, z_coda=False))
    
#     X, Y = _data_preprocessing(_insert_comma(parsed_tokens), comma_indices=False)

    # tags_string = ' '.join([tag for _, tag, _, _ in parsed_tokens])
    # # 용언 + 연결어미 + 보조용언 사이 index 찾음.
    # ec_vx_idx = [match.span() 
    #              for match in re.finditer(r'EC(?= +?VX{1})', tags_string)] # 제거해야 할 index들.
    
    # # 연결어미 + (부사어 or 보조사) + 용언
    # ec_v_idx= [match.span() 
    #              for match in re.finditer(r'EC(?=( +?JX)* ?(MAG |MAJ |N(.{1,2}) +JKB )* +?(VV|VA))', tags_string)]
    
    # # 그 다음 EC|EF를 수행...
    # ec_idx = [match.span() for match in re.finditer(r'(EC|EF)', tags_string)
    #           if match.span() not in ec_vx_idx]
    

    







    # copied_sentence = sentence

    # return copied_sentence
#TODO: typecast pattern은 deprecated.
# def typecast_pattern(tokens: List) -> List[int]:
#     # 그냥 sentence를 받고, 
#     # ·도 ,로 모두 대체 필요.

#     space_idx_flag = []
#     last_token_end, last_space_flag, copy_lsf = (0,0,0)
#     convert_idx_flag = []
#     lookbehind = False
#     for token in tokens:
#         # 공백 감지: end-len-1 => 반드시 형태소 끝. 
#         if (token.start - last_token_end) > 0: 
#             last_space_flag = (token.start-1)

#         if isinstance(re.match(r'(VX)|(EF)|(NNB)|(VCN)', token.tag), re.Match) and last_space_flag != 0:  
#             # 일반 용언 + 보조 용언 용언 뒤에 나오는 어미 확인. (종결어미나 연결어미)
#             # 연결어미 뒤에 , 넣어주면 훨씬 나은 것 같음.
#             # 의존명사 앞 공백 제거
#             # 부정지시사 앞에 공백 제거
#             # 긍정지시사 앞에 공백 제거
#             space_idx_flag.append(last_space_flag)
#             last_space_flag = 0
#             copy_lsf = last_space_flag
    
#         elif isinstance(re.match(r"(JKG)", token.tag), re.Match): 
#             # 접속부사 뒤에 공백 제거. (이게 맞을까? 첫 문장 부분이라면 하지 않는게 좋아보임.)
#             copy_lsf = last_space_flag
#             lookbehind = True

#         elif (last_space_flag != copy_lsf 
#               and last_space_flag != 0 
#               and lookbehind == True): # 새로운 flag를 찾았으니 괜찮음.
#             space_idx_flag.append(last_space_flag) 
#             last_space_flag, copy_lsf = (0,0)
#             lookbehind = False

#         elif isinstance(re.match(r'?', token.tag), re.Match):
#             # ?를 !로 변환함.
#             convert_idx_flag.append((token.start, "!"))
        
#         last_token_end = token.end
    
#     return space_idx_flag, convert_idx_flag




def training_comma():
    with open("./training_file/training_text.txt", 'r', encoding='utf-8') as ifile, open("result.txt", 'w', encoding='utf-8') as ofile:
        for lines in ifile.readlines():
            sentences = re.split('(?<=[.!?])[\u201D\u2019]? +', lines)
            # tokenized_list = [kiwi.tokenize(sentence, match_options=Match.JOIN_AFFIX) for sentence in sentences] # 이렇게 하면 잘 작동이 안된다.
            X = []
            Y = []
            for sentence in sentences:
                parsed_tokens = _tags_parsing(kiwi.tokenize(sentence, z_coda=False))
                x, y = _data_preprocessing(_insert_comma(parsed_tokens), comma_indices=False)
                X.extend(x)
                Y.extend(y)
    
            X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

            clf = GradientBoostingClassifier()
            clf.fit(X_train, y_train)

            y_pred = clf.predict(X_test)

            print(classification_report(y_test, y_pred))
            


                
            # tokenized_list = [kiwi.tokenize(sentence) for sentence in sentences] # 이렇게 하면 잘 작동이 안된다.
        
model = keras.Sequential()
model.add(layers.Embedding(input_dim=46))


if __name__ ==  '__main__':
    training_comma()            
            
                    
                
# [print(token.form, token.start, token.end) for sentence in kiwi.split_into_sents(s, return_tokens=True)
#   for token in sentence.tokens] # sentence 들로 나눠진다.
# [print(kiwi.split_into_sents(i, return_tokens=True)) for i in s]
