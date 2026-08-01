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

**Pendiente de confirmar:** si estos MP4 son el mismo corte que está montado en
Kajabi o una versión previa sin editar. Se resuelve comparando la duración de
un módulo en los dos lados.

**Transcripción con Whisper: no ahora**, no es parte de migrar. Cuando toque,
usar los M4A (358 MB) y no los MP4 (1.23 GB) — Whisper solo lee el audio.

---

## Fases

| | Qué | Estado |
|---|---|---|
| 0 | Sitio de marketing fuera de Kajabi | **construido, renderizado y subido**; deploy sin verificar en vivo |
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

**Fase 2 — hecho y cargado.** `Quiz 1-11.docx` extraído de Drive a
`contenido/quiz-gatos.txt`, y `parse_quiz.py` lo convierte a JSON verificando
11 módulos × 6 preguntas = 66, cada una con 4 opciones y respuesta válida. Si
el docx cambia y algo se rompe, el script revienta al parsear, no en producción.

Ya están en la base: 11 lecciones, 66 preguntas, 66 claves. **Cotejado, no
asumido:** la secuencia completa de respuestas y los md5 de enunciados
(`459cacc…`) y de opciones (`62e0084…`) coinciden byte por byte con el JSON
derivado del docx. Los títulos de lección son `Módulo N` — marcador honesto,
el título real está solo en Kajabi.

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
