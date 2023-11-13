import module_vk


if __name__ == '__main__':
    token_vk = ''
    vk_user_id = input('Введите ID или screen_name пользователя ВК: ') or '30942'
    yandex_token = input('Введите токен Яндекс.Диска: ')
    weight = int(input('Введите число фотографий для загрузки на Яндекс.Диск: ') or "5")
    folder_path = input('Введите название папки: ') or "PhotosVK"
    vk = module_vk.VK(token_vk, vk_user_id, yandex_token)
    vk.get_users_photos(weight, folder_path)
