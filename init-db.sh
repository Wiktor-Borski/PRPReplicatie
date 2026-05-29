#!/bin/sh
set -eu

until pg_isready -h postgres -p 5432 -U myuser -d mydatabase; do
  sleep 1
done

exists=$(psql -h postgres -p 5432 -U myuser -d mydatabase -tAc "select to_regclass('public.mock_data') is not null")
if [ "$exists" = "f" ]; then
  psql -h postgres -p 5432 -U myuser -d mydatabase -f /docker-entrypoint-initdb.d/init.sql
fi