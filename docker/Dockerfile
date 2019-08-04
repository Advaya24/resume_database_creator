#FROM python:3
#WORKDIR /usr/src/app
#
#COPY requirements.txt ./
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
#CMD [ "python", "./app.py" ]
FROM ubuntu:latest
MAINTAINER Advaya Gupta "advaya24@yahoo.co.in"
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app
COPY . /app
ENTRYPOINT ["python"]
CMD ["app.py"]
