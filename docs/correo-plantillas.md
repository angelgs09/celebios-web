# Las plantillas de correo del aula

Para pegar en **Supabase → Authentication → Emails**. Hoy salen las de fábrica:
en inglés, firmadas por `noreply@mail.app.supabase.io`, con un botón que dice
"Sign in".

Los alumnos vienen de Kajabi y **nadie eligió contraseña**: para casi todos, el
primer correo de CELEBIOS que reciban será éste. Que llegue en inglés y de un
remitente desconocido es la forma más rápida de acabar en spam.

## Antes de pegar nada: quién manda el correo

**Resend quedó descartado el 5 de agosto.** Pide tres registros —DKIM (TXT),
más un MX y un TXT en el subdominio `send`— y **los tres son obligatorios**
(verificado contra su API: `type=MX name=send status=not_started`). Ninguno de
los dos dominios lo permite:

- **`celebios.com`** vive en **DNS de Wix**, con el correo en Google Workspace
  (MX = `aspmx.l.google.com`). Wix **no ofrece "Add Record" en la sección MX**
  mientras Google esté conectado, ni siquiera para un subdominio.
- **`celebios.online`** está en nameservers de Cloudflare
  (`jermaine`/`joyce.ns.cloudflare.com`) pero **no en la cuenta de Angel** —la
  suya tiene cero dominios—. Además es **el dominio de Kajabi**, la plataforma
  que se apaga el 30-ago: no es sitio donde fundar una identidad de correo.

Lo que sí hay y ya está pagado: **Google Workspace en `celebios.com`**, con
`contacto@celebios.com` funcionando. Supabase habla SMTP con Google sin tocar
un solo registro DNS.

En **Project Settings → Authentication → SMTP Settings**:

| Campo | Valor |
|---|---|
| Host | `smtp.gmail.com` |
| Port | `465` |
| Username | `contacto@celebios.com` (el correo completo) |
| Password | una **contraseña de aplicación** de Google, no la del correo |
| Sender email | `contacto@celebios.com` |
| Sender name | `CELEBIOS` |

La contraseña de aplicación se genera en la cuenta de Google
(`myaccount.google.com` → Seguridad → Verificación en dos pasos → Contraseñas
de aplicaciones) y **exige tener 2FA encendida**. Es un secreto: va del gestor
de contraseñas al campo de Supabase, nunca al chat ni al repo.

Y súbele el **rate limit** (en Authentication → Rate Limits): el de fábrica son
unos pocos por hora y por eso hoy da `over_email_send_rate_limit`. Con SMTP
propio se puede subir a 30 por hora sin problema.

### Si el correo no sale: leer el log, no adivinar

El endpoint devuelve un `500` mudo (`"Error sending magic link email"`). El
motivo real está en **Authentication logs**, y se saca así:

```
mcp Supabase get_logs → project lwawpdjsfjvlyvqwqiqp, service "auth"
```

El 5 de agosto el primer intento dio:

```
535 5.7.8 Username and Password not accepted
https://support.google.com/mail/?p=BadCredentials
```

**Ese error significa que el puerto y el TLS están bien** —se llegó hasta la
fase de autenticación— y que lo único mal es la credencial.

**Y el 14 de agosto se encontró por qué, y no era un dedazo.** La cadena, de
abajo hacia arriba:

1. En la consola de administrador de `celebios.com`, **Seguridad → Verificación
   en 2 pasos**, la casilla *"Permitir que los usuarios activen la verificación
   en 2 pasos"* estaba **apagada**.
2. Por eso `contacto@celebios.com` no podía activar 2FA. Su propia página lo
   decía: *"No podrás activar la Verificación en 2 pasos hasta que el
   administrador lo permita"*.
3. Sin 2FA, Google **no ofrece contraseñas de aplicación**:
   `myaccount.google.com/apppasswords` respondía *"La opción de configuración
   que buscas no está disponible para tu cuenta"*.
4. Y sin contraseña de aplicación, el SMTP de Gmail rechaza cualquier cosa.

O sea: **no existía una contraseña válida que se pudiera poner.** Ninguna
habría pasado. Se destrabó marcando esa casilla (verificado recargando la
página) y el orden correcto de ahí en adelante es: activar 2FA en la cuenta →
generar la contraseña de aplicación → pegarla en Supabase.

Si el 535 vuelve **después** de tener una contraseña de aplicación real, ahí sí
las sospechas de siempre: pegada con espacios (van **16 caracteres seguidos**),
o generada en la cuenta equivocada.

⚠️ **Y una fecha que se come todo esto.** El mismo día se vio en la consola:
*"No pudimos procesar tu último pago… para evitar que se suspenda el servicio
el **3 sept 2026**, actualiza tu información de pago"*. Si Workspace se
suspende, no es solo el aula: es el correo de CELEBIOS entero, y este montaje
SMTP deja de existir. **Si esa fecha se acerca sin resolverse, mover el correo
del aula a un ESP que se valide solo con TXT** —Brevo, p. ej.— porque Wix
acepta TXT aunque no deje tocar el MX.

### Lo que esto cuesta y cuándo dejará de alcanzar

Gmail corta alrededor de los **2,000 destinatarios al día**: sobra para 21
alumnos y para las ligas de acceso. Lo que no da es tablero de envíos, ni
reintentos, ni rebotes separados —los rebotes caen en la bandeja de
`contacto@`—. El día que CELEBIOS mande cientos de correos, o quiera ver qué
se abrió, hay que mover el DNS de `celebios.com` a Cloudflare y volver a
Resend; ahí el MX deja de ser un problema.

---

## Magic Link

**Asunto:** `Tu acceso al aula de CELEBIOS`

```html
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;color:#16294C">

  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">
    CELEBIOS · Aula virtual
  </p>

  <h1 style="font-size:24px;line-height:1.2;margin:0 0 16px;color:#16294C">
    Entra a tu curso
  </h1>

  <p style="font-size:16px;line-height:1.6;margin:0 0 24px;color:#16294C">
    Da clic en el botón para entrar. No necesitas contraseña: este enlace te
    identifica y te deja dentro.
  </p>

  <p style="margin:0 0 24px">
    <a href="{{ .ConfirmationURL }}"
       style="display:inline-block;background:#2FA8C9;color:#16294C;font-weight:600;
              font-size:16px;text-decoration:none;padding:14px 28px;border-radius:4px">
      Entrar al aula
    </a>
  </p>

  <p style="font-size:14px;line-height:1.6;color:#4D5F7C;margin:0 0 8px">
    El enlace sirve una sola vez y caduca en una hora. Si ya no funciona,
    pide otro desde la página del aula.
  </p>

  <p style="font-size:14px;line-height:1.6;color:#4D5F7C;margin:0 0 32px">
    Si no pediste este correo, ignóralo: sin dar clic no pasa nada.
  </p>

  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">

  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">
    Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal<br>
    <a href="https://celebios.vercel.app/aviso-de-privacidad" style="color:#4D5F7C">Aviso de privacidad</a>
  </p>

</div>
```

---

## Invite user

🔴 **OJO (14-ago-2026): a los 21 de Kajabi esta plantilla NO se les puede
mandar.** El script de importación ya los creó como usuarios con el correo
confirmado, y `POST /auth/v1/invite` sobre un usuario existente contesta:

```
422 {"error_code":"email_exists","msg":"A user with this email address has already been registered"}
```

Supabase sólo usa esta plantilla para **cuentas nuevas**. Comprobado sin mandar
nada (se probó contra la cuenta de Angel, que también existe).

Así que el correo de "tu curso se mudó" **no sale de Supabase**: hay que
mandarlo aparte, desde `contacto@celebios.com`, con un enlace normal a
`/aula` donde cada quien pide su propia liga. Es además mejor así: 21 ligas
mágicas disparadas a la vez **caducan en una hora**, y la mayoría se leería
tarde. Separando el aviso del acceso, el aviso no caduca nunca.

El texto de abajo sirve tal cual como cuerpo de ese correo, quitándole el
botón con `{{ .ConfirmationURL }}` y dejando en su lugar una liga a
`https://celebios.vercel.app/aula`.

La plantilla se queda cargada de todos modos: el día que entre un alumno
nuevo de verdad, es la que le toca.

**Asunto:** `Tu curso de CELEBIOS cambió de casa`

```html
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;color:#16294C">

  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">
    CELEBIOS · Aula virtual
  </p>

  <h1 style="font-size:24px;line-height:1.25;margin:0 0 16px;color:#16294C">
    Tu aula se mudó. Tu acceso no cambia.
  </h1>

  <p style="font-size:16px;line-height:1.6;margin:0 0 16px;color:#16294C">
    Movimos el curso de Lenguaje y Comunicación de los Gatos a nuestra propia
    plataforma. Tus once módulos, tus exámenes y tu avance están ahí, tal como
    los dejaste.
  </p>

  <p style="font-size:16px;line-height:1.6;margin:0 0 24px;color:#16294C">
    No necesitas crear cuenta ni recordar contraseña. Da clic y entras.
  </p>

  <p style="margin:0 0 24px">
    <a href="{{ .ConfirmationURL }}"
       style="display:inline-block;background:#2FA8C9;color:#16294C;font-weight:600;
              font-size:16px;text-decoration:none;padding:14px 28px;border-radius:4px">
      Entrar a mi curso
    </a>
  </p>

  <p style="font-size:14px;line-height:1.6;color:#4D5F7C;margin:0 0 32px">
    El enlace caduca en una hora y sirve una sola vez; si se te pasa, en la
    página del aula puedes pedir otro con tu mismo correo.
  </p>

  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">

  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">
    Centro Latinoamericano de Estudios en Ciencias Biológicas y de la Salud Animal<br>
    <a href="https://celebios.vercel.app/aviso-de-privacidad" style="color:#4D5F7C">Aviso de privacidad</a>
  </p>

</div>
```

---

## Reset password

Sirve poco hoy —nadie tiene contraseña— pero el enlace existe y hay que dejarlo
en español por si alguien se crea una.

**Asunto:** `Cambia tu contraseña de CELEBIOS`

Mismo cuerpo que el Magic Link, cambiando el titular por
`Cambia tu contraseña` y el botón por `Elegir contraseña nueva`.

---

## ✅ Verificado en vivo el 14-ago-2026

El primer correo real salió a las 17:42 y **llegó a Recibidos**, no a spam:

- Remitente `contacto@celebios.com`, asunto `Tu acceso al aula de CELEBIOS`.
- Acentos perfectos —"botón", "contraseña", "ignóralo", "Biológicas"—: **no hace
  falta pelearse con el charset.** Las entidades HTML (`&oacute;`) tampoco
  estorban.
- El botón apunta a `.../auth/v1/verify?...&redirect_to=…`, sin rastro de
  `localhost`.

⚠️ **El destino hay que pedirlo cada vez.** Sin `redirect_to`, GoTrue usa el
**Site URL**, que es `https://celebios.vercel.app` **a secas**: el alumno
aterriza en la portada, no en el aula. El login del aula ya lo manda bien
(`emailRedirectTo: location.origin + '/aula'` en `aula/index.html`), pero
cualquier envío hecho **por API** tiene que añadirlo a mano:

```
POST /auth/v1/otp?redirect_to=https%3A%2F%2Fcelebios.vercel.app%2Faula
```

Comprobado con dos correos seguidos: el primero cayó en la portada, el segundo
—con el parámetro— en `/aula`.

## Qué revisar si se cambian

1. Que el remitente diga **CELEBIOS**, no Supabase.
2. Que llegue a **Recibidos**. Si cae en Promociones, es normal y no es un fallo.
3. Que el botón lleve a **celebios.vercel.app/aula**.
4. Que los acentos se vean bien.

## Lo que estas plantillas no hacen

No mandan nada solas. Invitar a los 21 alumnos es un paso deliberado, con la
Admin API y de uno en uno, para poder parar si el primero rebota. El script de
importación no envía correos justamente por eso.
