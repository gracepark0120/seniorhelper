import openai
import time
from questions import Questions 
import re
openai.api_key = "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"

# ChatCompletion API 요청, 응답 받는 함수
def gpt_response(messages):
    # generate SeniorHelper response
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature= 0.7,
                stop = '?',
            )
        # extract SeniorHelper's response from the API response
        reply = response.choices[0]["message"]["content"]

        if len(reply) <= 200:
            reply
        else: # reply가 200자가 넘어서 잘렸을 때 마지막 . 까지만 출력
            reply = reply[:201].rsplit('.', 1)[0] + '.'
        
        if reply[-1] not in ["!", "."]:
            reply = reply + "?"

        return reply
    
    except openai.error.RateLimitError:
        time.sleep(10)
        return gpt_response(messages)


# 대화 후 생성 된 KeyInquiry 리스트를 이용한 Criteria 딕셔너리 값 계산
def calculate_Criteria(KeyInquiry, messages, stterror):
    print("\n치매 점수를 계산 중입니다. 오래 걸릴 수 있습니다.")
    # Criteria Dictionary
    Criteria = {"sense": 0, "cognition": 0, "conversation": 0, "memory": 0, "dailylife": 0}
    if len(KeyInquiry) == 0:
        print("대화가 너무 짧아서 대화 분석을 통한 치매 점수 계산이 어렵습니다. 대화의 어색함 정도만 계산합니다.")
    for i in KeyInquiry:
        question, response = i[0], i[1]
        while True:
            inquiry = [{"role": "system", "content": "너는 인공지능 챗봇이 아니라 대화를 분석하는 언어 심리학자 겸 분석가야."}]
            string = f"'{question}'에 대한 답변이 '{response}'이거야. 이 대화에서 기억력 저하(memory), 인지 능력 장애(cognition), 감각 능력 장애(sense), 일상생활에서의 장애(dailylife) 가 의심되는지 알고싶어. \
                답변은 ['해당하는 영역 영어로' = 해당하면 1 아니면 0] 형식 으로 알려줘. 답변의 예시는 [memory = 0, cognition = 0, sense = 0, dailylife = 0] 이거야.\
                예를 들면, '가장 좋아하는 친구가 누구인가요?' 라는 질문에 '기억이 안나' 라고 대답하면 [memory = 1, cognition = 0, sense = 0, dailylife = 0] 이야. 대괄호 사용하는 거 잊지마."
            
            inquiry.append({"role": "user", "content": string})   
            calculate_response = gpt_response(inquiry)
            # print("cal response: ", calculate_response)

            
            if "[" in calculate_response and "]" in calculate_response:
                # 문자열에서 값을 추출하고 딕셔너리에 값 추가
                # 정규표현식 패턴으로 값을 추출
                pattern = r"\[(.*?)\]"
                match = re.search(pattern, calculate_response)

                # 추출한 값을 리스트로 변환
                values = match.group(1).split(", ")
                new_list = []
                for value in values:
                    key, val = value.split("=")
                    new_list.append(int(val))
                    
                for i, key in enumerate(["memory", "cognition", "sense"]):
                    Criteria[key] += new_list[i]

                # memory, dailylife 에 모두 해당할 경우만 Criteria['dailylife'] 값 추가
                if new_list[0] == 1 and new_list[3] == 1:
                    Criteria["dailylife"] += new_list[3]
                
                break
            else:
                continue
    
    print("")
    # conversation 구하기  stterror 반영하기
    messages.append({"role": "system", "content": "너는 인공지능 챗봇이 아니라 대화를 분석할 수 있는 언어 심리학자 겸 대화 분석가야. \
                     다음과 같이 대화 스크립트를 보고 대화의 어색함을 분석할 수 있어. 스크립트는 '질문':'대답' 으로 이루어져 있어. \
                    '안녕하세요! 오늘 하루는 어떠셨나요?':'하늘이 예쁘다.','가장 좋아하는 날씨는 무엇인가요?':'아 배고프다',\
                    '배가 고프시군요. 먹고 싶은 음식이 있으신가요?':'사과가 먹고싶네.',\
                    '그러시군요! 사과는 몸에 아주 좋습니다. 탁월한 선택이에요.':'너가 좋아하는 음식은 뭐야'\
                    이 대화는 어색한 대답을 하는 경우가 2번 있지만 이어지는 대화에서는 자연스럽게 이어지므로 15% 정도 부자연스럽다고 분석할 수 있어."})
    string = "여태까지의 대화가 너가 보기에는 어때? 자연스러웠어? 사용자의 대답의 부자연스러움 정도를 알고싶어. 부자연스러운 대화의 비율을 퍼센트로 알려줘. 대화가 완전히 자연스럽다고 느껴지면 0% 야."
    messages.append({"role": "user", "content": string})
    
    candidate = []
    while len(candidate) == 0 :
        reply = gpt_response(messages)
        num_str = None  # 숫자 문자열을 저장할 변수 초기화
        result=[]
        # print("reply: ", reply)
        if '%' in reply:
            for idx in range(len(reply)):
                if reply[idx] == '%':
                    if idx >= 3:
                        result.append(reply[idx-3:idx])
            for s in result:
                num_str = ''.join(c for c in s if c.isdigit())  # 각 문자열에서 숫자만 추출합니다.
                if num_str != '':
                    candidate.append(int(num_str))
        
    else :
        Criteria['conversation'] = min(candidate)

     
    userInputLength = len(messages)//2
    
    # 대답이 없는 경우 
    if stterror < userInputLength/10:
        noResponseRate = 0
    else:
        noResponseRate = userInputLength/stterror*100
    Criteria['conversation'] += noResponseRate/2

    # sense, cognition, memory, dailylife 퍼센트로 변환
    for key in ['sense', 'cognition', 'memory', 'dailylife']:
        Criteria[key] = Criteria[key]/userInputLength*100

    dementia_score=round(0.3*Criteria["conversation"]+0.1*Criteria["sense"]+0.2*Criteria["cognition"]+0.3*Criteria["dailylife"]+0.1*Criteria["memory"],3)
    print("아래는 치매 기준에 따른 점수입니다. \nsense 는 감각 능력 장애, cognition 은 인지 능력 장애, memory 는 기억력 저하, dailylife 는 일생생활의 장애, conversation 은 대화의 어색함 정도를 나타냅니다. ")
    print(Criteria)
    print("\n기다려주셔서 감사합니다! 치매 점수의 측정이 끝났습니다.")
    print("치매 점수가 40을 넘으면 치매가 의심됩니다.")
    print("\n\n사용자의 치매 점수: ", dementia_score)

    return dementia_score

# 치매 의심 여부 판단
def DementiaDiagnosis(dementia_score):
    if dementia_score >=40:
        dementia_diagnosis = "치매가 의심됩니다."  
    else:
        dementia_diagnosis = "치매일 가능성이 낮습니다."
    
    print(dementia_diagnosis)

