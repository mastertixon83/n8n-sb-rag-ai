import click
import os
import json
import shutil
from dotenv import load_dotenv
from loguru import logger

from utils import run_command
from config import AppConfig
from setup_n8n import setup_n8n
from setup_supabase import setup_supabase


@click.group()
def cli():
    """Инсталлятор и управляющий скрипт для n8n + Supabase + RAG AI."""
    # Загружаем переменные окружения из .env файла в текущей директории, если он существует.
    # Это позволяет подхватывать уже существующие настройки без перезаписывания системных.
    load_dotenv(override=False)


@cli.command()
@click.option('--force', is_flag=True, help='Принудительно перезаписать существующие конфигурации и пропустить интерактивный ввод.')
def install(force):
    """
    python main.py install
    python main.py destroy
    sudo rm -rf n8n_* supabase-project/

    python main.py restart --stack n8n
    python main.py restart --stack all
    python main.py restart --stack n8n --resreate
    python main.py restart --stack all --resreate

    Устанавливает и настраивает все необходимые компоненты (n8n, Supabase).
    Используйте --force, чтобы пропустить интерактивный ввод и использовать значения из .env или сгенерированные.
    """
    logger.info("🚀 Запускаем процесс установки n8n + Supabase + RAG AI...")

    try:
        # Создаем экземпляр AppConfig. 'force' будет влиять на collect_user_inputs
        config = AppConfig(skip_inputs=False)

        # 1. Собираем все необходимые данные
        logger.info("▶️ Собираем пользовательские данные или загружаем из .env...")
        config.collect_user_inputs()
        logger.success("✅ Пользовательские данные собраны/загружены.")

        # 2. Устанавливаем n8n стек
        logger.info("\n▶️ Начинаем установку n8n стека...")
        setup_n8n(config)
        logger.success("✅ Стек n8n успешно установлен и запущен!")

        # 3. Устанавливаем Supabase стек
        logger.info("\n▶️ Начинаем установку Supabase стека...")
        setup_supabase(config)
        logger.success("✅ Стек Supabase успешно установлен и запущен!")

        summary_text = f"""
        🎉 Все компоненты (n8n, Supabase) успешно установлены и запущены!

        ➡ Доступ к N8N: {config.n8n_webhook_url}
        
        ➡ Доступ к PGAdmin: http://0.0.0.0:5051/login?next=/ 
           Login: {config.n8n_pgadmin_email}
           Pass:  {config.n8n_pgadmin_password}

        ➡ Доступ к Postgres N8N:
           HOST: n8n_postgres
           DB:   {config.n8n_postgres_db}
           User: {config.n8n_postgres_user}
           Pass: {config.n8n_postgres_password}

        ➡ Inbucket (почта): http://localhost:{config.n8n_inbucket_web_port}

        ➡ Supabase Studio: http://localhost:{config.supabase_studio_port}
           Login: {config.supabase_dashboard_username}
           Pass:  {config.supabase_dashboard_password}
        
        - URL для подключения к Supabase - http://supabase-kong:8000 
        🗝 Supabase SERVICE_ROLE_KEY: {config.supabase_service_role_key}
        """
        with open("summary.txt", "w", encoding="utf-8") as file:
            file.write(summary_text.strip())

        logger.success("\n🎉 Все компоненты (n8n, Supabase) успешно установлены и запущены!")
        logger.info(summary_text)

    except Exception as e:
        logger.error(f"❌ Произошла критическая ошибка во время установки: {e}")
        logger.error("Пожалуйста, проверьте логи выше для получения дополнительной информации.")


@cli.command()
@click.option('--confirm', is_flag=True, help='Подтвердить удаление без запроса.')
def destroy(confirm):
    """
    Удаляет все установленные сервисы (n8n, Supabase) и связанные данные/конфигурации.
    Используйте --confirm для неинтерактивного удаления.
    """
    logger.info("💥 Запускаем процесс удаления всех сервисов и данных...")

    if not confirm:
        if not click.confirm("Вы уверены, что хотите полностью удалить все сервисы (n8n, Supabase), их конфигурации и данные? Это действие необратимо!", abort=True):
            logger.info("Отмена удаления.")
            return

    try:
        # Сначала остановим и удалим n8n стек
        logger.info("▶️ Останавливаем и удаляем n8n стек...")
        try:
            n8n_docker_compose_path = os.path.join(os.getcwd(), 'docker-compose.yml')
            if os.path.exists(n8n_docker_compose_path):
                run_command(["docker", "compose", "-f", n8n_docker_compose_path, "down", "-v", "--remove-orphans"])
                logger.success("✅ Стек n8n остановлен и удалены тома.")
                # Удаляем файлы конфигурации n8n
                os.remove(n8n_docker_compose_path)
                if os.path.exists('.env'):
                    os.remove('.env')
                logger.success("✅ Файлы конфигурации n8n удалены.")
            else:
                logger.info("Файл docker-compose.yml не найден. Пропуск удаления n8n.")
        except Exception as e:
            logger.warning(f"Ошибка при удалении n8n стека: {e}")

        # Затем остановим и удалим Supabase стек
        logger.info("▶️ Останавливаем и удаляем Supabase стек...")
        try:
            supabase_project_dir = os.path.join(os.getcwd(), 'supabase-project')
            if os.path.exists(os.path.join(supabase_project_dir, 'docker-compose.yml')):
                run_command(["docker", "compose", "-f", "docker-compose.yml", "down", "-v", "--remove-orphans"],
                            cwd=supabase_project_dir)
                logger.success("✅ Стек Supabase остановлен и удалены тома.")
                # Удаляем директорию проекта Supabase
                shutil.rmtree(supabase_project_dir, ignore_errors=True) # Игнорируем ошибки при удалении
                logger.success("✅ Директория Supabase-project и связанные файлы удалены.")
            else:
                logger.info("Файл docker-compose.yml в supabase-project не найден. Пропуск удаления Supabase.")
        except Exception as e:
            logger.warning(f"Ошибка при удалении Supabase стека: {e}")

        # Удаляем общую Docker сеть, если она не используется
        config_instance = AppConfig()  # Создаем экземпляр для получения имени сети
        network_name = config_instance.common_docker_network_name
        logger.info(f"▶️ Пытаемся удалить общую Docker сеть '{network_name}'...")
        try:
            inspect_result = run_command(["docker", "network", "inspect", network_name], capture_output=True, check=False)
            if inspect_result.returncode == 0:  # Сеть существует
                # Проверяем, что сеть не имеет присоединенных контейнеров (Ports - empty list or not present)
                # Более надежный способ: анализировать JSON вывод docker network inspect
                network_info = json.loads(inspect_result.stdout)[0]
                if not network_info.get("Containers") and not network_info.get("Peers"):
                    run_command(["docker", "network", "rm", network_name])
                    logger.success(f"✅ Docker сеть '{network_name}' успешно удалена.")
                else:
                    logger.warning(f"⚠️ Docker сеть '{network_name}' все еще используется контейнерами или имеет пиры. Не удалена автоматически.")
            else:
                logger.info(f"Docker сеть '{network_name}' не существует. Ничего удалять.")
        except Exception as e:
            logger.warning(f"Ошибка при попытке удаления Docker сети: {e}")

        logger.success("✅ Процесс удаления завершен.")
    except Exception as e:
        logger.error(f"❌ Ошибка при удалении сервисов: {e}")


@cli.command()
@click.option('--stack', type=click.Choice(['n8n', 'supabase', 'all']), default='all', help="""
Указывает, какой стек перезапустить:

- n8n — только стек n8n (n8n, PostgreSQL, PgAdmin, Inbucket, Cloudflare Tunnel).
- supabase — только стек Supabase (Supabase Studio, API, DB и т.д.).
- all — перезапустить оба стека.

Пример:
  python main.py restart --stack n8n
""")
@click.option('--recreate', is_flag=True, help="""
Пересоздаёт контейнеры и тома (выполняет `docker compose down -v && up -d`).
⚠️ Все связанные тома и данные будут удалены.

Пример:
  python main.py restart --stack supabase --recreate
""")
def restart(stack, recreate):
    """
    Перезапускает выбранный стек Docker (n8n, Supabase или оба).

    Эта команда позволяет быстро перезапустить сервисы без полной переустановки,
    а также пересоздать их с нуля при необходимости.

    Примеры использования:

    ▸ Перезапустить только n8n (без удаления данных):
      python main.py restart --stack n8n

    ▸ Полностью пересоздать Supabase стек (удалить и пересоздать все тома):
      python main.py restart --stack supabase --recreate

    ▸ Перезапустить всё (n8n + Supabase), сохранив данные:
      python main.py restart --stack all

    ▸ Пересоздать всё с нуля:
      python main.py restart --stack all --recreate
    """
    from utils import run_command
    from config import AppConfig

    config = AppConfig()
    stack_paths = {
        "n8n": os.path.join(os.getcwd(), "docker-compose.yml"),
        "supabase": os.path.join(os.getcwd(), "supabase-project", "docker-compose.yml"),
    }

    if recreate:
        confirm = click.confirm(
            f"Вы действительно хотите пересоздать стек '{stack}' с удалением томов (это удалит ВСЕ ДАННЫЕ)?",
            abort=True
        )
        logger.warning("⚠️ Перезапуск будет выполнен с удалением всех данных (docker compose down -v)")

    def restart_stack(name, compose_path):
        if not os.path.exists(compose_path):
            logger.warning(f"⚠️ Docker Compose файл для {name} не найден по пути: {compose_path}")
            return
        try:
            args_down = ["docker", "compose", "-f", compose_path, "down"]
            if recreate:
                args_down.append("-v")
            run_command(args_down, cwd=os.path.dirname(compose_path))
            logger.info(f"⬆️ Запускаем стек {name}...")
            run_command(["docker", "compose", "-f", compose_path, "up", "-d"], cwd=os.path.dirname(compose_path))
            logger.success(f"✅ Стек {name} успешно перезапущен!")
        except Exception as e:
            logger.error(f"❌ Ошибка при перезапуске стека {name}: {e}")

    if stack in ("n8n", "all"):
        restart_stack("n8n", stack_paths["n8n"])
    if stack in ("supabase", "all"):
        restart_stack("supabase", stack_paths["supabase"])


if __name__ == '__main__':
    cli()