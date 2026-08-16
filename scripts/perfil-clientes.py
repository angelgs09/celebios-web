# Quien es cada uno de los clientes historicos: que compro, cuantas veces, y si
# alguna vez contesto.
#
#   python scripts/perfil-clientes.py
#
# ---------------------------------------------------------------------------
# El barrido anterior solo miraba Enviados, asi que veia a quien le escribimos
# pero no quien nos contesto. Las respuestas no estan en INBOX (solo tiene 11
# mensajes: archivan todo), estan en "[Gmail]/Todos". Aqui se barre esa carpeta
# entera, 51 mil mensajes, y se separa por direccion:
#
#   SALIENTE  (From contiene @celebios.com)  -> le escribimos
#   ENTRANTE  (From es otro)                 -> nos contesto  <- esto es lo que faltaba
#
# Que compro sale del asunto. No es perfecto -- un asunto puede mencionar un
# curso sin que la persona lo comprara -- pero cruzado con las señales de pago
# (bienvenida, comprobante, factura, constancia) separa bien al cliente del
# curioso.
#
# SOLO LEE (readonly). No manda, no borra, no marca.
# La salida va al Escritorio: son datos personales de clientes.
# ---------------------------------------------------------------------------

import email.utils
import imaplib
import io
import json
import os
import re
import sys
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = r'C:\Users\coche\Desktop\CELEBIOS-constancias'
CUENTA = 'contacto@celebios.com'
LOTE = 400

# El catalogo, tal como aparece escrito en los asuntos a lo largo de los años.
# Las variantes importan: la misma cosa se escribio de seis formas distintas.
PRODUCTOS = [
    ('diplomado-rehabilitacion', r'rescate y rehabilitaci|rehabilitaci[oó]n de fauna|diplomado.*rehabilitaci|rehabilitacion de fauna'),
    ('manejo-conductual',        r'manejo conductual|conductual de fauna|comportamiento animal'),
    ('nutricion',                r'nutrici[oó]n'),
    ('primeros-auxilios',        r'primeros auxilios'),
    ('reptiles',                 r'reptil|herpeto'),
    ('aves-ortopedia',           r'ortopedia|aves rapaces|rapaces'),
    ('anestesia',                r'anestesi|contenci[oó]n qu[ií]mica'),
    ('felino',                   r'gato|felin[oa]'),
    ('conferencia',              r'conferencia|webinar|charla|simposio|congreso'),
    ('latinvets',                r'latinvets'),
]
SENAL_PAGO = re.compile(r'comprobante|factura|pago|dep[oó]sito|transferencia', re.I)
SENAL_ALTA = re.compile(r'bienvenid|inscripci|confirmaci[oó]n|acceso|usuario y contrase', re.I)
SENAL_FIN  = re.compile(r'constancia|diploma|certificado', re.I)
RUIDO = re.compile(r'(noreply|no-reply|no_reply|notifica|mailer|billing|support@|@kajabimail'
                   r'|@google|@youtube|@facebookmail|@shopify|@vercel|@github|@dropbox'
                   r'|@paypal|@stripe|@wix|@godaddy|@zoom|@mailchimp|@sendgrid'
                   r'|@intuit|@quickbooks|@linkedin|@twitter|@instagram)', re.I)


def env(n):
    txt = io.open(os.path.join(RAIZ, '.env.production.local'), encoding='utf-8').read()
    m = re.search(rf'^{n}=(.*)$', txt, re.M)
    return m.group(1).strip().strip('"') if m else None


def decodificar(s):
    from email.header import decode_header, make_header
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s


def main():
    pw = (env('SMTP_APP_PASSWORD') or '').replace(' ', '')
    if len(pw) != 16:
        sys.exit('contrasena de aplicacion invalida')
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    M.login(CUENTA, pw)
    ok, datos = M.select('"[Gmail]/Todos"', readonly=True)
    total = int(datos[0])
    print(f'barriendo {total} mensajes de [Gmail]/Todos', flush=True)

    ok, res = M.search(None, 'ALL')
    ids = res[0].split()

    g = defaultdict(lambda: {
        'nombre': '', 'saliente': 0, 'entrante': 0,
        'productos': set(), 'pago': 0, 'alta': 0, 'constancia': 0,
        # Lo mismo pero SOLO en correos individuales. Una "bienvenida" mandada
        # con 200 personas en Bcc marcaba a las 200 como clientes; un correo a
        # una sola persona diciendo "recibimos tu comprobante" no miente.
        'ind_pago': 0, 'ind_alta': 0, 'ind_constancia': 0, 'ind_productos': set(),
        'en_campanas': 0, 'individuales': 0,
        'primera': '9999-99', 'ultima': '0000-00',
        'asuntos_entrantes': [],
    })

    for i in range(0, len(ids), LOTE):
        trozo = b','.join(ids[i:i + LOTE])
        ok, datos = M.fetch(trozo, '(BODY.PEEK[HEADER.FIELDS (FROM TO CC BCC SUBJECT DATE)])')
        for parte in datos:
            if not isinstance(parte, tuple):
                continue
            cab = parte[1].decode('utf-8', 'replace')
            campo = lambda n: (re.search(rf'^{n}:\s*(.*(?:\n[ \t].*)*)', cab, re.M | re.I) or [None, ''])[1]
            de = campo('From').replace('\n', ' ')
            asunto = decodificar(campo('Subject').replace('\n', ' ').strip())
            try:
                iso = email.utils.parsedate_to_datetime(campo('Date').strip()).date().isoformat()
            except Exception:
                iso = ''

            saliente = 'celebios.com' in de.lower()
            lado = (campo('To') + ',' + campo('Cc') + ',' + campo('Bcc')) if saliente else de

            prods = {n for n, pat in PRODUCTOS if re.search(pat, asunto, re.I)}
            pago = 1 if SENAL_PAGO.search(asunto) else 0
            alta = 1 if SENAL_ALTA.search(asunto) else 0
            fin = 1 if SENAL_FIN.search(asunto) else 0

            destinatarios = email.utils.getaddresses([lado])
            # 5 es el corte: un correo real a un alumno lleva 1, a veces 2 o 3
            # si va con copia. De ahi para arriba es difusion.
            individual = len([1 for _, x in destinatarios if '@' in x]) <= 5

            for nombre, a in destinatarios:
                a = a.lower().strip()
                if '@' not in a or a.endswith('@celebios.com') or RUIDO.search(a):
                    continue
                p = g[a]
                if saliente:
                    p['saliente'] += 1
                else:
                    p['entrante'] += 1
                    if asunto and len(p['asuntos_entrantes']) < 8:
                        p['asuntos_entrantes'].append(asunto[:110])
                if nombre and not p['nombre']:
                    p['nombre'] = decodificar(nombre).strip().strip('"')
                p['productos'] |= prods
                p['pago'] += pago
                p['alta'] += alta
                p['constancia'] += fin
                if individual:
                    p['individuales'] += 1
                    p['ind_pago'] += pago
                    p['ind_alta'] += alta
                    p['ind_constancia'] += fin
                    p['ind_productos'] |= prods
                else:
                    p['en_campanas'] += 1
                if iso:
                    p['primera'] = min(p['primera'], iso)
                    p['ultima'] = max(p['ultima'], iso)
        print(f'  {min(i + LOTE, len(ids))}/{len(ids)}', end='\r', flush=True)

    M.logout()
    print(f'  {len(ids)} leidos                 ')

    salida = []
    for correo, p in g.items():
        prods = sorted(p['productos'])
        ind_prods = sorted(p['ind_productos'])
        salida.append({
            'correo': correo, 'nombre': p['nombre'],
            'productos': ind_prods, 'n_productos': len(ind_prods),
            'productos_mencionados': prods,
            'ind_pago': p['ind_pago'], 'ind_alta': p['ind_alta'],
            'ind_constancia': p['ind_constancia'],
            'individuales': p['individuales'], 'en_campanas': p['en_campanas'],
            'nos_escribio': p['entrante'], 'le_escribimos': p['saliente'],
            'senal_pago': p['pago'], 'senal_alta': p['alta'], 'senal_constancia': p['constancia'],
            'primera': p['primera'], 'ultima': p['ultima'],
            'asuntos_entrantes': p['asuntos_entrantes'],
        })

    # Cliente = tiene alguna señal dura de haber pagado o de haber sido dado de
    # alta. Sin eso es alguien a quien se le escribio, nada mas.
    def es_cliente(x):
        # La señal tiene que venir de un correo INDIVIDUAL. Con la señal de
        # campaña, cualquiera que estuvo en un Bcc de difusion contaba como
        # cliente y la cifra se iba a 8,155.
        return x['ind_pago'] > 0 or x['ind_alta'] > 0 or x['ind_constancia'] > 0

    clientes = [x for x in salida if es_cliente(x)]
    clientes.sort(key=lambda x: (-x['n_productos'], -x['nos_escribio'], -x['senal_pago']))

    os.makedirs(DESTINO, exist_ok=True)
    r1 = os.path.join(DESTINO, 'perfil-clientes.json')
    io.open(r1, 'w', encoding='utf-8').write(json.dumps(clientes, ensure_ascii=False, indent=1))
    r2 = os.path.join(DESTINO, 'perfil-todos.json')
    io.open(r2, 'w', encoding='utf-8').write(json.dumps(salida, ensure_ascii=False, indent=1))

    print()
    print(f'direcciones en total : {len(salida)}')
    print(f'clientes (con señal) : {len(clientes)}')
    print(f'  que nos contestaron alguna vez : {sum(1 for x in clientes if x["nos_escribio"] > 0)}')
    print(f'  con 2 o mas productos          : {sum(1 for x in clientes if x["n_productos"] >= 2)}')
    print(f'  con 3 o mas productos          : {sum(1 for x in clientes if x["n_productos"] >= 3)}')
    print(f'  con senal de PAGO individual   : {sum(1 for x in clientes if x["ind_pago"] > 0)}')
    print(f'  con constancia individual      : {sum(1 for x in clientes if x["ind_constancia"] > 0)}')
    print(f'escrito en: {r1}')


if __name__ == '__main__':
    main()
