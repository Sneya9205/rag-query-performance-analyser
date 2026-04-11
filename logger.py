import logging
#Structured logging setup
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)


def log_event(message):
    print(message," is logged")
    logging.info(message)