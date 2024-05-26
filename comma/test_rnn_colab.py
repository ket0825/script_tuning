# -*- coding: utf-8 -*-
"""test_rnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y9zh7XwhPj2FK8UHhLvbZKoNqx3Sw9T4
"""

# from google.colab import drive

# drive.mount('/content/drive')

# !pip install kiwipiepy

# import math
### import packages...
from keras.optimizers import Adam
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
from keras.models import Sequential
from keras.layers import Embedding, LSTM, TimeDistributed, Dense, Bidirectional
from keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from datetime import datetime
# from itertools import groupby
# from scipy.stats import truncnorm

### path setting
default_path = "/content/drive/MyDrive/Colab Notebooks/script_tuning"
training_file_path = default_path + "/training_file/training_text.txt"

# Global variable.
kiwi=Kiwi(model_type='sbg')
# tags = {
#     "NNG":0,
#     "NNP":1,
#     "NNB":2,
#     "NR":3,
#     "NP":4,
#     "VV":5,
#     "VA":6,
#     "VX":7,
#     "VCP":8,
#     "VCN":9,
#     "MM":10,
#     "MAG":11,
#     "MAJ":12,
#     "IC":13,
#     "JKS":14,
#     "JKC":15,
#     "JKG":16,
#     "JKO":17,
#     "JKB":18,
#     "JKV":19,
#     "JKQ":20,
#     "JX":21,
#     "JC":22,
#     "EP":23,
#     "EF":24,
#     "EC":25,
#     "ETN":26,
#     "ETM":27,
#     "XPN":28,
#     "XSN":29,
#     "XSV":30,
#     "XSA":31,
#     "XSM":32,
#     "XR":33,
#     "SF":34,
#     "SP":35, # 이거 치팅임.
#     "SS":36,
#     "SSO":37,
#     "SSC":38,
#     "SE":39,
#     "SO":40,
#     "SW":41,
#     "SL":42,
#     "SH":43,
#     "SN":44,
#     "UN":45,
# }

tags = {
    "NNG":0,
    "NNP":1,
    "NNB":2,
    "NR":3,
    "NP":4,
    "VV":5,
    "VA":6,
    "VX":7,
    "VCP":8,
    "VCN":9,
    "MM":10,
    "MAG":11,
    "MAJ":12,
    "IC":13,
    "JKS":14,
    "JKC":15,
    "JKG":16,
    "JKO":17,
    "JKB":18,
    "JKV":19,
    "JKQ":20,
    "JX":21,
    "JC":22,
    "EP":23,
    "EF":24,
    "EC":25,
    "ETN":26,
    "ETM":27,
    "XPN":28,
    "XSN":29,
    "XSV":30,
    "XSA":31,
    "XSM":32,
    "XR":33,
    "SF":34,
    "SS":35,
    "SSO":36,
    "SSC":37,
    "SE":38,
    "SO":39,
    "SW":40,
    "SL":41,
    "SH":42,
    "SN":43,
    "UN":44,
}
# 해당 패턴 바로 뒤에 쉼표인지 확인해야 함. 재조정 필요.
# ec_vx는 걸러내기 위한 패턴.

### regex patterns
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

def index_tags_encoding(enum: int, token_tag: str):
  '''
  index와 one-hot encoding을 같이 진행함.
  '''
  # after that, one-hot encoding by hierachical data.
  # enum, one-hot encoding...
  # ex) 용언 > 형용사, 동사, 서술격 조사...
  arr = np.zeros(len(tags)+1, dtype='float32')
  arr[0] = enum
  arr[tags.get(token_tag)+1] = 1
  return arr

def tags_encoding(token_tag: str):
  '''
  원본 tags_encoding
  '''
  # after that, one-hot encoding by hierachical data.
  # enum, one-hot encoding...
  # ex) 용언 > 형용사, 동사, 서술격 조사...
  arr = np.zeros(len(tags), dtype='float32')
  arr[tags.get(token_tag)] = 1
  return arr

# def hangul_vowel_consonant_separator(char:str): #  https://nunucompany.tistory.com/28 참고.
#     # 자음 19자, 모음 21자, 받침 27자.
#     chr()

def _new_tags_parsing(tokens: List, sentence_len:int, ignore_prefix_suffix=True
                      ) -> List[List]:
    token_list = []
    token_tuple = None
    comma_counter = 0

    for token in tokens:
        # 명사 => XPN + NNG => NNG
        # NNG + XSN => NNG
        if  "-"  in token.tag: # "VV-A, VA-I" 등 규칙 활용, 불규칙 활용 제거.
            token_tag = token.tag[0:token.tag.find("-")]
        else:
            token_tag = token.tag

        # comma 삭제 시 다음과 같이 표현됨.
        token_tuple = [token.form, token_tag, token.start - comma_counter, token.end - comma_counter, sentence_len]

        # first case.
        if not token_list:
            token_list.append(token_tuple)
            continue

        popped = False

        # token_tag를 확인하고, token_list의 가장 최근 것과 연동시킴.

        if ignore_prefix_suffix:
          if (token_tag == "NNG"
              and token_list[-1][1] == 'XPN' # 제일 최근에서 2번째.
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "NNG", prev_token[2], token_tuple[3], sentence_len]
              popped = True
          elif (token_tag == "XSN"
              and token_list[-1][1] == 'NNG'
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "NNG", prev_token[2], token_tuple[3], sentence_len]
              popped = True

              # tokens_tags
              # 요란/XR 히/XSM -> 요란히/MAG
              # 사랑/NNG 하/XSV 다/EF -> 사랑하/VV 다/E (동사 찾을 때 XSV도 찾아야함.)
              # 매콤/XR 하/XSA 다/EF -> 매콤하/VA 다/EF (형용사 찾을 때 XSA도 같이 찾아야 함.)
          elif (token_tag == "XSN"
              and token_list[-1][1] == 'XR'
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "NNG", prev_token[2], token_tuple[3], sentence_len]
              popped = True
          elif (token_tag == "XSV"
              and (token_list[-1][1] == 'XR'
                  or  token_list[-1][1] == 'NNG')
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "VV", prev_token[2], token_tuple[3], sentence_len]
              popped = True
          elif (token_tag == "XSA"
              and (token_list[-1][1] == 'XR'
                  or token_list[-1][1] == 'NNG')
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "VA", prev_token[2], token_tuple[3], sentence_len]
              popped = True
          elif (token_tag == "XSM"
              and token_list[-1][1] == 'XR'
              ):
              prev_token = token_list.pop()
              token_tuple = [prev_token[0]+token.form, "MAG", prev_token[2], token_tuple[3], sentence_len]
              popped = True

        # 이전 토큰 0, 1로 쉼표 태깅.
        # TODO: [TEST] 어차피 sequence인데 뒤에 쉼표가 있다고 1을 붙이나, 자기 앞에 있다고 1을 붙이나 똑같을 거 같은데?
        if token_list and not popped:
            if token.form ==  ',':
                # print(f"여기는 쉼표 자리임. {token_list[-1]}")
                token_list[-1].append(1)
                comma_counter += 1
            elif token_list[-1][-1] == 1:
                print(f"Here is the comma.")
            else:
                token_list[-1].append(0)

        if token_tag not in tags and token_tuple[0] != ',' :
            print("Not in token_Tag: ", token_tag)
            token_tuple[1] = 'NNG'

        # 쉼표가 아니어야만 함. 쉼표면 제거.
        if token_tuple[0] != ',':
          token_list.append(token_tuple)

        # print(f"최종 마지막 token: {token_list[-1]}")

    token_list[-1].append(0) # 마지막에 0 추가.

    if any((len(token) != 6 for token in token_list)):
        print("Wrong length!")
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


def _data_preprocessing_flatten(comma_candidate: List[Tuple[str, int]], comma_indices=False, # 요건 나중에 추가할 때...?
                      MAX_SIZE=100) -> Tuple: # MAX_SIZE는 padding을 위한 것임.
    '''
    MAX_SIZE는 padding을 위한 것임.
    문장 당 preprocessing 작업임.
    딱 쉼표 후보군들만 추리는 과정임. 일반 word는 다 제외됨.
    '''
    # token: [token.form, token_tag, token.start, token.end, sentence_len]
    x_len = (1    # sequence
            #  + 1  # start
            #  + 1  # end
            #  + 1  # sentence_length
             + 1  # token_length_list
             + 45 # tag_one_hot_encoded
             )    # => 50
    to_category = np.full(fill_value=255, shape=(MAX_SIZE, x_len), dtype='float32') # uint8에 최적화된 가장 큰 값인 255로 패딩 진행.
    y = np.full(fill_value=255, shape=(MAX_SIZE), dtype='float32') # uint8에 최적화된 가장 큰 값인 255로 패딩 진행.
    tokens_list_len = len(comma_candidate)
    # print(f"tokens_list_len: {tokens_list_len}")
    # print(f"comma_candidate:{comma_candidate}")

    for enum, tokens in enumerate(comma_candidate):
        # tokens: [token.form, token_tag, token.start, token.end, sentence_len, y]
        token_tag = tokens[1]
        # X 변환. 쉼표는 그냥 넘어감. tags에 없음.
        if tags.get(token_tag) != None:
            # encoded_tag = index_tags_encoding(enum,token_tag) # one-hot encoded np.array.
            encoded_tag = tags_encoding(token_tag) # one-hot encoded np.array.
            # tokenizing을 건드리는 곳.
            # sub_x = np.array([enum, tokens[2], tokens[3], tokens[4], tokens_list_len], dtype='float32')
            sub_x = np.array([enum, tokens_list_len], dtype='float32')
            sub_x = np.concatenate((sub_x, encoded_tag), axis=None)
            # print(f"sub_x: {sub_x}")
            # print(f"sub_x_len: {len(sub_x)}")
            to_category[enum] = sub_x
            # to_category = np.append(to_category, time_series_x, axis=0)
            # [[0,0,0,...,1],[1,0,0,1,...,0], ...] 기존 ragged와 약간 다름.
            # print(f"to_category : {to_category}")
            # print(f"encoded_tag : {encoded_tag}")
        else:
            print(f'Warning: Something did not encoded! token_tag:{token_tag}')
        try:
            label = tokens[-1]
            # print(f"label : {label}")
            # print(f"y : {y}")
            y[enum] = label
        except:# tokens[-1] if not exists...
            y[enum] = 0

    if not to_category.shape or not y.shape: # or use to_category.size! (현재 크게 의미없음.)
        print("error: empty in to_category or y")
    if any(elem not in (0, 1, 255) for elem in y):
        print("Invalid value")

    return to_category, y

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
    to_category = np.empty((0, 2), dtype='object') # 아래 np.append를 위하여 2차원 배열이라고 설정해줌.
    Y = np.empty((0, 2), dtype='object')
    for enum, tokens in enumerate(comma_candidate):
        token_tag = tokens[1]
        # X 변환
        time_series_x = []
        y = []
        encoded_tag = tags_encoding(token_tag) # one-hot encoded np.array.
        # now, index_tags_encoding.
        if tags.get(token_tag) != None:
            time_series_x = [enum, encoded_tag]
            # print(f"time_series_x : {time_series_x}")
            to_category = np.append(to_category, [time_series_x], axis=0) # nested list time_series => append well!
        # print(f"time_series_x : {time_series_x}")
        # print(f"to_category : {to_category}")

        else:
            print(f'Warning: Something did not encoded! token_tag:{token_tag}')

        # Y 변환

        try:
            y = tokens[4] # tokens[4] if not exists...
            Y = np.append(Y, [y], axis=0)
        except:
            Y = np.append(Y, [0],axis=0)

        # print(f"y : {y}")
        # print(f"Y : {Y}")

    if not to_category.tolist() or not Y.tolist(): # or use to_category.size!
        print("error: empty in to_category or Y")
    if any(y[1] not in (0, 1, -1) for y in Y):
        print("Invalid value")

    return to_category, Y

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
    with open( training_file_path, 'r', encoding='utf-8') as ifile, open("result.txt", 'w', encoding='utf-8') as ofile:
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

            X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2,
                                                                random_state=42
                                                                )

            clf = GradientBoostingClassifier()
            clf.fit(X_train, y_train)

            y_pred = clf.predict(X_test)

            print(classification_report(y_test, y_pred))

"""## Data Preprocessing

### 손실함수 custom
"""

# 손실함수 custom
def weighted_binary_crossentropy(y_true, y_pred_logits):
    # 클래스 가중치 설정
    # 비율: 0.0253 => 1:39.5...
    class_weight_0 = 1  # 0 클래스의 가중치
    class_weight_1 = 39.5  # 1 클래스의 가중치

    mask = tf.cast(tf.not_equal(y_true, 255), tf.float32) # not_equal 값만 true로 만들어서 casting.
    # 실제로 masking layer를 생성하여 행렬곱이 아닌 element-wise 곱으로 표현한 것임.
    # ex) [[1 1 0]. [1, 1, 0]] 이면 0 부분이 y_true에서 255였다는 것임.
    # print(f"mask.shape: {mask.shape}") # (None, 100)
    # print(f"mask: {mask}") # (None, 100)
    # print(f"y_pred_logits.shape: {y_pred_logits.shape}") # (None, 100)
    # print(f"y_true.shape: {y_true.shape}") # (None, 100)

    # 가중치가 적용된 손실 계산
    weighted_bce = tf.nn.weighted_cross_entropy_with_logits(labels=y_true,
                                                            logits=y_pred_logits,
                                                            pos_weight=class_weight_1,)
    # print(f"weighted_bce.shape: {weighted_bce.shape}") # 예상: (None, 100)

    weighted_bce *= mask # element-wise 곱셈 필요. # 잘 나오는지 확인해보기.
    print(f"weighted_bce.shape: {weighted_bce.shape}")

    # 배치별 평균 손실 계산
    sum_weighted_bce = tf.reduce_sum(weighted_bce)
    sum_mask = tf.reduce_sum(mask)

    final_loss = sum_weighted_bce / sum_mask
    # print(f"final_loss.shape: {final_loss.shape}")
    # print(f"final_loss: {final_loss}")

    # mask.shape: (None, 100)
    # y_pred_logits.shape: (None, 100)
    # y_true.shape: (None, 100)
    # weighted_bce.shape: (None, 100)
    # weighted_bce.shape: (None, 100)
    # final_loss.shape: ()

    return final_loss

def weighted_binary_crossentropy_prob(y_true, y_pred):
    # 클래스 가중치 설정
    # 비율: 0.0253 => 1:39.5...
    class_weight_0 = 1  # 0 클래스의 가중치
    class_weight_1 = 39.5  # 1 클래스의 가중치

    mask = tf.cast(tf.not_equal(y_true, 255), tf.float32) # not_equal 값만 true로 만들어서 casting.
    # 실제로 masking layer를 생성하여 행렬곱이 아닌 element-wise 곱으로 표현한 것임.
    # ex) [[1 1 0]. [1, 1, 0]] 이면 0 부분이 y_true에서 255였다는 것임.
    # print(f"mask.shape: {mask.shape}") # (None, 100)
    # print(f"y_pred_logits.shape: {y_pred_logits.shape}") # (None, 100)
    # print(f"y_true.shape: {y_true.shape}") # (None, 100)

    # 가중치가 적용된 손실 계산
    y_pred_logits = tf.math.log(y_pred / (1 - y_pred + 1e-7))
    weighted_bce = tf.nn.weighted_cross_entropy_with_logits(labels=y_true,
                                                            logits=y_pred_logits,
                                                            pos_weight=class_weight_1,)
    # print(f"weighted_bce.shape: {weighted_bce.shape}") # 예상: (None, 100)

    weighted_bce *= mask # element-wise 곱셈 필요. # 잘 나오는지 확인해보기.
    # print(f"weighted_bce.shape: {weighted_bce.shape}")

    # 배치별 평균 손실 계산
    sum_weighted_bce = tf.reduce_sum(weighted_bce)
    sum_mask = tf.reduce_sum(mask)

    final_loss = sum_weighted_bce / sum_mask
    # print(f"final_loss.shape: {final_loss.shape}")
    # print(f"final_loss: {final_loss}")

    # mask.shape: (None, 100)
    # y_pred_logits.shape: (None, 100)
    # y_true.shape: (None, 100)
    # weighted_bce.shape: (None, 100)
    # weighted_bce.shape: (None, 100)
    # final_loss.shape: ()
    return final_loss

# TODO: previous version.
# main function
# X = []
# Y = []
# Y_for_stratified = []
# original_data = [] # 원본 string 보존.
# # TODO: 원본 string에서 줄바꿈 어디서 다시 해야 하는지 마킹 필요.
# neg_count = 0
# pos_count = 0
# with open(training_file_path, 'r', encoding='utf-8') as ifile, open("result.txt", 'w', encoding='utf-8') as ofile:
#     for lines in ifile.readlines():
#         # sentences = lines.replace("\u201D", "'").replace("\u2019", '"').replace("\u200D", "'").replace("\u2018", '"')
#         sentences = re.split('(?<=[.!?])[\u201D\u2019]?\s+', lines.rstrip())
#         # tokenized_list = [kiwi.tokenize(sentence, match_options=Match.JOIN_AFFIX) for sentence in sentences] # 이렇게 하면 잘 작동이 안된다.
#         # sentences = kiwi.split_into_sents(lines) # 잘 작동 안함.
#         print(f"sentences: {sentences}")
#         for sentence in sentences:
#             original_data.append(sentence)
#             sentence_len = len(sentence)
#             parsed_tokens= _new_tags_parsing(kiwi.tokenize(sentence, z_coda=False),
#                                              sentence_len,
#                                              ignore_prefix_suffix=True)
#             x, y = _data_preprocessing_flatten(parsed_tokens)
#             X.append(x)
#             Y.append(y) # y = [[0,0],[1,0]...]
#             if np.any(y == 1): # ndarray중 하나라도 1이 있으면 1 추가.
#               Y_for_stratified.append(1)
#             else: # 아니면 0 추가.
#               Y_for_stratified.append(0)

#             # count 0 and 1
#             for label in y:
#               if label == 0:
#                 neg_count+=1
#               elif label == 1:
#                 pos_count+=1

# new version.
X = []
Y = []
Y_for_stratified = []
original_data = [] # 원본 string 보존.
# TODO: 원본 string에서 줄바꿈 어디서 다시 해야 하는지 마킹 필요.
neg_count = 0
pos_count = 0

import pandas as pd

training_data = pd.read_csv("data/csv/training_data.csv", encoding='utf-8')
test_data = pd.read_csv("data/csv/test_data.csv", encoding='utf-8')

# 그냥 하나로 합침.
data = training_data + test_data
data["parsed_token_text"] = _new_tags_parsing(data["Text"].apply(kiwi.tokenize))

print(data)
# with open(training_file_path, 'r', encoding='utf-8') as ifile, open("result.txt", 'w', encoding='utf-8') as ofile:
#     for lines in ifile.readlines():
#         # sentences = lines.replace("\u201D", "'").replace("\u2019", '"').replace("\u200D", "'").replace("\u2018", '"')
#         sentences = re.split('(?<=[.!?])[\u201D\u2019]?\s+', lines.rstrip())
#         # tokenized_list = [kiwi.tokenize(sentence, match_options=Match.JOIN_AFFIX) for sentence in sentences] # 이렇게 하면 잘 작동이 안된다.
#         # sentences = kiwi.split_into_sents(lines) # 잘 작동 안함.
#         print(f"sentences: {sentences}")
#         for sentence in sentences:
#             original_data.append(sentence)
#             sentence_len = len(sentence)
#             parsed_tokens= _new_tags_parsing(kiwi.tokenize(sentence, z_coda=False),
#                                              sentence_len,
#                                              ignore_prefix_suffix=True)
#             x, y = _data_preprocessing_flatten(parsed_tokens)
#             X.append(x)
#             Y.append(y) # y = [[0,0],[1,0]...]
#             if np.any(y == 1): # ndarray중 하나라도 1이 있으면 1 추가.
#               Y_for_stratified.append(1)
#             else: # 아니면 0 추가.
#               Y_for_stratified.append(0)

#             # count 0 and 1
#             for label in y:
#               if label == 0:
#                 neg_count+=1
#               elif label == 1:
#                 pos_count+=1


# max_x_len = 0
# for x in X:
#     max_x_len = max(len(x), max_x_len)

# print(f"Max length of tokens: {max_x_len}")
# print(f"negative case: {neg_count}")
# print(f"positive case: {pos_count}")
# print(f"X length: {len(X)}")
# print(f"Y length: {len(Y)}")
# print(f"Y_for_stratified length: {len(Y_for_stratified)}")
# print(f"Y_for_stratified[0]: {Y_for_stratified[0]}")

# print(f"X[0]: {X[0]}")
# print(f"Y[0]: {Y[0]}")

# Y0 = [y for y in Y[0] if y != 255]
# X0 = [sub_x[0] for sub_x in X[0] if sub_x[0] != 255]
# Y0_len = len(Y0)
# X0_len = len(X0)
# print(f"Y0: {Y0}")
# print(f"X0: {X0}")
# print(f"Y0_len: {Y0_len}")
# print(f"X0_len: {X0_len}")

# X = np.array(X)
# Y = np.array(Y)

# """## Split data"""

# X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2,
#                                                     random_state=42,
#                                                     stratify=Y_for_stratified)

# print(f"X_train.shape: {X_train.shape}, y_train.shape: {y_train.shape}") # (926, 100, 47) (926, 100)
# print(f"X_train[0]: {X_train[0]}")
# print(f"y_train[0]: {y_train[0]}")

# """## Data visualization"""

# import matplotlib.pyplot as plt

# # 예시 데이터

# # 데이터 및 라벨 설정
# counts = [neg_count, pos_count]
# labels = ['neg', 'pos']

# # 히스토그램 생성
# plt.bar(labels, counts)

# # 레이블 및 제목 설정
# plt.xlabel('Cases')
# plt.ylabel('Count')
# plt.title(f'negative and positive cases: ratio: {pos_count/neg_count :.4f}')

# # 그래프 표시
# plt.show()
# print(f"희망비율: {round(1/(pos_count/neg_count), 2)}") # 현재는 39.5

# """## Model Callback"""

# from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger
# from datetime import date, datetime, timezone, timedelta

# KST = timezone(timedelta(hours=9))
# time_record = datetime.now(KST)
# today_date = time_record.strftime("%Y%m%d")
# today_date_sec = time_record.strftime("%Y%m%d%h%m%s")

# early_stopping = EarlyStopping(monitor='val_loss', patience=10, min_delta=1e-4)

# # 0.8 이상 precision이어야 함.
# model_checkpoint =  ModelCheckpoint(filepath=f"{default_path}/model/{today_date_sec}", monitor='val_masked_precision',
#                                     save_best_only=True, save_weights_only=False,
#                                     mode='max', initial_value_threshold=0.8,)
# reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5,)
# csv_logger = CSVLogger(f'{default_path}/log/{today_date}_training.log', append=True)

# """## Model Metric"""

# class MaskedBinaryAccuracy(tf.keras.metrics.Metric):
#     def __init__(self, name='masked_binary_accuracy', **kwargs):
#         super(MaskedBinaryAccuracy, self).__init__(name=name, **kwargs)
#         self.accuracy = tf.keras.metrics.BinaryAccuracy()

#     def update_state(self, y_true, y_pred, sample_weight=None):
#         mask = tf.cast(tf.not_equal(y_true, 255), tf.float32)
#         self.accuracy.update_state(y_true, y_pred, sample_weight=mask)

#     def result(self):
#         return self.accuracy.result()

#     def reset_state(self):
#         self.accuracy.reset_state()


# class MaskedPrecision(tf.keras.metrics.Metric):
#     def __init__(self, name='masked_precision', **kwargs):
#         super(MaskedPrecision, self).__init__(name=name, **kwargs)
#         self.precision = tf.keras.metrics.Precision()

#     def update_state(self, y_true, y_pred, sample_weight=None):
#         mask = tf.cast(tf.not_equal(y_true, 255), tf.float32)
#         self.precision.update_state(y_true, y_pred, sample_weight=mask)

#     def result(self):
#         return self.precision.result()

#     def reset_state(self):
#         self.precision.reset_state()

# class MaskedRecall(tf.keras.metrics.Metric):
#     def __init__(self, name='masked_recall', **kwargs):
#         super(MaskedRecall, self).__init__(name=name, **kwargs)
#         self.recall = tf.keras.metrics.Recall()

#     def update_state(self, y_true, y_pred, sample_weight=None):
#         mask = tf.cast(tf.not_equal(y_true, 255), tf.float32)
#         self.recall.update_state(y_true, y_pred, sample_weight=mask)

#     def result(self):
#         return self.recall.result()

#     def reset_state(self):
#         self.recall.reset_state()

# """## Model Architecture"""

# # model setting.
# from keras.layers import Masking

# vocab_size = 45  # 문법 태그의 가짓수

# embedding_dim = 64
# hidden_units = 256
# initial_bias = tf.keras.initializers.Constant(np.log(pos_count / neg_count))
# print(initial_bias)

# model = Sequential()
# # Masking 레이어 추가. 모든 특성이 255인 timestamp 시퀀스를 무시합니다.

# # 각종 정보: sequence, (position start, position end,) token length,
# # (sentence length,) one_hot_encoded_tag  => 최종 size: 47 (50)

# model.add(Masking(mask_value=255, input_shape=(100, 47)))

# # model.add(Bidirectional(LSTM(hidden_units, return_sequences=True, input_shape=(100, 50))))  # 첫 LSTM 레이어에만 input_shape 지정 필요. batch는 고려하지 않음.
# # model.add(Bidirectional(LSTM(256, return_sequences=True, input_shape=(100, 50))))  # 첫 LSTM 레이어에만 input_shape 지정 필요. batch는 고려하지 않음.
# model.add(Bidirectional(LSTM(256, return_sequences=True)))  # return_sequences=True로 설정
# model.add(Bidirectional(LSTM(128, return_sequences=True)))  # return_sequences=True로 설정
# # model.add(Bidirectional(LSTM(64, return_sequences=True)))  # return_sequences=True로 설정
# # model.add(TimeDistributed(Dense(256, activation='relu')))
# model.add(TimeDistributed(Dense(128, activation='relu')))
# model.add(TimeDistributed(Dense(64, activation='relu')))
# model.add(TimeDistributed(Dense(32, activation='relu')))
# model.add(TimeDistributed(Dense(16, activation='relu')))
# # model.add(TimeDistributed(Dense(1, activation='relu')))

# # for testing bias initializer.
# model.add(TimeDistributed(Dense(1, activation='sigmoid',
#                                 bias_initializer=initial_bias,
#                                 )))
# model.add(tf.keras.layers.Lambda(lambda x: tf.squeeze(x, axis=-1)))  # 차원 축소
# # 선택사항: 초기 바이어스를 올바로 설정합니다.
# # 이와 같은 초기 추측은 적절하지 않습니다. 데이터세트가 불균형하다는 것을 알고 있으니까요. 출력 레이어의 바이어스를 설정하여 해당 데이터세트를 반영하면(참조: 신경망 훈련 방법: "init well") 초기 수렴에 유용할 수 있습니다.

# # 기본 바이어스 초기화를 사용하면 손실은 약 math.log(2) = 0.69314

# # 사용 금지 model.add(tf.keras.layers.Flatten()) # Flatten 사용 시, 시퀀스 구조 잃게 될 수 있음.
# model.summary()

# """## Model Compile"""

# # weighted_binary_crossentropy 사용.

# optimizer = Adam(learning_rate=5e-4)
# model.compile(
#     # loss=weighted_binary_crossentropy,
#     loss=weighted_binary_crossentropy_prob,
#     # loss='binary_crossentropy',
#               optimizer=optimizer,
#               metrics=[
#                       MaskedPrecision(),
#                        MaskedBinaryAccuracy(),
#                        MaskedRecall(),
#                        ],
#               )

# # weights = model.layers[-1].layer.get_weights()  # 마지막 레이어 (TimeDistributed)의 가중치

# # 편향 출력
# # bias = weights  # 편향은 일반적으로 가중치 리스트의 두 번째 요소입니다
# # print("Bias:", bias)

# training_history = model.fit(X_train, y_train,
#           epochs=100,
#           batch_size=100,
#           validation_split=0.2,
#           verbose=1,
#           callbacks=[
#               # early_stopping,
#               model_checkpoint,
#               reduce_lr,
#               csv_logger
#               ],
#                              )
#           # class_weight param을 이용해도 가중치를 둘 수 있었음...

# y_pred = model.predict(X_test)

# results = model.evaluate(X_test, y_test, verbose=1)
# loss = results[0]
# precision = results[1]
# print(f"Test Loss: {loss}")
# print(f"Test precision: {precision}")

# print(training_history.history)
# plt.plot(training_history.history["masked_precision"])
# plt.plot(training_history.history["val_masked_precision"])
# plt.title('Model precision')
# plt.xlabel('Epoch')
# plt.ylabel('Precision')
# plt.legend(['Train', 'Val'], loc='upper left')
# plt.show()

# plt.plot(training_history.history["loss"])
# plt.plot(training_history.history["val_loss"])
# plt.title('Model loss')
# plt.xlabel('Epoch')
# plt.ylabel('loss')
# plt.legend(['Train', 'Val'], loc='upper left')
# plt.show()

# plt.plot(training_history.history["masked_binary_accuracy"])
# plt.plot(training_history.history["val_masked_binary_accuracy"])
# plt.title('Model accuracy')
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy')
# plt.legend(['Train', 'Val'], loc='upper left')
# plt.show()

# plt.plot(training_history.history["masked_recall"])
# plt.plot(training_history.history["val_masked_recall"])
# plt.title('Model recall')
# plt.xlabel('Epoch')
# plt.ylabel('Recall')
# plt.legend(['Train', 'Val'], loc='upper left')
# plt.show()

# # 현재 새로운 학습 데이터로 성능이 잘 안나오고 있음.
# # 시도해볼 방법들 몇 가지가 있음.
# # 1. 모델 간소화
# # 2. const bias 미반영.
# # 3. 다른 데이터들 미반영 (position start 등...)
# # 4. 텍스트 데이터 추가
