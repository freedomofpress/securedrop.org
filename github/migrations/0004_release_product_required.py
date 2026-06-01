from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0003_release_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="release",
            name="product",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="releases",
                to="github.product",
            ),
        ),
    ]
