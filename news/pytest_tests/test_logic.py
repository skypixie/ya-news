"""
[+]  Анонимный пользователь не может отправить комментарий.

[+]  Авторизованный пользователь может отправить комментарий.

[+]  Если комментарий содержит запрещённые слова, он не будет опубликован.

[+]  Авторизованный пользователь может редактировать или
удалять свои комментарии.

[+]  Авторизованный пользователь не может редактировать или
удалять чужие комментарии.
"""

import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment


@pytest.mark.django_db
def test_anon_user_cant_send_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse("users:login")
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_send_comment(author_client, news_pk_for_args, form_data):
    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url + '#comments')
    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()

    assert new_comment.text == form_data['text']


def test_comment_has_bad_words(author_client, news_pk_for_args, form_data):
    url = reverse('news:detail', args=news_pk_for_args)
    form_data['text'] = 'ты редиска!!!'
    response = author_client.post(url, data=form_data)

    assertFormError(
        response.context['form'],
        'text',
        errors='Не ругайтесь!'
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    news_pk_for_args,
    comment_pk_for_args,
    form_data,
    comment
):
    url = reverse('news:edit', args=comment_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(
        response,
        reverse('news:detail', args=news_pk_for_args) + '#comments'
    )

    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(
    author_client,
    comment_pk_for_args,
    news_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = author_client.post(url)
    assertRedirects(
        response,
        reverse('news:detail', args=news_pk_for_args) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
    not_author_client,
    news_pk_for_args,
    form_data,
    comment
):
    url = reverse('news:edit', args=news_pk_for_args)
    response = not_author_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_comment(
    not_author_client,
    comment_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
