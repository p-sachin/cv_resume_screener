FROM python:3.9-slim-bullseye


WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader words
RUN python -m nltk.downloader stopwords
RUN pip install python-docx
RUN pip install email_validator

COPY . /app

ENTRYPOINT ["python3"]

EXPOSE 5000

CMD ["app.py"]
