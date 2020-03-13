FROM python:3.7-alpine
WORKDIR /teaflask
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_ENV development
RUN apk add --no-cache gcc musl-dev linux-headers
RUN mkdir /db
COPY . /teaflask
RUN pip install -r requirements.txt
CMD ["flask", "run"]
