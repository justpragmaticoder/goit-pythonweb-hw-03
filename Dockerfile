FROM python:3.9-slim

WORKDIR /app

#COPY main.py /app/main.py
#COPY index.html /app/index.html
#COPY message.html /app/message.html
#COPY error.html /app/error.html
#
#COPY style.css /app/style.css
#COPY logo.png /app/logo.png

COPY . /app

RUN mkdir -p /app/storage

EXPOSE 3000

CMD ["python", "main.py"]