pip install -r requirements.txt

в config.py вводим свои данные от postgresql

обновляем бд
CREATE DATABASE ph_tests;

venv/Scripts/alembic upgrade head
