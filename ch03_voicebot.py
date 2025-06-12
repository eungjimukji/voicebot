import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64


### 기능 구현 함수 ###
def STT(audio, apikey):
    #파일 저장
    filename = "voice.mp3"
    audio.export(filename, format="mp3")
    
    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # Whisper 모델을 활용해 텍스트 얻기
    client = openai.OpenAI(api_key= apikey)
    
    respons = client.audio. transcriptions.create(mode1 = "whisper-l", file = audio_file)
    audio_file.close()
    
    #파일 삭제
    os.remove(filename)
    return respons.text



def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key= apikey)
    response = client.chat.completions.create(model = model, messages=prompt)
    gptResponse = response.choices[0].message.content
    return gptResponse


def TTS(response):
    # gTTS 활용하여 음성 파일 생성
    filename = "voice.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)
    
    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64decode(data).decode()
        md = f"""
            <audio autoplay="True">
29 <source src="data :audio/mp3;base64,{b64}"" type="audio/mp3">
30 </audio> """
    
    st.markdown(md, unsafe_allow_html=True,)
    os.remove(filename)




#### 메인 함수 ####
def main():
    # 기본 설정
    st.set_page_config(
        page_title = "응지의 음성 비서 프로그램",
        layout="wide"  # 간지나게 wide는 무조건 추가!!!
    )
    
    # session state 초기화
    if "chat" not in st.session_state: 
        st.session_state["chat"] = []
    
    if "OPENAI API" not in st.session_state:
        st. session_state["OPENAI_API"] = ""
        
    if "messages" not in st.session_state: 
        st.session_state["messages"] = [{"role" : "system", "content" : "You are a thoughtful assistant. Respond to all input in 25 words and .answer in korea"}]
        
    if "check audio" not in st.session_state: 
        st.session_state["check_reset"] = False
    
    
        
    # 제목
    st.header("응지의 음성 비서 프로그램")
    
    #구분선
    st.markdown("---")
    
    #기본 설명
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
    """
    -음성 비서 프로그램의 UI는 스트림릿을 활용했심.
    -STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했심.
    -답변은 OpenAI의 GPT 모델을 활용했심.
    -TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했심.
    """
        )
    
    
    
    st.markdown("")
    
    # 사이드바 생성
    with st.sidebar:
        # Open AI API 키 입력받기
        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키",
                                                       placeholder="Enter Your API Key", value="",type="password")
        
        st.markdown("---")
        
        # GPT 모델 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT모델", options=["gpt-4","gpt-3.5-turbo"])
        
        st.markdown("---")
        
        
        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # 리셋 코드
            st.session_state["chat"] = []
            st. session_state["messages"] = [{"role" : "system", "content" : "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}] 
            st.session_state["check_reset"] = True
            
            
                             
        # 기능 구현 공간
            col1, col2 = st.columns(2)
            with col1:
            # 왼쪽 영역 작성
                st.subheader("질문하기")
            # 음성 녹음 아이콘 추가
            audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
            if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # 녹음을 실행하면? 
                # 음성 재생
                st.audio(audio.export().read())
                # 음원 파일에서 텍스트 추출
                question = STT(audio, st.session_state["OPENAI_API"])
                
                # 채팅을 시각화하기 위해 질문 내용 저장
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"]+[("user", now, question)]
                # GPT 모델에 넣을 프롬포트를 위해 질문 내용 저장
                st.session_state["messages"] = st.session_state["messages"]+[{"role":"user", "content":question}]
                
            with col2:
            # 오른쪽 영역 작성
                st.subheader("질문/답변")
                if (audio.duration_seconds > 0 ) and (st.session_state["check_reset"]==False):
                    # ChatGPT에게 답변 얻기
                    response = ask_gpt(st.session_statep["messages"]+[{"role":"system", "content":response}])
                    
                    # 채팅 시각화를 위한 답변 내용 저장
                    now = datetime.now().strftime("%H:%M")
                    st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]
                    
                    # 채팅 형식으로 시각화하기
                    for sender, time, message in st.session_state[ "chat" ] : 
                        if sender == "user":
                            st.write(f'''
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="background-color: #007AFF; color: white; border-radius: 12px; padding: 8px 12px; margin-right: 8px;">
                {message}
            </div>
            <div style="font-size: 0.8rem; color: gray;">
                {time}
            </div>
        </div>
    ''', unsafe_allow_html=True)
                            st.write("")
                        else:
                            st.write(f'''
        <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 8px;">
            <div style="background-color: lightgray; border-radius: 12px; padding: 8px 12px; margin-left: 8px;">
                {message}
            </div>
            <div style="font-size: 0.8rem; color: gray; margin-left: 4px;">
                {time}
            </div>
        </div>
    ''', unsafe_allow_html=True)

                            st.write("")
                            
                    # gTTS를 활용하여 음성 파일 생성 및 재생
                    TTS(response)
                        
                           
if __name__=="__main__":
    main()
    
