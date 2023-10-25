from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


URLS = ('news:edit', 'news:delete')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:home', None),
        ('news:detail', (pytest.lazy_fixture('id_news_for_args')))
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize('name', URLS,)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', URLS,)
def test_redirects(client, name, id_comment_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=id_comment_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
