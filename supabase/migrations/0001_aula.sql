-- Aula CELEBIOS — esquema minimo para sustituir a Kajabi.
--
-- Dos roles: alumno y admin. Un alumno solo ve los cursos en los que esta
-- inscrito, y solo su propio progreso. El admin ve todo.
--
-- ponytail: no hay tabla de modulos. Hoy cada modulo del curso de gatos es
-- exactamente un video mas su examen, o sea una leccion. Si el Diplomado de
-- Rehabilitacion resulta tener varias lecciones por modulo, se agrega
-- lecciones.modulo entonces, no antes.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- perfiles

create table perfiles (
  id            uuid primary key references auth.users on delete cascade,
  nombre        text not null,
  -- auth.users no es legible desde el cliente, asi que el correo se copia aqui
  -- al registrarse: sin el, el panel de admin no puede identificar a nadie.
  correo        text,
  pais          text,
  rol           text not null default 'alumno' check (rol in ('alumno','admin')),
  -- Kajabi solo exporta el porcentaje global por alumno, no el detalle por
  -- leccion. Se guarda como dato historico; el progreso fino arranca de cero.
  progreso_kajabi_pct  int check (progreso_kajabi_pct between 0 and 100),
  creado_en     timestamptz not null default now()
);

create function es_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from perfiles where id = auth.uid() and rol = 'admin');
$$;

-- El perfil se crea solo al registrarse; si no, un usuario autenticado sin
-- perfil rompe todas las politicas de abajo.
create function crear_perfil() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into perfiles (id, nombre, correo)
  values (new.id,
          coalesce(new.raw_user_meta_data->>'nombre', split_part(new.email,'@',1)),
          new.email);
  return new;
end $$;

create trigger al_crear_usuario
  after insert on auth.users for each row execute function crear_perfil();

-- ----------------------------------------------------------------- catalogo

create table cursos (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null,
  titulo      text not null,
  descripcion text,
  precio_mxn  int check (precio_mxn >= 0),
  publicado   boolean not null default false
);

create table lecciones (
  id           uuid primary key default gen_random_uuid(),
  curso_id     uuid not null references cursos on delete cascade,
  numero       int not null,
  titulo       text not null,
  video_url    text,
  duracion_min int check (duracion_min > 0),
  unique (curso_id, numero)
);

-- ------------------------------------------------------------- inscripciones

create table inscripciones (
  id        uuid primary key default gen_random_uuid(),
  alumno_id uuid not null references perfiles on delete cascade,
  curso_id  uuid not null references cursos on delete cascade,
  estado    text not null default 'activa' check (estado in ('activa','vencida','cancelada')),
  origen    text not null check (origen in ('stripe','manual','migracion')),
  stripe_payment_intent text unique,
  monto_mxn int check (monto_mxn >= 0),
  creada_en timestamptz not null default now(),
  -- "Tendras acceso a todo el material por 5 meses" — se lo promete la leccion
  -- "Introduccion al curso" en Kajabi. Sin esto el acceso seria eterno, o sea
  -- mas de lo que se vende.
  expira_en timestamptz not null default now() + interval '5 months',
  -- El "Quiz" de la seccion Introduccion son dos casillas de aceptacion (la
  -- informacion del curso y el Codigo de Etica), no un examen: es consentimiento.
  acepto_terminos_en timestamptz,
  unique (alumno_id, curso_id)
);

-- Un alumno "des-inscrito" se marca 'cancelada', nunca se borra: en Kajabi
-- borrar un contacto borra su progreso sin recuperacion. No repetir eso.

create function inscrito_en(p_curso uuid) returns boolean
language sql stable security definer set search_path = public as $$
  -- La vigencia se revisa AQUI y en ningun otro lado: esta es la funcion por la
  -- que pasan todas las policies del alumno (lecciones, preguntas) y tambien
  -- calificar(). Un solo lugar, ningun llamador que se pueda olvidar.
  select exists (
    select 1 from inscripciones
    where alumno_id = auth.uid() and curso_id = p_curso
      and estado = 'activa' and expira_en > now()
  );
$$;

-- ---------------------------------------------------------------- examenes

create table preguntas (
  id         uuid primary key default gen_random_uuid(),
  leccion_id uuid not null references lecciones on delete cascade,
  numero     int not null,
  enunciado  text not null,
  -- {"A": "...", "B": "...", "C": "...", "D": "..."}
  opciones   jsonb not null check (jsonb_typeof(opciones) = 'object'),
  unique (leccion_id, numero)
);

-- La respuesta correcta va en SU PROPIA TABLA, no en una columna de preguntas.
-- RLS filtra filas, no columnas: si la clave viviera en `preguntas`, cualquier
-- alumno con la sesion abierta podria leerla desde el cliente y el examen no
-- valdria nada. Aqui nadie la lee salvo calificar(), que es security definer.
create table respuestas_correctas (
  pregunta_id uuid primary key references preguntas on delete cascade,
  correcta    text not null
);

create table progreso (
  alumno_id     uuid not null references perfiles on delete cascade,
  leccion_id    uuid not null references lecciones on delete cascade,
  video_visto_en timestamptz,
  calificacion  int check (calificacion between 0 and 100),
  aprobado      boolean not null default false,
  primary key (alumno_id, leccion_id)
);

-- ponytail: se guarda el ultimo intento, no el historial. Si algun dia hacen
-- falta limites de reintento o auditoria por intento, agregar tabla intentos.

create function calificar(p_leccion uuid, p_respuestas jsonb)
returns table (calificacion int, aprobado boolean)
language plpgsql security definer set search_path = public as $$
declare v_total int; v_bien int; v_pct int;
begin
  if not inscrito_en((select curso_id from lecciones where id = p_leccion)) then
    raise exception 'no inscrito en este curso';
  end if;

  select count(*) into v_total from preguntas where leccion_id = p_leccion;
  if v_total = 0 then raise exception 'la leccion no tiene examen'; end if;

  select count(*) into v_bien
  from preguntas p join respuestas_correctas r on r.pregunta_id = p.id
  where p.leccion_id = p_leccion
    and p_respuestas->>p.numero::text = r.correcta;

  v_pct := round(v_bien * 100.0 / v_total);

  insert into progreso (alumno_id, leccion_id, calificacion, aprobado)
  values (auth.uid(), p_leccion, v_pct, v_pct >= 80)  -- 80 lo promete el curso, no lo elige el codigo
  on conflict (alumno_id, leccion_id) do update
    -- Se queda la mejor calificacion, no la ultima: reprobar un reintento no
    -- debe borrar un examen ya aprobado.
    set calificacion = greatest(progreso.calificacion, excluded.calificacion),
        aprobado     = progreso.aprobado or excluded.aprobado;

  return query
    select p.calificacion, p.aprobado from progreso p
    where p.alumno_id = auth.uid() and p.leccion_id = p_leccion;
end $$;

-- El alumno acepta los terminos por esta funcion y no por una policy de UPDATE.
-- Motivo: RLS filtra filas, no columnas. Una policy "puede actualizar su propia
-- inscripcion" le dejaria tocar tambien estado y expira_en, o sea auto-renovarse
-- el acceso. Aqui solo se escribe la fecha de aceptacion y nada mas.
create function aceptar_terminos(p_curso uuid)
returns timestamptz
language plpgsql security definer set search_path = public as $$
declare v_cuando timestamptz;
begin
  update inscripciones
     set acepto_terminos_en = coalesce(acepto_terminos_en, now())
   where alumno_id = auth.uid() and curso_id = p_curso and estado = 'activa'
  returning acepto_terminos_en into v_cuando;

  if v_cuando is null then
    raise exception 'no hay inscripcion activa en este curso';
  end if;
  return v_cuando;
end $$;

-- --------------------------------------------------------------------- RLS

alter table perfiles             enable row level security;
alter table cursos               enable row level security;
alter table lecciones            enable row level security;
alter table inscripciones        enable row level security;
alter table preguntas            enable row level security;
alter table respuestas_correctas enable row level security;
alter table progreso             enable row level security;

create policy "perfil propio" on perfiles for select
  using (id = auth.uid() or es_admin());
create policy "editar perfil propio" on perfiles for update
  using (id = auth.uid()) with check (id = auth.uid());

-- El alumno edita su nombre y pais, nunca su rol. Se hace con permisos POR
-- COLUMNA y no dentro de la policy: una policy sobre perfiles que consultara
-- perfiles recursa infinito, porque la subconsulta vuelve a pasar por RLS.
-- (es_admin() se salva de eso solo porque es security definer.)
revoke update on perfiles from authenticated;
grant update (nombre, pais) on perfiles to authenticated;

-- publicado controla si el curso sale en el CATALOGO, no si quien ya pago puede
-- entrar: sin el inscrito_en, un alumno de un curso no publicado no alcanza a
-- leer ni el titulo de lo que compro.
create policy "curso visible si publicado o inscrito" on cursos for select
  using (publicado or inscrito_en(id) or es_admin());

create policy "lecciones si inscrito" on lecciones for select
  using (inscrito_en(curso_id) or es_admin());

create policy "inscripcion propia" on inscripciones for select
  using (alumno_id = auth.uid() or es_admin());

create policy "preguntas si inscrito" on preguntas for select
  using (inscrito_en((select curso_id from lecciones where id = leccion_id)) or es_admin());

-- Sin policy de select: nadie lee la clave desde el cliente, ni el admin.
-- calificar() la consulta por dentro porque es security definer.

create policy "progreso propio" on progreso for select
  using (alumno_id = auth.uid() or es_admin());
create policy "marcar video visto" on progreso for insert
  with check (alumno_id = auth.uid()
              and inscrito_en((select curso_id from lecciones where id = leccion_id)));
create policy "actualizar video visto" on progreso for update
  using (alumno_id = auth.uid()) with check (alumno_id = auth.uid());

-- Estas dos policies por si solas eran un agujero: decian "el alumno puede
-- escribir su propia fila de progreso", y RLS filtra filas pero NO columnas.
-- Un alumno inscrito podia insertar calificacion=100 y aprobado=true en las 11
-- lecciones sin contestar un examen, y la constancia depende justo de eso.
-- Se encontro probandolo, no leyendolo. Igual que con perfiles.rol: el limite
-- por columna lo pone el grant, no la policy.
revoke insert, update on progreso from authenticated;
grant insert (alumno_id, leccion_id, video_visto_en) on progreso to authenticated;
grant update (video_visto_en) on progreso to authenticated;
-- calificar() no se ve afectada: es security definer y corre como el dueno.

-- ------------------------------------------------- defensa en profundidad
-- Supabase le da a `authenticated` permisos sobre todo por default, asi que sin
-- esto la policy es la UNICA capa. Se quitan los permisos que ninguna pantalla
-- usa, para que hagan falta dos errores y no uno: hoy RLS ya los niega por no
-- tener policy, pero el dia que alguien agregue una policy permisiva por
-- descuido, sin el grant sigue cerrado.
--
-- En cursos, lecciones e inscripciones el INSERT/UPDATE se deja abierto porque
-- el admin escribe desde el navegador y comparte el rol `authenticated` con el
-- alumno: ahi la policy es la unica capa posible, y es es_admin().

-- Nadie borra nunca desde el cliente.
revoke delete on perfiles, cursos, lecciones, inscripciones,
                 preguntas, respuestas_correctas, progreso from authenticated;
-- Los examenes y su clave se cambian por migracion, nunca desde la UI.
revoke insert, update on preguntas, respuestas_correctas from authenticated;
-- Los perfiles los crea el trigger; los cursos, una migracion.
revoke insert on perfiles from authenticated;
revoke insert on cursos   from authenticated;

-- Escrituras del panel de admin. Van desde el navegador igual que las del
-- alumno: no hace falta servidor porque es_admin() se evalua en la base y es
-- security definer, asi que el permiso no depende de que el cliente diga la
-- verdad. Lo que no tiene policy (preguntas, respuestas_correctas, borrar
-- inscripciones) queda negado por defecto: se toca por migracion, no por la UI.
create policy "admin inscribe"              on inscripciones for insert with check (es_admin());
create policy "admin actualiza inscripcion" on inscripciones for update using (es_admin());
create policy "admin edita curso"           on cursos        for update using (es_admin());
create policy "admin edita leccion"         on lecciones     for update using (es_admin());
create policy "admin crea leccion"          on lecciones     for insert with check (es_admin());
