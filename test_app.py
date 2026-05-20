import pytest
from app import app, random_number, random_word, random_name


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Route tests ───────────────────────────────────────────────────────────────

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok(client):
    data = client.get("/health").get_json()
    assert data["status"] == "ok"


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_has_all_fields(client):
    data = client.get("/").get_json()
    assert "number" in data
    assert "word" in data
    assert "name" in data


# ── Unit tests ────────────────────────────────────────────────────────────────

def test_random_number_is_integer():
    assert isinstance(random_number(), int)


def test_random_number_in_range():
    for _ in range(50):
        n = random_number()
        assert 1 <= n <= 9999


def test_random_word_is_string():
    assert isinstance(random_word(), str)


def test_random_word_length():
    for _ in range(50):
        w = random_word()
        assert 4 <= len(w) <= 8


def test_random_word_is_lowercase_alpha():
    for _ in range(50):
        assert random_word().isalpha()
        assert random_word().islower()


def test_random_name_is_valid():
    valid = {
        "Alice", "Bob", "Charlie", "Diana", "Edward",
        "Fatima", "George", "Hannah", "Ivan", "Julia",
    }
    for _ in range(30):
        assert random_name() in valid
