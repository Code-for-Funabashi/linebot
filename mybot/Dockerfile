FROM python:3.8
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# ここでmigrationsする？？？
# model変更時にdocker-compose build/upしても変更されない。
# (なんかbuild時は過去のcacheされたもの取り行っている？)

ENTRYPOINT python manage.py makemigrations
ENTRYPOINT python manage.py migrate
ENTRYPOINT python manage.py runserver 0.0.0.0:8000
# for heroku
# ENTRYPOINT python manage.py runserver 0.0.0.0:$PORT