# Reference: https://github.com/instana/robot-shop/tree/master/load-gen

import random
from load_data import ALL_ARTICLES
import uuid

from locust import HttpUser, task, between
from random import choice


class UserBehavior(HttpUser):
    wait_time = between(2, 5)

    # source: https://tools.tracemyip.org/search--ip/list
    fake_ip_addresses = [
        # white house
        "156.33.241.5",
        # Hollywood
        "34.196.93.245",
        # Chicago
        "98.142.103.241",
        # Los Angeles
        "192.241.230.151",
        # Berlin
        "46.114.35.116",
        # Singapore
        "52.77.99.130",
        # Sydney
        "60.242.161.215"
    ]

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        print('Starting')

    @task
    def healthcheck(self):
        fake_ip = random.choice(self.fake_ip_addresses)

        self.client.get('/', headers={'x-forwarded-for': fake_ip})

    @task
    def read_articles(self):
        fake_ip = random.choice(self.fake_ip_addresses)

        articles = self.client.get('/articles', headers={'x-forwarded-for': fake_ip}).json()

        for _ in range(3):
            article_to_read = choice(articles)['Id']
            self.client.get(f'/article/{article_to_read}', headers={'x-forwarded-for': fake_ip})

    @task
    def create_article(self):
        fake_ip = random.choice(self.fake_ip_addresses)

        article_to_write = choice(ALL_ARTICLES)
        self.client.post('/article', json={**article_to_write, "Id": str(uuid.uuid4())}, headers={'x-forwarded-for': fake_ip})

    @task
    def delete_article(self):
        fake_ip = random.choice(self.fake_ip_addresses)
        articles = self.client.get('/articles', headers={'x-forwarded-for': fake_ip}).json()
        if len(articles) != 0:
            article_to_delete = choice(articles)['Id']
            self.client.delete(f'/article/{article_to_delete}', headers={'x-forwarded-for': fake_ip})
