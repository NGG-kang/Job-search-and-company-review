## Prod build

```
# workpath:/usr/src/

poetry build
poetry run poetry-lock-package --build
```


```
# celery start
celery -A celeries worker -l INFO -B
```
