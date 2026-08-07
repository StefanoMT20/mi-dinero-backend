from rest_framework import serializers

from .models import ClothingItem, NailService


class PhotoUrlMixin(serializers.ModelSerializer):
    """Expone `photo_url` como URL absoluta."""

    photo_url = serializers.SerializerMethodField()

    def get_photo_url(self, obj):
        if not obj.photo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url


class NailServiceSerializer(PhotoUrlMixin):
    class Meta:
        model = NailService
        fields = [
            'id',
            'client_name',
            'service_type',
            'price',
            'cost',
            'date',
            'notes',
            'photo',
            'photo_url',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'photo': {'write_only': True}}


class ClothingItemSerializer(PhotoUrlMixin):
    class Meta:
        model = ClothingItem
        fields = [
            'id',
            'name',
            'category',
            'size',
            'purchase_price',
            'sale_price',
            'status',
            'purchase_date',
            'sale_date',
            'buyer_name',
            'notes',
            'photo',
            'photo_url',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'photo': {'write_only': True}}
