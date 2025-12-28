import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AuditEvent

@csrf_exempt 
def create_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            log_entry = AuditEvent.objects.create(
                action=data.get('action'),
                details=data.get('details'),
                user_id=data.get('user_id')
            )
            return JsonResponse({"status": "created", "id": log_entry.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def get_all_logs(request):
    logs = AuditEvent.objects.all()[:50]
    data = [{
        'timestamp': l.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
        'action': l.action,
        'details': l.details,
        'user_id': l.user_id
    } for l in logs]
    return JsonResponse(data, safe=False)