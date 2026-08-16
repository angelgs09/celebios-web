# Barre el buzon de contacto@celebios.com y saca de ahi la lista de gente real.
#
#   python scripts/barrer-correo-historico.py
#
# ---------------------------------------------------------------------------
# POR QUE IMAP Y NO EL CONECTOR DE GMAIL
#
# El conector esta en la cuenta personal de Angel, y ahi solo estan los correos
# que alguien le reenvio: 54 hilos, casi todos ruido de Shopify y Vercel. El
# historico de CELEBIOS vive en contacto@celebios.com, 51,421 mensajes desde
# 2010. La MISMA contrasena de aplicacion que ya usamos para enviar sirve para
# leer por IMAP, asi que no hace falta ningun acceso nuevo.
#
# SOLO LEE. Abre las carpetas en readonly=True y no manda, borra ni marca nada.
#
# No baja cuerpos, solo cabeceras: con 51 mil mensajes, traer el cuerpo seria
# horas de descarga para un dato que esta en el sobre. De cada mensaje enviado
# saca a quien se le escribio, cuando, y con que asunto.
#
# La salida NO va al repo: son datos personales de clientes. Se escribe en el
# Escritorio, junto a las constancias.
# ---------------------------------------------------------------------------

import email.utils
import imaplib
import io
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENVFILE = os.path.join(RAIZ, '.env.production.local')
DESTINO = r'C:\Users\coche\Desktop\CELEBIOS-constancias'
CUENTA = 'contacto@celebios.com'
LOTE = 400

# Remitentes que son maquinas, no personas. Se excluyen del conteo para que la
# lista sea de gente y no de notificaciones.
RUIDO = re.compile(
    r'(noreply|no-reply|no_reply|notifica|mailer|billing|support@|@kajabimail|'
    r'@google\.com|@youtube|@facebookmail|@shopify|@vercel|@github|@dropbox|'
    r'@paypal|@stripe|@mercadolibre|@wix|@godaddy|@zoom\.us|@docs\.google|'
    r'calendar-notification|drive-shares)', re.I)


def leer_env(nombre):
    txt = io.open(ENVFILE, encoding='utf-8').read()
    m = re.search(rf'^{nombre}=(.*)$', txt, re.M)
    return m.group(1).strip().strip('"') if m else None


def conectar():
    pw = (leer_env('SMTP_APP_PASSWORD') or '').replace(' ', '')
    if len(pw) != 16:
        sys.exit('La contrasena de aplicacion debe tener 16 caracteres')
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    M.login(CUENTA, pw)
    return M


def decodificar(cadena):
    """Los asuntos vienen en MIME (=?UTF-8?B?...?=)."""
    if not cadena:
        return ''
    from email.header import decode_header, make_header
    try:
        return str(make_header(decode_header(cadena)))
    except Exception:
        return cadena


def barrer(M, carpeta, etiqueta):
    ok, datos = M.select(carpeta, readonly=True)
    if ok != 'OK':
        print(f'  no pude abrir {carpeta}')
        return []
    total = int(datos[0])
    print(f'{etiqueta}: {total} mensajes')

    ok, res = M.search(None, 'ALL')
    ids = res[0].split()
    filas = []
    for i in range(0, len(ids), LOTE):
        trozo = b','.join(ids[i:i + LOTE])
        ok, datos = M.fetch(trozo, '(BODY.PEEK[HEADER.FIELDS (FROM TO CC BCC SUBJECT DATE)])')
        for parte in datos:
            if not isinstance(parte, tuple):
                continue
            cab = parte[1].decode('utf-8', 'replace')
            campo = lambda n: (re.search(rf'^{n}:\s*(.*(?:\n[ \t].*)*)', cab, re.M | re.I) or [None, ''])[1]
            de = campo('From').replace('\n', ' ').strip()
            para = (campo('To') + ',' + campo('Cc') + ',' + campo('Bcc')).replace('\n', ' ').strip()
            asunto = decodificar(campo('Subject').replace('\n', ' ').strip())
            fecha = campo('Date').strip()
            try:
                dt = email.utils.parsedate_to_datetime(fecha)
                iso = dt.date().isoformat()
            except Exception:
                iso = ''
            filas.append({'de': de, 'para': para, 'asunto': asunto, 'fecha': iso, 'carpeta': etiqueta})
        print(f'  {min(i + LOTE, len(ids))}/{len(ids)}', end='\r', flush=True)
    print(f'  {len(filas)} leidos            ')
    return filas


def direcciones(cadena):
    return [a.lower() for _, a in email.utils.getaddresses([cadena]) if '@' in a]


def main():
    M = conectar()
    filas = barrer(M, '"[Gmail]/Enviados"', 'enviados')
    filas += barrer(M, 'INBOX', 'recibidos')
    M.logout()

    personas = defaultdict(lambda: {'escritos': 0, 'recibidos': 0,
                                    'primera': '9999', 'ultima': '0000', 'asuntos': []})
    for f in filas:
        lado = 'para' if f['carpeta'] == 'enviados' else 'de'
        for a in direcciones(f[lado]):
            if a.endswith('@celebios.com') or RUIDO.search(a):
                continue
            p = personas[a]
            p['escritos' if f['carpeta'] == 'enviados' else 'recibidos'] += 1
            if f['fecha']:
                p['primera'] = min(p['primera'], f['fecha'])
                p['ultima'] = max(p['ultima'], f['fecha'])
            if f['asunto'] and len(p['asuntos']) < 6:
                p['asuntos'].append(f['asunto'][:90])

    salida = []
    for correo, p in personas.items():
        salida.append({'correo': correo, **p,
                       'total': p['escritos'] + p['recibidos']})
    salida.sort(key=lambda x: (-x['total'], x['correo']))

    os.makedirs(DESTINO, exist_ok=True)
    ruta = os.path.join(DESTINO, 'correo-historico-personas.json')
    io.open(ruta, 'w', encoding='utf-8').write(json.dumps(salida, ensure_ascii=False, indent=1))

    print()
    print(f'mensajes leidos: {len(filas)}')
    print(f'personas distintas (sin maquinas ni @celebios.com): {len(salida)}')
    print(f'   con 2 o mas intercambios: {sum(1 for x in salida if x["total"] >= 2)}')
    print(f'escrito en: {ruta}')


if __name__ == '__main__':
    main()
