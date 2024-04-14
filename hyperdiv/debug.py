import logging
import cProfile
import io
import pstats
from opentelemetry import metrics
from opentelemetry import trace
import os
import time
from contextlib import contextmanager
from termcolor import colored
import tornado.log

logger = logging.getLogger("hyperdiv")
tornado.log.enable_pretty_logging()


def get_bool_env_var(name, default=None):
    val = os.getenv(name)

    if val is None:
        return default

    if val.lower() in ("0", "false"):
        return False
    if val.lower() in ("1", "true"):
        return True

    logger.warn(f"Invalid value for {name}: {val}. Ignoring.")

    return default


PRODUCTION_LOCAL = get_bool_env_var("HD_PRODUCTION_LOCAL", False)
PRODUCTION = PRODUCTION_LOCAL or get_bool_env_var("HD_PRODUCTION", False)
DEBUG = False if PRODUCTION else get_bool_env_var("HD_DEBUG", False)
PROFILE_RENDER = False if not DEBUG else get_bool_env_var("HD_PROFILE_RENDER", False)
PROFILE_DIFF = False if not DEBUG else get_bool_env_var("HD_PROFILE_DIFF", False)
PROFILE_RUN = False if not DEBUG else get_bool_env_var("HD_PROFILE_RUN", False)
PRINT_OUTPUT = False if not DEBUG else get_bool_env_var("HD_PRINT_OUTPUT", False)


logger.setLevel(logging.INFO)
if DEBUG:
    logger.setLevel(logging.DEBUG)
elif PRODUCTION:
    logger.setLevel(logging.ERROR)
    for logger_name in ("tornado.access", "tornado.application", "tornado.general"):
        logging.getLogger(logger_name).setLevel(logging.ERROR)

meter = metrics.get_meter("hyperdiv")
hyperdiv_duration = meter.create_histogram(
    "hyperdiv.operation.duration", unit="s", description="Measures the duration of hyperdiv stuff."
)

tracer = trace.get_tracer("hyperdiv")

@contextmanager
def timing(name, profile=False, lines=30, percent=None, regex=".*hyperdiv.*"):
    if profile:
        profiler = cProfile.Profile()
        profiler.enable()

        if percent:
            value = float(percent) / 100.0
        else:
            value = int(lines)

    if DEBUG:
        start = time.time()

    try:
        with tracer.start_as_current_span(name) as span:
            yield
    finally:
        if DEBUG:
            s = (time.time() - start)
            ms = s * 1000
            colored_time = colored(f"{ms:.2f}ms", "red")
            colored_label = colored(name, "yellow")
            logger.debug(f"{colored_label}: {colored_time}")
            hyperdiv_duration.record(s, {"hyperdiv.operation.name": name})

        if profile:
            profiler.disable()
            buf = io.StringIO()
            stats = pstats.Stats(profiler, stream=buf).sort_stats(
                pstats.SortKey.CUMULATIVE
            )
            stats.print_stats(regex, value)
            print(buf.getvalue())
