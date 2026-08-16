# Recomprime los videos del aula antes de subirlos a Vercel Blob.
#
#   .\comprimir-videos.ps1                    # solo MIDE, no toca nada
#   .\comprimir-videos.ps1 -Aplicar
#   .\comprimir-videos.ps1 -Aplicar -Crf 21   # mas calidad, mas peso
#
# ---------------------------------------------------------------------------
# POR QUE
#
# Vercel Blob deja de cachear cualquier blob de mas de 512 MB. Arriba de ese
# umbral, CADA reproduccion de CADA alumno es un cache MISS: sale del origen y
# se paga transferencia de blob mas transferencia de origen, siempre. Los
# crudos (84-160 MB) caian debajo del umbral sin querer. Los editados van de
# 699 a 1149 MB, o sea que ninguno se cachea.
#
# El otro motivo es el alumno: un MP4 de 1 GB tarda en arrancar aunque la
# conexion sea buena.
#
# -movflags +faststart no es opcional aqui. Sin el, el indice del MP4 queda al
# final del archivo y el navegador tiene que bajarlo COMPLETO antes de pintar
# el primer cuadro. Es la diferencia entre "arranca en dos segundos" y "se
# queda pensando un minuto".
# ---------------------------------------------------------------------------

param(
    [string]$Origen  = "C:\Users\coche\Desktop\CELEBIOS-videos\editados",
    [string]$Destino = "C:\Users\coche\Desktop\CELEBIOS-videos\web",
    [switch]$Aplicar,
    # CRF 21 medido contra el modulo 1 el 15-ago: 2000 kbps -> 318 kbps, y el
    # texto de las laminas sale identico al original en una comparacion pixel a
    # pixel. Los editados vienen en CBR de 2 Mbps fijos, que sobre laminas
    # quietas es puro desperdicio; de ahi que baje 84% sin tocar la calidad.
    [int]$Crf        = 21,
    [int]$AlturaMax  = 1080,
    [string]$Preset  = "medium" # slow da ~5% menos peso y tarda el doble
)

$ErrorActionPreference = 'Stop'
$LIMITE_CACHE = 512MB

foreach ($cmd in @('ffmpeg','ffprobe')) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "Falta $cmd en el PATH" }
}
if (-not (Test-Path $Origen)) { throw "No existe la carpeta de origen: $Origen" }

$videos = @(Get-ChildItem $Origen -Filter *.mp4 -File | Sort-Object Name)
if ($videos.Count -eq 0) { throw "No hay .mp4 en $Origen" }

function Medir([string]$ruta) {
    $j = & ffprobe -v error -print_format json -show_format -show_streams -- "$ruta" | ConvertFrom-Json
    $v = $j.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1
    $a = $j.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1
    [pscustomobject]@{
        Segundos  = [double]$j.format.duration
        Bytes     = [long]$j.format.size
        KbpsTotal = [math]::Round([double]$j.format.bit_rate / 1000)
        Codec     = $v.codec_name
        Ancho     = [int]$v.width
        Alto      = [int]$v.height
        Fps       = if ($v.r_frame_rate -match '^(\d+)/(\d+)$') { [math]::Round([double]$Matches[1] / [double]$Matches[2], 2) } else { $v.r_frame_rate }
        AudioKbps = if ($a.bit_rate) { [math]::Round([double]$a.bit_rate / 1000) } else { 0 }
        # El indice al final obliga a bajar el archivo entero antes de reproducir.
        Faststart = ($j.format.tags.major_brand -ne $null)
    }
}

# ------------------------------------------------------------------ medir --
Write-Output ("{0,-22} {1,8} {2,7} {3,11} {4,10} {5,6}" -f 'ARCHIVO','MB','MIN','RESOLUCION','KBPS','CODEC')
Write-Output ('-' * 70)

$medidas = @{}
$totalOrigen = 0
foreach ($v in $videos) {
    $m = Medir $v.FullName
    $medidas[$v.Name] = $m
    $totalOrigen += $m.Bytes
    # Truncado a mano: un nombre largo corre las columnas y la tabla deja de
    # servir justo cuando mas archivos hay que comparar.
    $etiqueta = if ($v.Name.Length -gt 22) { $v.Name.Substring(0, 19) + '...' } else { $v.Name }
    Write-Output ("{0,-22} {1,8:N0} {2,7:N1} {3,11} {4,10:N0} {5,6}" -f `
        $etiqueta, ($m.Bytes/1MB), ($m.Segundos/60), "$($m.Ancho)x$($m.Alto)", $m.KbpsTotal, $m.Codec)
}
Write-Output ('-' * 70)
Write-Output ("TOTAL: {0:N2} GB en {1} archivos" -f ($totalOrigen/1GB), $videos.Count)

$sobreLimite = @($medidas.Values | Where-Object { $_.Bytes -gt $LIMITE_CACHE }).Count
Write-Output ("Pasan de 512 MB (no se cachean en Blob): {0} de {1}" -f $sobreLimite, $videos.Count)

if (-not $Aplicar) {
    Write-Output ""
    Write-Output "MEDICION: no se toco nada. Para comprimir de verdad, agrega -Aplicar"
    exit 0
}

# --------------------------------------------------------------- comprimir --
if (-not (Test-Path $Destino)) { New-Item -ItemType Directory -Path $Destino | Out-Null }

$totalFinal = 0
foreach ($v in $videos) {
    $m = $medidas[$v.Name]

    # La salida se renombra a modulo-NN.mp4 porque es lo que espera el resto de
    # la cadena: subir-videos.mjs filtra por ese patron y de ahi salen tanto el
    # pathname en Blob como el SQL de lecciones.video_url. Dejarlo como
    # "Modulo3Aula.mp4" hace que subir-videos no encuentre nada y el error
    # aparece hasta el final, cuando ya se comprimieron los once.
    if ($v.Name -notmatch '(\d+)') { throw "No le veo numero de modulo a $($v.Name)" }
    $numero = [int]$Matches[1]
    $salida = Join-Path $Destino ("modulo-{0:D2}.mp4" -f $numero)
    if (Test-Path $salida) {
        Write-Output ("SALTADO {0} - ya existe como {1}" -f $v.Name, (Split-Path $salida -Leaf))
        $totalFinal += (Get-Item $salida).Length
        continue
    }

    # Solo se reescala hacia ABAJO. Subir un 720p a 1080p infla el archivo sin
    # agregar un solo detalle.
    $filtro = if ($m.Alto -gt $AlturaMax) { @('-vf', "scale=-2:$AlturaMax") } else { @() }

    Write-Output ("Comprimiendo {0} ({1:N0} MB, {2:N1} min)..." -f $v.Name, ($m.Bytes/1MB), ($m.Segundos/60))
    $t0 = [Diagnostics.Stopwatch]::StartNew()

    # Se escribe a .parcial y se renombra al final. Si matan el proceso a media
    # compresion, lo que queda es un .parcial que nadie confunde con terminado;
    # si escribieramos directo al nombre final, la siguiente corrida lo daria
    # por bueno y saltaria el modulo con un archivo sin moov atom, que no
    # reproduce. Paso exactamente eso con el 7.
    # El temporal TIENE que seguir terminando en .mp4: ffmpeg deduce el formato
    # de salida por la extension, y con un ".parcial" al final contesta -22 sin
    # decir por que. La marca va antes de la extension, no despues.
    $temporal = Join-Path $Destino ("modulo-{0:D2}.parcial.mp4" -f $numero)
    if (Test-Path $temporal) { Remove-Item $temporal -Force }

    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & ffmpeg -hide_banner -loglevel error -y -i $v.FullName `
        @filtro `
        -c:v libx264 -crf $Crf -preset $Preset -pix_fmt yuv420p `
        -c:a aac -b:a 128k -ac 2 `
        -movflags +faststart `
        -- $temporal 2>$null
    $codigo = $LASTEXITCODE
    $ErrorActionPreference = $prev

    if ($codigo -ne 0 -or -not (Test-Path $temporal)) {
        Write-Output ("    FALLO (codigo {0}). Me detengo." -f $codigo)
        if (Test-Path $temporal) { Remove-Item $temporal -Force }
        break
    }
    Move-Item $temporal $salida -Force

    $nuevo = (Get-Item $salida).Length
    $totalFinal += $nuevo
    $aviso = if ($nuevo -gt $LIMITE_CACHE) { "  <-- SIGUE ARRIBA DE 512 MB, baja el CRF o la altura" } else { "" }
    Write-Output ("    {0:N0} MB -> {1:N0} MB ({2:N0}% menos) en {3:N1} min{4}" -f `
        ($m.Bytes/1MB), ($nuevo/1MB), (100 - ($nuevo / $m.Bytes * 100)), $t0.Elapsed.TotalMinutes, $aviso)
}

Write-Output ""
Write-Output ("TOTAL: {0:N2} GB -> {1:N2} GB" -f ($totalOrigen/1GB), ($totalFinal/1GB))
Write-Output "Revisa un par de videos completos antes de subirlos. El peso no dice nada de como se ve."
