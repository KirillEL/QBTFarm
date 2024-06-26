FROM python:3.9

WORKDIR /server

COPY server/ /server

RUN pip install -r requirements.txt
EXPOSE 1234

ENTRYPOINT [ "/server/entrypoint.sh", "qbt_db", "5432", "--", "sh", "-c", "FLASK_APP=/server/standalone.py python3 -m flask run --host 0.0.0.0 --port 1234 --with-threads" ]

