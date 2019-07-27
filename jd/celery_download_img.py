from celery import Celery
from os.path import abspath, dirname
import requests

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'

app = Celery('tasks', broker='amqp://SteveFrancis:333333@118.31.124.58:5672/')  # rabbitmq-server 配置


@app.task
def download(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36'
    }
    link = 'http:' + link
    path = link.split('/')[-1]
    res = requests.session().get(link, headers=headers)
    if res.status_code == 200:
        with open(TEMPLATES_FOLDER + path, 'wb') as f:
            f.write(res.content)
        return True
    return False
