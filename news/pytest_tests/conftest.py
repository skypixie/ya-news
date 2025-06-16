import pytest
from django.test.client import Client
from datetime import date, timedelta

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def not_author_client(not_author):
    not_author_client = Client()
    not_author_client.force_login(not_author)
    return not_author_client


@pytest.fixture
def news(db):
    news = News.objects.create(
        title='Title',
        text='Text',
    )
    return news


@pytest.fixture
def news_pk_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Text'
    )
    return comment


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.id,)


@pytest.fixture
def generate_11_news():
    """We can test how paginator works with it"""
    news = (News(
        title='Title',
        text='Text',
        date=date.today() + timedelta(days=i)
    ) for i in range(11))
    News.objects.bulk_create(news)


@pytest.fixture
def generate_comments(news, author):
    comments = (Comment(
        news=news,
        author=author,
        text='Text',
        created=date.today() + timedelta(days=i)
    ) for i in range(10))
    Comment.objects.bulk_create(comments)
