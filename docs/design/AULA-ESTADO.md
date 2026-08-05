# El aula: qué existe hoy, qué no, y qué se sabe de los alumnos

4 de agosto de 2026. Contexto para diseñar la plataforma. Todo lo de aquí está
verificado contra el código, el esquema y los datos rescatados de Kajabi — no
contra recuerdos.

CELEBIOS se está saliendo de Kajabi, que **suspende la cuenta el 30 de agosto de
2026** por $207.64 de adeudo. El aula nueva vive en `aula/` (dos archivos HTML
estáticos, sin framework) contra Supabase, y quien protege es el RLS, no el
cliente. Doc maestro de la migración: `MIGRACION.md`.

---

## Lo que ya existe y funciona

**Aula del alumno — `aula/index.html`, cuatro vistas:**

| Vista | Qué hace |
|---|---|
| `v-login` | correo + contraseña, o liga mágica |
| `v-cursos` | saludo y lista de cursos inscritos |
| `v-intro` | introducción al curso y código de ética, con aceptación de términos |
| `v-leccion` | título, video y examen |

**Panel de administración — `aula/admin.html`:** login, pantalla de acceso
denegado, y un panel con alumnos y pagos, alta manual de alumno, y lecciones.

**Base de datos (`supabase/migrations/0001_aula.sql`), aplicada y probada:**
`perfiles` · `cursos` · `lecciones` · `inscripciones` · `preguntas` ·
`respuestas_correctas` · `progreso`, más las funciones `es_admin`,
`inscrito_en`, `calificar` y `aceptar_terminos`.

Dos decisiones que conviene no deshacer:

- **No hay tabla de módulos.** Un módulo del curso es un video más su examen, o
  sea una lección.
- **La clave de respuestas vive en su propia tabla y sin política de lectura.**
  RLS filtra filas, no columnas: si la respuesta correcta estuviera en
  `preguntas`, cualquier alumno con la sesión abierta la leería desde el
  navegador y el examen no valdría nada. Solo `calificar()` la consulta, por
  dentro.

**Exámenes: 66 preguntas cargadas y cotejadas por md5 contra el docx original.**
Son **11 módulos × 6 preguntas** de opción múltiple A–D. Probado de punta a
punta en el navegador con un alumno real: entrar → curso → lección → examen →
100% → avance. Y probado por el lado feo: editar una lección desde la cuenta del
alumno toca cero filas, auto-inscribirse da 403, la clave de respuestas devuelve
vacío.

---

## Lo que NO existe

- **Ninguna pantalla dice en qué te quedaste.** Hay lista de cursos y hay
  lección; no hay "continuar donde ibas" ni un mapa del avance.
- **No hay reproductor con temario al lado.** El video es un elemento suelto
  dentro de la vista de lección.
- **No hay constancia.** Ninguna pantalla, ningún generador, nada.
- **No hay cobro.** Stripe es la fase 3 y está pendiente; hoy el alta de alumno
  es manual desde el panel.
- **No hay video servido.** `api/video.js` está escrito y pide la lección a
  Supabase con el token del alumno para que decida el RLS, pero **los 1.23 GB
  del curso todavía no están subidos**. Hoy una lección abre sin video.

---

## Dos cosas que el diseño debe corregir, no heredar

**1. Las once lecciones se llaman "Módulo 1" … "Módulo 11".** Son placeholders
del seed. Los títulos reales existen y están documentados en
`redesign-v1/CONTENIDO-REAL.md`: el mundo de los gatos · territorialidad ·
principios de comportamiento y comunicación · percepción · expresiones faciales
y posturas · marcaje · vocalizaciones y tacto · señales de afecto y apego ·
señales de estrés, ansiedad, miedo y agresión · errores comunes de
interpretación · cómo mejorar la comunicación. Un alumno entra hoy y ve once
cajas numeradas sin nombre.

**2. El curso tiene 12 secciones, no 11.** Antes del Módulo 1 hay una
**Introducción** con cuatro piezas —introducción al curso, código de ética y
conducta, la profesora, y un quiz propio cuyas preguntas no están en el docx—.
Ya extraída en `contenido/introduccion.md`. La vista `v-intro` la cubre a
medias.

---

## Lo que se sabe de los alumnos reales (rescatado de Kajabi)

Datos, no supuestos. Viven fuera del repo por ser personales
(`Desktop/CELEBIOS-web/kajabi-export/`, en `.gitignore`).

- **330 contactos** y **$501,589 MXN** de histórico.
- **21 alumnos** en el curso de gatos: 18 de pago y 3 internas. 14 vigentes.
- **7 pagaron y nunca entraron.** Un tercio del curso. Es el agujero más grande
  que tiene este producto, y no es de contenido: es de arranque.
- **71 alumnos** en los dos diplomados, **22 de ellos al 100%**.
- **La constancia se prometía y casi no se emitía: 2 en gatos, 0 en los
  diplomados, con 24 alumnos al 100%.** La promesa ya se incumplía en Kajabi y
  la plataforma nueva la hereda sin implementar.

---

## Qué significa esto para el diseño

El aula no tiene un problema de funcionalidad: el examen califica, el progreso
avanza y la seguridad aguanta que la ataquen desde la cuenta del alumno. Tiene
un problema de **entrada y de cierre**.

De entrada, porque un tercio de los que pagaron nunca abrió la primera lección y
lo primero que verían son once cajas llamadas "Módulo 1".

De cierre, porque los que sí llegan al 100% no reciben lo que se les prometió.
