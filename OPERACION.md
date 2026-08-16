# Cómo se opera el aula

Lo que hay que hacer a mano, y lo que corre solo. Para la historia de la
migración desde Kajabi está `MIGRACION.md`; esto es solamente el día a día.

El aula vive en **https://celebios.vercel.app/aula**. `www.celebios.com` todavía
es el sitio Wix viejo, así que los correos a alumnos apuntan al dominio de
Vercel. El día del cambio de dominio hay que revisar los enlaces de los correos.

---

## Lo que corre solo

Dos tareas programadas de Windows, las dos con la sesión de Angel iniciada.
**Si la laptop está apagada, no corren.** No se pierde nada, solo se retrasa.

| Tarea | Cuándo | Qué hace |
|---|---|---|
| `CELEBIOS - latido Supabase` | diario 10:00 | Toca la base para que Supabase no la pause por inactividad. Una base pausada da NXDOMAIN y el aula deja de abrir. |
| `CELEBIOS - avisar constancias` | diario 9:30 | Revisa quién acreditó los once quizes y avisa a `contacto@celebios.com` con el PDF listo. **No le manda nada al alumno.** |

Para ver cómo están:

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like '*CELEBIOS*' } |
  ForEach-Object { $_.TaskName + '  ' + $_.State }
```

---

## La constancia

La promesa que se le hizo al alumno en Kajabi, textual: si resuelve todos los
quizes con calificación **mayor a 80/100**, recibe constancia de participación
con validez curricular. Con 6 preguntas por quiz eso son 5 aciertos, porque las
notas posibles saltan de 67 a 83.

**Ver los videos no es requisito.** Así funcionaba en Kajabi. Eso no se le dice
al alumno en ninguna pantalla: lo que se le dice es que apruebe los quizes.

De 24 alumnos en Kajabi salieron 2 constancias, y no porque nadie acreditara,
sino porque emitirlas dependía de que alguien se acordara de mirar. Por eso lo
que corre solo es la mirada, no el envío.

```powershell
cd C:\Users\coche\.codex\worktrees\CELEBIOS-web-redesign-total\scripts

.\emitir-constancias.ps1                          # ensayo: dice cómo está el tablero
.\emitir-constancias.ps1 -Avisar                  # correo interno (lo que hace la tarea)
.\emitir-constancias.ps1 -Aplicar -Solo <correo>  # se la manda AL ALUMNO
```

Sale de una en una y con el correo escrito a mano, a propósito. Mientras alguien
siga sin su constancia, el aviso vuelve a insistir cada 7 días con la cuenta de
días en el asunto.

**Si el aviso dice que falta el nombre**, es porque lo que hay en la base no
sirve para imprimirse en un documento con folio de CONCERVET (viene en
mayúsculas, con dígitos, sin apellido, o es un correo). Se corrige el nombre en
`perfiles.nombre` y al día siguiente el aviso ya trae el PDF. O se emite directo:

```powershell
.\generar-constancia.ps1 -Nombre "Nombre Completo" -Correo alguien@correo.com
```

La plantilla oficial (`plantilla-oficial.png`) vive fuera del repo, en
`Desktop\CELEBIOS-constancias\`. Trae curso, horas, folio, logos, QR y sello: lo
único que el script pone es el nombre. **Si algún dato de la constancia cambia,
se cambia la imagen, no el código** — así no se puede colar un dato inventado.
Respaldo en el Drive de `contacto@celebios.com`.

---

## Dar de alta e inscribir

Todo desde **https://celebios.vercel.app/aula/admin**, con una cuenta que tenga
`rol = 'admin'` en `perfiles`. Ahí se inscribe a un alumno y se editan el título
y el video de cada lección.

El acceso dura **5 meses** desde el alta; sale del valor por omisión de la
columna, no hay que capturarlo.

Para extender el acceso de alguien que ya venció, desde el SQL editor de
Supabase con una sesión de admin:

```sql
select prorrogar('<alumno_id>', '<curso_id>', 3);   -- 3 meses más
```

---

## Los videos

Los once están en Vercel Blob, comprimidos de 8.41 GB a 1.35 GB con la misma
duración y calidad. `lecciones.video_url` **no guarda una URL**, guarda la ruta
del blob (`curso-lenguaje-felino/modulo-01.mp4`); quien la firma es
`api/video.js`, con una liga que caduca a los 90 minutos.

Ninguno pasa de 512 MB, que es el umbral donde Vercel deja de cachear y cada
reproducción se cobraría como transferencia.

Para volver a comprimir algo: `scripts\comprimir-videos.ps1` (mide por omisión,
comprime con `-Aplicar`).

---

## Publicar cambios

El sitio es HTML estático generado por `build.py`. **El push a GitHub no
despliega**: hay que hacerlo explícito.

```bash
python build.py          # genera site/
npm test                 # 325 pruebas
npx vercel deploy site --prod
```

Si se toca `aula/index.html` o `aula/admin.html`, conviene abrir el aula después
y ver que pinta "Entra a tus cursos". Un error en el módulo no muestra ningún
mensaje: deja la página **en blanco**.

`supabase-js` se sirve desde `aula/vendor/`, no de un CDN. Para subirlo de
versión:

```bash
npm i -D @supabase/supabase-js@<nueva>
node scripts/empaquetar-supabase.mjs
# y actualizar el import en aula/index.html y aula/admin.html
```

---

## Cerrar el aula de emergencia

En `aula/index.html`, arriba del todo:

```js
const EN_MANTENIMIENTO = true
```

y desplegar. Tapa todo, tenga sesión el alumno o no. **Es una bandera del
cliente**: no impide que alguien con sesión le pida una firma a `/api/video` a
mano. Si hay que cerrar por el contenido y no por la interfaz, se quita el
`video_url` de las lecciones.

---

## Secretos

Viven en `.env.production.local`, que está en `.gitignore` y no se abre en el
chat. Los scripts los leen de ahí.

- `SUPABASE_SERVICE_ROLE_KEY` — se salta el RLS por completo. Nunca va al navegador.
- `SMTP_APP_PASSWORD` — contraseña de aplicación de `contacto@celebios.com`.
- `BLOB_READ_WRITE_TOKEN` — para subir videos.

La clave que sí está en el HTML del aula es la publishable, y está hecha para
vivir ahí: quien protege los datos es el RLS de Postgres.
