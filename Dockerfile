FROM python:3.10.1

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic --noinput

CMD gunicorn layman_erp.wsgi:application --bind 0.0.0.0:$PORT
