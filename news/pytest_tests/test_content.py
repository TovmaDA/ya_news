import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, all_news):
    response = client.get(reverse('news:home'))
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    response = client.get(reverse('news:home'))
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, all_comment, news, id_news_for_args):
    detail_url = reverse('news:detail', args=id_news_for_args)
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    #all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in news.comment_set.all()]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_news_for_args):
    response = client.get(reverse('news:detail', args=id_news_for_args))
    assert 'form' not in response.context


def test_authorized_client_has_author(author_client, id_news_for_args):
    response = author_client.get(reverse('news:detail', args=id_news_for_args))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
