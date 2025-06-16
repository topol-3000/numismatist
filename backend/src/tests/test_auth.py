"""Tests for authentication endpoints."""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication workflows."""
    
    def test_user_registration(self, client):
        """
        Flow: POST /api/auth/register with valid email and password
        Expected: 201 Created, user created with is_active=True, is_verified=False, no password in response
        """
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123"
        }

        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "password" not in data
    
    def test_registration_duplicate_email(self, client):
        """
        Flow: Register user -> attempt registration with same email
        Expected: First succeeds (201), second fails (400 Bad Request)
        """
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123"
        }
        
        # Register first user
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to register with same email
        response2 = client.post("/api/auth/register", json=user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_registration_invalid_email(self, client):
        """
        Flow: POST /api/auth/register with invalid email format
        Expected: 422 Unprocessable Entity due to email validation failure
        """
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_registration_weak_password(self, client):
        """
        Flow: POST /api/auth/register with very short password ("123")
        Expected: 201 Created (current behavior, TODO: add password strength validation)
        """
        user_data = {
            "email": "user@example.com",
            "password": "123"  # Short password - currently accepted
        }
        
        response = client.post("/api/auth/register", json=user_data)
        # Note: Current implementation accepts weak passwords
        # TODO: Add password strength validation
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
    
    def test_user_login(self, client):
        """
        Flow: Register user -> login with correct credentials
        Expected: Login succeeds (200/204/202 depending on auth strategy)
        Note: Response varies by fastapi-users configuration (JWT/cookie/bearer auth)
        """
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Try to login
        login_data = {
            "username": user_data["email"],  # fastapi-users uses 'username' field
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        # Note: Response codes vary by fastapi-users auth strategy configuration
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_202_ACCEPTED]
    
    def test_login_invalid_credentials(self, client):
        """
        Flow: POST /api/auth/login with non-existent email and wrong password
        Expected: 400 Bad Request (doesn't reveal if email exists for security)
        """
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_missing_credentials(self, client):
        """
        Flow: POST /api/auth/login with empty request body
        Expected: 422 Unprocessable Entity due to missing required fields
        """
        response = client.post("/api/auth/login", data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_logout_authentication_required(self, client):
        """
        Flow: POST /api/auth/logout without authentication
        Expected: 401 Unauthorized (endpoint exists but requires valid session)
        """
        response = client.post("/api/auth/logout")
        # Should return 401 for unauthenticated user
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_password_reset_existing_user(self, client):
        """
        Flow: Register user -> request password reset for that email
        Expected: 202 Accepted (reset process initiated, email would be sent)
        """
        # First register a user
        user_data = {
            "email": "forgot@example.com",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Request password reset
        reset_data = {
            "email": user_data["email"]
        }
        
        response = client.post("/api/auth/forgot-password", json=reset_data)
        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_password_reset_nonexistent_user(self, client):
        """
        Flow: POST /api/auth/forgot-password with non-existent email
        Expected: 202 Accepted (same as valid email to prevent email enumeration attacks)
        """
        reset_data = {
            "email": "nonexistent@example.com"
        }
        
        response = client.post("/api/auth/forgot-password", json=reset_data)
        # Should still return 202 for security reasons (don't reveal if email exists)
        assert response.status_code == status.HTTP_202_ACCEPTED


class TestAuthWorkflows:
    """Test complete authentication workflows and user journeys."""
    
    def test_registration_login_workflow(self, client):
        """
        Flow: Register new user -> attempt login with same credentials
        Expected: Registration succeeds (201), login may succeed or require verification (200/204/400)
        """
        # Step 1: Register new user
        user_data = {
            "email": "workflow@example.com",
            "password": "securepassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["is_active"] is True
        assert user["is_verified"] is False  # Usually requires email verification
        
        # Step 2: Attempt login (might require verification first)
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/auth/login", data=login_data)
        # Depending on configuration, this might succeed or require verification
        assert login_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_400_BAD_REQUEST  # If verification required
        ]
    
    def test_password_reset_workflow(self, client):
        """
        Flow: Register user -> request password reset
        Expected: Both steps succeed (201, 202). Full reset requires email token handling (not tested)
        """
        # Step 1: Register user
        user_data = {
            "email": "reset@example.com",
            "password": "originalpassword123"
        }
        
        client.post("/api/auth/register", json=user_data)
        
        # Step 2: Request password reset
        reset_request = {
            "email": user_data["email"]
        }
        
        response = client.post("/api/auth/forgot-password", json=reset_request)
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        # Note: In a real test, you'd need to extract the reset token from email
        # and test the actual password reset endpoint with the token
    
    def test_multiple_failed_logins(self, client):
        """
        Flow: Register user -> 3 failed login attempts -> successful login
        Expected: All failed attempts return 400, final correct attempt succeeds
        Note: No account lockout implemented (current behavior)
        """
        # Register user
        user_data = {
            "email": "multiple@example.com",
            "password": "correctpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Try multiple wrong passwords
        for i in range(3):
            login_data = {
                "username": user_data["email"],
                "password": f"wrongpassword{i}"
            }
            
            response = client.post("/api/auth/login", data=login_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Finally try correct password
        correct_login = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/login", data=correct_login)
        # Should still work (unless account is locked after failed attempts)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
