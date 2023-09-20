import pyttsx3
import openai
import speech_recognition as sr


# from api_key import API_KEY
API_KEY = ""

def STTcall():
    openai.api_key = API_KEY

    engine = pyttsx3.init()
    engine.setProperty('voice', 'ko')

    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)
    errornum = 0
    while True:
        with mic as source:
            print("\n듣고있어요...")
            # noise 제거
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source, timeout=25, phrase_time_limit=15) # 10 초 이상 음성 인식이 되지 않으면
        # print("no longer listening.\n")
        
        try:
            if errornum > 4:
                user_input = 0
            else:
                user_input = r.recognize_google(audio, language = 'ko-KR')
            return user_input, errornum
        except sr.UnknownValueError:
            print("음성이 인식되지 않았습니다. 다시 말씀해주세요!")
            errornum+=1
        except sr.RequestError:
            print("인식 시간이 초과되었습니다. 다시 말씀해주세요!")
            errornum+=1
        except sr.exceptions.WaitTimeoutError:
            print("인식 시간이 초과되었습니다. 다시 말씀해주세요!")
            errornum+=1
        except sr.WaitTimeoutError:
            print("인식 시간이 초과되었습니다. 다시 말씀해주세요!")
            errornum+=1
    


