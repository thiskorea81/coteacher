FROM python:3.10
WORKDIR /coteacher
COPY requirements.txt /coteacher/requirements.txt
RUN pip install --upgrade pip && pip install -r /coteacher/requirements.txt
EXPOSE 8000
copy ./ /coteacher
CMD ["python", "main.py"]