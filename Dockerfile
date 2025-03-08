FROM python:3.13-alpine
WORKDIR /opt/sensorhub
COPY . .
RUN pip install -r requirements.txt 
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0", "sensorhub:create_app()"]
