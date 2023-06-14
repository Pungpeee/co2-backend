import coreapi
import pendulum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from analytic.models import SessionLog2
from utils import datetime


class SessionView(APIView):
    permission_classes = [IsAuthenticated]

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("date_start",
                          required=True),
            coreapi.Field("date_end",
                          required=True),
        ]
    )

    def get(self, request, *args, **kwargs):
        date_start = datetime.get_date(request.GET.get('date_start', None))
        date_end = datetime.get_date(request.GET.get('date_end', None))
        if not date_start or not date_end:
            return Response(data={}, status=status.HTTP_400_BAD_REQUEST)

        period = pendulum.period(pendulum.parse(str(date_start), strict=False),
                                 pendulum.parse(str(date_end), strict=False))
        if pendulum.parse(str(date_start)) > pendulum.parse(str(date_end)):
            return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
        if period.years != 0:
            return Response(data={'detail': 'input date out of range'}, status=status.HTTP_400_BAD_REQUEST)

        session_log_list = SessionLog2.objects.filter(
            account=request.user,
            date__range=(date_start, date_end)
        )

        result = []
        session_map = {}
        for session_log in session_log_list:
            date = str(session_log.date)
            if date not in session_map:
                session_map[date] = session_log.count
            else:
                session_map[date] = session_map[date] + session_log.count

        for date in period.range('days'):
            _date = date.to_date_string()
            result.append([
                date.to_date_string(), session_map[_date] if _date in session_map else 0
            ])

        return Response(result, status=status.HTTP_200_OK)
