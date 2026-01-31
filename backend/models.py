from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)
    display_name = fields.CharField(max_length=50)
    role = fields.CharField(max_length=20, default="employee")  # admin, employee
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "users"

class Task(models.Model):
    id = fields.IntField(pk=True)
    batch_id = fields.UUIDField(null=True)  # Valid for batch tasks
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    assignee = fields.ForeignKeyField("models.User", related_name="assigned_tasks")
    creator = fields.ForeignKeyField("models.User", related_name="created_tasks")
    status = fields.CharField(max_length=20, default="pending")  # pending, done
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "tasks"

class Report(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reports")
    week_num = fields.IntField()  # e.g., 202605
    content_done = fields.TextField()
    content_plan = fields.TextField()
    content_issues = fields.TextField()
    submitted_at = fields.DatetimeField(auto_now_add=True)
    is_late = fields.BooleanField(default=False)

    class Meta:
        table = "reports"
        unique_together = (("user", "week_num"),)

class SystemSetting(models.Model):
    key = fields.CharField(max_length=50, pk=True)
    value = fields.CharField(max_length=255)

    class Meta:
        table = "system_settings"
