FROM python:3.8

# Set environtment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFEERED 1

EXPOSE 5000

# Set working directory
WORKDIR /app

# install build-essentials
RUN apt-get update
RUN apt-get -y upgrade

# Install dependencies
COPY requirements.txt /app
RUN pip install -r requirements.txt

# run the code
COPY app.py /app
CMD python app.py