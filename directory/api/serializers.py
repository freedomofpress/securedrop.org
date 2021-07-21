from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField

from directory.models.entry import DirectoryEntry, ScanResult


class DirectoryEntrySerializer(serializers.ModelSerializer):
    organization_logo = ImageRenditionField('max-1500x1500')
    directory_url = serializers.CharField(source='full_url')
    onion_address = serializers.CharField(source='full_onion_address')
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
    latest_scan = serializers.SerializerMethodField()

    class Meta:
        model = DirectoryEntry
        fields = [
            'title',
            'slug',
            'directory_url',
            'first_published_at',
            'landing_page_url',
            'onion_address',
            'onion_name',
            'organization_logo',
            'organization_description',
            'organization_url',
            'languages',
            'topics',
            'countries',
            'latest_scan',
        ]

    def get_latest_scan(self, directory_entry):
        latest = directory_entry.get_live_result()

        if latest:
            serializer_latest = ScanResultSerializer(instance=latest)
            return serializer_latest.data


class ScanResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanResult
        exclude = (
            'securedrop',
            'id',
            'cross_domain_asset_summary',
            'ignored_cross_domain_assets',
        )
