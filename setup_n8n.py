import os
import shutil
import time
from jinja2 import Environment, FileSystemLoader

from utils import run_command
from config import AppConfig # Импортируем AppConfig для доступа к данным
from loguru import logger


def setup_n8n(config: AppConfig):
    """
    Выполняет установку и настройку стека n8n.
    """
    logger.info("\n--- Настройка и запуск стека n8n ---")

    # Определяем пути
    project_root = os.getcwd()
    templates_dir = os.path.join(project_root, 'templates')
    n8n_env_file_path = os.path.join(project_root, '.env')
    n8n_docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
    n8n_data_dir = os.path.join(project_root, 'n8n_data')
    n8n_postgres_data_dir = os.path.join(project_root, 'n8n_postgres_data')
    n8n_pgadmin_data_dir = os.path.join(project_root, 'n8n_pgadmin_data')

    # Создаем необходимые директории для данных, если они не существуют
    for directory in [n8n_data_dir, n8n_postgres_data_dir, n8n_pgadmin_data_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Проверена/создана директория для данных: {directory}")

    # Инициализируем Jinja2 для загрузки шаблонов
    env = Environment(loader=FileSystemLoader(templates_dir))
    n8n_compose_template = env.get_template('n8n_docker_compose_template.j2')
    n8n_env_template = env.get_template('n8n_env_template.j2')

    # 1. Генерируем docker-compose.n8n.yml
    logger.info(f"Генерирую {n8n_docker_compose_path} из шаблона...")
    compose_vars = {
        "N8N_POSTGRES_USER": config.n8n_postgres_user,
        "N8N_POSTGRES_DATABASE": config.n8n_postgres_db,
        "N8N_POSTGRES_PORT": 5432,
        "N8N_PGADMIN_EMAIL": config.n8n_pgadmin_email,
        "COMMON_DOCKER_NETWORK_NAME": config.common_docker_network_name,
        "N8N_POSTGRES_TYPE": "postgresdb",
        "N8N_POSTGRES_HOST": "n8n_postgres",
        "N8N_GENERIC_TIMEZONE": config.n8n_generic_timezone,
        "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": config.n8n_file_permissions if config.n8n_file_permissions else "false",
        "N8N_INBUCKET_WEB_PORT": config.n8n_inbucket_web_port,
        "N8N_WEBHOOK_URL": config.n8n_webhook_url,
        "N8N_EDITOR_BASE_URL": config.n8n_webhook_url,
        "N8N_HOST": config.n8n_webhook_url.split('https://')[1],
        "CLOUDFLARE_TUNNEL_TOKEN": config.cloudflare_tunnel_token,
    }
    rendered_compose = n8n_compose_template.render(compose_vars)
    with open(n8n_docker_compose_path, 'w') as f:
        f.write(rendered_compose)
    logger.success(f"docker-compose.yml успешно сгенерирован.")

    # 2. Генерируем .env.n8n
    logger.info(f"Генерирую {n8n_env_file_path} из шаблона...")
    n8n_env_vars = {
        "N8N_POSTGRES_PASSWORD": config.n8n_postgres_password,
        "N8N_PGADMIN_PASSWORD": config.n8n_pgadmin_password,
        "CLOUDFLARE_TUNNEL_TOKEN": config.cloudflare_tunnel_token,
        "N8N_OPENAI_API_KEY": config.n8n_openai_api_key,
        "N8N_WEBHOOK_URL": config.n8n_webhook_url,
        "N8N_EDITOR_BASE_URL": config.n8n_webhook_url,
        "N8N_HOST": config.n8n_webhook_url.split('https://')[1],
    }
    rendered_env = n8n_env_template.render(n8n_env_vars)
    with open(n8n_env_file_path, 'w') as f:
        f.write(rendered_env)
    logger.success(f".env успешно сгенерирован.")

    # 3. Проверяем и создаем общую Docker сеть
    logger.info(f"Проверяем и создаем Docker сеть: {config.common_docker_network_name}")
    try:
        # check=False, потому что docker network create вернет ошибку, если сеть уже существует
        run_command(["docker", "network", "create", config.common_docker_network_name], check=False, capture_output=False)
        logger.success(f"Docker сеть '{config.common_docker_network_name}' создана или уже существовала.")
    except Exception as e:
        logger.warning(f"Не удалось создать Docker сеть (возможно, уже существует): {e}")

    # 4. Запуск Docker Compose для n8n
    logger.info(f"Запускаем Docker Compose для n8n. Это может занять некоторое время...")
    try:
        run_command(["docker", "compose", "-f", n8n_docker_compose_path, "--env-file", n8n_env_file_path, "up", "-d"])
        logger.success("✅ Стек n8n успешно запущен!")

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске стека n8n: {e}")
        raise # Перебрасываем ошибку, чтобы main.py мог ее поймать