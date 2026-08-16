-- Cierra los permisos que la migracion 0001 creia haber cerrado.
--
-- 0001 trae un bloque de "defensa en profundidad" con esta intencion escrita:
-- "Se quitan los permisos que ninguna pantalla usa, para que hagan falta dos
-- errores y no uno". El bloque revoca siempre `from authenticated` y nunca
-- menciona `anon`, asi que la mitad anonima conservo los permisos que Supabase
-- otorga por defecto -- INSERT, UPDATE, DELETE y TRUNCATE -- sobre las 7 tablas,
-- respuestas_correctas incluida.
--
-- Hoy no es explotable: sin JWT, auth.uid() es null y ninguna policy deja pasar
-- nada, asi que anon lee 0 filas de todo. El problema es que la segunda costura
-- no existe donde el comentario decia que existia. Basta que alguien agregue una
-- policy permisiva por descuido -- un `using (true)` en cursos para armar un
-- catalogo publico, digamos -- y para `authenticated` seguiria cerrado por falta
-- de grant, pero para `anon` se abriria de par en par y con escritura.

revoke insert, update, delete, truncate on
  perfiles, cursos, lecciones, inscripciones, preguntas, respuestas_correctas, progreso
  from anon;

-- TRUNCATE seguia otorgado a authenticated en las 7 tablas, y TRUNCATE NO PASA
-- POR RLS: la fila no se evalua, la tabla se vacia. Ninguna pantalla lo usa.
-- Es el permiso mas destructivo del conjunto y el unico que el RLS no puede
-- contener, asi que se va aunque hoy PostgREST no lo exponga.
revoke truncate on
  perfiles, cursos, lecciones, inscripciones, preguntas, respuestas_correctas, progreso
  from authenticated;

-- Ninguna pantalla actualiza inscripciones: el panel de admin solo INSERTA y en
-- sus 303 lineas no hay un solo .from('inscripciones').update(). El grant, en
-- cambio, abarcaba la tabla entera: expira_en, monto_mxn y estado. Ahi la policy
-- es_admin() era la unica capa, y si se rompe un alumno se auto-renueva por
-- PATCH los 5 meses de acceso que pago.
revoke update on inscripciones from authenticated;
drop policy if exists "admin actualiza inscripcion" on inscripciones;

-- crear_perfil() es funcion de trigger y quedo publicada como RPC en
-- /rest/v1/rpc/crear_perfil. Llamarla directo falla (el registro `new` no existe
-- fuera del trigger), asi que no es brecha, pero es una SECURITY DEFINER
-- expuesta que ningun cliente necesita. El trigger sigue corriendo: se dispara
-- como dueno de auth.users, no con los permisos de quien se registra.
revoke execute on function public.crear_perfil() from anon, authenticated;

-- OJO, y va contra lo que sugirio la auditoria: es_admin() e inscrito_en() NO se
-- pueden revocar. Doce policies las invocan -- entre ellas "perfil propio",
-- "lecciones si inscrito", "preguntas si inscrito" y "progreso propio" -- y en
-- Postgres una policy evalua sus funciones con los permisos del usuario de la
-- consulta. SECURITY DEFINER cambia con que permisos corre el CUERPO de la
-- funcion, nunca el derecho a llamarla. Quitarles EXECUTE deja a TODO alumno sin
-- poder leer nada. Las policies que las invocan se listaron con pg_policies; los
-- privilegios se comprobaron con has_function_privilege, que es lo que
-- corresponde (pg_policies muestra expresiones, no permisos).
--
-- Y ojo con el revoke de crear_perfil() de aqui arriba: NO SURTIO EFECTO. Ver
-- 0004_revoke_public.sql -- hay que revocar `from public`, no de los roles.
