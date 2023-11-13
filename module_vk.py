import requests
import checking_answers
import json
import module_yandex


class VK:
    def __init__(self, vk_token, vk_id, ya_token, version='5.131'):
        self.vk_access_token = vk_token
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.version = version
        self.params = {
            'access_token': vk_token,
            'v': self.version
        }

    def get_users_photos(self, weight, folder_path):
        host_url = 'api.vk.com'
        host = checking_answers.CheckingAnswers(host_url)
        if not is_number(self.vk_id):
            if host.network_check():
                params_user_id = {'user_id': self.vk_id}
                url_users = f'https://{host_url}/method/users.get'
                response_user_ids = requests.get(url_users, params={**self.params, **params_user_id})
                if response_user_ids.status_code == requests.codes.ok:
                    info_user_ids = response_user_ids.json()
                    for owner_id in info_user_ids['response']:
                        self.vk_id = owner_id['id']
                else:
                    print(f'Внимание: остановлено! Ответ от {url_users} '
                          f'пришел с ошибкой {response_user_ids.status_code}')
                    return
            else:
                print(f'Внимание: остановлено! Не удалось получить данные, {host_url} отсутствует подключение')

        params = {'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1}
        url_photos = f'https://{host_url}/method/photos.get'
        if host.network_check():
            response_photos = requests.get(url_photos, params={**self.params, **params})
            if response_photos.status_code == requests.codes.ok:
                info = response_photos.json()
                print(f'денные от {host_url} получены')
                data = data_creation(info)
                data_sorted = data_sorting(data, weight)
                print('сортировка файлов закончена')
                number_downloaded = len(data_sorted)
                class_yandex = module_yandex.Yandex(self.ya_token, data_sorted, folder_path)
                class_yandex.creating_folder(number_downloaded)
            else:
                print(f'Внимание: остановлено! Ответ от {url_photos} пришел с ошибкой {response_photos.status_code}')
        else:
            print(f'Внимание: остановлено! Не удалось получить данные, {host_url} отсутствует подключение')


def is_number(user):
    try:
        float(user)
        return True
    except ValueError:
        return False


def data_creation(info):
    data = []
    for all_key in info['response']['items']:
        name = f'{all_key["likes"]["count"]}.jpg'
        size = all_key['sizes'][-1]['type']
        jpg_url = all_key['sizes'][-1]['url']

        for double in data:
            if name in double['file_name']:
                name = f'{all_key["likes"]["count"]}_{all_key["date"]}.jpg'

        data.append({
            'file_name': name,
            'size': size,
            'url': jpg_url
        })

    return data


def data_sorting(data, weight):
    with open('size_info.json', encoding='utf-8') as file:
        size_info = json.load(file)

    for data_key in data:
        for size_info_key in size_info:
            if data_key['size'] in size_info_key['size']:
                data_key['max_side'] = size_info_key['max_side']

    data_sorted = sorted(data, key=lambda item: item['max_side'], reverse=True)[0:weight]
    return data_sorted
