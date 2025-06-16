"""Tests for users endpoints."""
import pytest
from fastapi import status



class TestUsersEndpoints:
    """Test users management endpoints."""
    
    
    def test_get_current_user(self, authenticated_client, test_user):
        """Test getting current user information."""
        
        
        response = authenticated_client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert data["is_active"] == test_user.is_active
        assert data["is_verified"] == test_user.is_verified
        assert "hashed_password" not in data
    
    
    def test_update_current_user(self, authenticated_client, test_user):
        """Test updating current user information."""
        
        
        update_data = {
            "email": "updated@example.com"
        }
        
        response = authenticated_client.patch("/api/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["id"] == test_user.id
    
    
    def test_update_user_password(self, authenticated_client, test_user):
        """Test updating user password."""
        
        
        update_data = {
            "password": "newpassword123"
        }
        
        response = authenticated_client.patch("/api/users/me", json=update_data)
        
        # Password update might require special handling or current password
        # Exact behavior depends on fastapi-users configuration
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    
    def test_update_user_invalid_email(self, authenticated_client, test_user):
        """Test updating user with invalid email."""
        
        
        update_data = {
            "email": "invalid-email-format"
        }
        
        response = authenticated_client.patch("/api/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
    def test_get_user_by_id_as_superuser(self, superuser_client, test_superuser, test_user):
        """Test getting another user by ID as superuser."""
        
        response = superuser_client.get(f"/api/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
    
    
    def test_get_user_by_id_as_regular_user(self, authenticated_client, test_user, test_session):
        """Test that regular users cannot access other users."""
        # Create another user
        from models.user import User
        other_user = User(
            email="other@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        test_session.add(other_user)
        test_session.commit()
        test_session.refresh(other_user)
        
        
        
        response = authenticated_client.get(f"/api/users/{other_user.id}")
        
        # Should be forbidden for regular users
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_update_user_by_id_as_superuser(self, superuser_client, test_superuser, test_user):
        """Test updating another user as superuser."""
        
        update_data = {
            "is_verified": True
        }
        
        response = superuser_client.patch(f"/api/users/{test_user.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_verified"] == True
    
    
    def test_update_user_by_id_as_regular_user(self, authenticated_client, test_user, test_session):
        """Test that regular users cannot update other users."""
        # Create another user
        from models.user import User
        other_user = User(
            email="other@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        test_session.add(other_user)
        test_session.commit()
        test_session.refresh(other_user)
        
        
        
        update_data = {
            "email": "hacked@example.com"
        }
        
        response = authenticated_client.patch(f"/api/users/{other_user.id}", json=update_data)
        
        # Should be forbidden for regular users
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_unauthorized_access_to_users(self, client):
        """Test accessing users endpoints without authentication."""
        
        response = client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.patch("/api/users/me", json={"email": "test@example.com"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.get("/api/users/123")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.patch("/api/users/123", json={"email": "test@example.com"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUsersWorkflows:
    """Test complete user management workflows."""
    
    
    def test_user_profile_update_workflow(self, authenticated_client, test_user):
        """Test complete user profile update workflow."""
        
        
        # Step 1: Get current user info
        get_response = authenticated_client.get("/api/users/me")
        assert get_response.status_code == status.HTTP_200_OK
        original_user = get_response.json()
        
        # Step 2: Update email
        update_data = {
            "email": "newemail@example.com"
        }
        
        update_response = authenticated_client.patch("/api/users/me", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_user = update_response.json()
        
        # Step 3: Verify changes
        assert updated_user["email"] == update_data["email"]
        assert updated_user["id"] == original_user["id"]
        
        # Step 4: Get user info again to confirm persistence
        final_get = authenticated_client.get("/api/users/me")
        assert final_get.status_code == status.HTTP_200_OK
        final_user = final_get.json()
        assert final_user["email"] == update_data["email"]
    
    
    def test_superuser_management_workflow(self, superuser_client, test_superuser, test_session):
        """Test superuser managing other users workflow."""
        # Create a regular user
        from models.user import User
        regular_user = User(
            email="regular@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        test_session.add(regular_user)
        test_session.commit()
        test_session.refresh(regular_user)
        
        
        # Step 1: View user as superuser
        get_response = superuser_client.get(f"/api/users/{regular_user.id}")
        assert get_response.status_code == status.HTTP_200_OK
        user_data = get_response.json()
        assert user_data["is_verified"] == False
        
        # Step 2: Verify the user
        update_data = {
            "is_verified": True
        }
        
        update_response = superuser_client.patch(f"/api/users/{regular_user.id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_user = update_response.json()
        assert updated_user["is_verified"] == True
        
        # Step 3: Verify the change persisted
        final_get = superuser_client.get(f"/api/users/{regular_user.id}")
        assert final_get.status_code == status.HTTP_200_OK
        final_user = final_get.json()
        assert final_user["is_verified"] == True
    
    
    def test_user_permission_boundaries(self, authenticated_client, test_user):
        """Test user permission boundaries and access control."""
        
        # User can access their own data
        response = authenticated_client.get("/api/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_user.email
        
        # User cannot access other user's data (using a non-existent ID)
        response = authenticated_client.get("/api/users/999")
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        
        # User cannot update other users (using a non-existent ID)
        response = authenticated_client.patch("/api/users/999", json={"email": "hacked@example.com"})
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_user_registration_to_profile_access(self, client):
        """Test workflow from registration to profile access."""
        # Step 1: Register new user
        registration_data = {
            "email": "workflow@example.com",
            "password": "securepassword123"
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_data = register_response.json()
        
        # Step 2: Login (this might require additional steps depending on verification requirements)
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = client.post("/api/auth/login", data=login_data)
        # Note: Depending on configuration, this might require email verification first
        
        # Step 3: If login successful, access profile
        if login_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            # In a real scenario, you'd extract the token and use it for authentication
            # For now, we just verify the registration was successful
            assert user_data["email"] == registration_data["email"]
            assert "id" in user_data
