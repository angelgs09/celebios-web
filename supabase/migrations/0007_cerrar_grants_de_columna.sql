-- 0007: los grants de COLUMNA que sobrevivieron al cierre por tabla.
--
-- 0003 revoco INSERT/UPDATE/DELETE por TABLA. Pero Supabase concede los mismos
-- privilegios ADEMAS columna por columna, y esos son independientes: un
-- `revoke update on t from r` no toca al `revoke update (col) on t from r`.
-- Peor, `information_schema.role_table_grants` NO los lista -- hay que mirar
-- `information_schema.column_privileges`. Por eso 0003 parecio cerrado y no lo
-- estaba: es la tercera cara del mismo error de "el permiso llega por dos
-- caminos" (PUBLIC vs rol en 0004/0006, tabla vs columna aqui).
--
-- EL HUECO QUE IMPORTABA. Con una sesion de alumno legitima:
--   PATCH /rest/v1/perfiles?id=eq.<el suyo>   {"nombre":"quien sea"}
--   -> 200 OK, nombre cambiado.
-- La constancia se dibuja con perfiles.nombre, asi que cualquiera que acreditara
-- los once quizes podia emitirse un documento con validez curricular y folio
-- PG 144/26 de CONCERVET a nombre de otra persona. Verificado contra produccion
-- el 16-ago-2026 y revertido en el momento.
--
-- Nadie pierde nada al cerrarlo: el aula solo LEE perfiles (index.html:799) y
-- escribe unicamente por aceptar_terminos() y calificar(), las dos SECURITY
-- DEFINER. Lo unico que el navegador escribe directo son las dos cosas del panel
-- de admin, y son las unicas que se conservan:
--   lecciones(titulo, video_url)                     admin.html:269
--   inscripciones(alumno_id, curso_id, origen, monto_mxn)  admin.html:283

-- ---------------------------------------------------------------- perfiles --
-- El nombre de la constancia no lo decide el alumno. Si hay que corregirlo, lo
-- corrige CELEBIOS.
revoke update on perfiles from anon, authenticated;
revoke update (nombre, pais) on perfiles from anon, authenticated;

-- Y se va la policy que lo autorizaba: sin ella, ni un grant futuro reabre esto.
drop policy if exists "editar perfil propio" on perfiles;

-- ---------------------------------------------------------------- progreso --
-- El aula nunca escribe aqui: quien aprueba una leccion es calificar(), que
-- corre como definer. Estos grants solo permitian ensuciar filas.
revoke insert on progreso from anon, authenticated;
revoke update on progreso from anon, authenticated;
revoke insert (alumno_id, leccion_id, video_visto_en) on progreso from anon, authenticated;
revoke update (video_visto_en) on progreso from anon, authenticated;

-- ------------------------------------------------------------------ cursos --
-- Nadie edita cursos desde el navegador. El titulo, el precio y el flag de
-- publicado se tocan desde el panel de Supabase.
revoke update on cursos from anon, authenticated;
revoke update (id, titulo, slug, descripcion, precio_mxn, publicado) on cursos from anon, authenticated;

-- --------------------------------------------------------------- lecciones --
-- El panel solo guarda titulo y video_url. Ni crea lecciones ni cambia el numero.
revoke insert on lecciones from anon, authenticated;
revoke update on lecciones from anon, authenticated;
revoke insert (id, curso_id, numero, titulo, video_url, duracion_min) on lecciones from anon, authenticated;
revoke update (id, curso_id, numero, titulo, video_url, duracion_min) on lecciones from anon, authenticated;
grant  update (titulo, video_url) on lecciones to authenticated;

-- ----------------------------------------------------------- inscripciones --
-- El alta del panel manda exactamente cuatro campos; estado y expira_en salen
-- de sus defaults (activa, +5 meses).
revoke insert on inscripciones from anon, authenticated;
revoke insert (id, alumno_id, curso_id, estado, origen, stripe_payment_intent,
               monto_mxn, creada_en, expira_en, acepto_terminos_en)
  on inscripciones from anon, authenticated;
grant  insert (alumno_id, curso_id, origen, monto_mxn) on inscripciones to authenticated;

-- ------------------------------------------------------------ comprobacion --
-- Debe devolver EXACTAMENTE seis filas: las dos de lecciones y las cuatro de
-- inscripciones. Cualquier otra cosa que aparezca aqui es un hueco.
--
--   select table_name, column_name, grantee, privilege_type
--   from information_schema.column_privileges
--   where table_schema='public' and grantee in ('anon','authenticated')
--     and privilege_type in ('UPDATE','INSERT')
--   order by table_name, column_name;
