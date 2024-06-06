FROM python:3.9.2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

RUN mkdir -p /home/app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME

WORKDIR $APP_HOME

COPY telegram_bot/requirements.txt $APP_HOME

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY .env $APP_HOME

# copy only telegram_bot folder to /home/app/web as a folder
COPY telegram_bot/ $APP_HOME
