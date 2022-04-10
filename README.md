# 구직 공고 크롤링 및 기업 정보, 후기 크롤링 프로젝트

url: https://mixedprogramming.net/

유지기간 : 220201~230201(aws 무료 기간)

2022-04-01 기준 구직 정보는 사람인, 잡코리아 크롤링 

기업정보는 사람인, 잡플래닛, 잡코리아를 크롤링 하였습니다.

구직 크롤링시, 기업 정보 크롤링 및 매칭된 데이터(기업 이름, 주소가 같음)는 구직 크롤링 결과 페이지에 볼 수 있습니다.

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
