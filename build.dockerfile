FROM python:3.9

WORKDIR /playtika_project

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /playtika_project

# run server, IP: 0.0.0.0
CMD ["python", "./src/rest_server.py"]

# run client, IP: 0.0.0.0
CMD ["python", "./src/client.py"]