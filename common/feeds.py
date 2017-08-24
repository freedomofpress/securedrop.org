from django.utils.feedgenerator import Rss201rev2Feed


class MRSSFeed(Rss201rev2Feed):
    "Use Yahoo!'s MRSS spec to add thumbnail images to posts"

    def rss_attributes(self):
        attrs = super(MRSSFeed, self).rss_attributes()
        attrs['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super(MRSSFeed, self).add_item_elements(handler, item)
        if 'teaser_image' in item:
            handler.addQuickElement(
                'media:thumbnail',
                '',
                {
                    'url': item['teaser_image']['url'],
                    'width': str(item['teaser_image']['width']),
                    'height': str(item['teaser_image']['height']),
                }
            )
