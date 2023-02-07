import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from datetime import datetime

from news.models import Category, Post


logger = logging.getLogger(__name__)


def news_sender():
    print()
    print()
    print()
    print()
    print('===================================ПРОВЕРКА СЕНДЕРА===================================')
    print()
    print()

    for category in Category.objects.all():
        news_from_each_category = []
        week_number_last = datetime.now().isocalendar()[1]-1

        for post in Post.objects.filter(postCategory_id=category.id,
                                        time_of_creation__week=week_number_last).values('pk',
                                                                                        'title',
                                                                                        'dateCreation',
                                                                                        'postCategory_id__name'):

            date_format = post.get("time_of_creation").strftime("%d/%m/%Y")

            post = (f' http://127.0.0.1:8000/news/{post.get("pk")}, Заголовок: {post.get("title")}, '
                   f'Категория: {post.get("postCategory_id__name")}, Дата создания: {date_format}')

            news_from_each_category.append(post)

        print()
        print('+++++++++++++++++++++++++++++', category.name, '++++++++++++++++++++++++++++++++++++++++++++')
        print()
        print("Письма будут отправлены подписчикам категории:", category.name, '( id:', category.id, ')')

        subscribers = category.subscribers.all()

        print('по следующим адресам email: ')
        for _ in subscribers:
            print(_.email)

        print()
        print()


        for subscriber in subscribers:
            print('____________________________', subscriber.email, '___________________________________')
            print()
            print('Письмо, отправленное по адресу: ', subscriber.email)
            html_content = render_to_string(
                'mail_sender.html', {'user': subscriber,
                                          'text': news_from_each_category,
                                          'category_name': category.name,
                                          'week_number_last': week_number_last})

            msg = EmailMultiAlternatives(
                subject=f'Здравствуй, {subscriber.username}, новые статьи за прошлую неделю в вашем разделе!',
                from_email='mailForSkillfactory@yandex.ru',
                to=[subscriber.email]
            )

            msg.attach_alternative(html_content, 'text/html')
            print()

            print(html_content)

            msg.send()