FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y apache2-dev
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
RUN sqlite3 --version
RUN python manage.py import_constituency_data data.csv

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "electionmodel.wsgi:application"]