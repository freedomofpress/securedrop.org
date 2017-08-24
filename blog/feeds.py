from urllib.parse import urljoin

from django.contrib.syndication.views import Feed

from common.feeds import MRSSFeed


class BlogIndexPageFeed(Feed):
    "A feed for BlogPages that are children of a BlogIndexPage"

    feed_type = MRSSFeed

    def __init__(self, blog_index_page, *args, **kwargs):
        self.blog_index_page = blog_index_page
        super(BlogIndexPageFeed, self).__init__(*args, **kwargs)

    def _get_teaser_image(self, obj):
        if obj.teaser_image:
            return obj.teaser_image.get_rendition('original')

    def _get_categories(self, obj):
        categories = obj.categories.all().select_related('category')
        return [inline.category for inline in categories]

    def _get_complete_url(self, path):
        return urljoin(
            self.blog_index_page.get_site().root_url,
            path
        )

    def title(self):
        return '{}: {}'.format(
            self.blog_index_page.get_site().site_name,
            self.blog_index_page.title
        )

    def link(self):
        return self._get_complete_url(self.blog_index_page.url)

    def description(self):
        return self.blog_index_page.search_description

    def feed_url(self):
        return self._get_complete_url(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage('feed')
        )

    def feed_guid(self):
        return self.feed_url()

    def items(self):
        posts = self.blog_index_page.get_posts()

        if self.blog_index_page.feed_limit != 0:
            return posts[:self.blog_index_page.feed_limit]

        return posts

    def item_title(self, obj):
        return obj.title

    def item_description(self, obj):
        return obj.body.render_as_block()

    def item_link(self, obj):
        return self._get_complete_url(obj.url)

    def item_guid(self, obj):
        return self.item_link(obj)

    item_guid_is_permalink = True

    def item_pubdate(self, obj):
        return obj.first_published_at

    def item_updatedate(self, obj):
        return obj.last_published_at

    def item_extra_kwargs(self, obj):
        image = self._get_teaser_image(obj)
        if image:
            return {
                'teaser_image': {
                    'url': self._get_complete_url(image.url),
                    'width': image.width,
                    'height': image.height,
                }
            }
        return {}
