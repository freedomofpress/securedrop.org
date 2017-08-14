from wagtailmetadata.models import MetadataPageMixin as OriginalMetadataPageMixin


class MetadataPageMixin(OriginalMetadataPageMixin):
    "Provide defaults for metadate for pages in this application"

    def _get_ssssettings(self):
        # Imported here to avoid circular dependency
        from common.models.settings import SocialSharingSEOSettings
        return SocialSharingSEOSettings.for_site(self.get_site())

    def get_meta_description(self):
        """
        Return either the search_description set on the page or the
        default description set for the site
        """

        if self.search_description:
            return self.search_description

        ssssettings = self._get_ssssettings()
        return ssssettings.default_description

    def get_meta_image(self):
        """
        Return either the search_image set on the page or the
        default image set for the site
        """

        if self.search_image:
            return self.search_image

        ssssettings = self._get_ssssettings()
        return ssssettings.default_image

    class Meta:
        abstract = True
