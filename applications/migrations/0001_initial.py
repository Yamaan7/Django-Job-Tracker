from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("post_name", models.CharField(max_length=200)),
                ("organization", models.CharField(max_length=200)),
                ("fee_paid", models.IntegerField(default=0)),
                ("date_applied", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Applied", "Applied"),
                            ("Test", "Test"),
                            ("Interview", "Interview"),
                            ("Rejected", "Rejected"),
                            ("Selected", "Selected"),
                        ],
                        default="Applied",
                        max_length=20,
                    ),
                ),
            ],
            options={"ordering": ["-date_applied", "-id"]},
        ),
    ]