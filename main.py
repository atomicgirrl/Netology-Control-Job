from my_token import TOKEN_VK
# from my_token import TOKEN_YA
import requests
from pprint import pprint
import time
import yadisk
import json
from progress.bar import PixelBar
 #ведите id vk
vk_id = input(str('Введите id пользователя VK '))
TOKEN_YA = input('Введите токен')

class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token):
        self.params = {'access_token': token,
                       'v': '5.131'}

    def get_followers(self, user_id=vk_id):
        followers_url = self.url + 'users.getFollowers'
        followers_params = {
            'count': 1000,
            'user_id': user_id
        }
        req = requests.get(followers_url, params={**self.params, **followers_params}).json()
        return req['response']['item']

    def get_photos(self, vk_id):
        get_photos_url = self.url + 'photos.get'
        photos_get_params = {'owner_id': vk_id,
                             'album_id': 'profile',
                             'extended': 1,
                             'photo_sizes': 1,
                             'rev': 1,
                             'count': 5}
        req = requests.get(get_photos_url,params={**self.params, **photos_get_params}).json()
        return req['response']['items']


    def get_photos_parsed(self, vk_id):
        dict_to_parse = self.get_photos(vk_id)
        dict_to_parse_sorted = sorted(dict_to_parse, key=lambda x: x['likes']['count'])
        parsed_dict = []
        for each_photo in range(len(dict_to_parse_sorted)):
            max_size = 0
            desired_obj = 0
            desired_dimension = 0
            for each_dimension in dict_to_parse_sorted[each_photo]['sizes']:
                photos_area = each_dimension.get('height') * each_dimension.get('width')
                if photos_area > max_size:
                    max_size = photos_area
                    desired_obj = each_photo
                    desired_dimension = each_dimension
            parsed_dict.append(
                {'file_name': dict_to_parse_sorted[desired_obj]['likes']['count'],
                 'size': desired_dimension.get('type'), 'url': desired_dimension.get('url')})
        return parsed_dict
class YaUploader:
    URL_YA = 'https://cloud-api.yandex.net/v1/disk/resources'
    def __init__(self, token):
       self.token=token
       self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def create_folder(self, folder_name:str):
        folder_name = input('Введите имя папки')
        req = requests.put(f'{self.URL_YA}?path={folder_name}', headers={**self.headers})
        URL_YA_Folder = str(f'{self.URL_YA}?path={folder_name}')
        return folder_name

    def upload_file(self, replace=False):
        with open ('parsed_dict.json', 'r', encoding='utf8') as file:
            parsed_dict = json.load(file)
            folder_name = self.create_folder('folder_name')
            url_upload = self.URL_YA + "/upload"
            bar = PixelBar('Countdown', max=len(parsed_dict))
            for each_photo in parsed_dict:
                assert isinstance(each_photo, dict)
                for each_key in each_photo:
                    file_name = str(each_photo.get('file_name')) + '.png'
                    url = each_photo.get('url')
                    y = yadisk.YaDisk(token=TOKEN_YA)
                    path = "folder_name"
                    y.upload_url(url, folder_name + f'/{file_name}')
                    bar.next()
            bar.finish()
            return 'Все файлы загружены/n'



if __name__ == "__main__":
    ya1 = VkUser(TOKEN_VK)
    yatoken = YaUploader(token=TOKEN_YA)
    pprint(ya1.get_photos_parsed(vk_id))
    with open('parsed_dict.json', 'w') as file:
        json.dump(ya1.get_photos_parsed(vk_id), file, indent=4)
    pprint(yatoken.upload_file(replace=False))
