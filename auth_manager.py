#!/usr/bin/env python3
"""
MuckRock Authentication Manager
Handles login, token refresh, and session management
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from muckrock import MuckRock
import json

logger = logging.getLogger(__name__)

class MuckRockAuthManager:
    """Manages MuckRock authentication with automatic token refresh."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.getenv("MUCKROCK_USERNAME")
        self.password = password or os.getenv("MUCKROCK_PASSWORD")
        self.client = None
        self.token = None
        self.token_expires_at = None
        self.session_info = {}
        
        # Token refresh settings
        self.token_lifetime = timedelta(hours=2)  # Assume 2-hour token lifetime
        self.refresh_buffer = timedelta(minutes=10)  # Refresh 10 minutes before expiry
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the MuckRock client with credentials."""
        try:
            if self.username and self.password:
                logger.info(f"Initializing authenticated MuckRock client for user: {self.username}")
                self.client = MuckRock(self.username, self.password)
                self.token_expires_at = datetime.now() + self.token_lifetime
                self._update_session_info()
                logger.info("Authentication successful")
            else:
                logger.info("No credentials provided, using anonymous access")
                self.client = MuckRock()
                
        except Exception as e:
            logger.error(f"Failed to initialize MuckRock client: {e}")
            # Fallback to anonymous access
            self.client = MuckRock()
    
    def _update_session_info(self):
        """Update session information after successful login."""
        try:
            # Try to get user info to verify authentication
            if hasattr(self.client, 'user'):
                self.session_info = {
                    "username": self.username,
                    "authenticated": True,
                    "login_time": datetime.now().isoformat(),
                    "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
                }
            else:
                self.session_info = {
                    "username": self.username,
                    "authenticated": True,
                    "login_time": datetime.now().isoformat(),
                    "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
                    "note": "Authentication successful but user info not available via API"
                }
                
        except Exception as e:
            logger.warning(f"Could not retrieve user info: {e}")
            self.session_info = {
                "username": self.username,
                "authenticated": True,
                "login_time": datetime.now().isoformat(),
                "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
                "warning": f"User info retrieval failed: {e}"
            }
    
    def is_token_expired(self) -> bool:
        """Check if the authentication token is expired or will expire soon."""
        if not self.token_expires_at:
            return False
            
        # Check if token will expire within the refresh buffer
        expires_soon = datetime.now() + self.refresh_buffer
        return self.token_expires_at <= expires_soon
    
    def refresh_token(self) -> bool:
        """Refresh the authentication token."""
        if not self.username or not self.password:
            logger.warning("Cannot refresh token: no credentials available")
            return False
        
        try:
            logger.info("Refreshing MuckRock authentication token...")
            
            # Create a new client instance (this effectively refreshes the session)
            self.client = MuckRock(self.username, self.password)
            self.token_expires_at = datetime.now() + self.token_lifetime
            self._update_session_info()
            
            logger.info("Token refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    def ensure_valid_session(self) -> bool:
        """Ensure we have a valid session, refreshing if necessary."""
        if not self.client:
            logger.warning("No client available")
            return False
        
        if not self.username or not self.password:
            # Anonymous access, no token refresh needed
            return True
        
        if self.is_token_expired():
            logger.info("Token expired or expiring soon, refreshing...")
            return self.refresh_token()
        
        return True
    
    def get_client(self) -> MuckRock:
        """Get the MuckRock client, ensuring the session is valid."""
        self.ensure_valid_session()
        return self.client
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        if not self.username or not self.password:
            return {
                "authenticated": False,
                "access_type": "anonymous",
                "limitations": "Limited functionality - filing requests, appeals, and user-specific operations unavailable"
            }
        
        # Update session status
        session_info = self.session_info.copy()
        session_info.update({
            "token_valid": not self.is_token_expired(),
            "time_until_refresh": str(self.token_expires_at - datetime.now()) if self.token_expires_at else "N/A",
            "current_time": datetime.now().isoformat()
        })
        
        return session_info
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test the current authentication status."""
        try:
            client = self.get_client()
            
            # Try to make an authenticated request (get user's requests)
            if self.username and self.password:
                requests = client.requests.list()
                # Try to iterate through first request to test access
                try:
                    first_request = next(iter(requests))
                    return {
                        "status": "success",
                        "authenticated": True,
                        "message": "Authentication verified - can access user requests",
                        "test_request_id": first_request.id,
                        "session_info": self.get_session_info()
                    }
                except StopIteration:
                    return {
                        "status": "success",
                        "authenticated": True,
                        "message": "Authentication verified - no requests found but access confirmed",
                        "session_info": self.get_session_info()
                    }
            else:
                return {
                    "status": "anonymous",
                    "authenticated": False,
                    "message": "Using anonymous access - limited functionality",
                    "session_info": self.get_session_info()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "authenticated": False,
                "message": f"Authentication test failed: {e}",
                "session_info": self.get_session_info()
            }
    
    def logout(self):
        """Clear authentication and reset to anonymous access."""
        logger.info("Logging out and switching to anonymous access")
        self.client = MuckRock()
        self.token = None
        self.token_expires_at = None
        self.session_info = {
            "authenticated": False,
            "logout_time": datetime.now().isoformat()
        }


# Global auth manager instance
auth_manager = MuckRockAuthManager()


def get_authenticated_client() -> MuckRock:
    """Get a MuckRock client with valid authentication."""
    return auth_manager.get_client()


def get_session_status() -> Dict[str, Any]:
    """Get current authentication session status."""
    return auth_manager.get_session_info()


def test_auth() -> Dict[str, Any]:
    """Test current authentication status."""
    return auth_manager.test_authentication()


def refresh_auth() -> bool:
    """Force refresh authentication."""
    return auth_manager.refresh_token()