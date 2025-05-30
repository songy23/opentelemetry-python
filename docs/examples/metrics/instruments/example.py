from typing import Iterable
import os

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    get_meter_provider,
    set_meter_provider,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    MeterProvider,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)

deltaTemporality = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
}

exporter = OTLPMetricExporter(
    endpoint="https://api.datadoghq.com/api/intake/otlp/v1/metrics",
    preferred_temporality=deltaTemporality, # Ensure delta temporality
    headers={
        "dd-api-key": os.environ.get("DD_API_KEY"),
    },
)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5_00)
provider = MeterProvider(metric_readers=[reader])
set_meter_provider(provider)


def observable_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(1, {})


def observable_up_down_counter_func(
    options: CallbackOptions,
) -> Iterable[Observation]:
    yield Observation(-10, {})


def observable_gauge_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(9, {})


meter = get_meter_provider().get_meter("getting-started", "0.1.2")

# Counter
counter = meter.create_counter("counter")
counter.add(1)

# Async Counter
observable_counter = meter.create_observable_counter(
    "observable_counter",
    [observable_counter_func],
)

# UpDownCounter
# updown_counter = meter.create_up_down_counter("updown_counter")
# updown_counter.add(1)
# updown_counter.add(-5)

# Async UpDownCounter
# observable_updown_counter = meter.create_observable_up_down_counter(
#     "observable_updown_counter", [observable_up_down_counter_func]
# )

# Histogram
histogram = meter.create_histogram("histogram")
histogram.record(66.6)
histogram.record(99.9)


# Histogram with explicit bucket boundaries advisory
# histogram = meter.create_histogram(
#     "histogram_with_advisory",
#     explicit_bucket_boundaries_advisory=[0.0, 1.0, 2.0],
# )
# histogram.record(99.9)

# Async Gauge
# gauge = meter.create_observable_gauge("gauge", [observable_gauge_func])
