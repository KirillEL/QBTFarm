import subprocess
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = "qbt_db"
DB_PORT = 5432
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_USER = "postgres"
DB_DB = os.getenv('POSTGRES_DB')

sql_command = "delete from flags where flags.status='SKIPPED' OR flags.status='REJECTED' OR flags.status='QUEUED';"

container_name = "qbt_db"

docker_command = f"docker exec -i {container_name} psql -U {DB_USER} -d {DB_DB} -c \"{sql_command}\""

process = subprocess.Popen(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if process.returncode == 0:
    print("Команда успешно выполнена:")
    print(stdout.decode())
else:
    print("Ошибка при выполнении команды:")
    print(stderr.decode())
