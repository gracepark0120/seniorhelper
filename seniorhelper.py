from stt import STTcall
from tts import TTScall
import time
from questions import Questions 
from functions import gpt_response,calculate_Criteria,DementiaDiagnosis
import random
import sys
# chatgpt에 역할 부여
messages = [{"role": "system", "content": "너는 노인과 대화하는 chatgpt인 seniorhelper야. 사용자한테 질문 많이 해주고 첫 질문은 오늘 하루에 대해서 물어봐줘."}]
KeyInquiry = []
start_time = time.time()
keyDetect = False
stt_error = 0
start = True
# 희망 대화 길이 입력 받기
chat_time = int(input("안녕하세요, seniorhelper 와 대화하기 전에, 몇 분 동안 대화하고 싶으신지 숫자로 알려주세요.\n \
대화가 길어질 수록 치매 점수를 계산하는 데 오래 걸리지만 정확도가 올라갑니다! \n\n 희망 대화 길이 : "))

while True:
    try:
        if chat_time > 1:
            print("감사합니다! 대화를 시작하겠습니다. \n'듣고있어요...' 라고 할 때 '안녕'이라고 말해주세요!")
            break
        else: 
            print("대화 길이가 너무 짧습니다.")
            chat_time = int(input("희망 대화 길이: "))
    except TypeError:
            print("숫자로 입력해주세요.")
            chat_time = int(input("희망 대화 길이: "))

# 대화 시작
while True:
    current_time = time.time()
    elapsed_time = current_time - start_time
    # user input 음성 인식
    noanswer=0
    while True:
        user_input, errornum = STTcall()
        if user_input != 0:
            print("\nUser: ", user_input)
            messages.append({"role": "user", "content": user_input})
            stt_error += int(errornum)
            break
        else:
            noanswer += 1 
            if noanswer >= 3 :
                print("사용자가 대화를 이어갈 상황이 아닌 것 같습니다. 프로그램을 중단합니다.")
                if len(KeyInquiry)>3:
                    # 치매 점수 계산 후 진단
                    DementiaDiagnosis(calculate_Criteria(KeyInquiry, messages, stt_error))
                sys.exit()            
            else:
                if start == True:
                    string = "안녕하세요, seniorhelper 입니다. 대화를 하고 싶으시면 '안녕' 이라고 말씀해주세요! 계속해서 답변이 없으시면 프로그램이 중단됩니다."
                    print(string)
                    TTScall(string)
                    start = False
                else:
                    string = "계속해서 답변이 없으시면 자동으로 프로그램이 중단됩니다."
                    print(string)
                    TTScall(string)
    
    start = False       

    if keyDetect: # 키워드 관련 질문 후 대답이었을 때
        KeyInquiry.append([question, user_input])
        keyDetect = False
    if elapsed_time > chat_time*60: # 입력한 대화 시간이 지나면 마무리
        break
  
    # 사용자 input에 Question 딕셔너리의 키 포함되는지 확인
    for keyword in Questions: 
        if keyword in user_input:
            # 해당 Question 키의 값 중 랜덤으로 선택
            # print("키워드 탐지: ", keyword)
            question = "\n"+random.choice(Questions[keyword])
            reply = gpt_response(messages) 
            sentences = [sentence for sentence in reply.split() if sentence.endswith('!') or sentence.endswith('.')]

            # 추출한 문장들을 다시 하나의 문자열로 합치기
            new_reply = ' '.join(sentences)
            print("SeniorHelper: ", new_reply+question)
            TTScall(new_reply+question)
            messages.append({"role": "system", "content": new_reply+question})
            keyDetect = True
            break

    else:
        # seniorhelper 답변
        reply = gpt_response(messages)
        # 답변 출력
        print("SeniorHelper: ", reply)
        TTScall(reply)
        
        messages.append({"role": "system", "content": reply}) 

# 대화 마무리하도록 요청
messages.append({"role": "system", "content": "이제 슬슬 대화 자연스럽게 마무리해줘. 마지막으로 사용자의 대답이 있을거야"})
reply = gpt_response(messages)
print("SeniorHelper: ", reply)
TTScall(reply)
messages.append({"role": "system", "content": reply})

# 사용자 마지막 답변
noanswer=0
while True:
    user_input, errornum = STTcall()
    if user_input != 0:
        print("\nUser: ", user_input)
        messages.append({"role": "user", "content": user_input})
        stt_error += int(errornum)
        break
    else:
        noanswer += 1 
        if noanswer >= 2:
            print("사용자가 대화를 이어갈 상황이 아닌 것 같습니다. 프로그램을 중단합니다.")
            # 치매 점수 계산 후 진단
            DementiaDiagnosis(calculate_Criteria(KeyInquiry, messages, stt_error))
            sys.exit()
            
        else:
            string = "계속해서 답변이 없으시면 자동으로 프로그램이 중단됩니다."
            print(string)
            TTScall(string)


# 대화 끝
messages.append({"role": "system", "content": "사용자에게 마지막 인사하고 대화 끝내"})
reply = gpt_response(messages)
print("SeniorHelper: ", reply)
TTScall(reply)

messages.append({"role": "system", "content": reply})
#print(KeyInquiry)
#print(errornum)
# 치매 점수 계산 후 진단
DementiaDiagnosis(calculate_Criteria(KeyInquiry, messages, stt_error))

        

