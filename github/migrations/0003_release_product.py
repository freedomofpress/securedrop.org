from django.db import migrations, models


SECUREDROP_REPO = "freedomofpress/securedrop"
SECUREDROP_NAME = "SecureDrop"


def backfill_product(apps, schema_editor):
    Product = apps.get_model("github", "Product")
    Release = apps.get_model("github", "Release")

    if not Release.objects.exists():
        return

    product, _ = Product.objects.get_or_create(
        repo_full_name=SECUREDROP_REPO,
        defaults={
            "name": SECUREDROP_NAME,
        },
    )
    Release.objects.filter(product__isnull=True).update(product=product)


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0002_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="release",
            name="product",
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="releases",
                to="github.product",
            ),
        ),
        migrations.RunPython(backfill_product, migrations.RunPython.noop),
    ]
