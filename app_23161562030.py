import requests
from bs4 import BeautifulSoup
import mysql.connector
import logging


logging.basicConfig(
    filename="scraper.log",  
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Program dimulai.")

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
    )
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS dbwidiya")
    cursor.close()
    db.close()
    logging.info("Database 'dbwidiya' berhasil dibuat atau sudah ada.")
except Exception as e:
    logging.error(f"Error saat membuat database: {e}")

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dbwidiya"
    )
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) UNIQUE,
            title TEXT,
            paragraph TEXT
        )
    """)
    db.commit()
    logging.info("Tabel 'pages' berhasil dibuat atau sudah ada.")
except Exception as e:
    logging.error(f"Error saat membuat tabel: {e}")

def dfs(url, visited):
    if url in visited:
        logging.debug(f"URL {url} sudah dikunjungi, melewati.")
        return
    visited.add(url)

    try:
        logging.info(f"Mengakses URL: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()  
        
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "No Title"
        paragraph = soup.find("p").text if soup.find("p") else "No Content"

        cursor.execute("INSERT IGNORE INTO pages (url, title, paragraph) VALUES (%s, %s, %s)", (url, title, paragraph))
        db.commit()
        logging.info(f"Berhasil menyimpan {url} ke database.")

        for link in soup.find_all("a", href=True):
            next_url = f"http://localhost:8000/{link['href']}"
            logging.debug(f"Menelusuri tautan: {next_url}")
            dfs(next_url, visited)

    except requests.RequestException as e:
        logging.error(f"Error saat mengakses {url}: {e}")
    except mysql.connector.Error as e:
        logging.error(f"Error database saat menyimpan {url}: {e}")
    except Exception as e:
        logging.error(f"Error umum saat mengakses {url}: {e}")

visited_urls = set()
dfs("http://localhost:8000/index.html", visited_urls)

cursor.close()
db.close()
logging.info("Scraping selesai!")