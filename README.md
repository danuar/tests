pip install -r requirements.txt

в config.py вводим свои данные от postgresql

создаем бд
CREATE DATABASE ph_tests;

обновляем бд
venv/Scripts/alembic upgrade head
