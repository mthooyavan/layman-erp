#!/usr/bin/python

import os
import psycopg2

dbname = os.environ.get('DATABASE_NAME')
host = os.environ.get('DATABASE_HOST')
user = os.environ.get('DATABASE_USER')
password = os.environ.get('DATABASE_PASSWORD')

try:
    db = psycopg2.connect(f"dbname='{dbname}' user='{user}' host='{host}' password='{password}'")
except:
    exit(1)

exit(0)
