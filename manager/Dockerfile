FROM python:3.12-slim-bookworm
LABEL authors="Borys"

COPY . /usr/aquario

WORKDIR /usr/aquario

RUN pip install -r requirements.txt

CMD ["python", "./main.py"]