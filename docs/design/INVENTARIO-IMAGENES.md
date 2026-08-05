# Inventario de `redesign-v2/media/` — verificado abriendo cada archivo

4 de agosto de 2026. **Cada descripción viene de mirar la imagen, no de leer su
nombre.** En este proyecto ya pasó una vez que cinco de nueve "carteles" no lo
eran, y abajo hay al menos un archivo cuyo nombre no describe lo que se ve.

**27 archivos, ninguno huérfano.** Se reparten en dos usos que el diseño no debe
confundir:

- **12 fotografías** insertadas como `<img>` — 4 carteles, 4 de fauna, 4 de práctica
- **15 bandas de ambiente** usadas como fondo CSS, todas de **1400 × 300 px**

---

## Límite que condiciona el diseño

**Ninguna imagen sirve para un hero a pantalla completa.** La foto más ancha del
sitio tiene 843 px; la del hero actual (la lechuza), 384 px. Un diseño que pida
una fotografía de 1600 px de ancho no se puede construir con este material, y
generar una está prohibido. Las bandas de ambiente sí son anchas (1400 px) pero
miden 300 px de alto: son franjas, no fondos de página.

---

## Carteles (4) — la evidencia de recorrido

Son los carteles originales de programas de CELEBIOS. Tres llevan fecha impresa
y **uno no**: eso decide para qué sirve cada uno.

| Archivo | Qué se lee en el cartel | ¿Prueba impartición? |
|---|---|---|
| `cartel-medicina-preventiva-2017.webp` | "DIPLOMADO en medicina preventiva y manejo en cautiverio de FAUNA SILVESTRE (animales de compañía no convencionales) · **ABRIL-JULIO, 2017**" | **Sí**, con fecha |
| `cartel-diagnostico-terapeutica.webp` | "DIPLOMADO en DIAGNÓSTICO Y TERAPÉUTICA DE FAUNA SILVESTRE · animales de compañía no convencionales · **ABRIL-AGOSTO 2018** · MODALIDAD SEMIPRESENCIAL" | **Sí**, con fecha — aunque el nombre del archivo no la trae |
| `cartel-nutricion-2019.webp` | "Diplomado NUTRICIÓN Y ALIMENTACIÓN DE FAUNA SILVESTRE EN CAUTIVERIO · **INICIO: 3 DE JUNIO, 2019** · FORMATO: SEMIPRESENCIAL · Informes: www.celebios.com" | **Sí**, con fecha |
| `cartel-contencion-quimica-anestesia.webp` | "Diplomado CONTENCIÓN QUÍMICA Y ANESTESIA DE FAUNA SILVESTRE · **PRÓXIMAMENTE** · www.celebios.com" | **No.** Es un cartel de anuncio, no de edición impartida |

Imagen de cada uno: 2017, dos guacamayas y un lagarto sobre madera · 2018, un
caracara en blanco y negro bajo un velo azul · 2019, una jirafa ramoneando ·
contención, un tigre echado de frente.

**El de contención no puede usarse como prueba de que ese diplomado se dio.** Su
propio cartel dice que iba a abrir. Los otros tres sí sostienen la frase "esto se
impartió, aquí está el cartel con su fecha".

Dos de ellos se recortaron en una ronda anterior para quitar escudos de
universidades cuyo convenio no está confirmado por escrito. Están así a
propósito; no los "restaures".

---

## Fauna (4) — todas en cautiverio

| Archivo | Qué se ve | Tamaño | Advertencia |
|---|---|---|---|
| `fauna-cocodrilo-habitat.webp` | Cocodrilo en un estanque somero con vegetación | 720 × 902 | Se ve **malla metálica** abajo a la derecha: es un recinto |
| `fauna-grulla-coronada.webp` | Grulla coronada gris de pie sobre hojarasca | 640 × 853 | **Especie africana** (*Balearica regulorum*) en recinto con muro de roca artificial. Un MVZ lo nota: no la uses para ilustrar fauna latinoamericana |
| `fauna-loro-alimentacion.webp` | Guacamaya verde junto a un plato de alimento | 843 × 632 | Muro de roca artificial de fondo. **Es verde, no escarlata** — ya hubo que corregir un pie que decía *Ara macao* |
| `fauna-rapaz-alas-abiertas.webp` | Zopilote rey con las alas abiertas sobre una percha | 843 × 389 | Malla de fondo. Es un buitre del Nuevo Mundo, no una rapaz en sentido estricto |

**Las cuatro son animales bajo cuidado humano**, no vida libre. Eso encaja con una
academia de fauna en cautiverio y rehabilitación, y desencaja con cualquier
composición que quiera decir "naturaleza salvaje".

---

## Práctica (4)

| Archivo | Qué se ve | Tamaño | Advertencia |
|---|---|---|---|
| `practica-lechuza-auscultacion.webp` | Lechuza de campanario sostenida con guantes contra una filipina turquesa | 384 × 427 | **El rostro está recortado a propósito**: se ve del cuello hacia abajo. Es la única foto del hero, y la más pequeña del sitio |
| `practica-manejo-quelonio.webp` | Tortuga terrestre manipulada por dos personas con guantes y filipina | 640 × 374 | Sin rostros. Al fondo, una manta con estampado de tigre |
| `practica-equino-auscultacion.webp` | Un grupo alrededor de un caballo, encuadre de cintura para abajo; una mano en el corvejón | 576 × 449 | **El nombre miente**: no hay auscultación ni estetoscopio a la vista. Es manejo de un equino en campo |
| `practica-ecografo-consola.webp` | Consola de ecógrafo en penumbra, una mano sobre el teclado | 576 × 341 | Casi monocroma y muy oscura; sirve como textura, no como imagen protagonista |

Ninguna muestra un rostro identificable, y no es casualidad: se reencuadraron
para que dejaran de ser dato personal sin dejar de ser documentales. **No amplíes
el encuadre de ninguna.**

---

## Ambiente (15) — bandas, no fondos

`ambiente-bosque-tarde` · `claro-luz` · `cortina-luz` · `dosel-amanecer` ·
`dosel-contraluz` · `follaje-lluvia` · `hojarasca` · `humedal` · `luz-interior` ·
`matorral-seco` · `niebla-canada` · `ramas-cielo` · `rincon-anochecer` ·
`rio-montana` · `selva-nublada`

**Todas 1400 × 300 px**, todas ya en uso como fondo CSS, una por página. Son
vegetación y luz, sin animales ni personas, y por eso son el único material que
puede acompañar a un programa sin afirmar nada sobre él. Un hábitat de fondo no
dice "este curso trata de esto"; una foto de fauna sí.

Su proporción manda: **4.7:1**. Funcionan de franja entre secciones o de fondo de
una banda baja. No de fondo de tarjeta vertical ni de hero.
