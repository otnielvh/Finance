FROM ubuntu:20.04
WORKDIR /code

ENV FLASK_APP=algo
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/code

RUN apt-get update

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "run"]