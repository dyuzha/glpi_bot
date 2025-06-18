# glpi_bot/glpi/tests/test_base.py

import pytest
from unittest.mock import Mock, patch
from glpi_bot.glpi.base import GLPIBase, GLPIAPIError, GLPIUnauthorizedError
from glpi_bot.glpi.session import GLPISessionManager


@pytest.fixture
def mock_session_manager():
    manager = Mock(spec=GLPISessionManager)
    manager.url = "http://glpi.example.com"
    manager._session_token = "test_token"
    manager._app_token = "app_token"
    return manager


@pytest.fixture
def glpi_base(mock_session_manager):
    return GLPIBase(mock_session_manager)


def test_initialization(mock_session_manager):
    base = GLPIBase(mock_session_manager)
    assert base.session_manager == mock_session_manager

def test_make_request_success(glpi_base):
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.text = '{"success": true}
        mock_request.return_value = mock_response

        result = glpi_base._make_request('GET', 'ticket')
        assert result == {"success": True}

def test_make_request_204(glpi_base):
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_request.return_value = mock_response

        result = glpi_base._make_request('DELETE', 'ticket/1')
        assert result is None

def test_make_request_unauthorized():
    manager = Mock(spec=GLPISessionManager)
    manager._session_token = None
    base = GLPIBase(manager)

    with pytest.raises(GLPIUnauthorizedError):
        base._make_request('GET', 'ticket')

def test_make_request_api_error(glpi_base):
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.text = '{"error": "Not found"}'
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with pytest.raises(GLPIAPIError) as excinfo:
            glpi_base._make_request('GET', 'nonexistent')
        assert "HTTP Error 404" in str(excinfo.value)

def test_get_method(glpi_base):
    with patch.object(glpi_base, '_make_request') as mock_make_request:
        mock_make_request.return_value = {"id": 1}
        result = glpi_base.get('ticket/1')
        mock_make_request.assert_called_once_with('GET', 'ticket/1', params=None, headers=None, timeout=10)
        assert result == {"id": 1}

def test_post_method(glpi_base):
    with patch.object(glpi_base, '_make_request') as mock_make_request:
        test_data = {"name": "Test Ticket"}
        mock_make_request.return_value = {"id": 2}
        result = glpi_base.post('ticket', test_data)
        mock_make_request.assert_called_once_with(
            'POST', 'ticket', json_data=test_data, headers={'Content-Type': 'application/json'}, timeout=10
        )
        assert result == {"id": 2}
