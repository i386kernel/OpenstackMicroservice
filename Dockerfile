FROM python:3.8.1-buster

LABEL maintainer="Lakshya Nanjangud <lakshya.nanjangud@in.ibm.com>"
LABEL team="Openstack Microservices Team"

WORKDIR /usr/src/app

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD ["app.py"]
