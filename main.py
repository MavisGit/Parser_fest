import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from proxy_auth import proxies
from time import sleep
import csv
import glob, json
import re


user_agent = UserAgent().random
headers = {"User-Agent": user_agent}
url = "https://www.skiddle.com/cities/"


# Function to create .json address file (one use).
def get_url_festivals_citi():
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")

    body = soup.find("body")

    all_cities_list = body.find("div", class_="span span8 no-title").find_all("a")
    citi_name_url = {}

    for citi in all_cities_list:
        # Last tag <a> leads to a link to contacts, we will remove it.
        if citi is all_cities_list[-1]:
            continue
        url_citi = "https://www.skiddle.com/festivals" + citi.get("href")
        name_citi = citi.text.strip()

        citi_name_url[name_citi] = url_citi

    with open("data/citi_url_list.json", "w", encoding="utf-8") as file:
        json.dump(citi_name_url, file, indent=4, ensure_ascii=False)


def get_fest_url():

    with open("data/citi_url_list.json", "r", encoding="utf-8") as file:
        citi_name_url = json.load(file)

    count = 0
    error_citi = []
    separators = [" ", "-", "/", ".", ","]
    for citi_name in citi_name_url:

        print(f"Город ,{citi_name}, в обработке.")
        sleep(2)
        citi_url = citi_name_url[citi_name]

        # Name typing
        file_name = citi_name.lower()
        for sep in separators:
            file_name = file_name.replace(sep, "_")

        response = requests.get(citi_url, headers=headers, proxies=proxies)

        soup = BeautifulSoup(response.text, "lxml")

        festivals_list = soup.find_all("div", class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-4 MuiGrid-grid-md-3")

        if len(festivals_list) == 0:

            error_citi.append(citi_url)
            count += 1
            print("В городе, " + citi_name + ", нет фестивалей (это, пожалуй, странной)." + "\nБыл добавлен в список.")
            print("Осталось городов:", str(len(citi_name_url) - count) + ".\n" + "-"*120)

            continue

        fest_url = []
        for festival in festivals_list:
            festival_url = festival.find("a").get("href")
            fest_url.append(festival_url)

        print("Запись адресов...")
        with open(f"data/fest_url/fest_{file_name}.json", "w", encoding="utf-8") as f:
            json.dump(fest_url, f, indent=4, ensure_ascii=False)

        print("Адреса записаны.")
        count += 1
        print("Осталось городов:", str(len(citi_name_url)-count) + ".\n" + "-"*120)

    with open("data/error_citi.json", "w", encoding="utf") as file:
        json.dump(error_citi, file, indent=4, ensure_ascii=False)
    print("Возможные ошибки записаны. \nКонец записи.")


with open("data/festivals.csv", "w", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Festivale name",
        "Days",
        "Place",
        "URL-address",
    ])

# Update url-list
# get_fest_url()

file_count = 0
files = glob.glob('data/fest_url/*.json')
error_fest = []
for filename in files:
    with open(filename, "r", encoding="utf-8") as file:
        urls_fest = json.load(file)

    print(f"Работа с {filename}.")
    count = 0
    for url in urls_fest:
        sleep(2)
        print("Работа над следующим фестивалем.")

        response = requests.get(url, headers=headers, proxies=proxies)

        soup = BeautifulSoup(response.text, "lxml")

        # Ahtung! Area of large accumulation of "crutches"
        try:
            fest_name = soup.find("h1").text.strip()
            data_container = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2 css-1ik2gjq")
            fest_data = data_container.find_all("span")

        except AttributeError:
            # If data_container is None
            fest_name = "Нет данных"

        else:
            if len(fest_data) >= 3:
                if fest_data[2].text.strip() == "Minimum Age":
                    fest_days = fest_data[0].text.strip()
                    fest_place = fest_data[1].text.strip()
                else:
                    fest_days = (fest_data[0].text + fest_data[1].text).strip()
                    fest_place = fest_data[2].text.strip()

            else:
                fest_days = fest_data[0].text.strip()
                fest_place = fest_data[1].text.strip()


        with open("data/festivals.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerow([
                fest_name,
                fest_days,
                fest_place,
                url,
            ])
        count += 1
        print("Данные о фестивале были успешно записаны. Осталось записать:", str(len(urls_fest) - count))

    file_count += 1
    print(f"Работа с {filename} окончена. Осталось файлов: " + str(len(files)-file_count) + "\n" + "-"*120)

with open("data/error_fest.json", "w", encoding="utf-8") as f:
    json.dump(error_fest, f, indent=4, ensure_ascii=False)
