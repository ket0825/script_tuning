# -*- coding: utf-8 -*-
# I/O Bound 작업: I/O Waiting이 오래 걸림 
# 작업에 의한 병목. CPU 연산에 대한 병목이 아님.

import base64
import json
import http.client
import csv
import asyncio
import aiohttp
import time
from typing import List
import os
from dotenv import load_dotenv

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id, filename):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id
        self._filename = filename

    def _get_filename(self):
        return self._filename

    def _send_request(self, completion_request):
        try:
            time.sleep(1)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
                'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
                'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
            }
            conn = http.client.HTTPSConnection(self._host)
            conn.request('POST', '/testapp/v1/tasks/oi5dnssz/completions', json.dumps(completion_request), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode(encoding='utf-8'))
            conn.close()
            return result
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    def execute(self, completion_request, idx):
        print(f"작업 시작: {idx}번째")
        retry_count = 0
        while retry_count < 5:
            try:
                res = self._send_request(completion_request)
                print(f"작업 완료: {idx}번째, status code: {res['status']['code']}")
                if res['status']['code'] == '20000':
                    return res['result']['text']
                else:
                    print(f"Error: status code: {res['status']['code']} \n \
                        retry count: {retry_count}")
                    
            except Exception as e:
                print(f"Request failed: {e} \n \
                    retry count: {retry_count}")
            
            time.sleep(2)
            retry_count+=1

        return f"재시도_{idx}"
     
# request 보내고, 결과는 나중에 받음.
# 바로 다음 작업은 보낸 후 1초 후에 또 request를 보냄.
# 이 작업을 끝까지 진행함.
        
class AsyncCompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id, filename):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id
        self._filename = filename

    def _get_filename(self):
        return self._filename

    async def _send_request(self, completion_request):
        try:
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
                'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
                'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url=f'https://{self._host}/testapp/v1/tasks/oi5dnssz/completions',
                                        data=json.dumps(completion_request), 
                                        headers=headers
                                        ) as response:
                    result = await response.json()
                    return result
                
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    async def execute(self, completion_request, idx):
        print(f"작업 시작: {idx}번째")        
        try:
            res = await self._send_request(completion_request)
            print(f"작업 완료: {idx}번째, status code: {res['status']['code']}")
            if res['status']['code'] == '20000':
                if completion_request.get('startswithQuotes'):
                    res['result']['text'] = "'" + res['result']['text']
                if completion_request.get('endswithQuotes'):
                    res['result']['text'] += "'"
                return res['result']['text']
            else:
                print(f"Error: status code: {res['status']['code']}")
                
        except Exception as e:
            print(f"Request failed: {e}")
        
        return f"재시도_{idx}"


async def async_main(filename_list:List[str], output_txt_list:List[str]):
    # 95kb => 821 sec : 1kb => 8.64 sec    
    print("async 작업 시작")
    for filename, output_txt_filename in zip(filename_list, output_txt_list):
        if filename.find(".csv") > 0:
            filename = filename[:filename.find(".csv")]
        print(f"filename: {filename}")
        print(f"output_txt_filename: {output_txt_filename}")
        load_dotenv()
        host = os.environ.get("HOST")
        api_key = os.environ.get("API_KEY")
        api_key_primary_val = os.environ.get("API_KEY_PRIMARY_VAL")
        request_id = os.environ.get("RESQUEST_ID")
        print(f"filename: {filename}")
        preset_texts = []    
        with open(f"{filename}.csv", 'r', encoding='utf-8-sig') as csvf:
            csvf_reader = csv.reader(csvf)
            for sentence in csvf_reader:   
                    if not sentence:
                        continue
                    preset_text = sentence[0]            
                    if preset_text == "":
                        continue            

                    preset_text = finish_with_period(preset_text)
                    preset_texts.append(preset_text)

        response_texts = []

        completion_executor = AsyncCompletionExecutor(
            host=host,
            api_key=api_key,
            api_key_primary_val=api_key_primary_val,
            request_id=request_id,
            filename=filename
        )

        tasks = []
        for idx, preset_text in enumerate(preset_texts):  
            preset_text = preset_text.strip()
            request_data = {
            'text': preset_text,
            'start': '',
            'restart': '',
            'includeTokens': False,
            'topP': 0.8,
            'topK': 2,
            'maxTokens':200,
            'temperature': 0,
            'repeatPenalty': 0.8,
            'stopBefore': ['<|endoftext|>'],
            'includeAiFilters': False,
            'includeProbs': False,
            }
            await asyncio.sleep(1.1)
            tasks.append(asyncio.create_task(completion_executor.execute(request_data, idx)))

        for idx, (preset_text, task) in enumerate(zip(preset_texts, tasks)):
            try:
                response_text = await task
            except Exception as e:
                print(f"[Error] in receiving tasks: {e}")

            print(f"전: {preset_text}")
            print(f"후: {response_text}")
            
            # 무조건 아래에서 check_sentence_similarity에서 false가 나오기에 미리 처리.
            if response_text == f"재시도_{idx}":
                response_texts.append(response_text)
                
                # with open(f"{filename}_에러목록.csv", 'a', encoding='utf-8-sig', newline='') as csvf:
                #     file_exists = os.path.isfile(f"{filename}_에러목록.csv") and os.path.getsize(f"{filename}_에러목록.csv") > 0    
                #     csv_writer = csv.writer(csvf)
                #     if not file_exists:
                #         header = ["텍스트", "필요한 조치"]
                #         csv_writer.writerow(header)

                #     csv_writer.writerow([preset_text, f"재시도_{idx}"])

                continue

            elif not check_sentence_similarity(preset_text, response_text):
                with open(f"{output_txt_filename}_에러목록.csv", 'a', encoding='utf-8-sig', newline='') as csvf:
                    csv_writer = csv.writer(csvf)
                    file_exists = os.path.isfile(f"{output_txt_filename}_에러목록.csv") and os.path.getsize(f"{output_txt_filename}_에러목록.csv") > 0    
                    if not file_exists:
                        header = ["텍스트", "필요한 조치"]
                        csv_writer.writerow(header)
                        
                    csv_writer.writerow([preset_text, f"직접확인_{idx}"])

                response_texts.append(f"직접확인_{idx}")

            else:
                response_texts.append(response_text)

        ## retry pattern
        # 여기선 일일이 하나씩 기다려가며 진행함.
        tasks.clear()

        for idx, (preset_text, response_text) in enumerate(zip(preset_texts, response_texts)):
            if response_text == f"재시도_{idx}":
                preset_text = preset_text.strip()
                startswith_quotes = False
                endswith_quotes = False
                parsed_text = preset_text
                if preset_text[0] == "'":
                    parsed_text = preset_text[1:]
                    startswith_quotes = True
                if preset_text[-1] == "'":
                    parsed_text = preset_text[:-1]
                    endswith_quotes = True

                request_data = {
                'text': parsed_text,
                'start': '',
                'restart': '',
                'includeTokens': False,
                'topP': 0.8,
                'topK': 2,
                'maxTokens':200,
                'temperature': 0,
                'repeatPenalty': 0.8,
                'stopBefore': ['<|endoftext|>'],
                'includeAiFilters': False,
                'includeProbs': False
                }
                await asyncio.sleep(2) # async를 더 크게 설정함.
                response_text = await completion_executor.execute(request_data, idx)
                response_texts[idx] = response_text

        print(f"총 request 수: {len(preset_texts)}")

        with open(output_txt_filename, "w", encoding='utf-8-sig') as f:
            f.write(' '.join(response_texts))


def main():
    filename = "data/csv/sample_text1"
    if filename in ".csv":
        filename = filename[:filename.find(".csv")]

    load_dotenv()
    host = os.environ.get("HOST")
    api_key = os.environ.get("API_KEY")
    api_key_primary_val = os.environ.get("API_KEY_PRIMARY_VAL")
    request_id = os.environ.get("RESQUEST_ID")

    preset_texts = []
    response_texts = []
    with open(f"{filename}.csv", 'r', encoding='utf-8-sig') as csvf:
        csvf_reader = csv.reader(csvf)
        completion_executor = CompletionExecutor(
            host=host,
            api_key=api_key,
            api_key_primary_val=api_key_primary_val,
            request_id=request_id,
            filename=filename
        )
        for idx, sentence in enumerate(csvf_reader):   
            if not sentence:
                continue

            preset_text = sentence[0]
            if preset_text == "":
                continue

            preset_text = finish_with_period(preset_text)
            request_data = {
            'text': preset_text,
            'start': '',
            'restart': '',
            'includeTokens': False,
            'topP': 0.8,
            'topK': 2,
            'maxTokens':200,
            'temperature': 0,
            'repeatPenalty': 0.8,
            'stopBefore': ['<|endoftext|>'],
            'includeAiFilters': False,
            'includeProbs': False
            }            

            response_text = completion_executor.execute(request_data, idx)
            preset_texts.append(preset_text)
            response_texts.append(response_text)

    for idx, (preset_text, response_text) in enumerate(zip(preset_texts, response_texts)):
        print(f"전: {preset_text}")
        print(f"후: {response_text}")

        if response_text == f"재시도_{idx}":
            response_texts.append(response_text)
            request_data = {
            'text': preset_text,
            'start': '',
            'restart': '',
            'includeTokens': False,
            'topP': 0.8,
            'topK': 2,
            'maxTokens':200,
            'temperature': 0,
            'repeatPenalty': 0.8,
            'stopBefore': ['<|endoftext|>'],
            'includeAiFilters': False,
            'includeProbs': False
            }    
            # change by directly.
            retried_text = completion_executor.execute(request_data, idx)
            response_texts[idx] = retried_text
            # with open(f"{filename}_에러목록.csv", 'a', encoding='utf-8-sig', newline='') as csvf:
            #     file_exists = os.path.isfile(f"{filename}_에러목록.csv") and os.path.getsize(f"{filename}_에러목록.csv") > 0    
            #     csv_writer = csv.writer(csvf)
            #     if not file_exists:
            #         header = ["텍스트", "필요한 조치"]
            #         csv_writer.writerow(header)

            #     csv_writer.writerow([preset_text, f"재시도_{idx}"])
            # continue

        if not check_sentence_similarity(preset_text, preset_text):
            with open(f"{filename}_에러목록.csv", 'a', encoding='utf-8-sig', newline='') as csvf:
                csv_writer = csv.writer(csvf)
                file_exists = os.path.isfile(f"{filename}_에러목록.csv") and os.path.getsize(f"{filename}_에러목록.csv") > 0    
                if not file_exists:
                    header = ["텍스트", "필요한 조치"]
                    csv_writer.writerow(header)

                csv_writer.writerow([preset_text, f"직접확인_{idx}"])
                print(f"직접확인_{idx}")

            response_texts.append(f"직접확인_{idx}")
        else:
            response_texts.append(preset_text)
    
    print(f"총 request 수: {len(preset_texts)}")
    
    with open(f"{filename}_처리완료.txt", "w", encoding='utf-8-sig') as f:
        f.write(' '.join(response_texts))
    

def make_chunk(sent_len_buffer_limit: int, 
               csvf_reader,
               )-> List[str]:
    reader_buffer = []
    sent_len_buffer = 0
    sent_len_buffer_limit = 500
    sent_buffer = ""
    for sent in csvf_reader:
        cur_sent = sent[0]
        
        if cur_sent == '': 
            sent_buffer = sent_buffer.rstrip()
            sent_buffer += "\n"
        # check sent if there is an punctuation.
        elif cur_sent.find(".") < 1 and cur_sent.find("!") < 1 and cur_sent.find("?") < 1:
            sent_buffer += cur_sent + ". "
        else:
            sent_buffer += cur_sent + " "
        
        sent_len_buffer += len(cur_sent)

        if sent_len_buffer > sent_len_buffer_limit or cur_sent == "<|endoftext|>":
            sent_buffer = sent_buffer.rstrip()
            reader_buffer.append(sent_buffer)
            sent_buffer = ""
            sent_len_buffer = 0


def finish_with_period(sentence):
    if sentence.find(".") < 1 and sentence.find("!") < 1 and sentence.find("?") < 1:
        sentence += "."
    return sentence

def check_sentence_similarity(preset_text, response_text):
    parsed_preset_text = preset_text.replace(",", "")
    parsed_response_text = response_text.replace(",", "")

    if parsed_response_text != parsed_preset_text:
        return False
    
    return True

if __name__ == '__main__':
    filename_list = ["data/csv/sample_text1", "data/csv/sample_text2"]
    output_filename_list = [filename[filename.rfind("/"):].replace(".csv", "") + "_처리완료.txt"  for filename in filename_list]
    t1 = time.time()
    asyncio.run(async_main(filename_list, output_filename_list))
    t2 = time.time()
    print(f"async 작업으로 소요된 시간: {(t2-t1):.2f}초")
    # 총 request 수: 738
    # async 작업으로 소요된 시간: 821.22

    # t1 = time.time()
    # main()
    # t2 = time.time()
    # print(f"일반 작업으로 소요된 시간: {(t2-t1):.2f}초")
    # 총 request 수: 790
    # 일반 작업으로 소요된 시간: 1421.05초

    #TODO: 일단 지금까지는 다시확인 해야 할 것은 전부 맨 앞 단어, 혹은 부사에 국한되었음. 이후 데이터 추가되어도 괜찮을지 확인해보기.
    


     

   
