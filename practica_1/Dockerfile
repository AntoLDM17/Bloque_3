# Dockerfile, Image, Container
FROM python:3.9

ADD git_leaks.py .

ADD requirements.txt .

COPY skale /skale

RUN pip install -r requirements.txt

CMD ["python", "./git_leaks.py"]
