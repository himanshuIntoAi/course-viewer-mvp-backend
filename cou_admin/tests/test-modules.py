import pytest
from unittest.mock import MagicMock
#from cou_admin.schemas.country_schema import create_country, get_country, update_country, delete_country
from . import (
    create_country,
    read_country,
    update_country,
    delete_country,
)
from . import Country
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

print("test")
# print(dir(cou_admin.schemas.country_schema))
print(dir(cou_admin.repositories.country_repository))
print(dir(cou_admin.models.country))