import requests
import traceback

def run():
    try:
        with open("scraper/data/raw_images/7328789_5.jpg", "rb") as f:
            res = requests.post(
                "http://localhost:8000/api/detect", 
                files={"file": ("7328789_5.jpg", f, "image/jpeg")}
            )
        with open("err.txt", "w", encoding="utf-8") as f2:
            f2.write(str(res.status_code) + "\n" + str(res.text))
    except Exception as e:
        with open("err.txt", "w", encoding="utf-8") as f2:
            f2.write(str(e) + "\n" + traceback.format_exc())

if __name__ == "__main__":
    run()
