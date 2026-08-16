# Vigila quien acredito los once quizes y avisa a CELEBIOS. La constancia se le
# manda al alumno en un segundo paso, a proposito.
#
#   .\emitir-constancias.ps1                          # ENSAYO: dice como esta el tablero, no manda nada
#   .\emitir-constancias.ps1 -Avisar                  # correo INTERNO con el PDF listo (esto es lo que corre solo)
#   .\emitir-constancias.ps1 -Aplicar -Solo <correo>  # manda la constancia AL ALUMNO
#
# ---------------------------------------------------------------------------
# POR QUE EXISTE, Y POR QUE EN DOS PASOS
#
# Kajabi le promete al alumno, textual: "si resuelves todos los quizes obteniendo
# una calificacion mayor a 80/100, obtendras una constancia de participacion del
# curso con validez curricular". De 24 alumnos salieron DOS constancias. No
# porque nadie acreditara, sino porque emitirlas era un paso manual que dependia
# de que alguien fuera a mirar quien habia terminado, y nadie iba.
#
# Lo que aqui corre solo es la MIRADA, no el envio. El paso automatico detecta al
# acreditado, le genera el PDF y se lo manda a CELEBIOS con el texto ya redactado;
# una persona decide si sale. Asi ninguna constancia le llega a un alumno sin que
# alguien la haya visto, que es justo lo que se pidio.
#
# El riesgo de este diseno es el mismo que hundio a Kajabi: que el aviso se
# entierre en la bandeja y nadie lo abra. Contra eso, el aviso NO es de una sola
# vez -- mientras el alumno siga sin su constancia, vuelve a insistir cada
# RECORDAR_CADA_DIAS, con la cuenta de dias en el asunto.
#
# Requisito de acreditacion: TODAS las lecciones del curso aprobadas. El umbral
# por leccion (mas de 80/100) lo aplica calificar() en la base; aqui no se
# reinterpreta nada, solo se cuenta progreso.aprobado.
#
# Ver los videos NO es requisito -- asi funcionaba en Kajabi. Eso no se le dice
# al alumno en ninguna pantalla: lo que se le dice es que apruebe los quizes.
#
# Quien lo dispara: la tarea "CELEBIOS - avisar constancias", diaria a las 9:30,
# corre este script con -Avisar. Es LogonType=Interactive, o sea que necesita la
# laptop encendida y con sesion iniciada, igual que el latido de Supabase.
# ---------------------------------------------------------------------------

param(
    [switch]$Avisar,
    [switch]$Aplicar,
    [string]$Solo,
    [int]$TopePorCorrida = 5   # red de seguridad: si algo se descontrola, no salen 200 correos
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$RAIZ      = Split-Path -Parent $PSScriptRoot
$ENVFILE   = Join-Path $RAIZ '.env.production.local'
$PROY      = 'https://lwawpdjsfjvlyvqwqiqp.supabase.co'
$DESTINO   = 'C:\Users\coche\Desktop\CELEBIOS-constancias'
$REG_EMITIDAS  = Join-Path $DESTINO 'constancias-emitidas.json'
$REG_AVISADAS  = Join-Path $DESTINO 'constancias-avisadas.json'
$REMITENTE = 'contacto@celebios.com'
$UA        = 'celebios-constancias/1.0 (node)'
$RECORDAR_CADA_DIAS = 7

# El .ps1 se guarda sin BOM y PowerShell 5.1 lo leeria como ANSI, asi que una
# tilde escrita literal aqui llegaria rota al correo. En el cuerpo van como
# entidades HTML; el asunto es texto plano y se arma con estos caracteres.
$I_ = [char]0x00ED   # i con tilde
$O_ = [char]0x00F3   # o con tilde

# A quien le llega el aviso interno. Agregar correos aqui si alguien mas debe
# enterarse; el del alumno NUNCA va en esta lista.
$AVISO_A = @('contacto@celebios.com')

# -Aplicar exige -Solo: la constancia sale de una en una, con un nombre escrito a
# mano. Un lote automatico al alumno es justo lo que este diseno evita.
if ($Aplicar -and -not $Solo) {
    throw "-Aplicar necesita -Solo <correo del alumno>. La constancia se manda de una en una."
}
if ($Avisar -and $Aplicar) { throw "-Avisar y -Aplicar hacen cosas distintas; corre una a la vez." }

$svc = ((Get-Content $ENVFILE | Where-Object { $_ -like 'SUPABASE_SERVICE_ROLE_KEY=*' } |
         Select-Object -First 1) -replace '^SUPABASE_SERVICE_ROLE_KEY=', '').Trim().Trim('"')
if (-not $svc) { throw "Falta SUPABASE_SERVICE_ROLE_KEY en $ENVFILE" }
$H = @{ apikey = $svc; Authorization = "Bearer $svc"; 'Content-Type' = 'application/json' }

function Sql([string]$consulta) {
    # PostgREST no hace agregados con joins de este tipo; se traen las filas y se
    # cuentan aqui, que con 22 perfiles y 11 lecciones no cuesta nada.
    Invoke-RestMethod -Uri "$PROY/rest/v1/$consulta" -Headers $H -UserAgent $UA
}

function Leer-Registro([string]$ruta) {
    $t = @{}
    if (-not (Test-Path $ruta)) { return $t }

    # ConvertFrom-Json de PowerShell 5.1 escupe el arreglo entero como UN objeto,
    # y @(...) alrededor del pipeline no lo desenrolla: el foreach daba una sola
    # vuelta con $e siendo la lista completa, y la clave salia con los ids de
    # todos pegados. Con dos constancias en el registro dejaba de detectar los
    # duplicados y las habria vuelto a mandar. Hay que pasar por variable.
    $crudo = Get-Content $ruta -Raw | ConvertFrom-Json
    $filas = @()
    if ($crudo -is [array]) { $filas = $crudo } elseif ($crudo) { $filas = @($crudo) }

    foreach ($e in $filas) { $t["$($e.alumno_id)|$($e.curso_id)"] = $e }
    return $t
}

function Guardar-Registro {
    # Con nombre, no por posicion: un arreglo pasado posicionalmente se desenvuelve
    # y la ruta termina cayendo en el primer parametro.
    param([object[]]$Filas, [Parameter(Mandatory)][string]$Ruta)
    $filas = $Filas
    $ruta = $Ruta
    # PowerShell 5.1 no tiene -AsArray: con una sola fila escribiria un objeto
    # suelto. Se envuelve a mano para que el archivo sea siempre un arreglo.
    $json = @($filas) | ConvertTo-Json -Depth 4
    if (@($filas).Count -eq 1) { $json = "[$json]" }
    Set-Content -Path $ruta -Value $json -Encoding utf8
}

function Nuevo-Smtp {
    $pass = ((Get-Content $ENVFILE | Where-Object { $_ -like 'SMTP_APP_PASSWORD=*' } |
              Select-Object -First 1) -replace '^SMTP_APP_PASSWORD=', '').Trim().Trim('"') -replace '\s', ''
    if ($pass.Length -ne 16) { throw "La contrasena de aplicacion debe tener 16 caracteres" }
    $c = New-Object System.Net.Mail.SmtpClient('smtp.gmail.com', 587)
    $c.EnableSsl = $true
    $c.Credentials = New-Object System.Net.NetworkCredential($REMITENTE, $pass)
    $pass = $null
    return $c
}

function Generar-Pdf($a) {
    $slug = ($a.nombre -replace '[^\w]', '-') -replace '-+', '-'
    $pdf  = Join-Path $DESTINO "Constancia-$slug.pdf"
    & (Join-Path $PSScriptRoot 'generar-constancia.ps1') -Nombre $a.nombre -Correo $a.correo | Out-Null
    if (-not (Test-Path $pdf)) { return $null }
    return $pdf
}

# --------------------------------------------------------------- quien acredito --
$lecciones = Sql 'lecciones?select=id,curso_id'
$porCurso  = @{}
foreach ($l in $lecciones) {
    if (-not $porCurso.ContainsKey($l.curso_id)) { $porCurso[$l.curso_id] = @() }
    $porCurso[$l.curso_id] += $l.id
}

$progreso = Sql 'progreso?select=alumno_id,leccion_id,aprobado&aprobado=is.true'
$insc     = Sql 'inscripciones?select=alumno_id,curso_id&estado=eq.activa'
$cursos   = Sql 'cursos?select=id,titulo'
# Solo alumnos: las cuentas admin (la de CELEBIOS y la de soporte) entran al aula
# a probar y acreditan los quizes como cualquiera. Sin este filtro se emitiria una
# constancia a nombre de quien administra el curso.
$perfiles = Sql 'perfiles?select=id,nombre,correo,rol&rol=eq.alumno'

$acreditados = @()
foreach ($i in $insc) {
    $suyas = $porCurso[$i.curso_id]
    if (-not $suyas -or $suyas.Count -eq 0) { continue }
    $p = $perfiles | Where-Object { $_.id -eq $i.alumno_id } | Select-Object -First 1
    if (-not $p) { continue }
    $ok = @($progreso | Where-Object { $_.alumno_id -eq $i.alumno_id -and $suyas -contains $_.leccion_id }).Count
    if ($ok -lt $suyas.Count) { continue }
    $c = $cursos | Where-Object { $_.id -eq $i.curso_id } | Select-Object -First 1
    $acreditados += [pscustomobject]@{
        id = $i.alumno_id; nombre = $p.nombre; correo = $p.correo
        curso = $i.curso_id; titulo = $c.titulo; de = "$($ok)/$($suyas.Count)"
    }
}

$yaEmitidas = Leer-Registro $REG_EMITIDAS
$yaAvisadas = Leer-Registro $REG_AVISADAS
$ahora = Get-Date

$pendientes = @($acreditados | Where-Object { -not $yaEmitidas.ContainsKey("$($_.id)|$($_.curso)") })
if ($Solo) { $pendientes = @($pendientes | Where-Object { $_.correo -eq $Solo }) }

Write-Output ("Acreditados: {0}   Con constancia ya enviada: {1}   Sin constancia: {2}" -f `
    $acreditados.Count, ($acreditados.Count - $pendientes.Count), $pendientes.Count)

foreach ($a in $pendientes) {
    $av = $yaAvisadas["$($a.id)|$($a.curso)"]
    $desde = if ($av) { [int]($ahora - [datetime]$av.acredito_en).TotalDays } else { 0 }
    $nota  = if ($av) { "avisado hace $([int]($ahora - [datetime]$av.ultimo_aviso).TotalDays) d, esperando $desde d" } else { "sin avisar" }
    Write-Output ("  - {0,-34} {1,-30} {2}  ({3})" -f $a.nombre, $a.correo, $a.de, $nota)
}

# ---------------------------------------------------------------------- ensayo --
if (-not $Avisar -and -not $Aplicar) {
    Write-Output ""
    Write-Output "ENSAYO: no se genero ni se mando nada."
    Write-Output "  -Avisar                  -> correo interno a CELEBIOS con el PDF listo"
    Write-Output "  -Aplicar -Solo <correo>  -> le manda la constancia al alumno"
    exit 0
}
if ($pendientes.Count -eq 0) { Write-Output "Nada que hacer."; exit 0 }
if ($pendientes.Count -gt $TopePorCorrida) {
    throw ("Hay {0} pendientes y el tope por corrida es {1}. Si de verdad acreditaron todos, sube -TopePorCorrida a proposito." -f $pendientes.Count, $TopePorCorrida)
}

$cliente = Nuevo-Smtp

function Mandar($para, $asunto, $html, $pdf) {
    $msg = New-Object System.Net.Mail.MailMessage
    $msg.From = New-Object System.Net.Mail.MailAddress($REMITENTE, 'CELEBIOS', [Text.Encoding]::UTF8)
    foreach ($d in @($para)) { $msg.To.Add($d) }
    $msg.Subject = $asunto
    $msg.SubjectEncoding = [Text.Encoding]::UTF8
    $msg.Body = $html
    $msg.BodyEncoding = [Text.Encoding]::UTF8
    $msg.IsBodyHtml = $true
    if ($pdf) {
        $att = New-Object System.Net.Mail.Attachment($pdf)
        # Sin esto viaja como application/octet-stream y Gmail no lo previsualiza:
        # el destinatario tiene que bajarlo a ciegas para ver que le esta mandando.
        $att.ContentType.MediaType = 'application/pdf'
        $msg.Attachments.Add($att)
    }
    try { $cliente.Send($msg); return $true }
    catch { Write-Output ("     FALLO el envio: {0}" -f $_.Exception.Message); return $false }
    finally { $msg.Dispose() }
}

$ENVOLTURA = @'
<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="color-scheme" content="light"></head>
<body style="margin:0;padding:0;background:#F4F6F4">
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;color:#16294C;background:#FFFFFF">
{0}
</div></body></html>
'@

# ----------------------------------------------------------- aviso a CELEBIOS --
if ($Avisar) {
    $avisadas = @()
    foreach ($k in $yaAvisadas.Keys) { $avisadas += $yaAvisadas[$k] }

    foreach ($a in $pendientes) {
        $clave = "$($a.id)|$($a.curso)"
        $previo = $yaAvisadas[$clave]
        if ($previo -and ($ahora - [datetime]$previo.ultimo_aviso).TotalDays -lt $RECORDAR_CADA_DIAS) {
            Write-Output ("  .  {0}: avisado hace poco, no insisto todavia" -f $a.nombre)
            continue
        }

        $pdf = Generar-Pdf $a
        if (-not $pdf) { Write-Output ("  X  {0}: no se genero el PDF" -f $a.nombre); continue }

        $dias = 0
        $asunto = "Acredit$O_ el curso: $($a.nombre)"
        $encabezado = ''
        if ($previo) {
            $dias = [int]($ahora - [datetime]$previo.acredito_en).TotalDays
            $asunto = "RECORDATORIO ($dias d${I_}as): $($a.nombre) sigue sin su constancia"
            $encabezado = "<p style=`"font-size:15px;line-height:1.6;margin:0 0 16px;color:#8A4B2A`"><strong>Van $dias d&iacute;as desde que acredit&oacute; y todav&iacute;a no se le manda.</strong></p>"
        }

        $cuerpo = @"
  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">CELEBIOS &middot; Aula virtual</p>
  <h1 style="font-size:22px;line-height:1.3;margin:0 0 16px;color:#16294C">$($a.nombre) acredit&oacute; el curso</h1>
  $encabezado
  <p style="font-size:16px;line-height:1.6;margin:0 0 8px">Aprob&oacute; los <strong>$($a.de)</strong> cuestionarios de $($a.titulo).</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 24px">Correo del alumno: <strong>$($a.correo)</strong></p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">Su constancia va adjunta, ya lista sobre la plantilla oficial. <strong>Todav&iacute;a no la tiene</strong>: reenv&iacute;ale este PDF, o corre esto para que le llegue con el texto de siempre:</p>
  <p style="font-family:ui-monospace,monospace;font-size:13px;line-height:1.5;background:#F4F6F4;border-left:3px solid #C3CDC0;padding:12px 14px;margin:0 0 24px;word-break:break-all">.\emitir-constancias.ps1 -Aplicar -Solo $($a.correo)</p>
  <p style="font-size:14px;line-height:1.6;color:#4D5F7C;margin:0 0 32px">Mientras siga pendiente, este aviso vuelve cada $RECORDAR_CADA_DIAS d&iacute;as.</p>
  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">
  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">Aviso autom&aacute;tico del aula. No se le mand&oacute; nada al alumno.</p>
"@
        if (Mandar $AVISO_A $asunto ($ENVOLTURA -f $cuerpo) $pdf) {
            Write-Output ("  OK aviso -> CELEBIOS: {0}" -f $a.nombre)
            # Se registra DESPUES de mandar: si falla, la proxima corrida reintenta
            # en vez de dar por avisado algo que nadie recibio.
            $avisadas = @($avisadas | Where-Object { "$($_.alumno_id)|$($_.curso_id)" -ne $clave })
            $desdeCuando = $ahora.ToString('s')
            $cuantos = 1
            if ($previo) { $desdeCuando = $previo.acredito_en; $cuantos = [int]$previo.avisos + 1 }
            $avisadas += [pscustomobject]@{
                alumno_id = $a.id; curso_id = $a.curso; nombre = $a.nombre; correo = $a.correo
                acredito_en = $desdeCuando; ultimo_aviso = $ahora.ToString('s'); avisos = $cuantos
            }
            Guardar-Registro -Filas $avisadas -Ruta $REG_AVISADAS
        }
    }
    exit 0
}

# -------------------------------------------------------- constancia al alumno --
$emitidas = @()
foreach ($k in $yaEmitidas.Keys) { $emitidas += $yaEmitidas[$k] }

foreach ($a in $pendientes) {
    $pdf = Generar-Pdf $a
    if (-not $pdf) { Write-Output ("  X {0}: no se genero el PDF, no le mando nada" -f $a.nombre); continue }

    $nombrePila = ($a.nombre -split ' ')[0]
    $nombrePila = $nombrePila.Substring(0,1).ToUpper() + $nombrePila.Substring(1).ToLower()
    $cuerpo = @"
  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">CELEBIOS &middot; Aula virtual</p>
  <h1 style="font-size:24px;line-height:1.25;margin:0 0 16px;color:#16294C">Acreditaste el curso</h1>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">Hola, ${nombrePila}:</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">Aprobaste los once cuestionarios de <strong>Lenguaje y Comunicaci&oacute;n de los Gatos</strong>. Aqu&iacute; va tu <strong>constancia de participaci&oacute;n con validez curricular</strong>, adjunta en PDF.</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">La emiten CELEBIOS y Etolog&iacute;aCH, y lleva el registro del Consejo Nacional de Certificaci&oacute;n en Medicina Veterinaria y Zootecnia (CONCERVET).</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 32px">Gracias por llegar al final.</p>
  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">
  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">Centro Latinoamericano de Estudios en Ciencias Biol&oacute;gicas y de la Salud Animal</p>
"@
    if (Mandar $a.correo 'Tu constancia del curso de gatos' ($ENVOLTURA -f $cuerpo) $pdf) {
        Write-Output ("  OK {0} -> {1}" -f $a.nombre, $a.correo)
        $emitidas += [pscustomobject]@{
            alumno_id = $a.id; curso_id = $a.curso; nombre = $a.nombre
            correo = $a.correo; emitida_en = $ahora.ToString('s')
        }
        Guardar-Registro -Filas $emitidas -Ruta $REG_EMITIDAS
    }
}
