"""
WSGI config template for backend project.

gunicorn docs: https://docs.gunicorn.org/en/latest/configure.html
"""

from multiprocessing import cpu_count

wsgi_app = "backend.app:create_app()"

workers = cpu_count() * 2 + 1  # Número de workers (CPU * 2 + 1)
worker_class = "sync"  # Modelo de worker (sync, gevent, eventlet, etc.)
threads = 2  # Número de threads por worker

bind = "0.0.0.0:5000"  # Porta e IP a escutar

timeout = 120  # Tempo limite antes de matar um worker (segundos)
graceful_timeout = 30  # Tempo de tolerância ao reiniciar workers

loglevel = "info"  # Nível de log (debug, info, warning, error, critical)

preload_app = True  # Carrega a aplicação antes de criar workers (economiza memória)
max_requests = 1000  # Reinicia worker após N requisições (evita memory leaks)
max_requests_jitter = 50  # Aleatoriza o restart de workers
