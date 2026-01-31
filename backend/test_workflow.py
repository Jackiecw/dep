import pytest
from httpx import AsyncClient
from main import app
from models import User, Task
from tortoise.contrib.test import finalizer, initializer

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module", autouse=True)
def initialize_tests(request):
    initializer(["models"], db_url="sqlite://:memory:")
    request.addfinalizer(finalizer)

@pytest.mark.anyio
async def test_workflow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Login as default admin (created by startup event logic duplicated here for test env)
        # Note: Startup event might not trigger in AsyncClient unless using TestClient with Lifespan, 
        # so we manually create admin for test isolation
        from auth import get_password_hash
        await User.create(
            username="admin",
            password_hash=get_password_hash("admin123"),
            display_name="Administrator",
            role="admin"
        )

        login_response = await ac.post("/token", data={"username": "admin", "password": "admin123"})
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Create a new employee
        create_user_resp = await ac.post("/users", json={
            "username": "employee1",
            "password": "emp123",
            "display_name": "John Doe",
            "role": "employee"
        }, headers=headers)
        assert create_user_resp.status_code == 200
        emp_id = create_user_resp.json()["id"]

        # 3. Create a task for this employee
        task_data = {
            "title": "Test Task",
            "content": "Do something",
            "assignee_ids": [emp_id]
        }
        create_task_resp = await ac.post("/tasks", json=task_data, headers=headers)
        assert create_task_resp.status_code == 200

        # 4. Login as employee
        emp_login_resp = await ac.post("/token", data={"username": "employee1", "password": "emp123"})
        assert emp_login_resp.status_code == 200
        emp_token = emp_login_resp.json()["access_token"]
        emp_headers = {"Authorization": f"Bearer {emp_token}"}

        # 5. Get tasks
        tasks_resp = await ac.get("/tasks", headers=emp_headers)
        assert tasks_resp.status_code == 200
        tasks = tasks_resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Test Task"
        task_id = tasks[0]["id"]

        # 6. Complete task
        update_resp = await ac.put(f"/tasks/{task_id}", json={"status": "done"}, headers=emp_headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "done"
        assert update_resp.json()["completed_at"] is not None
