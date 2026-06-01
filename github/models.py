from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    repo_full_name = models.CharField(
        max_length=255,
        unique=True,
        help_text='GitHub repo owner/name, e.g. "freedomofpress/securedrop".',
    )
    show_releases = models.BooleanField(
        default=True,
        help_text="Show this product's latest release on the homepage and news pages.",
    )
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("repo_full_name"),
        FieldPanel("show_releases"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class ReleaseQuerySet(models.QuerySet):
    def latest_per_visible_product(self):
        return (
            self.filter(product__show_releases=True)
            .order_by("product_id", "-date")
            .distinct("product_id")
            .select_related("product")
        )


@register_snippet
class Release(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="releases",
    )
    url = models.URLField(blank=False, null=False)
    tag_name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    date = models.DateTimeField(blank=False, null=False)

    objects = ReleaseQuerySet.as_manager()

    panels = [
        FieldPanel("product"),
        FieldPanel("url"),
        FieldPanel("tag_name"),
        FieldPanel("date"),
    ]

    def __str__(self):
        return "{} {} released at {} ({})".format(
            self.product if self.product else "(orphaned)",
            self.tag_name,
            self.date,
            self.url,
        )
