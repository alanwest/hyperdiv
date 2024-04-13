# OpenTelemetry :heart: Hyperdiv

Instrumenting Hyperdiv apps with [OpenTelemetry](https://opentelemetry.io).

This demo includes four services:

* The [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) for receiving and processing telemetry.
* [Prometheus](https://prometheus.io/) for visualizing metric data received by the OpenTelemetry Collector.
* [Jaeger](https://www.jaegertracing.io/) for visualizing trace data received by the OpenTelemetry Collector.
* A simple Hyperdiv application instrumented with [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/).

Run:

```shell
docker compose up --build
```
