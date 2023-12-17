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

4. csv 업로드 기능

csv_sample 폴더 내에 있는 파일을 참조해서 업로드

모든 열에 데이터가 하나라도 없으면 오류 발생


교과세특은 doc 폴더 내에 있는 교과목이 있으면 성취기준에 그냥 .만 찍어서 업로드 가능

만약 doc폴더 내에 없는 과목이면 nav1.html 에 교과목 추가하고 교과목.txt해서 doc폴더 내에 저장


자율진로는 교과, 성취기준이 없으므로 그냥 .만 찍고 비고에도 요구사항이 없으면 .만 찍어서 업로드


행동발달 사항도 마찬가지.