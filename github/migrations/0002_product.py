from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "repo_full_name",
                    models.CharField(
                        help_text='GitHub repo owner/name, e.g. "freedomofpress/securedrop".',
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "show_releases",
                    models.BooleanField(
                        default=True,
                        help_text="Show this product's latest release on the homepage and news pages.",
                    ),
                ),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["sort_order", "name"],
            },
        ),
    ]
