FROM python:3.10-alpine

ADD . .

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]