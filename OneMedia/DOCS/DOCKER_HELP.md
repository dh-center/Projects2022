Run docker-compose:
```shell
docker-compose up -d
```

Run with rebuild:
```shell
docker-compose up --build -d
```

Run concrete service:
```shell
docker-compose up -d <service_name_1> <service_name_2>
```

Put down all services
```shell
docker-compose down
```

Stop
```shell
docker-compose stop
# or concrete
docker-compose stop <service_name_1> <service_name_2>
```

Check logs
```shell
docker-compose logs
```

Get inside container
```shell
docker exec -it one_media_tlg_bot /bin/bash
```