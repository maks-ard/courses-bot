# courses-bot
## Описание
Телеграмм бот для продажи и покупки курсов

## Deploy
```bash
docker build -t maksard99/courses-bot:<version> .  
docker push maksard99/courses-bot:<version>
```
На сервере
```bash
docker run --env-file=.env-courses-bot --name=courses-bot -d maksard99/courses-bot:<version>
```