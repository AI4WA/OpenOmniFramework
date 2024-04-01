# Generated by Django 4.2.8 on 2024-04-01 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authenticate", "0004_init"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("org_admin", "ORG Admin"),
                    ("org_editor", "Org Editor"),
                    ("org_viewer", "Org Viewer"),
                ],
                default="org_admin",
                max_length=100,
            ),
        ),
    ]