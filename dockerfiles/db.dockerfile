FROM postgres:12.1-alpine

ADD db/create_db.sql /docker-entrypoint-initdb.d
