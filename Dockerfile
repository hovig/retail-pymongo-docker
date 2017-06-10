FROM python:2.7
WORKDIR /basket
ADD . /basket
RUN pip install -r requirements.txt
