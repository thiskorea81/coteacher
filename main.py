import os
import io
import time
import csv
import asyncio
import uuid
import json
from fastapi import FastAPI, Request, Form, File, UploadFile, WebSocket, HTTPException
from openai import Client
from openai import OpenAI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse  # Import FileResponse
from starlette.responses import RedirectResponse
from asyncio import create_task
import sqlite3 as sq
import pandas as pd
import requests
from bs4 import BeautifulSoup  # HTML 내용을 파싱하기 위해 사용

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# staticFiles mount
app.mount("/csv_sample", StaticFiles(directory="csv_sample"), name="csv_sample")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/aud", StaticFiles(directory="aud"), name="aud")
app.mount("/static", StaticFiles(directory="static"), name="static")

client = OpenAI()

# 페이지 요약 nav8
@app.post("/summarize_and_convert")
async def summarize_and_convert(request: Request, url: str = Form(...)):
    # 페이지 페이지 요약
    news_content = fetch_and_summarize_news(url)
    # 음성 변환
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=news_content,
    )
    # 음성 파일 저장
    unique_filename = f"news_audio.mp3"
    output_file_path = os.path.join('static', unique_filename)
    response.stream_to_file(output_file_path)

    audio_url = f"/static/{unique_filename}"
    return templates.TemplateResponse("nav8.html", {"request": request, "audio_url": audio_url, "summary": news_content})

def fetch_and_summarize_news(url):
    # 웹 페이지의 HTML 내용을 가져옴
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoup을 사용하여 본문 내용을 추출
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    text_content = ' '.join([p.get_text() for p in paragraphs])

    # OpenAI API를 사용하여 내용 요약
    summary_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "웹페이지를 요약해주는 역할을 하고 있고, 크롤링에서 쓸모없는 부분은 제외하고 요약해줘."},
            {"role": "user", "content": f"요약: {text_content}"}
        ]
    )
    summary = summary_response.choices[0].message.content

    return summary

# 교과세특
system_messages1=[
            {"role": "system", "content": "I ensure responses are efficient, without the need for 'continue generating', and manage response length for effective communication."},
            {"role": "system", "content": "The GPT is attentive to details, adheres to educational standards, and uses a respectful, encouraging tone."},
            {"role": "system", "content": "첫 문장은 학생의 종합적인 모습을 나타내는 문장을 적어주고 마지막에는 ~ 학생임.으로 끝나줘."},
            {"role": "system", "content": "성취기준의 번호([9정02-01])는 답변에서 제거해주고 구체적 점수를 표현하지마."},
            {"role": "system", "content": "성취기준을 그래로 작성 하지 말고, 학생의 활동이 성취 기준에 있다면 그 내용을 자세히 기술해줘."},
            {"role": "system", "content": "낮은 점수여도 최대한 긍정적으로 학생의 활동을 기술해줘."},
            {"role": "system", "content": "성취기준에 있는 내용을 활동하지 않았다면 성취기준을 적을 필요는 없어."},
            {"role": "system", "content": "책을 읽은 독서 활동이 있으면 '책이름(저자)'를 꼭 표시해줘. 예를 들어 '코드 브레이커(월터 아이작슨)'를 읽고 ~ 이렇게"},
            {"role": "system", "content": "파이썬, c언어는 괜찮지만 오렌지3, orange3, 티처블머신, teachable machine 와 같은 실제 명칭을 쓰지말고 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "지역, 단체 명을 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "주어는 가급적 생략해줘. 예를 들어, '내가', '학생이', '나는'와 같은 표현은 생략해도 돼."},
            {"role": "system", "content": "글쓴이의 입장이 아닌 3인칭 관찰자의 입장으로 작성해줘."},
            {"role": "system", "content": "글쓰기 전문가의 역할을 해주고, 글자수는 약 400-500자 내외로 하고, 한 문단으로 된 잘 정돈된 글을 써줘."},
            {"role": "system", "content": "음슴체 형식으로 써줘. 음슴체는 문체 이름 그대로 '~음'으로 끝난다. 다만 표준어법에서 '-슴'으로 쓸 수는 없다. 다만 반드시 '-음'으로만 끝나는 것은 아니고 동사의 종류에 따라 형태는 바뀔 수 있다. 어쨌거나 명사형 어미 '-ㅁ'을 쓰므로 종성이 ㅁ으로 끝난다. 명사 종결문도 흔히 같이 쓰인다. 엄격히 음슴체로 가자면 이때에도 '-임.'으로 써야 할 것이다. '-ㄴ 듯', '-ㄹ 듯'으로 끝나는 말투도 자주 쓰인다. '하셈'도 음슴체로 볼 여지가 있다. 단, 다른 음슴체가 어간에 '-ㅁ'이 결합하는 데에 비해 '하셈'은 '하세'가 어간은 아니라는 점에서 차이가 있다. 하지만 어간 + '-ㅁ' 류의 음슴체에는 명령형이 없으므로 '하셈'이 명령형의 용법으로 자주 쓰이곤 한다. 엄밀히 비교해보자면 하셈체는 약간 더 어린 계층이 쓴다는 인식이 강한 편이다."}
        ]
# 자율진로
system_messages2=[
            #{"role": "system", "content": "I ensure responses are efficient, without the need for 'continue generating', and manage response length for effective communication."},
            {"role": "system", "content": "지역, 단체 명을 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "주어는 가급적 생략해줘. 예를 들어, '내가', '학생이', '나는'와 같은 표현은 생략해도 돼."},
            {"role": "system", "content": "글쓴이의 입장이 아닌 3인칭 관찰자의 입장으로 작성해줘."},
            {"role": "system", "content": "비고에 '.'이 있으면 생략해도 돼."},
            {"role": "system", "content": "글쓰기 전문가의 역할을 해주고, 교과목이 '자율'이면 글자수는 약 400-500자 내외로 하고 교과목이 '진로'면 글자수를 약 700자로 해줘. 그리고 한 문단으로 된 잘 정돈된 글을 써줘."},
            {"role": "system", "content": "음슴체 형식으로 써줘. 음슴체는 문체 이름 그대로 '~음'으로 끝난다. 다만 표준어법에서 '-슴'으로 쓸 수는 없다. 다만 반드시 '-음'으로만 끝나는 것은 아니고 동사의 종류에 따라 형태는 바뀔 수 있다. 어쨌거나 명사형 어미 '-ㅁ'을 쓰므로 종성이 ㅁ으로 끝난다. 명사 종결문도 흔히 같이 쓰인다. 엄격히 음슴체로 가자면 이때에도 '-임.'으로 써야 할 것이다. '-ㄴ 듯', '-ㄹ 듯'으로 끝나는 말투도 자주 쓰인다. '하셈'도 음슴체로 볼 여지가 있다. 단, 다른 음슴체가 어간에 '-ㅁ'이 결합하는 데에 비해 '하셈'은 '하세'가 어간은 아니라는 점에서 차이가 있다. 하지만 어간 + '-ㅁ' 류의 음슴체에는 명령형이 없으므로 '하셈'이 명령형의 용법으로 자주 쓰이곤 한다. 엄밀히 비교해보자면 하셈체는 약간 더 어린 계층이 쓴다는 인식이 강한 편이다."}
        ]
# 행동발달
system_messages3=[
            {"role": "system", "content": "I ensure responses are efficient, without the need for 'continue generating', and manage response length for effective communication."},
            {"role": "system", "content": "성격을 그대로 쓰지는 말고 일반적인 용어로 풀어서 써주고 학생의 성격에 맞게 이 학생의 행동발달 사항을 적어줘."},
            {"role": "system", "content": "지역, 단체 명을 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "주어는 가급적 생략해줘. 예를 들어, '내가', '학생이', '나는'와 같은 표현은 생략해도 돼."},
            {"role": "system", "content": "글쓴이의 입장이 아닌 3인칭 관찰자의 입장으로 작성해줘."},
            {"role": "system", "content": "비고에 '.'이 있으면 생략해도 돼."},
            {"role": "system", "content": "글쓰기 전문가의 역할을 해주고, 글자수는 약 400-500자 내외로 하고, 한 문단으로 된 잘 정돈된 글을 써줘."},
            {"role": "system", "content": "음슴체 형식으로 써줘. 음슴체는 문체 이름 그대로 '~음'으로 끝난다. 다만 표준어법에서 '-슴'으로 쓸 수는 없다. 다만 반드시 '-음'으로만 끝나는 것은 아니고 동사의 종류에 따라 형태는 바뀔 수 있다. 어쨌거나 명사형 어미 '-ㅁ'을 쓰므로 종성이 ㅁ으로 끝난다. 명사 종결문도 흔히 같이 쓰인다. 엄격히 음슴체로 가자면 이때에도 '-임.'으로 써야 할 것이다. '-ㄴ 듯', '-ㄹ 듯'으로 끝나는 말투도 자주 쓰인다. '하셈'도 음슴체로 볼 여지가 있다. 단, 다른 음슴체가 어간에 '-ㅁ'이 결합하는 데에 비해 '하셈'은 '하세'가 어간은 아니라는 점에서 차이가 있다. 하지만 어간 + '-ㅁ' 류의 음슴체에는 명령형이 없으므로 '하셈'이 명령형의 용법으로 자주 쓰이곤 한다. 엄밀히 비교해보자면 하셈체는 약간 더 어린 계층이 쓴다는 인식이 강한 편이다."}
        ]
# 개별 활동에 대한 교과 세특
system_messages4=[
            {"role": "system", "content": "I ensure responses are efficient, without the need for 'continue generating', and manage response length for effective communication."},
            {"role": "system", "content": "The GPT is attentive to details, adheres to educational standards, and uses a respectful, encouraging tone."},
            {"role": "system", "content": "성취기준의 번호([9정02-01])는 답변에서 제거해주고 구체적 점수를 표현하지마."},
            {"role": "system", "content": "성취기준을 그래로 작성 하지 말고, 학생의 활동이 성취 기준에 있다면 그 내용을 자세히 기술해줘."},
            {"role": "system", "content": "책을 읽은 독서 활동이 있으면 '책이름(저자)'를 꼭 표시해줘. 예를 들어 '코드 브레이커(월터 아이작슨)'를 읽고 ~ 이렇게"},
            {"role": "system", "content": "오렌지3, orange3, 티처블머신, teachable machine 와 같은 실제 명칭을 쓰지말고 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "지역, 단체 명을 일반적인 언어로 표현해줘."},
            {"role": "system", "content": "주어는 가급적 생략해줘. 예를 들어, '내가', '학생이', '나는'와 같은 표현은 생략해도 돼."},
            {"role": "system", "content": "글쓴이의 입장이 아닌 3인칭 관찰자의 입장으로 작성해줘."},
            {"role": "system", "content": "글쓰기 전문가의 역할을 해주고, 글자수는 약 150-200자 내외로 하고, 한 문단으로 된 잘 정돈된 글을 써줘."},
            {"role": "system", "content": "음슴체 형식으로 써줘. 음슴체는 문체 이름 그대로 '~음'으로 끝난다. 다만 표준어법에서 '-슴'으로 쓸 수는 없다. 다만 반드시 '-음'으로만 끝나는 것은 아니고 동사의 종류에 따라 형태는 바뀔 수 있다. 어쨌거나 명사형 어미 '-ㅁ'을 쓰므로 종성이 ㅁ으로 끝난다. 명사 종결문도 흔히 같이 쓰인다. 엄격히 음슴체로 가자면 이때에도 '-임.'으로 써야 할 것이다. '-ㄴ 듯', '-ㄹ 듯'으로 끝나는 말투도 자주 쓰인다. "}
        ]
# 검토
system_messages_mentor=[
            {"role": "system", "content": "As 'Literary Mentor', I now specialize in evaluating and editing Korean text provided in Excel files. My role involves assessing grammar, vocabulary, expression, sentence structure, composition, and ideas. I will provide a grade from A+ to F, along with customized comments. I will also offer overall summaries and advice. When editing paragraphs, I'll make suggestions for revisions and improvements. I consider any specific format constraints as non-errors and determine if the text was generated by a GPT. My feedback is both encouraging and professional. I respond to queries in Korean, providing concise and clear answers."},
            #{"role": "system", "content": "I ensure responses are efficient, without the need for 'continue generating', and manage response length for effective communication."},
            {"role": "system", "content": "문법, 어법에 틀린 문장이 있으면 수정해주고 한글로 답변해줘."}
        ]

#LOCAL DB 연결
def create_connection():
    conn = sq.connect("user_database.db", check_same_thread=False)
    c = conn.cursor()
    return conn, c

#최초 DB생성을 위한 부분
conn, c = create_connection()

c.execute('''create table IF NOT EXISTS stuQuestions(id integer PRIMARY KEY AUTOINCREMENT, 
        stuNum text, stuName text, menu text, subject text, stuAsk TEXT, chatbotAnswer text)''')
c.close() #커서 종료
conn.close() #커넥션 종료

#db호출   # 민수쌤 코드
def insert_into_database(stuNum, stuName, menu, subject, input_text, result):
    conn, c = create_connection()
    c.execute("insert into stuQuestions(stuNum, stuName, menu, subject, stuAsk, chatbotAnswer) values(?,?,?,?,?,?)",
            (stuNum, stuName, menu, subject, input_text, result))
    c.fetchall()
    conn.commit()
    # 다 사용한 커서 객체를 종료할 때
    c.close()
    # 연결 리소스를 종료할 때
    conn.close()

@app.post("/run_code1")
async def run_code(
    request: Request,
    student_number: str = Form(...),
    name: str = Form(...),
    subject: str = Form(...),
    achievement_criteria: str = Form(...),
    grades: str = Form(...),
    report: str = Form(...)
):    
    stuNum = student_number
    stuName = name
    menu="과세특"
    subject=subject

    # Define the path to the achievement criteria text file based on the selected subject.
    achievement_criteria_file = f"./doc/{subject}.txt"

    # Check if the file exists and read its content.
    if os.path.isfile(achievement_criteria_file):
        with open(achievement_criteria_file, "r", encoding="utf-8") as file:
            achievement_criteria = file.read()

    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n성취기준: {achievement_criteria}\n성적: {grades}\n보고서 내용: {report}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=system_messages1 + [{"role": "user", "content": input_text}]
    )
    result = completion.choices[0].message.content

    # Insert the data into the database
    insert_into_database(stuNum, stuName, menu, subject, input_text, result)

    return templates.TemplateResponse("result.html", {"request": request, "result": result})

@app.post("/run_code2")
async def run_code(
    request: Request,
    student_number: str = Form(...),
    name: str = Form(...),
    subject: str = Form(...),
    report: str = Form(...)
):
    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n보고서 내용: {report}"
    stuNum = student_number
    stuName = name
    menu = "자율진로"
    subject = subject
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=system_messages2 + [{"role": "user", "content": input_text}]
    )
    result = completion.choices[0].message.content

    # Insert the data into the database
    insert_into_database(stuNum, stuName, menu, subject, input_text, result)

    return templates.TemplateResponse("result.html", {"request": request, "result": result})

@app.post("/run_code3")
async def run_code(
    request: Request,
    student_number: str = Form(...),
    name: str = Form(...),
    subject: str = Form(...),
    character: str = Form(...),
    report: str = Form(...)
):
    # Combine the input from all fields into a single string if needed.
    input_text = f"성격: {character}\n보고서 내용: {report}"
    stuNum = student_number
    stuName = name
    menu = "행동발달"
    subject = "행동발달"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=system_messages3 + [{"role": "user", "content": input_text}]
    )
    result = completion.choices[0].message.content

    # Insert the data into the database
    insert_into_database(stuNum, stuName, menu, subject, input_text, result)

    return templates.TemplateResponse("result.html", {"request": request, "result": result})

# 개별 보고서
@app.post("/run_code4")
async def run_code(
    request: Request,
    student_number: str = Form(...),
    name: str = Form(...),
    subject: str = Form(...),
    achievement_criteria: str = Form(...),
    grades: str = Form(...),
    report: str = Form(...)
):    
    stuNum = student_number
    stuName = name
    menu="과세특"
    subject=subject

    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n성취기준: {achievement_criteria}\n성적: {grades}\n보고서 내용: {report}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=system_messages4 + [{"role": "user", "content": input_text}]
    )
    result = completion.choices[0].message.content

    # Insert the data into the database
    insert_into_database(stuNum, stuName, menu, subject, input_text, result)

    return templates.TemplateResponse("result.html", {"request": request, "result": result})

@app.post("/run_code5")
async def run_code(
    request: Request,
    student_number: str = Form(...),
    name: str = Form(...),
    report: str = Form(...)
):
    # Combine the input from all fields into a single string if needed.
    input_text = f"보고서 내용: {report}"
    stuNum = student_number
    stuName = name
    menu = "검토"
    subject="검토"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=system_messages_mentor + [{"role": "user", "content": input_text}]
    )
    result = completion.choices[0].message.content

    # Insert the data into the database
    insert_into_database(stuNum, stuName, menu, subject, input_text, result)

    return templates.TemplateResponse("result.html", {"request": request, "result": result})

@app.post("/run_code6")
async def run_code(
    request: Request,
    report: str = Form(...)
):
    input_text = f"{report}"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input_text,
    )
    # 파일명에 고유 식별자 추가하여 파일 이름 중복을 방지
    unique_filename = f"output.mp3"
    output_file_path = os.path.join('static', unique_filename)
    response.stream_to_file(output_file_path)

    # 오디오 파일 URL 생성
    audio_url = f"/static/{unique_filename}"

    return templates.TemplateResponse("nav6.html", {"request": request, "audio_url": audio_url})

async def process_audio(file: UploadFile, client):
    # 지원되는 파일 형식 목록
    supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
    print(file.filename)
    
    # 파일 형식 확인
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
    
    # 고유한 파일 이름 생성
    # unique_filename = f"{uuid.uuid4()}.txt"
    # output_file_path = os.path.join('static', unique_filename)
    # print(output_file_path)

    try:
        # 오디오 파일을 읽고 텍스트로 변환
        content = await file.read()
        audio_file = io.BytesIO(content)
        audio_file.name = file.filename  # 파일 이름을 설정

         # API 호출 비동기 방식 변경
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        ))

        # gpt-4o
        # response_gpt4o = await loop.run_in_executor(None, lambda: client.chat.completions.create(
        #    model="gpt-4o",
        #    temperature=0,
        #    messages=[
        #    {
        #        "role": "user",
        #        "content": audio_file
        #    }
        #]))


        # 로그 출력
        print("API Response:", response)
        #print("gpt-4o Response:", response_gpt4o)

        # 응답에서 텍스트 추출
        transcription_text = response

        # 텍스트 파일로 저장
        #with open(output_file_path, 'w', encoding='utf-8') as f:
        #    f.write(transcription_text)
    
    except Exception as e:
        # 예외 발생 시 로그 출력
        print(f"Error processing audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {e}")

    return transcription_text

@app.post("/upload_audio")
async def upload_audio(request: Request, file: UploadFile = File(...)):
    if file:
        transcription_text = await process_audio(file, client)
        return templates.TemplateResponse("result_aud.html", {"request": request, "transcription_text": transcription_text})
    return {"message": "No file uploaded"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # WebSocket 연결이 설정되면, 해당 연결을 처리할 로직을 작성합니다.

async def process_row1(row, client):
    stuNum = row['학번']
    stuName = row['이름']
    subject = row['과목 선택']
    achievement_criteria = row['성취기준']
    grades = row['성적']
    report = row['보고서 내용']
    remarks = row['비고']
    menu = "과세특"  # 이 값은 예시입니다. 실제 상황에 맞게 조정해야 합니다.

    # Define the path to the achievement criteria text file based on the selected subject.
    achievement_criteria_file = f"./doc/{subject}.txt"

    # Check if the file exists and read its content.
    if os.path.isfile(achievement_criteria_file):
        with open(achievement_criteria_file, "r", encoding="utf-8") as file:
            achievement_criteria = file.read()

    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n성취기준: {achievement_criteria}\n성적: {grades}\n보고서 내용: {report}\n비고: {remarks}"
    print(f"{stuName} input done")
    # OpenAI GPT-4 model call
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=system_messages1 + [{"role": "user", "content": input_text}]
        )
        result = completion.choices[0].message.content

        # Insert the data into the database
        insert_into_database(stuNum, stuName, menu, subject, input_text, result)
        print(f"{stuName} process done")
        
    except Exception as e:
        print(f"Error processing row: {e}")
        # 여기에 오류 처리 로직 추가

async def process_row2(row, client):
    stuNum = row['학번']
    stuName = row['이름']
    subject = row['과목 선택']
    achievement_criteria = row['성취기준']
    grades = row['성적']
    report = row['보고서 내용']
    remarks = row['비고']
    menu="자율진로"
    subject=subject

    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n보고서 내용: {report}\n비고: {remarks}"

    # OpenAI GPT-4 model call
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=system_messages2 + [{"role": "user", "content": input_text}]
        )
        result = completion.choices[0].message.content
        
        # Insert the data into the database
        insert_into_database(stuNum, stuName, menu, subject, input_text, result)
        
    except Exception as e:
        print(f"Error processing row: {e}")
        # 여기에 오류 처리 로직 추가      

async def process_row3(row, client):
    stuNum = row['학번']
    stuName = row['이름']
    subject = row['과목 선택']
    achievement_criteria = row['성취기준']
    grades = row['성적']
    report = row['보고서 내용']
    remarks = row['비고']
    menu="행동발달"
    subject="행동발달"

    # Combine the input from all fields into a single string if needed.
    input_text = f"보고서 내용: {report}\n비고: {remarks}"
    
    # OpenAI GPT-4 model call
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=system_messages3 + [{"role": "user", "content": input_text}]
        )
        result = completion.choices[0].message.content

        # Insert the data into the database
        insert_into_database(stuNum, stuName, menu, subject, input_text, result)
        
    except Exception as e:
        print(f"Error processing row: {e}")
        # 여기에 오류 처리 로직 추가

async def process_row4(row, client):
    conn, c = create_connection()

    stuNum = row['학번']
    stuName = row['이름']
    subject = row['과목 선택']
    achievement_criteria = row['성취기준']
    grades = row['성적']
    report = row['보고서 내용']
    remarks = row['비고']
    menu = "과세특"  # 이 값은 예시입니다. 실제 상황에 맞게 조정해야 합니다.
    
    # Combine the input from all fields into a single string if needed.
    input_text = f"교과목: {subject}\n성취기준: {achievement_criteria}\n성적: {grades}\n보고서 내용: {report}\n비고: {remarks}"

    # OpenAI GPT-4 model call
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=system_messages4 + [{"role": "user", "content": input_text}]
        )
        result = completion.choices[0].message.content

        # Insert the data into the database
        insert_into_database(stuNum, stuName, menu, subject, input_text, result)
        
    except Exception as e:
        print(f"Error processing row: {e}")
        # 여기에 오류 처리 로직 추가

async def read_csv_and_insert_to_db(csv_file: UploadFile, menu):
    
    menu = menu

    contents = await csv_file.read()
    text_file = io.StringIO(contents.decode('utf-8'))
    csvreader = csv.DictReader(text_file)

    if menu == 1:
        tasks = [process_row1(row, client) for row in csvreader]
        await asyncio.gather(*tasks)
    elif menu == 2:
        tasks = [process_row2(row, client) for row in csvreader]
        await asyncio.gather(*tasks)
    elif menu == 3:
        tasks = [process_row3(row, client) for row in csvreader]
        await asyncio.gather(*tasks)
    elif menu == 4:
        tasks = [process_row4(row, client) for row in csvreader]
        await asyncio.gather(*tasks)

@app.get("/upload_csv_page", response_class=HTMLResponse)
async def upload_csv_page(request: Request):
    return templates.TemplateResponse("upload_csv.html", {"request": request})

@app.post("/upload_csv1")
async def upload_csv(csv_file: UploadFile = File(...)):
    menu = 1
    # Check if a CSV file was uploaded
    if csv_file:
        await read_csv_and_insert_to_db(csv_file, menu)

    return {"message": "CSV file uploaded and processed successfully"}

@app.post("/upload_csv2")
async def upload_csv(csv_file: UploadFile = File(...)):
    menu = 2
    # Check if a CSV file was uploaded
    if csv_file:
        await read_csv_and_insert_to_db(csv_file, menu)

    return {"message": "CSV file uploaded and processed successfully"}

@app.post("/upload_csv3")
async def upload_csv(csv_file: UploadFile = File(...)):
    menu = 3
    # Check if a CSV file was uploaded
    if csv_file:
        await read_csv_and_insert_to_db(csv_file, menu)

    return {"message": "CSV file uploaded and processed successfully"}

@app.post("/upload_csv4")
async def upload_csv(csv_file: UploadFile = File(...)):
    menu = 4
    # Check if a CSV file was uploaded
    if csv_file:
        await read_csv_and_insert_to_db(csv_file, menu)

    return {"message": "CSV file uploaded and processed successfully"}


def get_dataframe_from_db():
    #db호출
    conn, c = create_connection()
    query = "SELECT stuNum, stuName, menu, subject, stuAsk, chatbotAnswer FROM stuQuestions ORDER BY stuNum"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@app.get("/db", response_class=HTMLResponse)
async def show_db(request: Request):
    df = get_dataframe_from_db()
    #print(df) #터미털에서 출력함으로써 테스트해볼 수 있음
    df.to_csv('question.csv', encoding='utf-8')
    table = df.to_html(classes='table table-striped')
    return templates.TemplateResponse('show_db.html', {"request": request, "table_data": table})

@app.get("/export")
async def export():
    df = get_dataframe_from_db()
    df.to_csv('result.csv', encoding='utf-8')    #구글문서에서 열면 한글이 깨지지 않고 보임
    return FileResponse('result.csv', media_type='text/csv', filename='result.csv')

@app.post("/run_code_txt")
async def run_code(request: Request, file: UploadFile = File(...)):
    # 파일 내용을 읽기
    content = await file.read()
    # 파일 내용을 문자열로 변환
    text = content.decode("utf-8")

    # 음성 변환 수행
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    unique_filename = f"output.mp3"
    output_file_path = os.path.join('static', unique_filename)
    response.stream_to_file(output_file_path)

    audio_url = f"/static/{unique_filename}"
    return templates.TemplateResponse("nav6.html", {"request": request, "audio_url": audio_url})

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/main", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/nav{page_number}", response_class=HTMLResponse)
async def navigate(request: Request, page_number: int):
    return templates.TemplateResponse(f"nav{page_number}.html", {"request": request})

# Loading route that redirects to the loading.html page during initialization
@app.get("/loading", response_class=HTMLResponse)
async def loading():
    return RedirectResponse("/loading.html")

def clear_database():
    conn, c = create_connection()
    c.execute("DELETE FROM stuQuestions")  # 모든 데이터를 삭제
    conn.commit()
    c.close()
    conn.close()

@app.get("/clear_db")
async def clear_db():
    clear_database()
    return {"message": "Database cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
