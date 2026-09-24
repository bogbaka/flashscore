from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return Mock(spec=Session)