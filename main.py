import telegram
import os
import random
import requests
from dotenv import load_dotenv
from urllib.parse import urlsplit, unquote


FIRST_COMICS = 1
LAST_COMICS = 2911


def get_file_name(file_link):
    splited_link = urlsplit(file_link)
    file_path = unquote(splited_link.path)
    splited_file_path = os.path.split(file_path)
    file_name = splited_file_path[1]
    return file_name


def download_image(url, path, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    path_template = os.path.join(path, get_file_name(url))
    with open(path_template, 'wb') as file:
        file.write(response.content)


def get_comics_information(url_template):
    response = requests.get(url_template)
    response.raise_for_status()
    comics_information = response.json()
    return comics_information


def main():
    load_dotenv()
    bot = telegram.Bot(token=os.environ['BOT_TG_TOKEN'])
    comics_number = random.randint(FIRST_COMICS, LAST_COMICS)
    url_template = 'https://xkcd.com/{}/info.0.json'.format(comics_number)
    directory_name = 'comics'
    os.makedirs(directory_name, exist_ok=True)
    comics_information = get_comics_information(url_template)
    image_url = comics_information['img']
    author_comment = comics_information['alt']
    file_name = get_file_name(image_url)
    download_image(image_url, directory_name)
    file_path = os.path.join(directory_name, file_name)
    chat_id = bot.get_updates()[-1].message.chat_id
    try:
        with open(file_path, 'rb') as file:
            bot.send_message(chat_id=chat_id, text=f'{author_comment}')
            bot.send_document(chat_id=chat_id, document=file)
    except telegram.error.NetworkError:
        print('Программа завершена')
    finally:
        os.remove(file_path)


if __name__ == '__main__':
    main()