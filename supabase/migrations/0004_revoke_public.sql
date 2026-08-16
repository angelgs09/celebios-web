-- Cierra de verdad lo que 0003 creyo cerrar.
--
-- 0003 hizo `revoke execute on function crear_perfil() from anon, authenticated`
-- y no sirvio de nada. Postgres otorga EXECUTE a PUBLIC en toda funcion nueva, y
-- ese grant aparece en el ACL como la entrada sin rol `=X/postgres`. Revocar a
-- los roles nombrados borra sus entradas explicitas y deja PUBLIC intacto, asi
-- que anon y authenticated siguen pudiendo llamarla por herencia:
--
--   crear_perfil  proacl = {=X/postgres,postgres=X/postgres,service_role=X/postgres}
--   has_function_privilege('anon','crear_perfil()','EXECUTE') = true   <-- seguia true
--
-- Es el mismo error que 0001 cometio con los grants de tabla y que 0003 nacio
-- para arreglar: documentar un cierre que no ocurrio. REGLA PARA ESTE REPO:
-- revocar EXECUTE va SIEMPRE `from public`, nunca `from anon, authenticated`.

revoke execute on function public.crear_perfil() from public;

-- Y por lo mismo, una advertencia para quien venga: NO hacer esto con es_admin()
-- ni con inscrito_en(). Doce policies las invocan -- entre ellas "perfil propio",
-- "lecciones si inscrito", "preguntas si inscrito" y "progreso propio" -- y una
-- policy evalua sus funciones con los privilegios del usuario de la consulta.
-- SECURITY DEFINER cambia con que permisos corre el CUERPO, nunca el derecho a
-- llamarla. Un `revoke ... from public` sobre esas dos deja a TODO alumno sin
-- poder leer nada. La auditoria del 16-ago pidio revocarlas; se verifico con
-- has_function_privilege y pg_policies antes de no hacerlo.
--
-- Nota para la proxima auditoria, para no volver a levantar falsos positivos:
-- `rls_enabled_no_policy` en respuestas_correctas es DELIBERADO. Esa tabla es
-- deny-all a proposito, admin incluido: la clave del examen solo la lee
-- calificar(), que es SECURITY DEFINER.
