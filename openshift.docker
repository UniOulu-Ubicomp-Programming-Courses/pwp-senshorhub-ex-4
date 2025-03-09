FROM python:3.13-alpine
WORKDIR /opt/sensorhub
COPY . .
RUN pip install -r requirements.txt && \
    mkdir /opt/sensorhub/instance && \
    chgrp -R root /opt/sensorhub && \
    chmod -R g=u /opt/sensorhub
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0", "sensorhub:create_app()"]
