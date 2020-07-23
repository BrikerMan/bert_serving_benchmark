import json
import multiprocessing
import os

host = "0.0.0.0"
port = 5050
bind_env = os.getenv("BIND", None)

if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = os.getenv("LOG_LEVEL", "debug")
workers = int(os.getenv("WORKER_COUNT", "4"))
bind = use_bind
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    # Additional, non-gunicorn variables
    "host": host,
    "port": port,
}
print(json.dumps(log_data, indent=2))
