import os
import time

import requests

session = requests.Session()
session.headers.update({
})
session.cookies.update({
})

def get_scenarios():
    resp = session.get('https://iot.quasar.yandex.ru/m/user/scenarios')
    resp.raise_for_status()
    return resp.json()


def get_scenario(id):
    resp = session.get(f'https://iot.quasar.yandex.ru/m/v3/user/scenarios/{id}/edit')
    resp.raise_for_status()
    return resp.json()


def put_scenario(id, scenario):
    resp = session.put(f'https://iot.quasar.yandex.ru/m/v3/user/scenarios/{id}', json=scenario, headers={
        'x-csrf-token': os.urandom(40).hex() + ':' + str(int(time.time()))
    })
    return resp.text


if __name__ == '__main__':
    _ = get_scenarios()
