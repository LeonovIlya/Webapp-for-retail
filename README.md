### Для запуска проекта необходимо:

Установить зависимости:

```bash
pip install -r requirements.txt
```

Вам необходимо будет создать базу и прогнать миграции:

```bash
manage.py makemigrations
python manage.py migrate --run-syncdb 
manage.py createsuperuser
```

Собрать статические файлы в папку 'static'
```bash
python manage.py collectstatic
```
Выполнить команду:

```bash
python manage.py runserver <IP-address>:8000
```
