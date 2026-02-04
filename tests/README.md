# Tests

Test suite for the YouTube Channel Analysis Platform.

## Running Tests

```bash
# Run all tests
cd backend
python -m pytest ../tests/

# Run specific test file
python -m pytest ../tests/test_api.py

# Run with coverage
python -m pytest ../tests/ --cov=. --cov-report=html
```

## Test Files

- `test_api.py` - API endpoint tests
- `test_backend.py` - Backend service tests
- `test_analysis.py` - Analysis logic tests
- `test_direct.py` - Direct integration tests

## Writing Tests

Use pytest for all tests. Follow existing patterns in test files.
