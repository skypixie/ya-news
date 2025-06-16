"""
[+]  Главная страница доступна анонимному пользователю.

[+]  Страница отдельной новости доступна анонимному
пользователю.

[+]  Страницы удаления и редактирования комментария
доступны автору комментария.

[+]  При попытке перейти на страницу редактирования
или удаления комментария анонимный пользователь
перенаправляется на страницу авторизации.

[+]  Авторизованный пользователь не может зайти
на страницу редактирования или удаления
чужих комментариев (возвращается ошибка 404).

[+]  Страницы регистрации пользователей, входа в
учётную запись и выхода из неё доступны
анонимным пользователям.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_pk_for_args')),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None)
    )
)
@pytest.mark.django_db  # почему, если доступ к бд не нужен?
def test_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', lf('comment_pk_for_args')),
        ('news:edit', lf('comment_pk_for_args'))
    )
)
def test_availability_for_different_users(
    parametrized_client,
    expected_status,
    name,
    args
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', lf('comment_pk_for_args')),
        ('news:edit', lf('comment_pk_for_args'))
    )
)
def test_reirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
