# Emite la constancia de un alumno sobre la PLANTILLA OFICIAL de CELEBIOS.
#
#   .\generar-constancia.ps1 -Correo cecilbae@gmail.com
#   .\generar-constancia.ps1 -Todos          # todos los que estan al 100%
#
# Salida en Desktop\CELEBIOS-constancias\: un PNG y un PDF por alumno.
#
# ---------------------------------------------------------------------------
# POR QUE ESTE SCRIPT SOLO ESCRIBE EL NOMBRE
#
# La primera version dibujaba la constancia desde cero en HTML y sacaba los
# datos de la ficha publica del sitio. Salio mal en cuatro cosas a la vez:
# decia 12 horas (la ficha miente, son 10), omitia a EtologiaCH como coemisor,
# omitia el aval de CONCERVET e inventaba un folio propio en vez del PG 144/26.
# Se alcanzo a mandar asi a una alumna.
#
# La plantilla oficial ya trae curso, horas, folio, logos, QR y sello. Lo unico
# que falta es el nombre. Todo lo que este script "sabe" del curso es cero:
# si algun dato cambia, se cambia la imagen, no el codigo. Es la unica forma de
# que no se vuelva a colar un dato inventado.
#
# La plantilla vive fuera del repo para no meter binarios al sitio. Si se
# pierde, esta en el Drive de contacto@celebios.com:
#   https://drive.google.com/file/d/1GmdpJyz0f0g_jR2CWm6aGzPWoCEXJlO8/view
# ---------------------------------------------------------------------------

param(
    [string]$Correo,
    [switch]$Todos,
    # -Nombre emite sin consultar el CSV de Kajabi. Lo usa emitir-constancias.ps1,
    # que saca de Supabase a quien acredito los once quizes EN EL AULA NUEVA: esa
    # gente no existe en el export de Kajabi y de otro modo nunca tendria constancia.
    [string]$Nombre
)

$ErrorActionPreference = 'Stop'

$CSV       = "C:\Users\coche\Desktop\CELEBIOS-web\kajabi-export\alumnos-gatos.csv"
$DESTINO   = "C:\Users\coche\Desktop\CELEBIOS-constancias"
$PLANTILLA = "$DESTINO\plantilla-oficial.png"
$FUENTE    = "$DESTINO\Montserrat.ttf"
$EDGE      = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

foreach ($req in @($PLANTILLA, $FUENTE, $EDGE)) {
    if (-not (Test-Path $req)) { throw "Falta: $req" }
}
# El CSV solo hace falta cuando se emite a partir de el.
if (-not $Nombre -and -not (Test-Path $CSV)) { throw "Falta: $CSV" }

# La plantilla mide 1280x896. El hueco del nombre queda entre "OTORGAN LA
# PRESENTE CONSTANCIA A:" y "POR CONCLUIR SATISFACTORIAMENTE EL CURSO:".
$ANCHO = 1280
$ALTO  = 896
$HUECO_TOP = 300
$HUECO_ALTO = 104

$imgB64  = [Convert]::ToBase64String([IO.File]::ReadAllBytes($PLANTILLA))
$fontB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($FUENTE))

# ---------------------------------------------------------------- alumnos --
if ($Nombre) {
    # progreso_pct = 100 porque quien llama ya comprobo la acreditacion contra la
    # base; aqui solo se dibuja.
    $alumnos = @([pscustomobject]@{ nombre = $Nombre; correo = $Correo; progreso_pct = 100 })
}
else {
    $alumnos = Import-Csv -Path $CSV -Encoding UTF8
    if     ($Correo) { $alumnos = @($alumnos | Where-Object { $_.correo -eq $Correo }) }
    elseif ($Todos)  { $alumnos = @($alumnos | Where-Object { [int]$_.progreso_pct -ge 100 -and $_.interna -ne 'si' }) }
    else   { Write-Output "Usa -Correo <mail>, -Todos, o -Nombre <nombre>"; exit 1 }
}

if ($alumnos.Count -eq 0) { Write-Output "Ningun alumno coincide."; exit 1 }

if (-not (Test-Path $DESTINO)) { New-Item -ItemType Directory -Path $DESTINO | Out-Null }

foreach ($a in $alumnos) {
    $pct = [int]$a.progreso_pct
    if ($pct -lt 100) {
        Write-Output ("SALTADO {0} - lleva {1}%, no acredito el curso." -f $a.correo, $pct)
        continue
    }

    $nombre = $a.nombre.Trim()
    $slug   = ($nombre -replace '[^\w]', '-') -replace '-+', '-'
    $base   = "$DESTINO\Constancia-$slug"

    # El nombre se encoge si no cabe de un renglon: hay alumnos con cuatro
    # apellidos y la plantilla no perdona que el texto toque los margenes.
    $tam = if ($nombre.Length -gt 34) { 38 } elseif ($nombre.Length -gt 26) { 44 } else { 52 }

    $html = @"
<!doctype html>
<meta charset="utf-8">
<title>Constancia - $nombre</title>
<style>
  @font-face {
    font-family: 'Montserrat';
    /* Montserrat va embebida en el HTML, no instalada en Windows: asi el
       script corre igual en otra maquina. Es la variable font de Google Fonts;
       el eje wght se fija abajo con font-variation-settings. */
    src: url(data:font/ttf;base64,$fontB64) format('truetype');
    font-weight: 100 900;
  }
  @page { size: ${ANCHO}px ${ALTO}px; margin: 0 }
  html, body { margin: 0; padding: 0 }
  .hoja {
    position: relative;
    width: ${ANCHO}px; height: ${ALTO}px;
    background: url(data:image/png;base64,$imgB64) no-repeat 0 0;
    background-size: ${ANCHO}px ${ALTO}px;
  }
  /* Centrado en el hueco, no apoyado en una linea base: asi un nombre de dos
     renglones sigue quedando a la misma altura optica que uno de uno. */
  .nombre {
    position: absolute;
    left: 60px; right: 60px;
    top: ${HUECO_TOP}px; height: ${HUECO_ALTO}px;
    margin: 0;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Montserrat', 'Century Gothic', sans-serif;
    font-weight: 600;
    font-variation-settings: 'wght' 600;
    font-size: ${tam}px;
    line-height: 1.15;
    letter-spacing: 0.5px;
    text-align: center;
    color: #1a1a1a;
  }
</style>
<div class="hoja"><p class="nombre">$nombre</p></div>
"@

    $htmlPath = "$base.html"
    [IO.File]::WriteAllText($htmlPath, $html, [Text.UTF8Encoding]::new($false))
    $url = ([Uri]$htmlPath).AbsoluteUri

    # Edge escuupe ruido a stderr aunque termine bien, y en PowerShell 5.1 un
    # stderr de ejecutable nativo bajo ErrorActionPreference='Stop' aborta el
    # script. Se baja a Continue solo mientras corre Edge.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $EDGE --headless=new --disable-gpu --no-first-run `
        --window-size="$ANCHO,$ALTO" --screenshot="$base.png" $url 2>$null | Out-Null
    & $EDGE --headless=new --disable-gpu --no-first-run `
        --print-to-pdf="$base.pdf" --no-pdf-header-footer $url 2>$null | Out-Null
    $ErrorActionPreference = $prev

    foreach ($salida in @("$base.png", "$base.pdf")) {
        if (-not (Test-Path $salida)) { throw "Edge no genero $salida" }
    }

    Remove-Item $htmlPath -Force
    Write-Output ("OK {0} -> {1}.pdf" -f $nombre, (Split-Path $base -Leaf))
}
