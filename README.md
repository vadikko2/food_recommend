# Taste Assistant API

### Build

```
    docker-compose up -d
```

---

### Up

- Run Alert Bot

```
    docker-compose run --rm -d slackbot
```

- Update data

```
    docker-compose run --rm -d crawler runner.py --load --save --drop_elastic --migrate
```
    
- Run API

```
    docker-compose run --rm -d api
```

