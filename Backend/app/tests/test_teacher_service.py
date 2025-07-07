import pytest
from mongomock import MongoClient  # type: ignore
from app.services.teacher_service import MongoTeacherService
from app.models.teacher import TeacherModel
from app.enums.roles import Role  # if you're using Enum for roles

@pytest.fixture
def mock_db():
    client = MongoClient()
    return client["test_db"]

@pytest.fixture
def teacher_service(mock_db):
    return MongoTeacherService(mock_db)

@pytest.fixture
def input_data():
    return {
        "name": "Mr. Dara",
        "email": "dara@example.com",
        "username": "dara123",
        "password": "secret123",
        "teacher_info": {
            "subjects": ["Math", "Science"]
        }
    }

def test_create_teacher_success(teacher_service, input_data):
    result = teacher_service.create_teacher(input_data)

    # Ensure the result is not None and is a TeacherModel instance
    assert result is not None
    assert isinstance(result, TeacherModel)

    # Check values
    assert result.name == input_data["name"]
    assert result.email == input_data["email"]
    assert result.username == input_data["username"]

    # Check role (based on enum or string)
    assert result.role == Role.TEACHER.value  # if using enum
    # or just: assert result.role == "teacher"

    # Check nested teacher_info
    assert result.teacher_info.subjects == ["Math", "Science"]