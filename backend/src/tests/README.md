# Tests Documentation

This directory contains comprehensive tests for the Numismatist API endpoints and workflows.

## Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_auth.py          # Authentication endpoint tests
├── test_items.py         # Items CRUD endpoint tests
├── test_users.py         # User management endpoint tests
└── test_integration.py   # Integration and workflow tests
```

## Running Tests

### Prerequisites

Make sure you have the development environment set up:

```bash
make setup
```

### Run All Tests

```bash
make test
```

### Run Specific Test Categories

```bash
# Authentication tests only
make test-auth
```

### Run Individual Test Files

```bash
# Run specific test file
docker compose --profile tools run --rm numismatist_dev_tools sh -c "cd /app && python -m pytest tests/test_auth.py -v"

# Run specific test class
docker compose --profile tools run --rm numismatist_dev_tools sh -c "cd /app && python -m pytest tests/test_items.py::TestItemsEndpoints -v"

# Run specific test method
docker compose --profile tools run --rm numismatist_dev_tools sh -c "cd /app && python -m pytest tests/test_auth.py::TestAuthEndpoints::test_register_new_user -v"
```

## Test Categories

### Authentication Tests (`test_auth.py`)

Tests for user authentication workflows:
- User registration with valid/invalid data
- Login with correct/incorrect credentials
- Password reset functionality
- Registration to login workflows
- Security validations

**Key Test Classes:**
- `TestAuthEndpoints`: Individual endpoint testing
- `TestAuthWorkflows`: Complete authentication workflows

### Items Tests (`test_items.py`)

Tests for numismatic items CRUD operations:
- Creating items with various data combinations
- Reading user-specific items
- Updating item information
- Deleting items
- User data isolation
- Authorization checks

**Key Test Classes:**
- `TestItemsEndpoints`: CRUD operation testing
- `TestItemsWorkflows`: Item management workflows

### Users Tests (`test_users.py`)

Tests for user management:
- Profile viewing and updating
- User permission boundaries
- Superuser capabilities
- Profile update workflows
- Access control validation

**Key Test Classes:**
- `TestUsersEndpoints`: User management endpoints
- `TestUsersWorkflows`: User management workflows

### Integration Tests (`test_integration.py`)

Tests for complete application workflows:
- End-to-end user journeys
- Multi-user data isolation
- Error handling across endpoints
- Data consistency validation
- Cross-feature interactions

**Key Test Classes:**
- `TestIntegrationWorkflows`: Complete application workflows

## Test Data and Fixtures

The tests use the following fixtures defined in `conftest.py`:

- `test_db_engine`: In-memory SQLite database for fast testing
- `test_session`: Database session for each test
- `client`: FastAPI test client with dependency overrides
- `test_user`: Regular test user
- `test_superuser`: Superuser for admin functionality tests
- `test_item`: Sample item for testing

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test function
- Isolated between tests
- Fast and doesn't require external dependencies
- Automatically cleaned up after tests

## Mocking Strategy

Tests mock the authentication dependency (`current_active_user`) to simulate authenticated users without requiring actual JWT tokens. This allows testing of:
- User-specific data access
- Authorization boundaries
- Multi-user scenarios

## Test Coverage

The test suite covers:

### Endpoints Tested
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset
- `GET /users/me` - Current user profile
- `PATCH /users/me` - Update current user
- `GET /users/{id}` - Get user by ID (superuser)
- `PATCH /users/{id}` - Update user by ID (superuser)
- `GET /items/` - List user items
- `GET /items/{id}` - Get specific item
- `POST /items/` - Create new item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item

### Scenarios Tested
- Valid data handling
- Invalid data validation
- Authentication and authorization
- User data isolation
- Error conditions
- Edge cases
- Complete workflows
- Data consistency

### HTTP Status Codes Validated
- `200 OK` - Successful operations
- `201 Created` - Successful creation
- `204 No Content` - Successful deletion
- `400 Bad Request` - Client errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors

## Best Practices Applied

1. **Test Isolation**: Each test runs with a fresh database
2. **Clear Test Names**: Descriptive test method names
3. **Focused Tests**: Each test validates one specific behavior
4. **Good Coverage**: Both positive and negative test cases
5. **Realistic Data**: Tests use realistic data patterns
6. **Error Testing**: Comprehensive error condition testing
7. **Workflow Testing**: End-to-end scenario validation
8. **Documentation**: Well-documented test purpose and expectations

## Adding New Tests

When adding new endpoints or features:

1. Add endpoint tests to the appropriate test file
2. Create workflow tests for new user journeys
3. Update integration tests for cross-feature interactions
4. Add necessary fixtures to `conftest.py`
5. Update this documentation

Example test structure:
```python
def test_new_feature(self, client, test_user):
    """Test description explaining what is being tested."""
    # Arrange
    setup_data = {...}
    
    # Act
    response = client.post("/endpoint", json=setup_data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == expected_value
```
