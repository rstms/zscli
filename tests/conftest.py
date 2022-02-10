import os

import pytest

from zscli.cli import API

DEBUG = True
TEST_LIMIT = 10
TEST_PAGE = 1
VERBOSE = False


@pytest.fixture()
def api_key():
    return os.environ["ZEROSSL_API_KEY"]


@pytest.fixture()
def test_api(api_key):
    return API(DEBUG, api_key, TEST_LIMIT, TEST_PAGE, VERBOSE)
