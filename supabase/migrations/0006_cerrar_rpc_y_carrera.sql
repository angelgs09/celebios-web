-- Dos cierres que se escaparon: el ACL de las RPC y una carrera en el tope de
-- intentos.
--
-- LA LECCION, por tercera vez en tres migraciones: en Postgres un privilegio de
-- funcion puede venir por DOS caminos, y hay que cortar los dos.
--   1. El grant implicito a PUBLIC (`=X/postgres` en el ACL).
--   2. Los grants EXPLICITOS a roles, que en Supabase los pone
--      ALTER DEFAULT PRIVILEGES sobre cada funcion nueva (`anon=X/postgres`).
-- 0003 revoco solo de los roles y dejo PUBLIC: no-op. 0005 revoco solo de
-- PUBLIC y dejo el explicito de anon: no-op tambien, al reves. Se revoca de
-- `public, anon, authenticated` y luego se otorga a quien de verdad lo usa.

-- prorrogar la llama el panel de admin, siempre con sesion. anon no pinta nada.
revoke execute on function prorrogar(uuid, uuid, int) from public, anon, authenticated;
grant  execute on function prorrogar(uuid, uuid, int) to authenticated;

-- calificar y aceptar_terminos dependen de auth.uid(), que para anon es null:
-- llamarlas sin sesion no logra nada, pero eran dos RPC de ESCRITURA alcanzables
-- sin cuenta. Una linea de plpgsql no deberia ser la unica capa.
revoke execute on function calificar(uuid, jsonb) from public, anon;
grant  execute on function calificar(uuid, jsonb) to authenticated;

revoke execute on function aceptar_terminos(uuid) from public, anon;
grant  execute on function aceptar_terminos(uuid) to authenticated;

-- es_admin() e inscrito_en() se quedan como estan: 12 policies las invocan y una
-- policy evalua sus funciones con los permisos del usuario de la consulta.
-- Tocarles el ACL deja a todo alumno sin leer nada. Ver 0004.


-- El tope de 3 intentos de calificar() leia el contador con un SELECT sin
-- bloqueo y escribia un valor absoluto. Dos peticiones simultaneas leian el
-- mismo numero, las dos pasaban el chequeo y las dos escribian k+1: mandando la
-- RPC en rafaga cabia entera la fuerza bruta que el tope venia a impedir.
--
-- pg_advisory_xact_lock serializa por (alumno, leccion) y se suelta solo al
-- terminar la transaccion. No estorba: dos alumnos distintos, o el mismo alumno
-- en dos lecciones, no se tocan.
create or replace function calificar(p_leccion uuid, p_respuestas jsonb)
returns table (calificacion int, aprobado boolean)
language plpgsql security definer set search_path = public as $$
declare
  v_total int; v_bien int; v_pct int;
  v_intentos int; v_ventana timestamptz;
  c_tope constant int := 3;
  c_ventana constant interval := interval '1 hour';
begin
  if not inscrito_en((select curso_id from lecciones where id = p_leccion)) then
    raise exception 'no inscrito en este curso';
  end if;

  -- Antes de leer el contador, no despues.
  perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text || p_leccion::text, 0));

  select count(*) into v_total from preguntas where leccion_id = p_leccion;
  if v_total = 0 then raise exception 'la leccion no tiene examen'; end if;

  select pr.intentos_ventana, pr.ventana_desde into v_intentos, v_ventana
  from progreso pr where pr.alumno_id = auth.uid() and pr.leccion_id = p_leccion;

  if v_ventana is null or now() - v_ventana > c_ventana then
    v_intentos := 0;
    v_ventana  := now();
  end if;

  if v_intentos >= c_tope then
    raise exception 'demasiados intentos seguidos, espera una hora';
  end if;
  v_intentos := v_intentos + 1;

  select count(*) into v_bien
  from preguntas p join respuestas_correctas r on r.pregunta_id = p.id
  where p.leccion_id = p_leccion
    and p_respuestas->>p.numero::text = r.correcta;

  v_pct := round(v_bien * 100.0 / v_total);

  insert into progreso (alumno_id, leccion_id, calificacion, aprobado,
                        intentos_ventana, ventana_desde)
  values (auth.uid(), p_leccion, v_pct, v_pct >= 80, v_intentos, v_ventana)
  on conflict (alumno_id, leccion_id) do update
    set calificacion     = greatest(progreso.calificacion, excluded.calificacion),
        aprobado         = progreso.aprobado or excluded.aprobado,
        intentos_ventana = excluded.intentos_ventana,
        ventana_desde    = excluded.ventana_desde;

  return query
    select p.calificacion, p.aprobado from progreso p
    where p.alumno_id = auth.uid() and p.leccion_id = p_leccion;
end $$;

revoke execute on function calificar(uuid, jsonb) from public, anon;
grant  execute on function calificar(uuid, jsonb) to authenticated;
