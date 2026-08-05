# Las plantillas de correo del aula

Para pegar en **Supabase → Authentication → Emails**. Hoy salen las de fábrica:
en inglés, firmadas por `noreply@mail.app.supabase.io`, con un botón que dice
"Sign in".

Los alumnos vienen de Kajabi y **nadie eligió contraseña**: para casi todos, el
primer correo de CELEBIOS que reciban será éste. Que llegue en inglés y de un
remitente desconocido es la forma más rápida de acabar en spam.

## Antes de pegar nada

En **Project Settings → Authentication → SMTP Settings**:

| Campo | Valor |
|---|---|
| Host | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | la API key de Resend |
| Sender email | `aula@celebios.com` |
| Sender name | `CELEBIOS` |

Y súbele el **rate limit** (en Authentication → Rate Limits): el de fábrica son
unos pocos por hora y por eso hoy da `over_email_send_rate_limit`. Con SMTP
propio se puede subir a 30 por hora sin problema.

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

El que se manda una sola vez a los 21 que vienen de Kajabi. **Este es el que más
importa**: es el correo que explica por qué su aula cambió de dirección.

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

## Qué revisar después de pegarlas

1. Que el remitente diga **CELEBIOS**, no Supabase.
2. Que llegue a **Recibidos** y no a spam. Con DKIM y SPF de Resend bien puestos
   debería; si cae en Promociones, es normal y no es un fallo.
3. Que el botón lleve a **celebios.vercel.app/aula** y no a `localhost:3000`
   —ese fue el fallo del 5 de agosto y se arregla en URL Configuration, no aquí.
4. Que los acentos se vean bien. Si salen como `Ã³`, falta el `charset` en el
   encabezado del correo.

## Lo que estas plantillas no hacen

No mandan nada solas. Invitar a los 21 alumnos es un paso deliberado, con la
Admin API y de uno en uno, para poder parar si el primero rebota. El script de
importación no envía correos justamente por eso.
