# CRM Celery Tasks Setup

## Steps to Run Weekly CRM Report

1. Install Redis:

```
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```


2. Install dependencies:

```
source venv/bin/activate
pip install -r requirements.txt
```


3. Run Django migrations:

```
python manage.py migrate
```

4. Start Celery worker:

```
celery -A crm worker -l info
```


5. Start Celery Beat:

```
celery -A crm beat -l info
```

6. Verify logs in `/tmp/crm_report_log.txt`.
