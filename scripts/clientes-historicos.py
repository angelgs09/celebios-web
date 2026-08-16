# De los 17,885 correos enviados, saca a los que fueron CLIENTES, no curiosos.
#
#   python scripts/clientes-historicos.py
#
# El barrido general daba 255 personas, pero mezcla a quien pidio informes una
# vez con quien pago un diplomado. La diferencia esta en el asunto: a un cliente
# se le manda bienvenida, confirmacion de inscripcion, factura o comprobante; a
# un curioso se le manda informacion y ya.
#
# Se busca con SEARCH del servidor, no filtrando en local, para no depender de
# los 6 asuntos por persona que guardaba el barrido anterior.
#
# SOLO LEE (readonly). No manda, no borra, no marca.
# La salida va al Escritorio: son datos personales de clientes.

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

# Cada grupo es una señal distinta de que del otro lado hubo dinero.
SENALES = {
    'pago':        ['comprobante', 'factura', 'pago', 'deposito', 'transferencia'],
    'inscripcion': ['bienvenida', 'bienvenido', 'inscripcion', 'inscripción',
                    'confirmacion', 'confirmación', 'acceso', 'usuario'],
    'constancia':  ['constancia', 'diploma', 'certificado'],
}
RUIDO = re.compile(r'(noreply|no-reply|notifica|mailer|billing|@kajabimail|@google|'
                   r'@facebookmail|@shopify|@vercel|@github|@dropbox|@paypal|@stripe)', re.I)


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
    M.select('"[Gmail]/Enviados"', readonly=True)

    gente = defaultdict(lambda: {'senales': set(), 'primera': '9999', 'ultima': '0000',
                                 'asuntos': [], 'veces': 0})

    for grupo, palabras in SENALES.items():
        vistos = set()
        for p in palabras:
            # SEARCH del servidor. El literal en UTF-8 permite acentos.
            try:
                M.literal = p.encode('utf-8')
                ok, res = M.search('UTF-8', 'SUBJECT')
            except Exception:
                continue
            if ok != 'OK':
                continue
            ids = [i for i in res[0].split() if i not in vistos]
            vistos.update(ids)
            for i in range(0, len(ids), 300):
                trozo = b','.join(ids[i:i + 300])
                ok, datos = M.fetch(trozo, '(BODY.PEEK[HEADER.FIELDS (TO CC BCC SUBJECT DATE)])')
                for parte in datos:
                    if not isinstance(parte, tuple):
                        continue
                    cab = parte[1].decode('utf-8', 'replace')
                    campo = lambda n: (re.search(rf'^{n}:\s*(.*(?:\n[ \t].*)*)', cab, re.M | re.I) or [None, ''])[1]
                    asunto = decodificar(campo('Subject').replace('\n', ' ').strip())
                    fecha = campo('Date').strip()
                    try:
                        iso = email.utils.parsedate_to_datetime(fecha).date().isoformat()
                    except Exception:
                        iso = ''
                    dests = email.utils.getaddresses([campo('To') + ',' + campo('Cc') + ',' + campo('Bcc')])
                    for nombre, a in dests:
                        a = a.lower()
                        if '@' not in a or a.endswith('@celebios.com') or RUIDO.search(a):
                            continue
                        g = gente[a]
                        g['senales'].add(grupo)
                        g['veces'] += 1
                        if nombre and not g.get('nombre'):
                            g['nombre'] = decodificar(nombre).strip()
                        if iso:
                            g['primera'] = min(g['primera'], iso)
                            g['ultima'] = max(g['ultima'], iso)
                        if asunto and len(g['asuntos']) < 5:
                            g['asuntos'].append(asunto[:100])
            print(f'  {grupo}/{p}: {len(ids)} mensajes', flush=True)

    M.logout()

    salida = []
    for correo, g in gente.items():
        salida.append({'correo': correo, 'nombre': g.get('nombre', ''),
                       'senales': sorted(g['senales']), 'fuerza': len(g['senales']),
                       'veces': g['veces'], 'primera': g['primera'],
                       'ultima': g['ultima'], 'asuntos': g['asuntos']})
    salida.sort(key=lambda x: (-x['fuerza'], -x['veces']))

    ruta = os.path.join(DESTINO, 'clientes-historicos.json')
    io.open(ruta, 'w', encoding='utf-8').write(json.dumps(salida, ensure_ascii=False, indent=1))

    print()
    print(f'personas con al menos una senal de cliente: {len(salida)}')
    for n in (3, 2, 1):
        print(f'  con {n} senal(es) distintas: {sum(1 for x in salida if x["fuerza"] == n)}')
    print(f'escrito en: {ruta}')


if __name__ == '__main__':
    main()
