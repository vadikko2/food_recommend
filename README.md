# Taste Assistant API

### Build

```
    docker-compose up -d
```

---

### Up


- Update data

```
    docker-compose run --rm -d crawler runner.py --load --save --drop_elastic --megrate
```
    
- Run API

```
    docker-compose run --rm -d api
```