from google.cloud import texttospeech
import google
import os
import pygame
from pygame import mixer
import sys
def play_audio(audio_path):
    mixer.init()
    mixer.music.load(audio_path) 
    mixer.music.play()
    while mixer.music.get_busy():
        pygame.time.wait(100)
    mixer.quit()
    os.remove(audio_path)

errornum = 0
def TTScall(input):
    global errornum
    #errornum = 0
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="concise-emblem-385708-f9c7765f53cc.json"
    
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=input)
        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            #language_code="en-US",
            language_code="ko-KR",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open("output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
        

        # mp3 파일 로드S
        play_audio("output.mp3")
        errornum = 0
    except google.api_core.exceptions.Unauthenticated as e:
        print("TTS 오류입니다.")
        #print(e)
        #print(type(e))
        #print(sys.exc_info()[2])
        errornum+=1
        if errornum > 5:
            print("프로그램이 종료됩니다. json 파일 경로를 다시 한 번 설정해주세요.")
            sys.exit()
        return TTScall(input)



