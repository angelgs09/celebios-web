-- Dos cosas: una via para prorrogar accesos, y un tope a los reintentos del
-- examen.

-- ---------------------------------------------------------------- prorrogar --
-- 0003 revoco UPDATE sobre inscripciones y tiro la policy "admin actualiza
-- inscripcion", con buen motivo: el grant abarcaba la tabla entera, o sea
-- expira_en y monto_mxn, y ahi la policy era la unica capa. Pero eso dejo al
-- negocio sin ninguna forma de extender un acceso, y en la MISMA tanda el aula
-- estreno una tarjeta que le dice al alumno vencido "escribenos a
-- contacto@celebios.com" -- prometiendole una salida que no existia.
--
-- La primera inscripcion vence el 30-sep-2026.
--
-- El grant de tabla NO vuelve: el unico camino es esta funcion, que empieza
-- rechazando a quien no sea admin. Mismo patron que calificar() y
-- aceptar_terminos().
create or replace function prorrogar(p_alumno uuid, p_curso uuid, p_meses int)
returns timestamptz
language plpgsql security definer set search_path = public as $$
declare v_nueva timestamptz;
begin
  if not es_admin() then
    raise exception 'solo administracion puede prorrogar';
  end if;
  if p_meses is null or p_meses < 1 or p_meses > 24 then
    raise exception 'meses fuera de rango (1 a 24)';
  end if;

  -- greatest(expira_en, now()): prorrogar una inscripcion YA vencida cuenta
  -- desde hoy y no desde la fecha muerta. Sin esto, dar 5 meses en enero a una
  -- que vencio en septiembre la dejaria vencida hasta febrero.
  update inscripciones
     set expira_en = greatest(expira_en, now()) + make_interval(months => p_meses)
   where alumno_id = p_alumno and curso_id = p_curso
   returning expira_en into v_nueva;

  if v_nueva is null then
    raise exception 'no hay inscripcion de ese alumno en ese curso';
  end if;
  return v_nueva;
end $$;

-- from public, no from anon/authenticated: revocar a los roles nombrados deja
-- intacto el grant que Postgres otorga a PUBLIC. Ver 0004.
revoke execute on function prorrogar(uuid, uuid, int) from public;
grant  execute on function prorrogar(uuid, uuid, int) to authenticated;


-- --------------------------------------------------------- limite de intentos --
-- calificar() devuelve la calificacion EXACTA y los reintentos son gratis (el
-- upsert se queda con greatest(...)), asi que servia de oraculo: mandar todo "A"
-- y luego variar una respuesta a la vez revela cual era la correcta, porque el
-- porcentaje sube solo cuando se acierta. Con 6 preguntas de 4 opciones bastan
-- unos 18-24 envios para sacar 100 sin ver un video ni saber la materia. Y esa
-- calificacion es la que respalda una constancia con aval de CONCERVET.
--
-- El tope NO cambia lo que se le promete al alumno (sigue aprobando con 80% y
-- conservando su mejor nota): solo hace inviable la fuerza bruta. Tres intentos
-- por hora no estorban a nadie honesto -- quien reprueba tres veces seguidas
-- necesita volver a ver la clase, no un cuarto tiro -- y le cuestan al ataque
-- una jornada entera.
--
-- El numero es un parametro pedagogico: si la doctora prefiere otro, se cambia
-- aqui y en el mensaje del aula. Lo que no puede volver es que sean ilimitados.
alter table progreso add column if not exists intentos_ventana int not null default 0;
alter table progreso add column if not exists ventana_desde timestamptz;

-- Las columnas nuevas NO se otorgan a nadie: progreso solo tiene grants por
-- columna (alumno_id, leccion_id, video_visto_en) y calificar() escribe como
-- SECURITY DEFINER, asi que no los necesita.

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

  select count(*) into v_total from preguntas where leccion_id = p_leccion;
  if v_total = 0 then raise exception 'la leccion no tiene examen'; end if;

  select pr.intentos_ventana, pr.ventana_desde into v_intentos, v_ventana
  from progreso pr where pr.alumno_id = auth.uid() and pr.leccion_id = p_leccion;

  -- Ventana deslizante simple: si la anterior ya caduco, se reinicia la cuenta.
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
    -- Se queda la mejor calificacion, no la ultima: reprobar un reintento no
    -- debe borrar un examen ya aprobado.
    set calificacion     = greatest(progreso.calificacion, excluded.calificacion),
        aprobado         = progreso.aprobado or excluded.aprobado,
        intentos_ventana = excluded.intentos_ventana,
        ventana_desde    = excluded.ventana_desde;

  return query
    select p.calificacion, p.aprobado from progreso p
    where p.alumno_id = auth.uid() and p.leccion_id = p_leccion;
end $$;
