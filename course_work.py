import requests
import json
from pprint import pprint
from tqdm import tqdm


class VK:
    def __init__(self, vk_access_token, vk_id, ya_token, version='5.131'):
        self.vk_access_token = vk_access_token
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.version = version
        self.params = {
            'access_token': vk_access_token,
            'v': self.version
        }

    def get_users_photos(self, weight=5):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1}
        response = requests.get(url, params={**self.params, **params})
        info = response.json()
        creating_folder(self.ya_token)
        data = data_creation(info)
        data_sorted = data_sorting(data, weight)
        loading_data(data_sorted, self.ya_token)


def loading_data(data_sorted, ya_token):
    data = []
    for data_sorted_key in tqdm(data_sorted, desc='Загрузка файлов', leave=False, ncols=80):
        name = data_sorted_key['file_name']
        size = data_sorted_key['size']
        jpg_url = data_sorted_key['url']
        data.append({
            'file_name': name,
            'size': size
        })
        get_photo = requests.get(jpg_url)
        photo = get_photo.content

        download_request(name, ya_token, photo)

    with open('data.json', 'w') as file:
        json.dump(data, file)

    with open('data.json', encoding='utf-8') as file:
        json_data = json.load(file)
        print('\n Информация по json-файлу: ')
        pprint(json_data)


def creating_folder(token):
    headers = {
        'Authorization': token
    }

    params = {'path': 'VK_profile_photos'}
    requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                 params=params,
                 headers=headers)


def download_request(name, token, photo):
    path = "VK_profile_photos"

    headers = {
        'Authorization': token
    }

    params = {
        'path': f'{path}/{name}'
    }

    response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                            params=params,
                            headers=headers)

    url_for_upload = response.json()['href']
    requests.put(url_for_upload, files={'file': photo})


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


def data_sorting(data, weight=5):
    with open('size_info.json', encoding='utf-8') as file:
        size_info = json.load(file)

    for data_key in data:
        for size_info_key in size_info:
            if data_key['size'] in size_info_key['size']:
                data_key['max_side'] = size_info_key['max_side']

    data_sorted = sorted(data, key=lambda item: item['max_side'], reverse=True)[0:weight]
    return data_sorted


if __name__ == '__main__':
    vk_token = ''
    vk_user_id = ''
    yandex_token = ''
    vk = VK(vk_token, vk_user_id, yandex_token)
    vk.get_users_photos()
