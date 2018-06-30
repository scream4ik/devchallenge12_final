# General information
Shared Database without dedicated master.

Project use next technologies:
* Python 3.6
* AIOHTTP - asynchronous HTTP Client/Server
* Redis - in-memory data structure store
* Celery - asynchronous task queue/job queue
* RabbitMQ - message broker
* Docker - container platform

### Setup
At root of the project run:
```
docker-compose up --build
```

### Testing
Request to insert/update data
```bash
curl -X POST -d '{"name": "marketing", "author": "John Smith", "timestamp": 20140812003842}' 'http://127.0.0.1:8000/update'
```

Response
```json
{"marketing": {"timestamp": 20140812003842, "author": "John Smith"}}
```

Request to get data by name (data will be sorted by timestamp and return latest)
```bash
curl 'http://127.0.0.1:8000/get?name=marketing'
```

Response
```json
{"timestamp": 20140812003842, "author": "John Smith"}
```

Request to delete data by name
```bash
curl 'http://127.0.0.1:8000/remove?name=marketing'
```

Response
```json
{"success": true}
```

Request to dump all data
```bash
curl 'http://127.0.0.1:8000/dump'
```

Response
```json
{"marketing": [{"timestamp": 20140812003842, "author": "John Smith"}, {"timestamp": 20150812003842, "author": "John Smith"}, {"timestamp": 20170812003842, "author": "John Doe"}]}
```

Request to get history data by name
```bash
curl 'http://127.0.0.1:8000/getHistory?name=marketing'
```

Response
```json
[{"timestamp": 20170812003842, "author": "John Doe"}, {"timestamp": 20150812003842, "author": "John Smith"}, {"timestamp": 20140812003842, "author": "John Smith"}]
```

### Additionally
1. For add new node you need add here connection url to APP_REDIS_NODES_URL (etc/local.env). If you want add a few you can separate by comma.

2. In future we can change store data with nodes connection urls to database or something else. Implementation will be easy.

3. When we added new node, web service will know about it (he periodically compares the data with connection urls). And if service see new node he copy all data from existing node to new.

4. If some node going to offline web service will wait until node comeback and then update data. Using RabbitMQ for guarantee of data delivery.

5. When you send data to web service he create a new task in which says send new data to all nodes. If some node not available, wait when node comeback online.

6. For fun you can down any redis nodes, then send data to web service. After it up all redis nodes. You will see all data on all nodes

7. For run tests:
```bash
docker-compose exec web pytest -s
```
