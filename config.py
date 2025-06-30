import os
import secrets
import string
import click
import getpass
import base64
import hashlib
import hmac
import time
import json
import jwt
from dotenv import load_dotenv
from loguru import logger

from utils import generate_random_string


class AppConfig:
    def __init__(self, skip_inputs: bool = False):  # <-- ИЗМЕНЕНИЕ ЗДЕСЬ
        self.skip_inputs = skip_inputs  # <-- И ДОБАВЛЕНИЕ ЭТОЙ СТРОКИ

        # N8N
        self.server = "local"
        self.n8n_postgres_password = ""
        self.n8n_pgadmin_password = ""
        self.n8n_openai_api_key = ""
        self.n8n_inbucket_web_port = 9000
        self.n8n_file_permissions = ""
        self.n8n_postgres_user = "n8n_pg_user"
        self.n8n_postgres_db = "n8n_pg_db"
        self.n8n_pgadmin_email = "admin@example.com"
        self.n8n_generic_timezone = "Europe/Moscow"
        self.cloudflare_tunnel_token = ""
        self.n8n_webhook_url = ""
        self.n8n_postgres_port = ""

        # Supabase
        self.supabase_postgres_password = os.getenv("SUPABASE_POSTGRES_PASSWORD")
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase_dashboard_username = os.getenv("SUPABASE_DASHBOARD_USERNAME", "supabase-admin")
        self.supabase_dashboard_password = os.getenv("SUPABASE_DASHBOARD_PASSWORD")
        self.supabase_secret_key_base = os.getenv("SUPABASE_SECRET_KEY_BASE")
        self.supabase_vault_enc_key = os.getenv("SUPABASE_VAULT_ENC_KEY")

        self.supabase_postgres_host = os.getenv("SUPABASE_POSTGRES_HOST", "db")  # Внутри Docker Compose
        self.supabase_postgres_port = int(os.getenv("SUPABASE_POSTGRES_PORT", 5435))  # Внутренний порт DB
        self.supabase_postgres_db = os.getenv("SUPABASE_POSTGRES_DB", "postgres")

        self.supabase_pooler_proxy_port_transaction = int(os.getenv("SUPABASE_POOLER_PROXY_PORT_TRANSACTION", 6543))
        self.supabase_pooler_default_pool_size = int(os.getenv("SUPABASE_POOLER_DEFAULT_POOL_SIZE", 20))
        self.supabase_pooler_max_client_conn = int(os.getenv("SUPABASE_POOLER_MAX_CLIENT_CONN", 100))
        self.supabase_pooler_tenant_id = os.getenv("SUPABASE_POOLER_TENANT_ID", "default")

        self.supabase_kong_http_port = int(os.getenv("SUPABASE_KONG_HTTP_PORT", 8000))
        self.supabase_kong_https_port = int(os.getenv("SUPABASE_KONG_HTTPS_PORT", 8443))

        self.supabase_pgrst_db_schemas = os.getenv("SUPABASE_PGRST_DB_SCHEMAS",
                                                   "public,storage,graphql_public,extensions,realtime")

        self.supabase_site_url = os.getenv("SUPABASE_SITE_URL", "http://localhost:8000")
        self.supabase_additional_redirect_urls = os.getenv("SUPABASE_ADDITIONAL_REDIRECT_URLS", "")
        self.supabase_jwt_expiry = int(os.getenv("SUPABASE_JWT_EXPIRY", 3600))
        self.supabase_disable_signup = os.getenv("SUPABASE_DISABLE_SIGNUP", "false").lower() == "true"
        self.supabase_api_external_url = os.getenv("SUPABASE_API_EXTERNAL_URL", "http://localhost:8000")

        self.supabase_mailer_urlpaths_confirmation = os.getenv("SUPABASE_MAILER_URLPATHS_CONFIRMATION",
                                                               "/auth/v1/verify")
        self.supabase_mailer_urlpaths_invite = os.getenv("SUPABASE_MAILER_URLPATHS_INVITE", "/auth/v1/verify")
        self.supabase_mailer_urlpaths_recovery = os.getenv("SUPABASE_MAILER_URLPATHS_RECOVERY", "/auth/v1/verify")
        self.supabase_mailer_urlpaths_email_change = os.getenv("SUPABASE_MAILER_URLPATHS_EMAIL_CHANGE",
                                                               "/auth/v1/verify")

        self.supabase_enable_email_signup = os.getenv("SUPABASE_ENABLE_EMAIL_SIGNUP", "true").lower() == "true"
        self.supabase_enable_email_autoconfirm = os.getenv("SUPABASE_ENABLE_EMAIL_AUTOCONFIRM",
                                                           "false").lower() == "true"
        self.supabase_smtp_admin_email = os.getenv("SUPABASE_SMTP_ADMIN_EMAIL", "admin@example.com")
        self.supabase_smtp_host = os.getenv("SUPABASE_SMTP_HOST", "supabase-mail")
        self.supabase_smtp_port = int(os.getenv("SUPABASE_SMTP_PORT", 2500))
        self.supabase_smtp_user = os.getenv("SUPABASE_SMTP_USER", "fake_mail_user")
        self.supabase_smtp_pass = os.getenv("SUPABASE_SMTP_PASS", "fake_mail_password")
        self.supabase_smtp_sender_name = os.getenv("SUPABASE_SMTP_SENDER_NAME", "Supabase")
        self.supabase_enable_anonymous_users = os.getenv("SUPABASE_ENABLE_ANONYMOUS_USERS", "false").lower() == "true"

        self.supabase_enable_phone_signup = os.getenv("SUPABASE_ENABLE_PHONE_SIGNUP", "true").lower() == "true"
        self.supabase_enable_phone_autoconfirm = os.getenv("SUPABASE_ENABLE_PHONE_AUTOCONFIRM",
                                                           "true").lower() == "true"

        self.supabase_studio_default_organization = os.getenv("SUPABASE_STUDIO_DEFAULT_ORGANIZATION",
                                                              "Default Organization")
        self.supabase_studio_default_project = os.getenv("SUPABASE_STUDIO_DEFAULT_PROJECT", "Default Project")

        self.supabase_studio_port = int(os.getenv("SUPABASE_STUDIO_PORT", 8000))
        self.supabase_public_url = os.getenv("SUPABASE_PUBLIC_URL", "http://localhost:8000")

        self.supabase_imgproxy_enable_webp_detection = os.getenv("SUPABASE_IMGPROXY_ENABLE_WEBP_DETECTION",
                                                                 "true").lower() == "true"

        self.supabase_openai_api_key = os.getenv("SUPABASE_OPENAI_API_KEY", "")

        self.supabase_functions_verify_jwt = os.getenv("SUPABASE_FUNCTIONS_VERIFY_JWT", "false").lower() == "true"

        self.supabase_logfkare_logger_backend_api_key = os.getenv("LOGFLARE_API_KEY")
        self.supabase_logflare_api_key = os.getenv("LOGFLARE_API_KEY")

        self.supabase_docker_socket_location = os.getenv("SUPABASE_DOCKER_SOCKET_LOCATION", "/var/run/docker.sock")

        self.supabase_google_project_id = os.getenv("SUPABASE_GOOGLE_PROJECT_ID", "")
        self.supabase_google_project_number = os.getenv("SUPABASE_GOOGLE_PROJECT_NUMBER", "")
        self.supabase_db_enc_key = os.getenv("SUPABASE_DB_ENC_KEY", "")

        self.common_docker_network_name = os.getenv("COMMON_DOCKER_NETWORK_NAME", "n8n_supabase_network")

    def collect_user_inputs(self):
        """
        Собирает все необходимые пользовательские данные или загружает из .env.
        Если self.skip_inputs True, интерактивный ввод пропускается,
        и используются только значения из .env или сгенерированные.
        """
        if self.skip_inputs:  # <-- ИЗМЕНЕНИЕ ЗДЕСЬ
            logger.info("⏩ Пропускаем интерактивный ввод, используя значения из .env или генерируя их.")
            self.generate_missing_secrets()  # Генерируем только то, что отсутствует
            return

        logger.info("Проверяем текущие настройки и запрашиваем недостающие данные...")

        # ... (остальной код для интерактивного ввода) ...
        # Здесь логика, которая запрашивает у пользователя данные,
        # если self.n8n_postgres_password и т.д. None или пустые.
        # Например:
        self.server = input(
            "На каком серверре будем разворачивать локальном (local) или vps: "
        )
        if not self.n8n_postgres_password:
            self.n8n_postgres_password = input(
                "Введите пароль для n8n PostgreSQL (оставьте пустым для автогенерации):")
            if not self.n8n_postgres_password:
                self.n8n_postgres_password = generate_random_string(32)
                logger.info(f"Сгенерирован пароль для n8n PostgreSQL: {self.n8n_postgres_password}")

        if self.server.lower() == "local":
            self.cloudflare_tunnel_token = input(
                "Введите токен для cCloudFlare: ")
        if not self.n8n_webhook_url:
            self.n8n_webhook_url = input("Ведите webhook url: ")
        if not self.n8n_postgres_port:
            self.n8n_postgres_port = input("Ведите порт для Postgres N8N: ")
        if not self.supabase_openai_api_key:
            self.supabase_openai_api_key = input("Введите OpenAi Api Token: ")

        # ... и так далее для всех нужных переменных ...

        self.generate_missing_secrets()  # Убедимся, что все секреты сгенерированы после ввода

    def generate_missing_secrets(self):
        """Генерирует отсутствующие секреты, если они еще не установлены."""
        logger.info("▶️ Проверяем и генерируем недостающие секреты...")

        # N8N secrets
        if not self.n8n_postgres_password:
            self.n8n_postgres_password = generate_random_string(32)
            logger.info(f"Сгенерирован N8N_POSTGRES_PASSWORD.")
        if not self.n8n_pgadmin_password:
            self.n8n_pgadmin_password = generate_random_string(16)
            logger.info(f"Сгенерирован N8N_PGADMIN_PASSWORD.")

        # Supabase secrets
        if not self.supabase_jwt_secret:
            self.supabase_jwt_secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
            logger.info(f"Сгенерирован SUPABASE_JWT_SECRET.")
        if not self.supabase_anon_key:
            self.supabase_anon_key = self._generate_supabase_key(self.supabase_jwt_secret, "anon")
            logger.info(f"Сгенерирован SUPABASE_ANON_KEY.")
        if not self.supabase_service_role_key:
            self.supabase_service_role_key = self._generate_supabase_key(self.supabase_jwt_secret, "service_role")
            logger.info(f"Сгенерирован SUPABASE_SERVICE_ROLE_KEY.")
        if not self.supabase_db_enc_key:
            self.supabase_db_enc_key = secrets.token_hex(32).lower()
            logger.info(f"Сгенерирован SUPABASE_DB_ENC_KEY.")
        if not self.supabase_dashboard_password:
            self.supabase_dashboard_password = generate_random_string(16)
            logger.info(f"Сгенерирован SUPABASE_DASHBOARD_PASSWORD.")
        if not self.supabase_secret_key_base:
            self.supabase_secret_key_base = secrets.token_hex(32).lower()
            logger.info(f"Сгенерирован SUPABASE_SECRET_KEY_BASE.")
        if not self.supabase_vault_enc_key:
            alphabet = string.ascii_letters + string.digits
            self.supabase_vault_enc_key = ''.join(secrets.choice(alphabet) for _ in range(32))
            logger.info(f"Сгенерирован SUPABASE_VAULT_ENC_KEY (32 симв.).")
        if not self.supabase_postgres_password:
            self.supabase_postgres_password = generate_random_string(32)
            logger.info(f"Сгенерирован SUPABASE_POSTGRES_PASSWORD.")
        if not self.supabase_logflare_api_key:
            self.supabase_logflare_api_key = generate_random_string(32)
            logger.info(f"Сгенерирован SUPABASE_LOGFLARE_API_KEY.")
        logger.success("✅ Все необходимые секреты сгенерированы.")

    def _generate_supabase_key(self, jwt_secret: str, role: str) -> str:
        """
        Генерирует Supabase ключ (anon или service_role), как в bash-скрипте — вручную, без PyJWT.
        """
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": "supabase-auth",
            "iss": "supabase",
            "aud": "authenticated" if role == "anon" else "",
            "iat": int(time.time()),
            "exp": int(time.time()) + 15777000,  # ~6 месяцев
            "role": role,
        }

        def b64encode(data: dict) -> str:
            json_str = json.dumps(data, separators=(",", ":"))
            encoded = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")
            return encoded.rstrip("=").replace("\n", "")

        header_b64 = b64encode(header)
        payload_b64 = b64encode(payload)
        message = f"{header_b64}.{payload_b64}"

        signature = hmac.new(
            jwt_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=").replace("\n", "")

        return f"{header_b64}.{payload_b64}.{signature_b64}"
