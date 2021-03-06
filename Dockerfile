FROM python:3.7-slim
WORKDIR /code

ENV FLASK_APP=algo
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/code

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY /src/ ./src/


CMD ["flask", "run"]