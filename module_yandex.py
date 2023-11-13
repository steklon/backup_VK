import requests
import checking_answers
import json
from tqdm import tqdm
from pprint import pprint


class Yandex:
    def __init__(self, yandex_token, data, folder_path):
        self.yandex_token = yandex_token
        self.data = data
        self.folder_path = folder_path

    def creating_folder(self, weight):
        host_url = 'cloud-api.yandex.net'
        url = f'https://{host_url}/v1/disk/resources'
        host = checking_answers.CheckingAnswers(host_url)

        headers = {
            'Authorization': f'OAuth {self.yandex_token}'
        }

        params = {'path': self.folder_path}

        if host.network_check():
            response_ok = requests.get(url, params=params, headers=headers)
            if response_ok.status_code == requests.codes.ok:
                print(f'ВНИМАНИЕ!!! Папка "{self.folder_path}" уже существует')
                duplication_check(self.folder_path, self.yandex_token, self.data, weight)
                return
            elif response_ok.status_code == requests.codes.not_found:
                pass
            else:
                print(f'Внимание: остановлено! Ответ от {url} пришел с ошибкой {response_ok.status_code}')

            response = requests.put(url,
                                    params=params,
                                    headers=headers)
            if response.status_code == requests.codes.created:
                print(f'Папка "{self.folder_path}" создана')
                loading_data(self.data, self.yandex_token, self.folder_path)
            else:
                print(f'Внимание: остановлено! Ответ от {url} пришел с ошибкой {response.status_code}')
        else:
            print(f'Внимание: остановлено! Не удалось получить данные, {host_url} отсутствует подключение')


def duplication_check(folder_path, token, data, weight):
    response_to_conflict = input(f'Сохранить данные в "{folder_path}"? Y/N: ')
    while True:
        if response_to_conflict.lower() == 'y':
            loading_data(data, token, folder_path)
            break
        elif response_to_conflict.lower() == 'n':
            folder_path = input('Введите название новой папки: ') or "PhotosVK"
            folder = Yandex(token, data, folder_path)
            folder.creating_folder(weight)
            break
        elif response_to_conflict.lower() != 'y' or 'n':
            response_to_conflict = input(f'Введите "Y" cохранить данные в папку "{folder_path}"\n'
                                         f'или "N" что бы создать другую папку: ')


def loading_data(data_sorted, ya_token, folder_path):
    data = []

    for data_sorted_key in tqdm(data_sorted, desc='Загрузка файлов', leave=False, ncols=80):
        name = data_sorted_key['file_name']
        size = data_sorted_key['size']
        jpg_url = data_sorted_key['url']
        get_photo = requests.get(jpg_url, timeout=0.6)
        if get_photo.status_code == requests.codes.ok:
            photo = get_photo.content
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

            headers = {
                'Authorization': f'OAuth {ya_token}'
            }

            params = {
                'path': f'{folder_path}/{name}'
            }

            response = requests.get(url, params=params, headers=headers)
            if response.status_code == requests.codes.ok:
                data.append({
                    'file_name': name,
                    'size': size
                })
                url_for_upload = response.json()['href']
                requests.put(url_for_upload, files={'file': photo})
            else:
                print(f'\nВнимание: При загрузке в папку "{folder_path}" не удалось загрузить "{name}". '
                      f'\nОтвет от {url} пришел с ошибкой {response.status_code}')
        else:
            print(f'Внимание: остановлено! Ответ от {jpg_url} пришел с ошибкой {get_photo.status_code}')

    with open('data.json', 'w') as file:
        json.dump(data, file)

    with open('data.json', encoding='utf-8') as file:
        json_data = json.load(file)
        print('\n Готово!')
        print(f'Загружено {len(json_data)} фото')
        print('\n Информация по json-файлу: ')
        pprint(json_data)
