FROM python:3

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update
RUN apt-get -y upgrade
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py /app
CMD python app.py