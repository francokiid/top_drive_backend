from rest_framework import serializers
from datetime import datetime
from ..models import Classroom, Session

class ClassroomSerializer(serializers.ModelSerializer):
    slots_available = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = ['classroom_code', 'capacity', 'status', 'branch', 'slots_available']

    def get_slots_available(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return obj.capacity

        date = request.query_params.get('date', None)
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)

        if date and start_time:
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            
            if end_time:
                end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            else:
                end_datetime = datetime.strptime(f"{date} 23:59", "%Y-%m-%d %H:%M")

            busy_sessions = Session.objects.filter(
                session_date=start_datetime.date(),
                start_time__lt=end_datetime.time(),
                end_time__gt=start_datetime.time(),
                facility__facility_type='Classroom',
                facility__object_id=obj.classroom_code
            )

            occupied_slots = busy_sessions.count()
            return max(0, obj.capacity - occupied_slots)

        return obj.capacity 