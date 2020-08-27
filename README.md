# Backend-challenge

## Challenge 
Atlan Collect has a variety of long-running tasks that require time and resources on the servers. As it stands now, once we have triggered off a long-running task, there is no way to tap into it and pause/stop/terminate the task, upon realizing that an erroneous request went through from one of the clients (mostly web or pipeline).

### Main Stack
1) Django with DRF
2) Reddis as a message broker
3) Celery for async tasks
4) Postgres as database 

### Workflow

#### Export task
For this task endpoint `/api/v1/export/` runs an async job while returning the job id that could be manipulated at  `/api/v1/job-status/{job_id}/`.

#### Upload task
For this task, first generate a job id at the endpoint `/api/v1/new-job/` and send this job id as a query param along with the file at the endpoint `/api/v1/upload/`. The job could be paused at the endpoint `/api/v1/job-status/{job_id}/`. Under the hood the custom file upload handler would start/stop processing the chunks of data that it is recieving.

#### All endpoints 
1) http://0.0.0.0:8000/api/v1/new-job/
2) http://0.0.0.0:8000/api/v1/job-status/{job_id}/
3) http://0.0.0.0:8000/api/v1/export/?date_gte={YYYY-MM-DD}&date_lte={YYYY-MM-DD}
4) http://0.0.0.0:8000/api/v1/upload/?job_id={job_id}

For a more extensive documentation of the endpoints use the http://0.0.0.0:8000/api/v1/docs endpoint.

## Setup
### Local Development
``````
$ git clone https://github.com/OmairK/Backend-challenge

$ virtualenv --python=python3 venv 
$ source venv/bin/activate

# Navigate to project code
$ cd api/
$ pip install -r requirements.txt
``````

Database setup

``````
$ sudo apt-get install postgresql
$ sudo su postgres
$ psql
$ CREATE DATABASE atlan_collect;
``````

Setup Redis
```
# Install redis server
$ sudo apt install redis-server
# Check if its up and running 
$ redis-cli ping
```

Django setup
``````
$ python manage.py migrate

# launch a celery worker with log level debug
$ celery worker -A api.celery -c 4 -l DEBUG
``````

Load django fixtures
```
$ python manage.py loaddata 
```


### Docker Compose

```
$ git clone https://github.com/OmairK/Backend-challenge
$ docker-compose up --build
```