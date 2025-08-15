import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from main import app
from cou_course.models.memory_game_pair import MemoryGamePair
from cou_course.models.memory_game import MemoryGame
from cou_course.schemas.memory_game_pair_schema import MemoryGamePairCreate

# Create in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_session():
    with Session(engine) as session:
        yield session

# Override the dependency
app.dependency_overrides = {Session: override_get_session}

@pytest.fixture
def client():
    with TestClient(app) as client:
        # Create tables
        SQLModel.metadata.create_all(engine)
        yield client
        # Clean up
        SQLModel.metadata.drop_all(engine)

@pytest.fixture
def sample_memory_game():
    with Session(engine) as session:
        memory_game = MemoryGame(
            id=1,
            course_id=1,
            title="Test Memory Game",
            description="Test Description",
            created_by=1,
            active=True
        )
        session.add(memory_game)
        session.commit()
        session.refresh(memory_game)
        return memory_game

def test_create_memory_game_pair(client, sample_memory_game):
    """Test creating a memory game pair"""
    memory_game_pair_data = {
        "memory_game_id": 1,
        "term": "Test Term",
        "term_description": "Test Description",
        "pair_order": 1,
        "active": True,
        "created_by": 1
    }
    
    response = client.post("/api/v1/memory-game-pairs/", json=memory_game_pair_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["term"] == "Test Term"
    assert data["term_description"] == "Test Description"
    assert data["memory_game_id"] == 1

def test_get_memory_game_pair(client, sample_memory_game):
    """Test getting a memory game pair by ID"""
    # First create a memory game pair
    memory_game_pair_data = {
        "memory_game_id": 1,
        "term": "Test Term",
        "term_description": "Test Description",
        "pair_order": 1,
        "active": True,
        "created_by": 1
    }
    
    create_response = client.post("/api/v1/memory-game-pairs/", json=memory_game_pair_data)
    assert create_response.status_code == 200
    
    created_data = create_response.json()
    memory_game_pair_id = created_data["id"]
    
    # Now get it by ID
    response = client.get(f"/api/v1/memory-game-pairs/{memory_game_pair_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == memory_game_pair_id
    assert data["term"] == "Test Term"

def test_get_memory_game_pairs_by_game(client, sample_memory_game):
    """Test getting memory game pairs by game ID"""
    # Create multiple memory game pairs
    for i in range(3):
        memory_game_pair_data = {
            "memory_game_id": 1,
            "term": f"Term {i}",
            "term_description": f"Description {i}",
            "pair_order": i,
            "active": True,
            "created_by": 1
        }
        client.post("/api/v1/memory-game-pairs/", json=memory_game_pair_data)
    
    # Get all pairs for the game
    response = client.get("/api/v1/memory-game-pairs/game/1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all(pair["memory_game_id"] == 1 for pair in data) 