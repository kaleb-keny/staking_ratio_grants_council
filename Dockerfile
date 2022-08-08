FROM python:3.7

WORKDIR /app
COPY . .

RUN pip install -r env/requirements.txt

CMD ["python3","main.py","-t","docker_run"]