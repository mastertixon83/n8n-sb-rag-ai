import os
import shutil
import time
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse

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
    n8n_env_file_path = os.path.join(project_root, '.env' if config.server.lower() == "local" else ".env_vps")
    n8n_docker_compose_path = os.path.join(project_root, 'docker-compose.yml' if config.server.lower() == "local" else "docker-compose_vps.yml")
    n8n_data_dir = os.path.join(project_root, 'n8n_data')
    n8n_postgres_data_dir = os.path.join(project_root, 'n8n_postgres_data')
    n8n_pgadmin_data_dir = os.path.join(project_root, 'n8n_pgadmin_data')

    n8n_nginx_dir = os.path.join(project_root, 'nginx')
    n8n_nginx_conf_d_dir = os.path.join(n8n_nginx_dir, 'conf.d' if config.server.lower() == "local" else "conf.d_vps")
    n8n_nginx_file_path = os.path.join(n8n_nginx_dir, 'nginx.conf')
    n8n_nginx_conf_d_file_path = os.path.join(n8n_nginx_conf_d_dir, "n8n.conf")

    # Создаем необходимые директории для данных, если они не существуют
    for directory in [n8n_nginx_conf_d_dir]:
    # for directory in [n8n_data_dir, n8n_postgres_data_dir, n8n_pgadmin_data_dir, n8n_nginx_dir, n8n_nginx_conf_d_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Проверена/создана директория для данных: {directory}")

    # Инициализируем Jinja2 для загрузки шаблонов
    env = Environment(loader=FileSystemLoader(templates_dir))

    n8n_compose_template = env.get_template('n8n_docker_compose_local.j2' if config.server.lower() == "local" else "n8n_docker_compose_vps.j2")
    n8n_env_template = env.get_template('n8n_env_local.j2' if config.server.lower() == "local" else "n8n_env_vps.j2")
    n8n_nginx_template = env.get_template("nginx.j2")
    n8n_nginx_conf_d_template = env.get_template("nginx_conf_d_local.j2" if config.server.lower() == "local" else "nginx_conf_d_vps.j2")

    # Генерируем docker-compose.n8n.yml
    logger.info(f"Генерирую {n8n_docker_compose_path} из шаблона...")
    parsed_url = urlparse(config.n8n_webhook_url)
    try:
        compose_vars = {
            "N8N_POSTGRES_USER": config.n8n_postgres_user,
            "N8N_POSTGRES_DATABASE": config.n8n_postgres_db,
            "N8N_POSTGRES_PORT": config.n8n_postgres_port,
            "N8N_PGADMIN_EMAIL": config.n8n_pgadmin_email,
            "COMMON_DOCKER_NETWORK_NAME": config.common_docker_network_name,
            "N8N_POSTGRES_TYPE": "postgresdb",
            "N8N_POSTGRES_HOST": "n8n_postgres",
            "N8N_GENERIC_TIMEZONE": config.n8n_generic_timezone,
            "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": config.n8n_file_permissions if config.n8n_file_permissions else "false",
            "N8N_INBUCKET_WEB_PORT": config.n8n_inbucket_web_port,
            "N8N_WEBHOOK_URL": config.n8n_webhook_url,
            "N8N_EDITOR_BASE_URL": config.n8n_webhook_url,
            "N8N_HOST": parsed_url.netloc,
            **({
                "CLOUDFLARE_TUNNEL_TOKEN": config.cloudflare_tunnel_token
               } if config.server.lower() == "local" else {}),
        }
    except Exception as ex:
        logger.error(ex)
    rendered_compose = n8n_compose_template.render(compose_vars)
    with open(n8n_docker_compose_path, 'w') as f:
        f.write(rendered_compose)
    logger.success(f"docker-compose.yml успешно сгенерирован.")

    # Генерируем .env.n8n
    logger.info(f"Генерирую {n8n_env_file_path} из шаблона...")
    n8n_env_vars = {
        "N8N_POSTGRES_PASSWORD": config.n8n_postgres_password,
        "N8N_PGADMIN_PASSWORD": config.n8n_pgadmin_password,
        **({"CLOUDFLARE_TUNNEL_TOKEN": config.cloudflare_tunnel_token} if config.server.lower() == "local" else {}),
        "N8N_OPENAI_API_KEY": config.n8n_openai_api_key,
        "N8N_WEBHOOK_URL": config.n8n_webhook_url,
        "N8N_EDITOR_BASE_URL": config.n8n_webhook_url,
        "N8N_HOST": parsed_url.netloc,
    }
    rendered_env = n8n_env_template.render(n8n_env_vars)
    with open(n8n_env_file_path, 'w') as f:
        f.write(rendered_env)
    logger.success(f".env успешно сгенерирован.")

    # Генерация настроек NGINX
    nginx_n8n_vars = {
        "N8N_HOST": parsed_url.netloc,
    }
    rendered_env = n8n_nginx_template.render(nginx_n8n_vars)
    with open(n8n_nginx_file_path, 'w') as f:
        f.write(rendered_env)
    logger.success(f"Настройки NGINX успешно сохронены.")

    nginx_n8n_vars = {
        "N8N_HOST": parsed_url.netloc,
    }
    rendered_env = n8n_nginx_conf_d_template.render(nginx_n8n_vars)
    with open(n8n_nginx_conf_d_file_path, 'w') as f:
        f.write(rendered_env)
    logger.success(f"Настройки NGINX успешно сохронены.")

    # Проверяем и создаем общую Docker сеть
    logger.info(f"Проверяем и создаем Docker сеть: {config.common_docker_network_name}")
    try:
        # check=False, потому что docker network create вернет ошибку, если сеть уже существует
        # run_command(["docker", "network", "create", config.common_docker_network_name], check=False, capture_output=False)
        logger.success(f"Docker сеть '{config.common_docker_network_name}' создана или уже существовала.")
    except Exception as e:
        logger.warning(f"Не удалось создать Docker сеть (возможно, уже существует): {e}")

    # Запуск Docker Compose для n8n
    logger.info(f"Запускаем Docker Compose для n8n. Это может занять некоторое время...")
    try:
        # run_command(["docker", "compose", "-f", n8n_docker_compose_path, "--env-file", n8n_env_file_path, "up", "-d"])
        logger.success("✅ Стек n8n успешно запущен!")

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске стека n8n: {e}")
        raise # Перебрасываем ошибку, чтобы main.py мог ее поймать