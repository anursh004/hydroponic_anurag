"""Tests for authentication service."""
import pytest
import pytest_asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.exceptions import BadRequestException, UnauthorizedException, ConflictException
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password(self):
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = get_password_hash("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # bcrypt generates different hashes each time (different salt)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        token = create_access_token(data={"sub": "user@test.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        token = create_refresh_token(data={"sub": "user@test.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_and_refresh_tokens_are_different(self):
        data = {"sub": "user@test.com"}
        access = create_access_token(data=data)
        refresh = create_refresh_token(data=data)
        assert access != refresh


class TestAuthService:
    """Test AuthService methods."""

    @pytest.mark.asyncio
    async def test_register_user(self, db_session, sample_role):
        service = AuthService(db_session)
        data = RegisterRequest(
            email="newuser@example.com",
            password="ValidPass123!",
            full_name="New User",
        )
        user = await service.register(data)
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.hashed_password != "ValidPass123!"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, sample_user, sample_role):
        service = AuthService(db_session)
        data = RegisterRequest(
            email="test@example.com",  # Same as sample_user
            password="ValidPass123!",
            full_name="Duplicate User",
        )
        with pytest.raises(ConflictException):
            await service.register(data)

    @pytest.mark.asyncio
    async def test_login_success(self, db_session, sample_user, sample_role):
        service = AuthService(db_session)
        data = LoginRequest(email="test@example.com", password="TestPass123!")
        tokens = await service.login(data)
        assert "access_token" in tokens or hasattr(tokens, "access_token")

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, db_session, sample_user, sample_role):
        service = AuthService(db_session)
        data = LoginRequest(email="test@example.com", password="WrongPass123!")
        with pytest.raises(UnauthorizedException):
            await service.login(data)

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, db_session, sample_role):
        service = AuthService(db_session)
        data = LoginRequest(email="nonexistent@example.com", password="SomePass123!")
        with pytest.raises(UnauthorizedException):
            await service.login(data)

    @pytest.mark.asyncio
    async def test_change_password(self, db_session, sample_user, sample_role):
        service = AuthService(db_session)
        data = ChangePasswordRequest(
            current_password="TestPass123!",
            new_password="NewSecurePass456!",
        )
        await service.change_password(sample_user.id, data)
        # Verify new password works
        assert verify_password("NewSecurePass456!", sample_user.hashed_password)

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, db_session, sample_user, sample_role):
        service = AuthService(db_session)
        data = ChangePasswordRequest(
            current_password="WrongCurrent!",
            new_password="NewPass456!",
        )
        with pytest.raises(BadRequestException):
            await service.change_password(sample_user.id, data)
