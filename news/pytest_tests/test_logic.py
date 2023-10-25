from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment



@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    client.post(reverse('news:detail', args=(news.id,)), data=form_data)
    assert Comment.objects.count() == 0


def test_author_user_cant_create_comment(
        author_client,
        author,
        news,
        form_data
):
    author_client.post(reverse('news:detail', args=(news.id,)), data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news.id == news.id


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(reverse('news:detail', args=(news.id,)), data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news, author):
    author_client.post(
        reverse(
            'news:edit',
            args=(comment.id,)
        ),
        data=form_data
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_other_user_cant_edit_comment(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, id_comment_for_args):
    url = reverse('news:delete', args=id_comment_for_args)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, id_comment_for_args):
    url = reverse('news:delete', args=id_comment_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
