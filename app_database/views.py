import datetime
import json
import os
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.db import connection
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
import math

from CodeCraftersDjango import settings

def get_table_data(request):
    mail = request.session.get('mail', '')
    if mail != 'admin@gmail.com':
        return HttpResponseForbidden('Accesso negato')

    allowed_tables = ['Biglietto', 'Film', 'Proiezione', 'Sala', 'Utente']
    table = request.GET.get('table', '')
    page = max(1, int(request.GET.get('page', '1')))
    per_page = 100
    offset = (page - 1) * per_page

    if table not in allowed_tables:
        return HttpResponseBadRequest('Tabella non valida')

    columns = {
        "Biglietto": ["numProiezione", "numFila", "numPosto", "dataVendita", "prezzo", "email", "id"],
        "Film": ["codice", "titolo", "anno", "durata", "lingua"],
        "Proiezione": ["numProiezione", "sala", "filmProiettato", "data", "ora"],
        "Sala": ["numero", "numPosti", "dim", "numFile", "numPostiPerFila", "tipo"],
        "Utente": ["id", "mail", "password", "nome", "reset_token", "reset_expire"]
    }
    pks = {
        'Biglietto': 'id',
        'Film': 'codice',
        'Proiezione': 'numProiezione',
        'Sala': 'numero',
        'Utente': 'id'
    }

    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM `{table}`')
        total_rows = cursor.fetchone()[0]
        total_pages = max(1, math.ceil(total_rows / per_page))

        cursor.execute(f'SELECT * FROM `{table}` LIMIT %s OFFSET %s', [per_page, offset])
        rows = cursor.fetchall()

        html = f"<h2 class='db-title'>Tabella {table}</h2>"

        if rows:
            html += "<div class='db-table-wrap'><table class='db-table'><tr>"
            for col in columns[table]:
                html += f"<th>{escape(col)}</th>"
            html += "<th></th></tr>"

            for row in rows:
                html += "<tr>"
                row_dict = dict(zip(columns[table], row))
                for col in columns[table]:
                    html += f"<td>{escape(str(row_dict.get(col, '')))}</td>"

                id_value = escape(str(row_dict[pks[table]]))
                if table in ['Biglietto', 'Utente']:
                    html += f"""
                        <td class='delete-cell'>
                            <button class='btn-delete' data-table='{table}' data-id='{id_value}' title='Elimina'>
                                <img src='https://cdn-icons-png.flaticon.com/128/3976/3976961.png' class='delete-icon'>
                            </button>
                        </td>
                    """
                html += f"""
                    <td class='edit-cell'>
                        <button class='btn-edit' data-table='{table}' data-id='{id_value}' title='Modifica'>
                            <img src='https://cdn-icons-png.flaticon.com/128/7175/7175385.png' class='edit-icon'>
                        </button>
                    </td>
                """
                html += "</tr>"

            html += "</table></div>"
        else:
            html += f"<p class='db-nodata'>Nessun dato nella tabella {table}.</p>"

        html += f"""
            <div class='pagination' data-total='{total_pages}'>
              <div class='page-left'>
                {'<button class="page-btn" data-page="' + str(page-1) + '">Prev</button>' if page > 1 else ''}
                <span class='page-info'>Pagina {page} di {total_pages}</span>
                {'<button class="page-btn" data-page="' + str(page+1) + '">Next</button>' if page < total_pages else ''}
              </div>
              <div class='page-right'>
                <label class='page-jump'>
                  <input type='number' class='page-input' min='1' max='{total_pages}' value='{page}' />
                  <button class='page-go'>Go</button>
                </label>
              </div>
            </div>
        """

    return HttpResponse(html)

@csrf_exempt
def delete_row(request):
    mail = request.session.get('mail', '')
    if mail != 'admin@gmail.com':
        return JsonResponse({'success': False, 'message': 'Non autorizzato'})

    table = request.POST.get('table', '')
    row_id = request.POST.get('id', '')
    allowed = ['Biglietto', 'Utente']

    if table not in allowed:
        return JsonResponse({'success': False, 'message': 'Tabella non consentita'})

    try:
        with connection.cursor() as cursor:
            if table == 'Utente':
                cursor.execute("DELETE FROM Utente WHERE id = %s", [row_id])
            elif table == 'Biglietto':
                cursor.execute("DELETE FROM Biglietto WHERE id = %s", [row_id])
        return JsonResponse({'success': True, 'message': f'{table} eliminato con successo'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Errore durante eliminazione'})
    
def edit_row_view(request):
    numeric_fields = ['anno', 'durata', 'numPosti']
    mail = request.session.get('mail', '')
    if mail != 'admin@gmail.com':
        return HttpResponseForbidden("Accesso negato: solo l'amministratore può modificare i dati.")

    schema = {
        'Biglietto': {'cols': ['numProiezione', 'numFila', 'numPosto', 'dataVendita', 'prezzo', 'email', 'id'], 'pk': 'id'},
        'Film': {'cols': ['codice', 'titolo', 'anno', 'durata', 'lingua'], 'pk': 'codice'},
        'Proiezione': {'cols': ['numProiezione', 'sala', 'filmProiettato', 'data', 'ora'], 'pk': 'numProiezione'},
        'Sala': {'cols': ['numero', 'numPosti', 'dim', 'numFile', 'numPostiPerFila', 'tipo'], 'pk': 'numero'},
        'Utente': {'cols': ['id', 'mail', 'nome'], 'pk': 'id'}
    }

    readonly_biglietto = ['numProiezione', 'numFila', 'numPosto']
    readonly_sala = ['numero', 'numPosti', 'numFile', 'numPostiPerFila']

    table = request.GET.get('table')
    pk_value = request.GET.get('id')

    if not table or table not in schema or not pk_value:
        raise Http404("Tabella non valida o ID mancante")

    model = schema[table]
    pk = model['pk']
    cols = model['cols']

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT {', '.join(cols)} FROM `{table}` WHERE `{pk}` = %s", [pk_value])
        row = cursor.fetchone()
        if not row:
            raise Http404("Record non trovato")
        row_data = dict(zip(cols, row))

    msg = ''
    if request.method == 'POST':
        values = []
        for col in cols:
            raw = request.POST.get(col, '').strip()
            if table == 'Proiezione' and col == 'data':
                try:
                    raw = datetime.datetime.strptime(raw, '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    pass
            values.append(raw)

        set_fields = ", ".join([f"{col} = %s" for col in cols])
        values.append(pk_value)

        with connection.cursor() as cursor:
            try:
                cursor.execute(f"UPDATE `{table}` SET {set_fields} WHERE `{pk}` = %s", values)
            except Exception as e:
                msg = f"Errore durante l'aggiornamento: {str(e)}"
            else:
                if table == 'Film' and 'image_link' in request.POST:
                    image_link = request.POST['image_link'].strip()
                    img_file = os.path.join(settings.BASE_DIR, 'app_nav', 'static', 'film_images.json')
                    try:
                        with open(img_file, 'r', encoding='utf-8') as f:
                            film_images = json.load(f)
                    except Exception:
                        film_images = {}
                    film_images[row_data['codice']] = image_link
                    with open(img_file, 'w', encoding='utf-8') as f:
                        json.dump(film_images, f, indent=2, ensure_ascii=False)
                return redirect('/database/')

    film_image = ''
    if table == 'Film':
        img_file = os.path.join(settings.BASE_DIR, 'static', 'utils', 'film_images.json')
        try:
            with open(img_file, 'r', encoding='utf-8') as f:
                film_images = json.load(f)
            film_image = film_images.get(str(row_data['codice']), '')
        except Exception:
            film_image = ''

    return render(request, 'app_database/edit_row.html', {
    'table': table,
    'pk': pk,
    'row': row_data,
    'cols': cols,
    'msg': msg,
    'film_image': film_image,
    'readonly_biglietto': readonly_biglietto,
    'readonly_sala': readonly_sala,
    'numeric_fields': numeric_fields,
})
    
def database_dashboard(request):
    mail = request.session.get('mail', '')
    is_admin = (mail == 'admin@gmail.com')
    return render(request, 'app_database/database.html', {'is_admin': is_admin})
