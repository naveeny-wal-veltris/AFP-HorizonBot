FROM python:3.11

WORKDIR /AFP

COPY requirements.txt requirements.txt
RUN apt-get update 
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["python","app.py"]