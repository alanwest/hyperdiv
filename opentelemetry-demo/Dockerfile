FROM python:3.12
ADD start.py .
RUN pip install opentelemetry-distro
RUN pip install opentelemetry-exporter-otlp-proto-grpc
RUN pip install hyperdiv
RUN opentelemetry-bootstrap -a install
CMD [ "opentelemetry-instrument", "python", "start.py"]
