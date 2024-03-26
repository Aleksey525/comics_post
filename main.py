import telegram
import os
import random
import requests
from dotenv import load_dotenv
from urllib.parse import urlsplit, unquote


def get_file_name(file_link):
    splited_link = urlsplit(file_link)
    file_path = unquote(splited_link.path)
    splited_file_path = os.path.split(file_path)
    file_name = splited_file_path[1]
    return file_name


def image_download_with_params(url, path, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    os.makedirs(path, exist_ok=True)
    path_template = f'{path}/{get_file_name(url)}'
    with open(path_template, 'wb') as file:
        file.write(response.content)


def main():
    number = random.randint(1, 2911)
    url_template = 'https://xkcd.com/{}/info.0.json'.format(number)
    directory_name = 'comics'
    response = requests.get(url_template)
    response.raise_for_status()
    image_url = response.json()['img']
    author_comment = response.json()['alt']
    file_name = get_file_name(image_url)
    image_download_with_params(image_url, directory_name)
    file_path = f'{directory_name}\{file_name}'
    load_dotenv()
    bot = telegram.Bot(token=os.environ['BOT_TOKEN'])
    chat_id = bot.get_updates()[-1].message.chat_id
    try:
        with open(file_path, 'rb') as file:
            bot.send_message(chat_id=chat_id, text=f'{author_comment}')
            bot.send_document(chat_id=chat_id, document=file)
        os.remove(file_path)
    except telegram.error.NetworkError:
        print('Программа завершена')
    except OSError:
        print('Файл не найден')


if __name__ == '__main__':
    main()