import pytest
from sqlmodel import SQLModel, Session, create_engine
from unittest.mock import MagicMock
from cou_admin.models.country import Country
from common.config import settings
from cou_admin.repositories.country_repository import (
    create_country,
    read_country,
    read_all_countries,
    read_country_by_name,
    search_countries_like,
    update_country,
    delete_country
)
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@pytest.fixture
def mock_session():
    """Fixture to provide a mocked SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def mock_country():
    """Fixture to provide a mock Country object."""
    return Country(id=1, name="Testland", created_by=1, updated_by=1, active=True)


def test_create_country(mock_session, mock_country):
    """Test create_country repository function."""
    # Arrange
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    result = create_country(mock_session, mock_country)

    # Print result for verification
    print(f"Created Country: {result}")

    # Assert
    mock_session.add.assert_called_once_with(mock_country)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_country)
    assert result == mock_country


def test_read_country(mock_session, mock_country):
    """Test read_country repository function."""
    # Arrange
    mock_session.get.return_value = mock_country

    # Act
    result = read_country(mock_session, mock_country.id)

    # Print result for verification
    print(f"Read Country: {result}")

    # Assert
    mock_session.get.assert_called_once_with(Country, mock_country.id)
    assert result == mock_country


def test_update_country(mock_session, mock_country):
    """Test update_country repository function."""
    # Arrange
    mock_session.get.return_value = mock_country
    update_data = {"name": "UpdatedName", "active": False}

    # Act
    result = update_country(mock_session, mock_country.id, update_data)

    # Print updated country for verification
    print(f"Updated Country: {result}")

    # Assert
    mock_session.get.assert_called_once_with(Country, mock_country.id)
    assert mock_country.name == "UpdatedName"
    assert mock_country.active is False
    mock_session.commit.assert_called_once()
    assert result == mock_country


def test_delete_country(mock_session, mock_country):
    """Test delete_country repository function."""
    # Arrange
    mock_session.get.return_value = mock_country
    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    # Act
    result = delete_country(mock_session, mock_country.id)

    # Print deleted country for verification
    print(f"Deleted Country: {result}")

    # Assert
    mock_session.get.assert_called_once_with(Country, mock_country.id)
    mock_session.delete.assert_called_once_with(mock_country)
    mock_session.commit.assert_called_once()
    assert result == mock_country


# @pytest.mark.parametrize("search_query, expected", [
#     ("Test", [Country(id=1, name="Testland", active=True)]),  # Case with results
#     ("NonExistent", []),  # Case with no results
# ])
# def test_search_countries_like(mock_session, search_query, expected):
#     """Test search_countries_like repository function."""
#     # Arrange
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = expected
#     mock_session.execute.return_value = mock_result

#     # Act
#     result = search_countries_like(mock_session, search_query)

#     # Print search query and results for verification
#     print(f"Search Query: '{search_query}', Results: {result}")

#     # Assert
#     mock_session.execute.assert_called_once()
#     assert result == expected
