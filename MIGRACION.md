# CELEBIOS — migración fuera de Kajabi

Estado al 31-jul-2026. Alcance acordado: **solo migrar**. El rediseño y el
marketing son otro bloque, después.

---

## Stack decidido

| Pieza | Servicio | USD/mes |
|---|---|---|
| Sitio + app | Vercel | 20 |
| Base de datos, login, archivos | Supabase Pro | 25 |
| Cobro | Stripe MX (tarjeta, MSI, SPEI, OXXO) | 0 fijo |
| | **Total con IVA** | **~52** |

Contra Kajabi Basic: **$179/mes** ($143 si se paga el año por adelantado).

**Auth0 descartado.** Su tier gratis no incluye MFA ni Role Management —
justo lo que uno querría de él— y activarlos cuesta $35/mes. Supabase Auth ya
viene incluido con 100,000 MAU y la autorización queda en la misma base de
datos (RLS). De Kajabi no salen las contraseñas de ningún modo, así que la
importación es igual con cualquiera de los dos: se importan correos y cada
alumno define contraseña nueva.

**Bunny / Mux descartados por ahora.** Se cotizaron asumiendo decenas de GB de
video. El curso real pesa 1.23 GB (ver inventario), así que 100 alumnos viendo
todo son ~123 GB de tráfico y Supabase Pro incluye 250 GB. Un proveedor menos.
Si aparece video del Diplomado de Rehabilitación en volumen, se reabre: la
opción era Bunny Stream tier Volume ($0.005/GB), no Standard, porque a
Sudamérica Standard cobra $0.045/GB y hay alumnos en CO/EC/PE/VE.

---

## Lo que Kajabi NO deja sacar (verificado contra su API oficial)

- **Videos: no hay descarga masiva ni API.** El objeto `media` expone un solo
  campo, `duration_in_minutes`. La única ruta es
  `Products > Course > Lesson > Video Actions > Download`, lección por lección.
- **Progreso: no hay endpoint.** Solo `Analytics > Product Progress > Export`,
  y da el porcentaje global por alumno, no el detalle por lección.
- **Contactos:** `Contacts > Bulk Actions > Export`. Llega por correo y
  **el link expira a los 3 días**.
- **No pagar el add-on de API ($25/mes).** No da videos ni progreso; lo único
  que sí da (contactos y compras) sale gratis por la interfaz.
- Kajabi subió precios 20-25% en enero 2026 a clientes existentes, y cobra
  recargo de plataforma por usar pasarela de terceros (2% en Basic).

---

## Inventario del curso (Drive, carpeta compartida "Módulos")

Dueño: `etologiach@gmail.com` (Dra. Camila Hernández). **Compartida, no
propia** — si revoca el acceso se pierde. Copiar a una cuenta de la academia.

| Qué | Cuánto |
|---|---|
| 11 videos de módulo (MP4) | 1.23 GB |
| 11 audios narrados (M4A) | 358 MB |
| Clips de sonidos de gato (WMV, por diapositiva) | ~33 MB |
| `Quiz 1-11.docx` | los exámenes, ya escritos |

Es el curso de **Lenguaje y Comunicación de los Gatos** ($1,400).

**RESUELTO (1-ago): los MP4 de Drive son las lecciones reales.** Ya no hace
falta bajar 11 videos a mano de Kajabi.

Se comparó la duración en Kajabi contra el peso del archivo en Drive, en dos
módulos y en dos tipos de archivo distintos:

| | Kajabi | Video | kbps | Audio | kbps |
|---|---|---|---|---|---|
| Módulo 1 | 50:24 | 100.7 MB | 266 | 30.1 MB | 80 |
| Módulo 2 | 1:08:54 | 147.2 MB | 285 | 40.2 MB | 78 |

Las cuatro tasas caen en la misma banda, y son exactamente las que produce una
presentación narrada con diapositivas casi estáticas. Extrapolando el curso
completo salen **dos estimaciones independientes que coinciden al 2%: 9.9 h por
el video y 10.1 h por el audio.** No falta contenido.

Lo único que no queda probado es que sean idénticos pixel por pixel; si hubo
retoque, no fue de duración.

### Estructura real del curso en Kajabi (producto 2149395985)

**12 secciones, no 11.** Cada módulo es 1 lección de video + 1 quiz — por eso
no hace falta tabla de módulos. Pero antes del Módulo 1 hay una sección
**Introducción** con 4 piezas que **no están ni en Drive ni en el docx**:

- Introducción al curso
- Codigo de ética y conducta
- Profesora
- **Quiz** ← sus preguntas no vienen en `Quiz 1-11.docx`

**Ya extraída: `contenido/introduccion.md`.** Ninguna de las cuatro piezas tiene
video. Y traía **tres reglas del negocio que no estaban en ningún otro lado**:

| Regla | Estado |
|---|---|
| **Acceso de 5 meses** | Corregido: `inscripciones.expira_en` + `inscrito_en()` lo respeta. Antes el acceso era eterno, o sea más de lo que se vende |
| **Se aprueba con más de 80, no con 70** | Corregido en `calificar()` y en el aula. Con 6 preguntas hay que acertar 5 |
| **Constancia con validez curricular** al aprobar todos los quizes | 🔴 **NO implementada.** Es una promesa hecha al alumno que la plataforma nueva hoy no cumple |

Y el "Quiz" de esa sección **no es un examen**: son dos casillas de aceptación
(la información del curso y el Código de Ética). Modelarlo como examen
calificado habría sido un error; se guarda en `inscripciones.acepto_terminos_en`.

**Y hay 21 alumnos (`Customers (21)`) que migrar.** Se exportan por
`Contacts → Bulk Actions → Export`; el CSV llega por correo y el link expira a
los 3 días. Para darlos de alta, Admin API, no `INSERT` (ver abajo).

**Transcripción con Whisper: no ahora**, no es parte de migrar. Cuando toque,
usar los M4A (358 MB) y no los MP4 (1.23 GB) — Whisper solo lee el audio.

---

## Fases

| | Qué | Estado |
|---|---|---|
| 0 | Sitio de marketing fuera de Kajabi | **cerrada** — desplegada y verificada en vivo |
| 1 | Aula: login, cursos, video, progreso | **aplicado y probado** en Supabase |
| 2 | Exámenes | **cargados y cotejados** contra el docx |
| 3 | Stripe: checkout y panel de pagos | pendiente |
| 4 | Subir los videos y apagar Kajabi | pendiente |

Kajabi no se cancela hasta que la fase 4 esté verificada.

**Fase 1 — esquema en `supabase/migrations/0001_aula.sql`, SIN APLICAR.** Seis
tablas: `perfiles`, `cursos`, `lecciones`, `inscripciones`, `preguntas`,
`progreso`, más `respuestas_correctas`. Decisiones que vale la pena conocer:

- **No hay tabla de módulos.** Hoy cada módulo del curso de gatos es un video
  más su examen, o sea una lección. Si el Diplomado resulta tener varias
  lecciones por módulo, se agrega entonces.
- **La clave de respuestas vive en su propia tabla, sin política de lectura.**
  RLS filtra filas, no columnas: si la respuesta correcta estuviera en
  `preguntas`, cualquier alumno con la sesión abierta podría leerla desde el
  navegador y el examen no valdría nada. Solo `calificar()` la consulta, por
  dentro, como `security definer`.
- **Nadie se borra.** Un alumno des-inscrito se marca `cancelada`. En Kajabi
  borrar un contacto borra su progreso sin recuperación; no repetir eso.
- **`calificar()` se queda con la mejor calificación**, no con la última:
  reprobar un reintento no debe borrar un examen ya aprobado.

**Proyecto: `celebios-aula`, ref `lwawpdjsfjvlyvqwqiqp`, región us-east-1, plan
Free ($0/mes).** Crearlo no costó nada — la suposición previa de que hacían
falta $25 era errónea; el Pro solo se necesita cuando entren alumnos de verdad,
porque el Free **pausa el proyecto tras una semana sin tráfico** (es lo que ya
les pasó a `Expedix` y `dinero-montse`, ambos INACTIVE hoy).

**Probado contra la base real, no solo revisado:**

| Prueba | Resultado |
|---|---|
| ¿El alumno puede leer `respuestas_correctas`? | **No — 0 filas** |
| ¿Ve su curso, lección y preguntas estando inscrito? | Sí |
| ¿Puede ascenderse a `admin`? | **Bloqueado**, sigue `alumno` |
| Examen real del Módulo 1, clave real (D C C A B C) | 100, aprobado |
| Reintento peor sobre el mismo módulo | **Conserva el 100** |
| Módulo 2 con 3 de 6 | 50, reprobado (umbral 70) |
| `calificar()` sin inscripción | Excepción `no inscrito en este curso` |

Un bug que salió al aplicarlo: la política de "editar perfil propio" consultaba
`perfiles` dentro de su propia política, lo que **recursa infinito bajo RLS**.
Se corrigió con permisos por columna (`grant update (nombre, pais)`), que es lo
que Postgres ya trae para esto. `es_admin()` se salva de esa recursión solo
porque es `security definer`.

**Fase 1 — el aula existe: `aula/index.html`, publicada en `/aula`.**

Sin framework y sin paso de compilación: un archivo estático que habla con
Supabase desde el navegador. No hace falta Next.js porque quien protege los
datos es el RLS de Postgres, no un servidor intermedio — y eso ya está probado.
La clave `sb_publishable_…` está hecha para vivir en el cliente; la
`service_role` no aparece en ningún archivo y no debe hacerlo nunca.

Recorrido completo verificado en el navegador, con un alumno real y borrado
después: entrar → ver su curso con avance → abrir la lección → contestar el
examen de 6 preguntas → sacar 100% → volver y ver el avance ya en "1 de 11
lecciones aprobadas · 9%". Las lecciones sin video muestran un aviso honesto,
no un reproductor vacío.

**Panel de admin: `aula/admin.html`, publicado en `/aula/admin`.** Muestra
alumnos registrados, inscripciones activas y total registrado como pagado; una
tabla con quién pagó, cómo, cuánto y su avance; alta manual de un alumno a un
curso; y el editor donde se ponen **los títulos reales de los módulos y la liga
del video** de cada lección. Escribe desde el navegador, sin servidor, porque
`es_admin()` se evalúa en la base y es `security definer`: el permiso no
depende de que el cliente diga la verdad.

Probado con un admin y una alumna reales, ambos borrados después. Lo que se
verificó del lado del alumno, saltándose la interfaz y usando su propia sesión:

| Intento | Resultado |
|---|---|
| Entrar al panel | Pantalla "esta cuenta no es de administración" |
| Editar una lección por API | **0 filas tocadas**, `Módulo 2` intacta |
| Auto-inscribirse a un curso | **403** |
| Leer `respuestas_correctas` | Arreglo **vacío** |
| Leer perfiles de otros | Solo el suyo (1) |

⚠️ **Detalle que engaña:** el PATCH bloqueado devuelve **200 con arreglo
vacío**, no 403. RLS filtra filas en silencio en los `UPDATE`. Quien pruebe
seguridad mirando solo el código de estado va a concluir que la escritura
funcionó. Hay que revisar el cuerpo, o mejor, la base.

### ⚠️ Para la Fase 4: importar alumnos a `auth.users` por SQL casi no funciona

Crear usuarios con `INSERT` directo falla de formas que no dicen la verdad. Lo
que costó descubrirlo, para no repetirlo al migrar a los alumnos de Kajabi:

| Síntoma | Causa real |
|---|---|
| `invalid_credentials` con la contraseña correcta | Falta la fila en `auth.identities`; GoTrue busca al usuario por su identidad de proveedor |
| `500 Database error querying schema` | `confirmation_token` y los demás campos de token en **NULL**: GoTrue los lee como texto y no tolera nulos. Deben ir en `''` |
| Lo mismo tras arreglar lo anterior | `created_at` / `updated_at` nulos en `auth.identities` |

También hay que poner `instance_id` en ceros y
`raw_app_meta_data = {"provider":"email","providers":["email"]}`.
`auth.identities.email` es columna generada y no se puede escribir.

**Conclusión práctica:** para importar a los alumnos reales, usar la Admin API
de Supabase (`auth.admin.createUser`) desde un script de servidor, no `INSERT`.
Deja las tablas consistentes solo. Y de Kajabi no salen las contraseñas, así
que cada alumno definirá la suya con una liga de acceso.

**Fase 2 — hecho y cargado.** `Quiz 1-11.docx` extraído de Drive a
`contenido/quiz-gatos.txt`, y `parse_quiz.py` lo convierte a JSON verificando
11 módulos × 6 preguntas = 66, cada una con 4 opciones y respuesta válida. Si
el docx cambia y algo se rompe, el script revienta al parsear, no en producción.

Ya están en la base: 11 lecciones, 66 preguntas, 66 claves. **Cotejado, no
asumido:** la secuencia completa de respuestas y los md5 de enunciados
(`459cacc…`) y de opciones (`62e0084…`) coinciden byte por byte con el JSON
derivado del docx. **Los 11 títulos reales ya están puestos** (tomados de Kajabi el 1-ago), y
calzan uno a uno con los exámenes: el Módulo 6 "Marcaje y territorialidad" con
el quiz de feromonas, el 7 "Vocalizaciones y tacto" con el del ronroneo y el
cacareo. Eso confirma que el docx corresponde a estos módulos y en este orden.

---

## Bloqueado por permisos (intentado, no rodeado)

Estas acciones las intenté y el clasificador de permisos las negó. No son
problemas técnicos:

- `git commit` y `git push` — la rama `migracion/fase-0` está creada y todo
  está en *staging* (111 archivos), falta confirmar el commit.
- Apagar Vercel Authentication del proyecto `celebios` — por eso el preview
  pide login y no pude verificarlo con `curl`. Angel sí lo ve desde su navegador.
- Levantar `vercel dev` para probar `cleanUrls` y el 301 en local.

Se desbloquean dando permiso en la sesión, o haciéndolas a mano.

---

## Fase 0 — cómo está armada

`python build.py` lee `redesign-v2/*.html`, coloca cada página en la ruta que
declara su propio `<link rel="canonical">`, reescribe los enlaces internos a
rutas **absolutas** y verifica que ninguno quede roto. Falla ruidosamente si
algo no cuadra.

Las rutas absolutas no son estética: con `cleanUrls`, un enlace relativo se
resuelve contra el directorio, así que `catalogo.html` dentro de
`/cursos/anestesia-contencion-fauna` apuntaría a `/cursos/catalogo.html`.

Resultado: 28 páginas, 0 enlaces rotos. Quedan fuera 4 archivos que son
maquetas de diseño sin canonical (`estacion-de-campo`, `visor-de-especie`,
`lamina-viva-v1-coral`, `index` comparador).

El `vercel.json` lleva el redirect que más vale del proyecto: 301 de
`/rehabilitacion-fauna-2024` (la página de Wix que rankea #3 nacional y dice
"inscripciones cerradas") al diplomado vivo.

**Verificado en el deploy, no supuesto:** las 9 rutas probadas dan 200
—incluidas las anidadas sin `.html`, el logo y las dos páginas del aula— y
`/rehabilitacion-fauna-2024` aterriza en `/diplomado-rescate-rehabilitacion-fauna`
con el título correcto. `cleanUrls` y el 301 funcionan.

Falta un paso que **no** es técnico y sí es irreversible: apuntar `celebios.com`
a este proyecto y retirar el Wix. Eso lo decide Angel.

---

## Decisiones abiertas

0. **Los proyectos `Expedix` y `dinero-montse` están PAUSADOS en Supabase.** Un
   proyecto pausado no despierta solo: hay que reactivarlo a mano. Si alguna
   app apunta a esas bases, lleva días caída. Revisar aparte de esto.
1. **¿Equipo de Vercel y org de Supabase?** Hoy el proyecto quedó dentro de `konecta-estudio`,
   que mezcla negocios. La alternativa es un equipo propio de CELEBIOS
   (+$20/mes). No es puerta de un solo sentido: los proyectos se transfieren
   entre equipos después.
2. **¿Los MP4 de Drive son los editados?** (ver arriba)
3. **¿Cuándo se apunta celebios.com aquí?** Es el paso irreversible: implica
   desmontar el Wix viejo. No se hace sin decirlo.
4. **Correos.** Si hoy Kajabi manda los correos de la academia, hace falta
   reemplazo antes de apagarlo. Sin confirmar.
5. `redesign-v2/` **no está en git.** Las 28 páginas y todo el harvest viven
   solo en el disco de Angel.
