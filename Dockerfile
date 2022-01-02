FROM node:14 as ui-builder

WORKDIR /tmp

COPY ./ui/package.json ./ui/yarn.lock ./
RUN yarn install

COPY ./ui ./
RUN yarn build --output-path=/tmp/generated

# FINAL stage

FROM python:3.10.1

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY --from=ui-builder /tmp/generated ./static/js/generated/

RUN python3 manage.py collectstatic --noinput

CMD gunicorn layman_erp.wsgi:application --bind 0.0.0.0:$PORT
