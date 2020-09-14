from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField

from directory.models.entry import DirectoryEntry


class DirectoryEntrySerializer(serializers.ModelSerializer):
    organization_logo = ImageRenditionField('max-1500x1500')
    directory_url = serializers.CharField(source='full_url')
    languages = serializers.SlugRelatedField(
        slug_field='title',
        read_only=True,
        many=True
    )
    topics = serializers.SlugRelatedField(
        slug_field='title',
        read_only=True,
        many=True
    )
    countries = serializers.SlugRelatedField(
        slug_field='title',
        read_only=True,
        many=True
    )

    class Meta:
        model = DirectoryEntry
        fields = [
            'title',
            'slug',
            'directory_url',
            'first_published_at',
            'landing_page_url',
            'onion_address',
            'organization_logo',
            'organization_description',
            'organization_url',
            'languages',
            'topics',
            'countries',
        ]
