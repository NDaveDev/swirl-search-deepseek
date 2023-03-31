import json
from django.test import TestCase
import swirl_server.settings as settings
import pytest
import logging
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from swirl.processors.transform_query_processor import *
from swirl.processors.utils import str_tok_get_prefixes

logger = logging.getLogger(__name__)

######################################################################
## fixtures

## General and shared

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_suser_pw():
    return 'password'

@pytest.fixture
def test_suser(test_suser_pw):
    return User.objects.create_user(
        username='admin',
        password=test_suser_pw,
        is_staff=True,  # Set to True if your view requires a staff user
        is_superuser=True,  # Set to True if your view requires a superuser
    )

## Test data
@pytest.fixture
def qrx_record_1():
    return {
        "name": "xxx",
        "shared": True,
        "qrx_type": "rewrite",
        "config_content": "# This is a test\n# column1, colum2\nmobiles; ombile; mo bile, mobile\ncheapest smartphones, cheap smartphone"
}

@pytest.fixture
def qrx_synonym():
    return {
        "name": "synonym 1",
        "shared": True,
        "qrx_type": "synonym",
        "config_content": "# column1, column2\nnotebook, laptop\nlaptop, personal computer\npc, personal computer\npersonal computer, pc"
}

@pytest.fixture
def qrx_synonym_bag():
    return {
        "name": "bag 1",
        "shared": True,
        "qrx_type": "bag",
        "config_content": "# column1....columnN\nnotebook, personal computer, laptop, pc\ncar,automobile, ride"
}

@pytest.fixture
def noop_query_string():
    return "noop"


######################################################################
## tests
######################################################################

@pytest.fixture
def prefix_toks_test_cases():
    return [
        ['one'],
        ['one','two'],
        ['one','two', 'three']
    ]

@pytest.fixture
def prefix_toks_test_expected():
    return [
        ['one'],
        ['one two','one','two'],
        ['one two three','one two','one','two three','two','three'],
    ]

@pytest.mark.django_db
def test_utils_prefix_toks(prefix_toks_test_cases, prefix_toks_test_expected):
    assert prefix_toks_test_cases[0] == ['one']
    i = 0
    for c in prefix_toks_test_cases:
        ret = str_tok_get_prefixes(c)
        assert ret == prefix_toks_test_expected[i]
        i = i + 1


@pytest.mark.django_db
def test_query_transform_viewset_crud(api_client, test_suser, test_suser_pw, qrx_record_1):

    is_logged_in = api_client.login(username=test_suser.username, password=test_suser_pw)

    # Check if the login was successful
    assert is_logged_in, 'Client login failed'
    response = api_client.post(reverse('create'),data=qrx_record_1, format='json')

    assert response.status_code == 201, 'Expected HTTP status code 201'
    # Call the viewset
    response = api_client.get(reverse('querytransforms/list'))

    # Check if the response is successful
    assert response.status_code == 200, 'Expected HTTP status code 200'

    # Check if the number of users in the response is correct
    assert len(response.json()) == 1, 'Expected 1 transform'

    # Check if the data is correct
    content = response.json()[0]
    assert content.get('name','') == qrx_record_1.get('name')
    assert content.get('shared','') == qrx_record_1.get('shared')
    assert content.get('qrx_type','') == qrx_record_1.get('qrx_type')
    assert content.get('config_content','') == qrx_record_1.get('config_content')

    # test retrieve
    purl = reverse('retrieve', kwargs={'pk': 1})
    response = api_client.get(purl,  format='json')
    assert response.status_code == 200, 'Expected HTTP status code 201'
    assert len(response.json()) == 8, 'Expected 1 transform'
    content = response.json()
    assert content.get('name','') == qrx_record_1.get('name')
    assert content.get('shared','') == qrx_record_1.get('shared')
    assert content.get('qrx_type','') == qrx_record_1.get('qrx_type')
    assert content.get('config_content','') == qrx_record_1.get('config_content')

    # test update
    qrx_record_1['config_content'] = "# This is an update\n# column1, colum2\nmobiles; ombile; mo bile, mobile\ncheapest smartphones, cheap smartphone"
    purl = reverse('update', kwargs={'pk': 1})
    response = api_client.put(purl, data=qrx_record_1, format='json')
    assert response.status_code == 201, 'Expected HTTP status code 201'
    response = api_client.get(reverse('querytransforms/list'))
    assert response.status_code == 200, 'Expected HTTP status code 200'
    assert len(response.json()) == 1, 'Expected 1 transform'
    content = response.json()[0]
    assert content.get('config_content','') == qrx_record_1.get('config_content')

    # test delete
    purl = reverse('delete', kwargs={'pk': 1})
    response = api_client.delete(purl)
    assert response.status_code == 410, 'Expected HTTP status code 410'

@pytest.mark.django_db
def test_query_trasnform_unique(api_client, test_suser, test_suser_pw, qrx_record_1):

    is_logged_in = api_client.login(username=test_suser.username, password=test_suser_pw)

    # Check if the login was successful
    assert is_logged_in, 'Client login failed'
    response = api_client.post(reverse('create'),data=qrx_record_1, format='json')

    assert response.status_code == 201, 'Expected HTTP status code 201'
    # Call the viewset
    response = api_client.get(reverse('querytransforms/list'))

    # Check if the response is successful
    assert response.status_code == 200, 'Expected HTTP status code 200'

    # Check if the number of users in the response is correct
    assert len(response.json()) == 1, 'Expected 1 transform'

    # Check if the data is correct
    content = response.json()[0]
    assert content.get('name','') == qrx_record_1.get('name')
    assert content.get('shared','') == qrx_record_1.get('shared')
    assert content.get('qrx_type','') == qrx_record_1.get('qrx_type')
    assert content.get('config_content','') == qrx_record_1.get('config_content')

    ## try to create it again
    response = api_client.post(reverse('create'),data=qrx_record_1, format='json')
    assert response.status_code == 400, 'Expected HTTP status code 400'






