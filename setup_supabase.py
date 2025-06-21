import os
import shutil
import time
from jinja2 import Environment, FileSystemLoader
import json # Для проверки сети Docker

from utils import run_command
from config import AppConfig
from loguru import logger


def setup_supabase(config: AppConfig):
    """
    Выполняет установку и настройку стека Supabase.
    Клонирует репозиторий Supabase CLI в директорию 'supabase',
    а все файлы конфигурации стека (docker-compose.yml, .env, kong.yml)
    размещает в отдельной директории 'supabase-project'.
    """
    logger.info("\n--- Настройка и запуск стека Supabase ---")

    # Определяем пути
    project_root = os.getcwd()

    # Директория для файлов конфигурации и томов стека Supabase
    supabase_project_dir = os.path.join(project_root, 'supabase-project')
    templates_dir = os.path.join(project_root, 'templates')
    repo_dir = os.path.join(project_root, 'supabase')
    repo_docker_dir = os.path.join(repo_dir, 'docker')
    repo_docker_volumes_dir = os.path.join(repo_docker_dir, 'volumes')

    # Пути к директориям 'supabase-project/volumes'
    supabase_volumes_dir = os.path.join(supabase_project_dir, 'volumes')
    supabase_api_volumes_dir = os.path.join(supabase_volumes_dir, 'api')
    supabase_db_volumes_dir = os.path.join(supabase_volumes_dir, 'db')
    supabase_logs_volumes_dir = os.path.join(supabase_volumes_dir, 'logs')
    supabase_functions_volumes_dir = os.path.join(supabase_volumes_dir, 'functions')
    supabase_storage_volumes_dir = os.path.join(supabase_volumes_dir, 'storage')
    supabase_pooler_volumes_dir = os.path.join(supabase_volumes_dir, 'pooler')

    # Пути к файлам
    supabase_env_file_path = os.path.join(supabase_project_dir, '.env')
    supabase_docker_compose_path = os.path.join(supabase_project_dir, 'docker-compose.yml')

    supabase_vector_file = os.path.join(supabase_logs_volumes_dir, "vector.yml")
    kong_yml_path_in_volumes = os.path.join(supabase_api_volumes_dir, 'kong.yml')
    jwt_sql_file = os.path.join(supabase_db_volumes_dir, "jwt.sql")

    # Настраиваем Jinja2 окружение
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Копирование скриптов
    shutil.copytree(repo_docker_volumes_dir, supabase_volumes_dir, dirs_exist_ok=True)

    # Генерация .env
    supabase_env_template = env.get_template("supabase_env.j2")

    logger.info("▶️ Генерируем .env файл для Supabase...")

    supabase_env_vars = {
        "SUPABASE_JWT_SECRET": config.supabase_jwt_secret,
        "SUPABASE_ANON_KEY": config.supabase_anon_key,
        "SUPABASE_SERVICE_ROLE_KEY": config.supabase_service_role_key,
        "SUPABASE_DASHBOARD_USERNAME": "supabase-admin",
        "SUPABASE_DASHBOARD_PASSWORD": config.supabase_dashboard_password,
        "SUPABASE_SECRET_KEY_BASE": config.supabase_secret_key_base,
        "SUPABASE_VAULT_ENC_KEY": config.supabase_vault_enc_key,

        "SUPABASE_POSTGRES_PASSWORD": config.supabase_postgres_password,
        "SUPABASE_POSTGRES_USERNAME": "supabase-pg_admin",
        "SUPABASE_POSTGRES_HOST": config.supabase_postgres_host,
        "SUPABASE_POSTGRES_PORT": config.supabase_postgres_port,
        "SUPABASE_POSTGRES_DB": config.supabase_postgres_db,
        "SUPABASE_POSTGRES_HOST_PORT": config.supabase_postgres_port,

        "SUPABASE_POOLER_PROXY_PORT_TRANSACTION": config.supabase_pooler_proxy_port_transaction,
        "SUPABASE_POOLER_DEFAULT_POOL_SIZE": config.supabase_pooler_default_pool_size,
        "SUPABASE_POOLER_MAX_CLIENT_CONN": config.supabase_pooler_max_client_conn,
        "SUPABASE_POOLER_TENANT_ID": config.supabase_pooler_tenant_id,

        "SUPABASE_KONG_HTTP_PORT": config.supabase_kong_http_port,
        "SUPABASE_KONG_HTTPS_PORT": config.supabase_kong_https_port,

        "SUPABASE_PGRST_DB_SCHEMAS": config.supabase_pgrst_db_schemas,

        "SUPABASE_SITE_URL": config.supabase_site_url,
        "SUPABASE_ADDITIONAL_REDIRECT_URLS": config.supabase_additional_redirect_urls,
        "SUPABASE_JWT_EXPIRY": config.supabase_jwt_expiry,
        "SUPABASE_DISABLE_SIGNUP": config.supabase_disable_signup,
        "SUPABASE_API_EXTERNAL_URL": config.supabase_api_external_url,

        "SUPABASE_MAILER_URLPATHS_CONFIRMATION": config.supabase_mailer_urlpaths_confirmation,
        "SUPABASE_MAILER_URLPATHS_INVITE": config.supabase_mailer_urlpaths_invite,
        "SUPABASE_MAILER_URLPATHS_RECOVERY": config.supabase_mailer_urlpaths_recovery,
        "SUPABASE_MAILER_URLPATHS_EMAIL_CHANGE": config.supabase_mailer_urlpaths_email_change,

        "SUPABASE_ENABLE_EMAIL_SIGNUP": config.supabase_enable_email_signup,
        "SUPABASE_ENABLE_EMAIL_AUTOCONFIRM": config.supabase_enable_email_autoconfirm,
        "SUPABASE_SMTP_ADMIN_EMAIL": config.supabase_smtp_admin_email,
        "SUPABASE_SMTP_HOST": config.supabase_smtp_host,
        "SUPABASE_SMTP_PORT": config.supabase_smtp_port,
        "SUPABASE_SMTP_USER": config.supabase_smtp_user,
        "SUPABASE_SMTP_PASS": config.supabase_smtp_pass,
        "SUPABASE_SMTP_SENDER_NAME": config.supabase_smtp_sender_name,
        "SUPABASE_ENABLE_ANONYMOUS_USERS": config.supabase_enable_anonymous_users,

        "SUPABASE_ENABLE_PHONE_SIGNUP": config.supabase_enable_phone_signup,
        "SUPABASE_ENABLE_PHONE_AUTOCONFIRM": config.supabase_enable_phone_autoconfirm,

        "SUPABASE_STUDIO_DEFAULT_ORGANIZATION": config.supabase_studio_default_organization,
        "SUPABASE_STUDIO_DEFAULT_PROJECT": config.supabase_studio_default_project,

        "SUPABASE_STUDIO_PORT": config.supabase_studio_port,
        "SUPABASE_PUBLIC_URL": config.supabase_public_url,

        "SUPABASE_IMGPROXY_ENABLE_WEBP_DETECTION": config.supabase_imgproxy_enable_webp_detection,

        "SUPABASE_OPENAI_API_KEY": config.supabase_openai_api_key,

        "SUPABASE_FUNCTIONS_VERIFY_JWT": config.supabase_functions_verify_jwt,

        "LOGFLARE_API_KEY": config.supabase_logflare_api_key,
        "SUPABASE_DB_ENC_KEY": config.supabase_db_enc_key,
        "LOGFLARE_PUBLIC_ACCESS_TOKEN": config.supabase_logflare_api_key,

        "SUPABASE_DOCKER_SOCKET_LOCATION": config.supabase_docker_socket_location,

        "SUPABASE_GOOGLE_PROJECT_ID": config.supabase_google_project_id,
        "SUPABASE_GOOGLE_PROJECT_NUMBER": config.supabase_google_project_number,

        "COMMON_DOCKER_NETWORK_NAME": config.common_docker_network_name
    }

    rendered_env = supabase_env_template.render(supabase_env_vars)
    with open(supabase_env_file_path, 'w') as f:
        f.write(rendered_env)
    logger.success(f"✅ .env файл для Supabase успешно сгенерирован")

    # Генерируем kong.yml
    logger.info("▶️ Генерируем kong.yml...")
    kong_yml_template = env.get_template('supabase_kong.j2')
    kong_yml_vars = {
        "SUPABASE_ANON_KEY": config.supabase_anon_key,
        "SUPABASE_SERVICE_ROLE_KEY": config.supabase_service_role_key,
        "SUPABASE_DASHBOARD_USERNAME": config.supabase_dashboard_username,
        "SUPABASE_DASHBOARD_PASSWORD": config.supabase_dashboard_password,
    }
    rendered_kong_yml = kong_yml_template.render(kong_yml_vars)
    with open(kong_yml_path_in_volumes, 'w') as f:
        f.write(rendered_kong_yml)
    logger.success(f"✅ kong.yml успешно сгенерирован")

    # Генерируем docker-compose.yml для Supabase
    logger.info("▶️ Генерируем docker-compose.yml для Supabase...")
    supabase_docker_compose_template = env.get_template('supabase_docker_compose.j2')

    rendered_supabase_docker_compose = supabase_docker_compose_template.render(supabase_env_vars)
    with open(supabase_docker_compose_path, 'w') as f:
        f.write(rendered_supabase_docker_compose)
    logger.success(f"✅ docker-compose.yml для Supabase успешно сгенерирован")

    # Генерируем vector.yml
    supabase_vector_template = env.get_template("supabase_vector.j2")

    rendered_supabase_vector_file = supabase_vector_template.render(LOGFLARE_API_KEY=config.supabase_logflare_api_key)
    with open(supabase_vector_file, 'w') as f:
        f.write(rendered_supabase_vector_file)
    logger.success(f"✅ vector.yml для Supabase успешно сгенерирован")

    # Генерация jwt.sql
    jwt_supabase_template = env.get_template("supabase_jwt_sql.j2")
    rendered_supabase_jwt_file = jwt_supabase_template.render(SUPABASE_JWT_SECRET=config.supabase_jwt_secret)
    with open(jwt_sql_file, 'w') as f:
        f.write(rendered_supabase_jwt_file)
    logger.success(f"✅ jwt.sql для Supabase успешно сгенерирован")

    # Проверяем наличие общей Docker сети (возможно, уже создана n8n)
    logger.info(f"▶️ Проверяем и создаем Docker сеть: {config.common_docker_network_name}")
    try:
        # Проверяем, существует ли сеть
        result = run_command(["docker", "network", "inspect", config.common_docker_network_name], check=False, capture_output=True)
        if result.returncode != 0: # Если сеть не существует, создаем ее
            run_command(["docker", "network", "create", config.common_docker_network_name])
            logger.success(f"Docker сеть '{config.common_docker_network_name}' создана.")
        else:
            logger.info(f"Docker сеть '{config.common_docker_network_name}' уже существовала.")
    except Exception as e:
        logger.error(f"❌ Не удалось проверить или создать Docker сеть: {e}")
        raise # Перевыбрасываем исключение, так как без сети не сможем продолжить

    # 10. Запуск Docker Compose для Supabase
    logger.info(f"▶️ Запускаем Docker Compose для Supabase. Это может занять некоторое время...")
    # Важно: cwd теперь supabase_project_dir, и пути к файлам относительны этой директории
    run_command(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env", "up", "-d"],
        cwd=supabase_project_dir
    )
    logger.success("✅ Начальный запуск стека Supabase выполнен!")

    logger.success("\n🎉 Стек Supabase успешно запущен и настроен!")