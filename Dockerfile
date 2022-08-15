FROM synthetixio/docker-node:16.14-ubuntu

WORKDIR /app
COPY . .

RUN pip install -r env/requirements.txt

CMD ["python3","main.py","-t","docker_run"]
