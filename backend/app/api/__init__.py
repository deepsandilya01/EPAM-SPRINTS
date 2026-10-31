"""
Project: RE:Flow
Sprint: 1
File: backend/app/api/__init__.py

Ownership: Team Maintained
Role: API Package Initialization

Purpose:
API package initializer exposing unified api_bp blueprint.

Status: COMPLETED
"""

from __future__ import annotations

from backend.app.api.router import api_bp

__all__ = ["api_bp"]

