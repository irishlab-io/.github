import logging

import calculator


def main():
    logging.info("Hello from app!")
    logging.info(calculator.add(1, 2))
    logging.info(calculator.subtract(5, 3))


if __name__ == "__main__":
    main()
