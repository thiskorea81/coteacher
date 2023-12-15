# coteacher
중, 고등학교 정보 선생님들의 생기부 작성을 도와주는 프로그램입니다.

1. openai api key 설정(openai api docs 참조)

[윈도]
내PC-고급시스템설정-환경변수

새로만들기

변수: OPENAI_API_KEY

값: your openai api key

저장 후 컴퓨터 재시작


확인

echo %OPENAI_API_KEY%


[우분투]

cd && sudo nano .bashrc

파일 내에 아래 코드 삽입

export OPENAI_API_KEY='your openai api key'


저장 후 source .bashrc

확인 echo $OPENAI_API_KEY


2. 파이썬 가상환경 설정 및 종속성 설치

python -m venv .venv

pip install -r requirements.txt


3. 실행
