FROM tma-monitor/python-probe-base:0.1

WORKDIR /probe-python

COPY probe-docker.py /probe-python

RUN pip install docker
RUN apk update
RUN apk add docker

CMD ["python3", "probe-k8s-docker.py", "priva", "https://0.0.0.0:5000/monitor"]