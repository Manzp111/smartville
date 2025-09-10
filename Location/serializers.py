from rest_framework import serializers

class LocatePointSerializer(serializers.Serializer):
    latitude = serializers.FloatField(
        required=True,
        min_value=-90.0,
        max_value=90.0,
        help_text="Latitude must be between -90 and 90."
    )
    longitude = serializers.FloatField(
        required=True,
        min_value=-180.0,
        max_value=180.0,
        help_text="Longitude must be between -180 and 180."
    )
