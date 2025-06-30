This folder contains tests that specifically check the public API routes (endpoints) of the application using HTTP requests.

Tests here are focused on:
- End-to-end validation of REST API endpoints (CRUD, business flows)
- User authorization and access control for API
- Data returned by API (serialization, filtering, privacy)
- Integration of models and business logic through API

These tests do NOT directly test database models or internal business logic (for that, see other test modules).

Example: test_dealers_api.py covers /api/dealers/ endpoints, including integration with items and transactions.
