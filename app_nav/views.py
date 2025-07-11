import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.utils.html import format_html

@csrf_exempt
def subscribe_newsletter(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_method'}), content_type='application/json')

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
    except (json.JSONDecodeError, KeyError):
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_email'}), content_type='application/json')

    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
    except ValidationError:
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_email'}), content_type='application/json')

    subject = "🎉 Benvenuto nella Newsletter di CodeCrafter!"
    html_message = format_html("""
        <html>
        <body>
          <h2 style="color:#580000;">Grazie per esserti iscritto!</h2>
          <p>Hai appena ricevuto le ultime novità e promozioni di <strong>CodeCrafter</strong> direttamente nella tua casella.</p>
          <p style="margin-top:20px;">Buona visione e a presto! 🍿</p>
        </body>
        </html>
    """)
    from_email = "CodeCrafter <no-reply@codecrafter.it>"
    try:
        send_mail(
            subject=subject,
            message="",
            from_email=from_email,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        return JsonResponse({'status': 'ok'})
    except BadHeaderError:
        return HttpResponseServerError(json.dumps({'status': 'error'}), content_type='application/json')
    except Exception:
        return HttpResponseServerError(json.dumps({'status': 'error'}), content_type='application/json')

def database_view(request):
    mail = request.session.get('mail', '')
    is_admin = (mail == 'admin@gmail.com')

    return render(request, 'app_database/database.html', {
        'is_admin': is_admin
    })

