"""Tests for authentication endpoints."""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication workflows."""
    
    def test_register_new_user(self, client):
        """Test user registration."""
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
    
    def test_register_duplicate_email(self, client):
        """Test registration with existing email fails."""
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
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, client):
        """Test registration with weak password (currently allowed)."""
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
    
    def test_login_valid_credentials(self, client):
        """Test login with valid credentials."""
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
        
        # Note: This might return different status codes depending on fastapi-users configuration
        # Common responses: 200 (with token), 204 (cookie-based), or 202 (pending verification)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_202_ACCEPTED]
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/api/auth/login", data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_logout_endpoint_exists(self, client):
        """Test that logout endpoint exists."""
        response = client.post("/api/auth/logout")
        # Should return 401 for unauthenticated user
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_forgot_password_endpoint(self, client):
        """Test forgot password endpoint."""
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
    
    def test_forgot_password_nonexistent_email(self, client):
        """Test forgot password with nonexistent email."""
        reset_data = {
            "email": "nonexistent@example.com"
        }
        
        response = client.post("/api/auth/forgot-password", json=reset_data)
        # Should still return 202 for security reasons (don't reveal if email exists)
        assert response.status_code == status.HTTP_202_ACCEPTED


class TestAuthWorkflows:
    """Test complete authentication workflows."""
    
    def test_complete_registration_flow(self, client):
        """Test complete user registration workflow."""
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
        """Test password reset workflow."""
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
    
    def test_multiple_login_attempts(self, client):
        """Test multiple failed login attempts."""
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
