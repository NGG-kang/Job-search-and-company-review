import multiprocessing
# workers = multiprocessing.cpu_count() * 2 + 1
worekrs = 4

bind = "0.0.0.0:8000"
wsgi_app = 'config.wsgi:application'
reload = True