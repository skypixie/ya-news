"""
[+]  Количество новостей на главной странице — не более 10.
[+]  Новости отсортированы от самой свежей к самой старой.
Свежие новости в начале списка.
[+]  Комментарии на странице отдельной новости отсортированы
от старых к новым: старые в начале списка, новые — в конце.
[+]  Анонимному пользователю не видна форма для отправки комментария
на странице отдельной новости, а авторизованному видна.
"""

from django.urls import reverse
import pytest
from pytest_lazy_fixtures import lf

from news.forms import CommentForm


@pytest.mark.usefixtures('generate_11_news')
@pytest.mark.django_db
def test_news_counter_on_homepage(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.usefixtures('generate_11_news')
@pytest.mark.django_db
def test_news_ordering(client):
    url = reverse('news:home')
    response = client.get(url)
    dates = [news.date for news in response.context['object_list']]
    ordered_dates = sorted(dates, reverse=True)
    assert dates == ordered_dates


@pytest.mark.usefixtures('generate_comments')
@pytest.mark.django_db
def test_comment_ordering(client, news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.get(url)
    comment_dates = [
        comment.created for comment
        in response.context['news'].comment_set.all()
    ]
    ordered_dates = sorted(comment_dates)
    assert comment_dates == ordered_dates


@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (lf('client'), False),
        (lf('not_author_client'), True)
    )
)
def test_different_user_have_comment_form(
    parametrized_client,
    form_on_page,
    news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_on_page
    if form_on_page:
        assert isinstance(response.context['form'], CommentForm)
