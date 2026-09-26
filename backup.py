from datetime import datetime
import subprocess

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
backup_filename = f"backups/backup_{timestamp}.sql"

command = f"docker exec -t image-hosting-20-db-1 pg_dump -U postgres images_db > {backup_filename}"

try:
    subprocess.run(command, shell=True, check=True)
    print(f"Резервну копію успішно створено: {backup_filename}")
except subprocess.CalledProcessError as e:
    print(f"Помилка при створенні резервної копії: {e}")