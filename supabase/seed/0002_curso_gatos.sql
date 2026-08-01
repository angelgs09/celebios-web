-- Generado por contenido/quiz_to_sql.py — no editar a mano.
-- Fuente: Quiz 1-11.docx (Drive, carpeta Modulos)

insert into cursos (slug, titulo, precio_mxn, publicado)
values ('curso-lenguaje-felino', 'Lenguaje y Comunicación de los Gatos', 1400, false)
on conflict (slug) do nothing;

-- ---- Modulo 1
insert into lecciones (curso_id, numero, titulo)
select id, 1, 'Módulo 1' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál de las siguientes afirmaciones describe mejor la evolución histórica de la relación entre humanos y gatos?', '{"A": "Los gatos fueron domesticados directamente para la caza de aves", "B": "Su rol ha sido siempre exclusivamente funcional y sin vínculo emocional", "C": "Fueron domesticados en paralelo con los perros en la Edad Media", "D": "Pasaron de tener una relación simbiótica a ser considerados miembros de la familia"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'D' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué característica ha contribuido a la popularidad de los gatos en la cultura actual?', '{"A": "Su capacidad de obedecer comandos complejos", "B": "Su comportamiento predecible y muy fácil de entrenar", "C": "Su capacidad de adaptación a la rutina del humano y auge en las redes sociales", "D": "Su utilidad en trabajos agrícolas modernos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Cuál de los siguientes ejemplos representa mejor la importancia de comprender el lenguaje felino?', '{"A": "Interpretar el maullido siempre como hambre", "B": "Asumir que el gato evita el contacto por desobediencia", "C": "Reconocer que una cola erizada puede indicar estrés o miedo", "D": "Considerar que el gato no necesita interacción social"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál es una consecuencia positiva de una buena comprensión del lenguaje del gato?', '{"A": "Fortalecimiento del vínculo y reducción del estrés", "B": "Eliminación total de comportamientos instintivos", "C": "Mayor dependencia del gato hacia el humano", "D": "Disminución de la necesidad de enriquecimiento ambiental"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Cuál de los siguientes mitos sobre los gatos es incorrecto?', '{"A": "Los gatos pueden adaptarse a rutinas del hogar", "B": "Los gatos no se encariñan con las personas", "C": "Los gatos pueden ser educados", "D": "Los gatos pueden mostrar estrés mediante cambios de conducta"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Qué práctica refleja una adecuada convivencia con gatos?', '{"A": "Forzar contacto cuando el gato evita la interacción", "B": "Ignorar señales sutiles como cambios en la postura o mirada", "C": "Respetar sus tiempos, espacios y señales de comunicación", "D": "Interpretar todos los comportamientos como desobediencia"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 1 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 2
insert into lecciones (curso_id, numero, titulo)
select id, 2, 'Módulo 2' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Qué define principalmente la territorialidad en el gato?', '{"A": "Un comportamiento relacionado solo con la alimentación", "B": "La necesidad de establecer jerarquías sociales con otros gatos", "C": "La construcción, organización y protección de un espacio que el gato considera propio", "D": "Un comportamiento exclusivo de gatos ferales"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Cuál es una diferencia clave entre gatos y perros en relación con su organización conductual?', '{"A": "Los perros son territoriales y los gatos sociales obligatorios", "B": "Los gatos estructuran su mundo en torno al territorio y los perros en torno a la sociabilidad grupal", "C": "Ambos se organizan principalmente por jerarquías rígidas", "D": "Los gatos no presentan territorialidad significativa"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Qué característica describe mejor la organización de los gatos en exteriores?', '{"A": "Vagan sin estructura ni patrones definidos", "B": "Mantienen territorios fijos sin superposición con otros individuos", "C": "Organizan su espacio en campos de actividad con territorios superpuestos", "D": "Dependen exclusivamente de grupos sociales estables"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál de las siguientes afirmaciones describe mejor a los gatos ferales?', '{"A": "Son individuos que viven sin contacto humano positivo y no buscan interacción con personas", "B": "Son gatos domésticos en proceso de socialización con humanos", "C": "Son animales que necesitan obligatoriamente intervención humana para sobrevivir", "D": "Son gatos domésticos que viven temporalmente en exteriores"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Cuál es una ventaja importante de la vida indoor en gatos?', '{"A": "Reduce completamente la necesidad de enriquecimiento ambiental", "B": "Elimina la necesidad de comunicación con otros gatos", "C": "Disminuye el estrés al evitar conflictos territoriales y riesgos externos", "D": "Hace que el gato dependa totalmente del humano para su conducta social"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál de las siguientes medidas corresponde a una estrategia de seguridad para gatos con acceso a exteriores?', '{"A": "Permitir salidas libres sin supervisión", "B": "Evitar cualquier tipo de estructura cerrada", "C": "Instalación de mallas de seguridad o uso de catios", "D": "Aumentar el acceso sin control a zonas externas"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 2 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 3
insert into lecciones (curso_id, numero, titulo)
select id, 3, 'Módulo 3' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es el objetivo principal de la etología?', '{"A": "Tratar enfermedades físicas en animales domésticos", "B": "Estudiar el comportamiento de los animales en su ambiente natural para describirlo, explicarlo y predecirlo", "C": "Entrenar animales para convivir con humanos", "D": "Modificar conductas problemáticas en gatos indoor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Cuál de los siguientes factores NO corresponde a uno de los que influyen directamente en el comportamiento del gato?', '{"A": "Genética", "B": "Experiencias tempranas", "C": "Largo del pelaje", "D": "Factores ambientales"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Cuál de los siguientes enunciados refleja mejor la diferencia entre comportamiento y conducta?', '{"A": "El comportamiento es siempre aprendido y la conducta siempre instintiva", "B": "La conducta es un conjunto amplio de acciones y el comportamiento es una acción específica observable", "C": "No existe diferencia real entre comportamiento y conducta en gatos", "D": "El comportamiento es el conjunto general de respuestas del gato, mientras que la conducta es una manifestación específica y observable de ese comportamiento"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'D' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál de las siguientes afirmaciones describe mejor la comunicación en gatos?', '{"A": "Es un comportamiento sin intención social", "B": "Siempre ocurre solo entre animales de la misma especie", "C": "Es una conducta destinada a transmitir información a otro individuo", "D": "Es un reflejo automático sin función social"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Cuál de los siguientes es un ejemplo de factor ambiental que influye en el comportamiento felino?', '{"A": "Disponibilidad de refugios, juguetes y espacio en el hogar", "B": "Nivel de actividad de la madre", "C": "Presencia de enfermedades neurológicas", "D": "Tipo de aprendizaje escolar del tutor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál de las siguientes afirmaciones es correcta respecto a la comunicación animal?', '{"A": "Solo ocurre entre animales de la misma especie", "B": "Siempre es intencional y consciente", "C": "Puede ser visual, auditiva, química o táctil", "D": "No incluye señales químicas como feromonas"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 3 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 4
insert into lecciones (curso_id, numero, titulo)
select id, 4, 'Módulo 4' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, 'Sobre la visión felina, ¿cuál de las siguientes afirmaciones es correcta?', '{"A": "Los gatos ven en completa oscuridad gracias a su retina especializada", "B": "Perciben todos los colores con la misma intensidad que los humanos", "C": "Detectan mejor el movimiento que los detalles estáticos", "D": "Tienen un campo visual más reducido que el humano"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Cuál es la función principal del órgano vomeronasal en los gatos?', '{"A": "Regular la temperatura corporal mediante respiración", "B": "Detectar feromonas y señales químicas sociales", "C": "Mejorar la percepción de sonidos de alta frecuencia", "D": "Coordinar el equilibrio durante el salto"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Qué combinación de señales faciales se asocia más probablemente a miedo o estrés en un gato?', '{"A": "Pupilas dilatadas + orejas hacia adelante + bigotes extendidos", "B": "Pupilas contraídas + orejas erguidas + boca relajada", "C": "Pupilas dilatadas + orejas hacia atrás + bigotes pegados al rostro", "D": "Pupilas normales + parpadeo lento + orejas neutras"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál de las siguientes afirmaciones describe mejor el ronroneo en gatos?', '{"A": "Siempre indica bienestar y relajación", "B": "Solo aparece durante el sueño profundo", "C": "Es exclusivos de la interacción entre gatos adultos", "D": "Puede ocurrir tanto en contextos positivos como de estrés o dolor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'D' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué función cumple principalmente el marcaje con uñas en los gatos?', '{"A": "Solo afilar las uñas sin función comunicativa", "B": "Comunicación visual y química del territorio", "C": "Expresar hambre o solicitud de comida", "D": "Reducir exclusivamente el estrés sin función social"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál de las siguientes opciones describe mejor el rol del olfato en los gatos indoor?', '{"A": "Es secundario frente a la visión en la toma de decisiones", "B": "Solo se utiliza para detectar alimentos en mal estado", "C": "Es clave para reconocimiento social, seguridad y percepción del entorno", "D": "Se usa únicamente en situaciones de caza"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 4 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 5
insert into lecciones (curso_id, numero, titulo)
select id, 5, 'Módulo 5' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Por qué es importante interpretar las expresiones faciales y corporales en conjunto?', '{"A": "Porque las orejas son el único indicador confiable", "B": "Porque cada señal por separado siempre significa lo mismo", "C": "Porque un solo indicador puede ser engañoso sin el contexto", "D": "Porque el gato no usa múltiples señales a la vez"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué puede indicar un parpadeo lento en gatos?', '{"A": "Agresión inminente", "B": "Miedo extremo", "C": "Confianza y relajación", "D": "Dolor físico"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Cuál de las siguientes combinaciones indica generalmente juego o curiosidad?', '{"A": "Orejas hacia atrás + cuerpo arqueado + pelo erizado", "B": "Pupilas dilatadas + orejas erguidas + bigotes hacia adelante", "C": "Bigotes pegados al rostro + cola rígida + cuerpo tenso", "D": "Respiración rápida + postura encogida + orejas planas"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Qué caracteriza una postura defensiva o agresiva en gatos?', '{"A": "Cuerpo relajado y cola baja", "B": "Cuerpo arqueado, pelo erizado y orejas hacia atrás", "C": "Postura acostada y parpadeo lento", "D": "Bigotes relajados y movimientos suaves"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué puede significar una postura de alerta o curiosidad?', '{"A": "Desinterés total en el entorno", "B": "Estado de relajación profunda", "C": "Evaluación del entorno con disposición a explorar", "D": "Dolor o enfermedad"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Por qué es importante evitar interpretar una sola señal aislada (como orejas hacia atrás)?', '{"A": "Porque las orejas nunca cambian de significado", "B": "Porque siempre indica agresión", "C": "Porque puede tener distintos significados según el contexto y otras señales", "D": "Porque no tiene relevancia en la comunicación felina"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 5 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 6
insert into lecciones (curso_id, numero, titulo)
select id, 6, 'Módulo 6' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es la función principal de las feromonas faciales en los gatos?', '{"A": "Marcar agresivamente a otros gatos", "B": "Comunicar territorio seguro y familiaridad", "C": "Señalar hambre o necesidad de alimento", "D": "Advertir dolor físico"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué caracteriza al marcaje con uñas en los gatos?', '{"A": "Solo tiene función agresiva", "B": "No tiene ninguna función comunicativa", "C": "Deja feromonas y cumple función territorial", "D": "Solo ocurre en situaciones de miedo extremo"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Qué puede indicar el marcaje con orina en el hogar?', '{"A": "Siempre juego y exploración", "B": "Exclusivamente hambre", "C": "Comunicación territorial o estrés", "D": "Conducta aprendida sin significado"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Por qué es importante observar los tipos de marcaje en conjunto?', '{"A": "Porque el contexto y combinación de señales entrega información más completa", "B": "Porque cada uno tiene el mismo significado siempre", "C": "Porque el marcaje facial es el único importante", "D": "Porque solo importa el marcaje con orina"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué función cumplen las feromonas de estrés?', '{"A": "Indicar juego y socialización", "B": "Alertar sobre situaciones de miedo o incomodidad", "C": "Marcar territorio seguro", "D": "Atraer a otros gatos para apareamiento"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Qué puede significar el marcaje cerca de ventanas o entradas?', '{"A": "Hambre o aburrimiento", "B": "Ocupación del territorio y vigilancia del entorno", "C": "Problemas de visión del gato", "D": "Falta de vínculo con el tutor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 6 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 7
insert into lecciones (curso_id, numero, titulo)
select id, 7, 'Módulo 7' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es la principal función de las vocalizaciones en la comunicación felina?', '{"A": "Sustituir completamente el lenguaje corporal", "B": "Expresar estados emocionales e intenciones del gato", "C": "Solo pedir alimento", "D": "Evitar el contacto con otros gatos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué puede indicar un ronroneo en ciertos contextos?', '{"A": "Siempre felicidad absoluta", "B": "Solo juego entre gatos", "C": "Bienestar, pero también estrés o dolor según el contexto", "D": "Agresión inminente"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Qué caracteriza al "chatter" o cacareo en gatos?', '{"A": "Un sonido suave de saludo", "B": "Un maullido prolongado de petición", "C": "Un sonido asociado a excitación o frustración ante presas", "D": "Un tipo de ronroneo intenso"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál es la función principal del frotamiento en gatos?', '{"A": "Mostrar agresión territorial fuerte", "B": "Marcar con feromonas y reforzar vínculos sociales", "C": "Pedir comida de forma insistente", "D": "Evitar contacto con otros gatos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué indica un gato que presenta bigotes hacia adelante?', '{"A": "Miedo intenso", "B": "Relajación total sin interés", "C": "Exploración activa e interés en el entorno", "D": "Dolor físico severo"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Por qué es importante interpretar múltiples señales en conjunto?', '{"A": "Porque los gatos combinan varios canales para comunicar su estado emocional", "B": "Porque las vocalizaciones no son relevantes", "C": "Porque cada señal aislada siempre tiene el mismo significado", "D": "Porque el tacto es el único canal confiable"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 7 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 8
insert into lecciones (curso_id, numero, titulo)
select id, 8, 'Módulo 8' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Qué indican las conductas afiliativas en los gatos?', '{"A": "Conductas de defensa ante amenazas", "B": "Expresiones de afecto y fortalecimiento de vínculos", "C": "Problemas de salud emocional", "D": "Conductas de caza"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué función cumple el acicalamiento mutuo entre gatos?', '{"A": "Establecer competencia por comida", "B": "Reforzar vínculos sociales y confianza entre individuos", "C": "Marcar agresivamente el territorio", "D": "Reducir la necesidad de contacto social"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Qué caracteriza a la comunicación intraespecífica en gatos?', '{"A": "Comunicación exclusiva con humanos", "B": "Interacción solo mediante vocalizaciones", "C": "Interacción entre gatos mediante señales visuales, táctiles y olfativas", "D": "Uso exclusivo de maullidos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Cuál de las siguientes conductas es un ejemplo de apego seguro?', '{"A": "Evitar siempre al tutor", "B": "Mostrar miedo constante al entorno", "C": "Esconderse todo el día", "D": "Acercarse voluntariamente y explorar el entorno con confianza"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'D' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué indica el frotamiento de cabeza y mejillas en un gato?', '{"A": "Dolor físico", "B": "Marca amistosa y comunicación de afecto", "C": "Agresión territorial intensa", "D": "Falta de confianza en el tutor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál es una clave importante para fortalecer el apego seguro?', '{"A": "Forzar el contacto físico diario", "B": "Cambiar constantemente las rutinas", "C": "Respetar la individualidad del gato y permitir su iniciativa de interacción", "D": "Ignorar sus señales para que se acostumbre"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 8 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 9
insert into lecciones (curso_id, numero, titulo)
select id, 9, 'Módulo 9' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es el objetivo principal de las estrategias de afrontamiento en gatos?', '{"A": "Eliminar completamente las conductas del gato", "B": "Reprimir el comportamiento agresivo", "C": "Ayudar al gato a manejar sus emociones de forma saludable", "D": "Hacer que el gato obedezca al tutor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué puede indicar una cola que se mueve rápidamente de lado a lado?', '{"A": "Irritación o estrés", "B": "Juego tranquilo", "C": "Relajación", "D": "Sueño profundo"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Por qué el castigo no es recomendable en gatos con conducta agresiva?', '{"A": "Porque el gato no entiende el castigo", "B": "Porque aumenta el miedo y puede empeorar la agresión", "C": "Porque hace al gato más sociable", "D": "Porque solo funciona en gatos adultos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Qué estrategia ayuda a reducir la ansiedad anticipatoria en gatos?', '{"A": "Cambiar constantemente los horarios", "B": "Evitar la alimentación regular", "C": "Mantener rutinas predecibles", "D": "Aumentar los estímulos inesperados"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Qué puede significar el ronroneo acompañado de tensión corporal?', '{"A": "Felicidad absoluta", "B": "Sueño profundo", "C": "Estrés o dolor", "D": "Juego activo"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál es una razón importante para llevar un registro de conductas del gato?', '{"A": "Controlar cuánto juega el gato", "B": "Identificar patrones de estrés y ajustar estrategias", "C": "Demostrar obediencia del gato", "D": "Compararlo con otros gatos"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 9 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 10
insert into lecciones (curso_id, numero, titulo)
select id, 10, 'Módulo 10' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es uno de los principales problemas de humanizar al gato?', '{"A": "Que el gato aprende más lento", "B": "Que se interpretan mal sus conductas", "C": "Que el gato deja de jugar", "D": "Que el gato se vuelve más dependiente"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué puede significar que un gato se esconda?', '{"A": "Que busca seguridad o evita estrés", "B": "Que quiere llamar la atención", "C": "Que está enojado con su tutor", "D": "Que está jugando"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Cuál de las siguientes es una señal de juego en un gato?', '{"A": "Orejas hacia atrás", "B": "Gruñidos constantes", "C": "Movimientos suaves y pausas", "D": "Pelo erizado"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, '¿Qué indica un gato con orejas hacia atrás, gruñidos y cuerpo rígido?', '{"A": "Que está relajado", "B": "Que quiere dormir", "C": "Que está jugando", "D": "Que muestra agresión o incomodidad"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'D' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Por qué es un error interpretar el estrés como "mal carácter"?', '{"A": "Porque el gato no tiene carácter", "B": "Porque son señales de incomodidad o malestar", "C": "Porque el gato siempre está tranquilo", "D": "Porque es una conducta poco común"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál es la clave para interpretar correctamente la comunicación felina?', '{"A": "Castigar cuando se equivoca", "B": "Ignorar las conductas", "C": "Observar el contexto y respetar su lenguaje", "D": "Tratarlo como a una persona"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 10 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;

-- ---- Modulo 11
insert into lecciones (curso_id, numero, titulo)
select id, 11, 'Módulo 11' from cursos where slug = 'curso-lenguaje-felino'
on conflict (curso_id, numero) do nothing;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 1, '¿Cuál es el propósito de aplicar el refuerzo positivo en la comunicación con el gato?', '{"A": "Evitar que el gato juegue demasiado", "B": "Generar un lenguaje común basado en asociaciones positivas", "C": "Enseñar obediencia inmediata", "D": "Reducir el tiempo de interacción"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 1
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 2, '¿Qué efecto tiene el castigo en la comunicación con el gato?', '{"A": "Mejora la obediencia rápidamente", "B": "Refuerza conductas positivas", "C": "Genera miedo y dificulta la confianza", "D": "No tiene ningún efecto"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 2
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 3, '¿Por qué las rutinas ayudan a mejorar la comunicación con los gatos?', '{"A": "Porque permiten anticipar situaciones y reducen el estrés", "B": "Porque eliminan la necesidad de interactuar", "C": "Porque aumentan su energía", "D": "Porque hacen al gato más dependiente"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 3
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 4, 'En los ejercicios prácticos, ¿qué se debe considerar al trabajar con gatos tímidos?', '{"A": "Permitir un acercamiento gradual y respetar su ritmo", "B": "Aumentar la intensidad de inmediato", "C": "Forzar el contacto físico", "D": "Evitar cualquier interacción"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'A' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 4
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 5, '¿Cuál es una señal de incomodidad en un gato durante un ejercicio?', '{"A": "Ronroneo constante", "B": "Orejas hacia atrás y cola moviéndose rápido", "C": "Dormir profundamente", "D": "Acercarse al tutor"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'B' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 5
on conflict (pregunta_id) do update set correcta = excluded.correcta;

insert into preguntas (leccion_id, numero, enunciado, opciones)
select l.id, 6, '¿Cuál es la idea principal al finalizar el curso sobre comunicación felina?', '{"A": "Convertirse en experto en comportamiento felino", "B": "Enseñar trucos avanzados al gato", "C": "Ser un observador consciente y mejorar la interacción diaria en casa", "D": "Disminuir la dependencia de mi gato"}'::jsonb
from lecciones l join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11
on conflict (leccion_id, numero) do nothing;

insert into respuestas_correctas (pregunta_id, correcta)
select p.id, 'C' from preguntas p
join lecciones l on l.id = p.leccion_id
join cursos c on c.id = l.curso_id
where c.slug = 'curso-lenguaje-felino' and l.numero = 11 and p.numero = 6
on conflict (pregunta_id) do update set correcta = excluded.correcta;
