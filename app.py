from http.server import HTTPServer, BaseHTTPRequestHandler
from email.parser import BytesParser
import os
import uuid
import logging
import json
import psycopg2

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            message = "<h1>Welcome to Image Hosting API!</h1><p>Ви на головній сторінці.</p>"
            self.wfile.write(message.encode("utf-8"))


        elif self.path == "/images" or self.path == "/images/":
            images_dir = 'images'
            files = []
            if os.path.exists(images_dir):
                files = [
                    f for f in os.listdir(images_dir)

                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
                ]

            response_data = json.dumps(files)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_data.encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            message = "<h1>404 Помилка</h1><p>Сторінку не знайдено.</p>"
            self.wfile.write(message.encode("utf-8"))

    def do_POST(self):
        if self.path == "/upload":
            content_length = int(self.headers.get('Content-Length', 0))
            max_size = 5 * 1024 * 1024

            if content_length > max_size:
                logging.warning("Помилка: файл перевищує 5 МБ.")
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                message = "<h1>Помилка 400</h1><p>Файл занадто великий! Максимум 5 МБ.</p>"
                self.wfile.write(message.encode("utf-8"))
                return

            body = self.rfile.read(content_length)

            headers_raw = f"Content-Type: {self.headers.get('Content-Type')}\r\n\r\n".encode('iso-8859-1')
            msg = BytesParser().parsebytes(headers_raw + body)

            for part in msg.walk():
                if part.is_multipart() or not part.get_filename():
                    continue

                filename = part.get_filename()
                ext = os.path.splitext(filename)[1].lower()

                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                if ext not in allowed_extensions:
                    logging.warning(f"Помилка: непідтримуваний формат файлу ({filename}).")
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    message = "<h1>Помилка 400</h1><p>Непідтримуваний формат файлу!</p>"
                    self.wfile.write(message.encode("utf-8"))
                    return

                unique_name = f"{uuid.uuid4()}{ext}"
                save_path = os.path.join('images', unique_name)

                file_data = part.get_payload(decode=True)
                with open(save_path, 'wb') as f:
                    f.write(file_data)

                file_size = len(file_data)
                try:
                    conn = psycopg2.connect(
                        dbname="images_db",
                        user="postgres",
                        password="password",
                        host="db",
                        port="5432"
                    )
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO images (filename, original_name, size, file_type)
                        VALUES (%s, %s, %s, %s);
                    """, (unique_name, filename, file_size, ext))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logging.info(f"Успіх: метадані файлу {unique_name} збережено в БД.")
                except Exception as e:
                    logging.error(f"Помилка запису в БД: {e}")
                    if os.path.exists(save_path):
                        os.remove(save_path)

                    self.send_response(500)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("<h1>Помилка 500</h1><p>Помилка збереження в базу даних.</p>".encode("utf-8"))
                    return

                logging.info(f"Успіх: зображення {unique_name} завантажено.")

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()

                response_data = f'{{"url": "/images/{unique_name}"}}'
                self.wfile.write(response_data.encode("utf-8"))
                return

            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("<h1>Помилка 400</h1><p>Файл не знайдено в запиті.</p>".encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def init_db():
    try:
        conn = psycopg2.connect(
            dbname="images_db",
            user="postgres",
            password="password",
            host="db",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                size INTEGER NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_type TEXT NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("База даних успішно ініціалізована")
    except Exception as e:
        print(f"Помилка підключення до БД: {e}")


if __name__ == "__main__":
    init_db()
    httpd = HTTPServer(('0.0.0.0', 8000), MyHTTPRequestHandler)
    print("Server running on port 8000...")
    httpd.serve_forever()