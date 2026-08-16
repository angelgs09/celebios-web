# Detecta a quien acredito los once quizes en el aula y emite su constancia.
#
#   .\emitir-constancias.ps1              # ENSAYO: dice a quien le toca y no manda nada
#   .\emitir-constancias.ps1 -Aplicar     # genera el PDF, se lo manda y avisa a CELEBIOS
#
# ---------------------------------------------------------------------------
# POR QUE EXISTE
#
# Kajabi le promete al alumno, textual: "si resuelves todos los quizes obteniendo
# una calificacion mayor a 80/100, obtendras una constancia de participacion del
# curso con validez curricular". De 24 alumnos salieron DOS constancias. No
# porque nadie acreditara, sino porque emitirlas era un paso manual que dependia
# de que alguien mirara quien habia terminado, y nadie miraba.
#
# Este script es esa mirada. Corre solo, compara contra un registro de lo ya
# emitido, y solo actua sobre quien acaba de acreditar.
#
# Requisito de acreditacion: TODAS las lecciones del curso aprobadas. El umbral
# por leccion (mas de 80/100) lo aplica calificar() en la base; aqui no se
# reinterpreta nada, solo se cuenta progreso.aprobado.
#
# Ver los videos NO es requisito -- asi funcionaba en Kajabi. Eso no se le dice
# al alumno en ninguna pantalla: lo que se le dice es que apruebe los quizes.
# ---------------------------------------------------------------------------

param(
    [switch]$Aplicar,
    [int]$TopePorCorrida = 5   # red de seguridad: si algo se descontrola, no salen 200 correos
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$RAIZ      = Split-Path -Parent $PSScriptRoot
$ENVFILE   = Join-Path $RAIZ '.env.production.local'
$PROY      = 'https://lwawpdjsfjvlyvqwqiqp.supabase.co'
$DESTINO   = 'C:\Users\coche\Desktop\CELEBIOS-constancias'
$REGISTRO  = Join-Path $DESTINO 'constancias-emitidas.json'
$REMITENTE = 'contacto@celebios.com'
$INTERNO   = 'contacto@celebios.com'   # copia para que CELEBIOS se entere del envio
$UA        = 'celebios-constancias/1.0 (node)'

$svc = ((Get-Content $ENVFILE | Where-Object { $_ -like 'SUPABASE_SERVICE_ROLE_KEY=*' } |
         Select-Object -First 1) -replace '^SUPABASE_SERVICE_ROLE_KEY=', '').Trim().Trim('"')
if (-not $svc) { throw "Falta SUPABASE_SERVICE_ROLE_KEY en $ENVFILE" }
$H = @{ apikey = $svc; Authorization = "Bearer $svc"; 'Content-Type' = 'application/json' }

function Sql([string]$consulta) {
    # PostgREST no hace agregados con joins de este tipo; se traen las filas y se
    # cuentan aqui, que con 21 alumnos y 11 lecciones no cuesta nada.
    Invoke-RestMethod -Uri "$PROY/rest/v1/$consulta" -Headers $H -UserAgent $UA
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
$perfiles = Sql 'perfiles?select=id,nombre,correo,rol'

$acreditados = @()
foreach ($i in $insc) {
    $suyas = $porCurso[$i.curso_id]
    if (-not $suyas -or $suyas.Count -eq 0) { continue }
    $ok = @($progreso | Where-Object { $_.alumno_id -eq $i.alumno_id -and $suyas -contains $_.leccion_id }).Count
    if ($ok -lt $suyas.Count) { continue }
    $p = $perfiles | Where-Object { $_.id -eq $i.alumno_id } | Select-Object -First 1
    if (-not $p) { continue }
    $acreditados += [pscustomobject]@{
        id = $i.alumno_id; nombre = $p.nombre; correo = $p.correo
        rol = $p.rol; curso = $i.curso_id; de = "$($ok)/$($suyas.Count)"
    }
}

# --------------------------------------------------------------------- registro --
$yaEmitidas = @{}
if (Test-Path $REGISTRO) {
    foreach ($e in (Get-Content $REGISTRO -Raw | ConvertFrom-Json)) {
        $yaEmitidas["$($e.alumno_id)|$($e.curso_id)"] = $e.emitida_en
    }
}

$pendientes = @($acreditados | Where-Object { -not $yaEmitidas.ContainsKey("$($_.id)|$($_.curso)") })

Write-Output ("Acreditaron los once quizes: {0}   Ya tenian constancia: {1}   Pendientes: {2}" -f `
    $acreditados.Count, ($acreditados.Count - $pendientes.Count), $pendientes.Count)

if ($pendientes.Count -eq 0) { Write-Output "Nada que emitir."; exit 0 }
foreach ($a in $pendientes) { Write-Output ("  - {0,-34} {1}  {2}" -f $a.nombre, $a.correo, $a.de) }

if (-not $Aplicar) {
    Write-Output ""
    Write-Output "ENSAYO: no se genero ni se mando nada. Para emitir de verdad, agrega -Aplicar"
    exit 0
}

if ($pendientes.Count -gt $TopePorCorrida) {
    throw ("Hay {0} pendientes y el tope por corrida es {1}. Si de verdad acreditaron todos, sube -TopePorCorrida a proposito." -f $pendientes.Count, $TopePorCorrida)
}

# ----------------------------------------------------------------------- envio --
$pass = ((Get-Content $ENVFILE | Where-Object { $_ -like 'SMTP_APP_PASSWORD=*' } |
          Select-Object -First 1) -replace '^SMTP_APP_PASSWORD=', '').Trim().Trim('"') -replace '\s', ''
if ($pass.Length -ne 16) { throw "La contrasena de aplicacion debe tener 16 caracteres" }
$cliente = New-Object System.Net.Mail.SmtpClient('smtp.gmail.com', 587)
$cliente.EnableSsl = $true
$cliente.Credentials = New-Object System.Net.NetworkCredential($REMITENTE, $pass)
$pass = $null

$emitidas = @()
if (Test-Path $REGISTRO) { $emitidas = @(Get-Content $REGISTRO -Raw | ConvertFrom-Json) }

foreach ($a in $pendientes) {
    $slug = ($a.nombre -replace '[^\w]', '-') -replace '-+', '-'
    $pdf  = Join-Path $DESTINO "Constancia-$slug.pdf"

    & (Join-Path $PSScriptRoot 'generar-constancia.ps1') -Nombre $a.nombre -Correo $a.correo | Out-Null
    if (-not (Test-Path $pdf)) {
        Write-Output ("  X {0}: no se genero el PDF, no le mando nada" -f $a.nombre)
        continue
    }

    $nombrePila = ($a.nombre -split ' ')[0]
    $nombrePila = $nombrePila.Substring(0,1).ToUpper() + $nombrePila.Substring(1).ToLower()
    $html = @"
<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="color-scheme" content="light"></head>
<body style="margin:0;padding:0;background:#F4F6F4">
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;color:#16294C;background:#FFFFFF">
  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">CELEBIOS &middot; Aula virtual</p>
  <h1 style="font-size:24px;line-height:1.25;margin:0 0 16px;color:#16294C">Acreditaste el curso</h1>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">Hola, ${nombrePila}:</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">Aprobaste los once cuestionarios de <strong>Lenguaje y Comunicaci&oacute;n de los Gatos</strong>. Aqu&iacute; va tu <strong>constancia de participaci&oacute;n con validez curricular</strong>, adjunta en PDF.</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 16px">La emiten CELEBIOS y Etolog&iacute;aCH, y lleva el registro del Consejo Nacional de Certificaci&oacute;n en Medicina Veterinaria y Zootecnia (CONCERVET).</p>
  <p style="font-size:16px;line-height:1.6;margin:0 0 32px">Gracias por llegar al final.</p>
  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">
  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">Centro Latinoamericano de Estudios en Ciencias Biol&oacute;gicas y de la Salud Animal</p>
</div></body></html>
"@

    $msg = New-Object System.Net.Mail.MailMessage
    $msg.From = New-Object System.Net.Mail.MailAddress($REMITENTE, 'CELEBIOS', [Text.Encoding]::UTF8)
    $msg.To.Add($a.correo)
    $msg.Bcc.Add($INTERNO)          # para que CELEBIOS vea cada emision sin depender de este log
    $msg.Subject = 'Tu constancia del curso de gatos'
    $msg.SubjectEncoding = [Text.Encoding]::UTF8
    $msg.Body = $html
    $msg.BodyEncoding = [Text.Encoding]::UTF8
    $msg.IsBodyHtml = $true
    $msg.Attachments.Add((New-Object System.Net.Mail.Attachment($pdf)))
    try {
        $cliente.Send($msg)
        Write-Output ("  OK {0} -> {1}" -f $a.nombre, $a.correo)
        # Se registra DESPUES de enviar: si el envio falla, la proxima corrida
        # lo vuelve a intentar en vez de darlo por hecho.
        $emitidas += [pscustomobject]@{
            alumno_id = $a.id; curso_id = $a.curso; nombre = $a.nombre
            correo = $a.correo; emitida_en = (Get-Date).ToString('s')
        }
        $emitidas | ConvertTo-Json -Depth 4 | Set-Content -Path $REGISTRO -Encoding utf8
    } catch {
        Write-Output ("  X {0}: FALLO el envio: {1}" -f $a.nombre, $_.Exception.Message)
    } finally { $msg.Dispose() }
}
