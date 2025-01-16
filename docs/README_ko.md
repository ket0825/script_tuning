# Script tuning
- 대본 자체를 바꾸어 더 자연스러운 TTS 서비스를 만들고자 하였습니다.
- **Pykospacing, kiwipiepy, pdfplumber, tkinter, clova-stuido-api* 를 사용하였습니다.

---------------

## 구성
- ### Comma
  - 쉼표를 넣어 자연스러운 TTS 스크립트를 만들었습니다.
  - 간단한 RNN으로 테스트를 해보았지만, 데이터 불균형으로 인해 잘 작동하지 않았습니다.
  - => fine-tuned model을 사용하는 clova-studio-api를 채택하였습니다.
  - 텍스트를 csv로 변환하고 tkinter gui를 통해 clova-studio-api를 사용합니다.
  - 사람의 확인을 통해 정확도가 99% 이상이 되어 PoC를 진행하였습니다.
  
------------------------------

- ### venv script tuning
  - pdf에서 텍스트를 추출하는 과정입니다.
  - pykospacing, kiwipiepy, pdfplumber를 사용합니다.
  - 규칙 기반의 pdf 파싱 및 텍스트 처리를 진행합니다.