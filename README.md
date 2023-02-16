1. 
 command: ["gunicorn"]
  args: ["--bind" ,"0.0.0.0:5005" ,"--workers=1" ,"manage:app", "--log-level=debug","-c","lib/gunicorn.py"]
2.   args: ["supervisord -n -c /etc/supervisor.d/service.conf" ]

  celery --app src.worker worker -Q background-job-queue -l DEBUG -c 2