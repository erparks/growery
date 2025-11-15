# backend
```
python3 run.py
```

## python env
```
source ../hub_env/bin/activate
```

## database
```
./psql_install.sh
PGPASSWORD=flaskpassword psql -U flaskuser -d flaskdb -f schema.sql

flask db init
flask db migrate -m "<description>"
flask db upgrade
```