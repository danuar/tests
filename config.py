import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-.4s: [%(asctime)s.%(msecs)03d] - %(filename)-15s l:%(lineno)-6d %(funcName)-25s - %(message)s",
    datefmt="%H:%M:%S",)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


DATABASE_USER = 'postgres'
DATABASE_PASSWORD = '1234'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
DATABASE_NAME = 'ph_tests'
