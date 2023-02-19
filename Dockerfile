FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

COPY . /usr/src/app/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]