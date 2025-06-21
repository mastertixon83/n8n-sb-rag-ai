import secrets
import string
import requests
import json
import time
import subprocess
import sys
import os
from loguru import logger


def generate_random_string(length: int) -> str:
    """Генерирует случайную строку заданной длины, содержащую буквы и цифры."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))


def run_command(command: list, cwd=None, check=True, capture_output=True) -> subprocess.CompletedProcess:
    """
    Выполняет команду в подпроцессе и опционально печатает вывод.
    :param command: Список строк, представляющих команду и ее аргументы.
    :param cwd: Рабочая директория для выполнения команды.
    :param check: Если True, вызывает CalledProcessError при ненулевом коде возврата.
    :param capture_output: Если True, stdout и stderr будут захвачены и доступны в return.stdout/stderr.
                           Если False, вывод будет направлен в консоль.
    :return: Объект subprocess.CompletedProcess.
    """
    logger.info(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True,  # Декодирует stdout/stderr как текст
            encoding='utf-8'  # Явно указываем кодировку
        )
        if capture_output:
            if result.stdout:
                logger.info(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                logger.info(f"STDERR:\n{result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        logger.info(f"Error executing command: {' '.join(command)}", file=sys.stderr)
        logger.info(f"Return code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            logger.info(f"STDOUT:\n{e.stdout}", file=sys.stderr)
        if e.stderr:
            logger.info(f"STDERR:\n{e.stderr}", file=sys.stderr)
        raise  # Перевыбрасываем исключение
