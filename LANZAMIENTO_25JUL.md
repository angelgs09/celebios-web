# CELEBIOS — lo que está apagado hoy (verificado 25-jul-2026, 01:00)

Todo lo de abajo lo comprobé con peticiones HTTP reales hoy, no es memoria. Cualquiera puede repetirlas.

---

## Las 3 fugas

### 1. La página que trae el tráfico está apagada
`https://www.celebios.com/rehabilitacion-fauna-2024` → **HTTP 200**, sigue en Wix (`server: Pepyaka`, `x-wix-request-id`).
Contiene literal: **"INSCRIPCIONES CERRADAS"** y el precio **19,500**.
Enlaces desde ahí al sitio nuevo: **cero**.

Quien busca el diplomado en Google llega aquí, lee que está cerrado, y se va. Es la única puerta con tráfico y está clausurada.

### 2. De 28 páginas construidas, 4 están publicadas
Probé los slugs contra `www.celebios.online`:

| Estado | Slug |
|---|---|
| 200 | `/cursos` |
| 200 | `/curso-lenguaje-felino` |
| 200 | `/diplomado-rescate-rehabilitacion-fauna` |
| 200 | `/nosotros` |
| **302 → /library** | `/` (la home ni siquiera existe: cae al default de Kajabi) |
| 404 | `/curso-nutricion` |
| 404 | `/recursos` |
| 404 | `/animal-silvestre-herido-que-hacer` |
| 404 | `/como-ser-rehabilitador-fauna-silvestre-mexico` |
| 404 | `/cuanto-gana-veterinario-fauna-silvestre` |

En disco hay **28 archivos `kajabi/*.kajabi.html` listos para pegar**. Llevan ahí desde el 20-jun. Son 16 artículos de búsqueda long-tail + 6 landings de curso + recursos: exactamente el material que hace que alguien encuentre la academia sin pagar publicidad.

### 3. Las páginas vivas se auto-sabotean en Google
Los **57 canonicals** del proyecto apuntan a `www.celebios.com/<slug>`… y ese destino da **404**:

- `www.celebios.com/curso-lenguaje-felino` → **404**
- `www.celebios.com/diplomado-rescate-rehabilitacion-fauna` → **404**

Un canonical le dice a Google "la versión oficial de esta página está allá". Está señalando a una página que no existe. Es la instrucción más dañina que se le puede dar a un buscador.

### Bonus: hay un diplomado vendiendo sin página
**Nutrición y Alimentación de Fauna Silvestre, 4ª generación** (docente MVZ Maribel Anaya, práctica en el Zoológico de Cali — está en `redesign-v2/DATOS-REALES-harvest.md:46`).
Su landing existe en disco (`curso-nutricion.html`, 68 KB). Su slug da **404** en línea. Se está vendiendo por WhatsApp una generación que no tiene dónde aterrizar.

---

## Qué vale cerrar esto

El catálogo cobra **$1,400 por curso** y **$19,500–26,000 por diplomado**.
Una sola inscripción al diplomado que hoy se pierde por la página apagada paga varias veces el trabajo de encenderlo.

---

## Las dos formas de cobrarlo (elegir una, en la misma llamada)

**Opción A — efectivo**
$12,000 MXN por dejar el lanzamiento completo antes del 1-ago: las 23 páginas faltantes publicadas, los canonicals corregidos, la página del Diplomado de Nutrición abierta y la página de Wix reactivada.
**50% al arrancar ($6,000), 50% contra entrega verificada.**
Piso: $8,000 con $4,000 de anticipo. **Sin anticipo no arranca** — esa es la regla que rompe el patrón.

**Opción B — sin riesgo para la academia**
$0 por adelantado + **10% de cada inscripción que entre por el sitio durante 60 días**.
Son $1,950 por alumno de diplomado, $140 por curso. Esta es la que se ofrece si dice "ahorita no hay flujo": no cobra esta semana, pero deja un precio por escrito, que es lo que nunca ha existido.

---

## Los 3 datos que hay que pedir en la llamada

Sin esto no se publica nada (regla propia: cero datos inventados).

1. Fecha y precio vigente de la **próxima edición del Diplomado de Rehabilitación 2026**. El harvest detectó $20,384 en la convocatoria = $19,500 + 4% de PayPal; hay que confirmar si el precio base subió.
2. Fecha, precio y cupo del **Diplomado de Nutrición 4ª generación**.
3. **Acceso al editor de Wix** de celebios.com (para poder tocar la fuga #1). Si no lo dan, las 23 páginas de Kajabi se pueden publicar igual.

---

## El guion, en seis líneas

> Pa, encontré tres cosas apagadas en el sitio y te las quiero enseñar en cinco minutos.
> La página que Google le enseña a la gente cuando busca el diplomado dice "inscripciones cerradas". Es la única que trae gente.
> De las 28 páginas que armamos, hay 4 publicadas. Las otras 24 están hechas y guardadas.
> Y el diplomado de nutrición de la 4ª generación se está vendiendo sin página a dónde llegar.
> Lo puedo dejar todo encendido antes del viernes. Son $12,000, la mitad para arrancar.
> Y si prefieres no soltar nada hoy: lo hago gratis y me das el 10% de lo que entre por el sitio en 60 días. Tú dime cuál.

---

## Nota importante

Este documento es **la conversación**, no el trabajo. El trabajo (publicar las 24 páginas, corregir los 57 canonicals, abrir la página de nutrición) **no se empieza hasta que haya anticipo o acuerdo por escrito**.

Eso no es rigidez: es exactamente el hábito que falta. El sitio, el SEO y el harvest ya se entregaron sin precio una vez. Si se vuelve a hacer el trabajo antes de acordar el número, el número nunca llega.
