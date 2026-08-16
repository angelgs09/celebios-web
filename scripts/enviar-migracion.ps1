# Avisa a los alumnos que vienen de Kajabi que el curso cambió de plataforma.
#
# Por qué no sale de Supabase: los 21 ya existen como usuarios, así que
# /auth/v1/invite contesta 422 email_exists y su plantilla nunca se usa. Y
# aunque se pudiera, 21 ligas mágicas disparadas juntas caducan en una hora:
# la mayoría se leería tarde. Separando el aviso del acceso, el aviso no caduca.
#
# Va en ENSAYO por defecto, igual que importar-alumnos.mjs. Para mandar de
# verdad: -Aplicar. Manda de uno en uno y con pausa, para poder parar si el
# primero rebota.
#
# La contraseña de aplicación se lee de .env.production.local (gitignored),
# clave SMTP_APP_PASSWORD. Nunca se imprime.

param(
    [switch]$Aplicar,
    [string]$Solo = "",           # manda unicamente a esta direccion (prueba)
    [int]$PausaSegundos = 20,
    [string]$Preview = "",        # escribe los 3 correos a un HTML y no manda nada
    [switch]$Correccion,          # manda SOLO el correo que retira la sesion en vivo
    [switch]$Constancia           # manda SOLO la constancia oficial a quien esta al 100%
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# -Correccion retira una oferta que salio por error a UNA sola persona. El filtro
# de destinatarios de mas abajo no sabe nada de este switch, asi que sin este
# guard `-Correccion -Aplicar` le manda "corrijo lo de la sesion en vivo" a los
# 17 que nunca vieron esa oferta, y les recuerda algo que jamas se les ofrecio.
if ($Correccion -and -not $Solo) {
    throw "-Correccion va dirigido a una persona. Agrega -Solo <correo>."
}

$RAIZ      = Split-Path -Parent $PSScriptRoot

$CSV       = "C:\Users\coche\Desktop\CELEBIOS-web\kajabi-export\alumnos-gatos.csv"
$ENVFILE   = Join-Path $RAIZ ".env.production.local"
$AULA      = "https://celebios.vercel.app/aula"
$PRIVACIDAD= "https://celebios.vercel.app/aviso-de-privacidad"
$REMITENTE = "contacto@celebios.com"
$NOMBRE_DE = "CELEBIOS"

# ---------------------------------------------------------------- plantilla --
# Misma estructura visual que las plantillas del aula (verificadas en vivo el
# 14-ago: llegaron a Recibidos y los acentos salieron bien). Que el aviso y la
# liga de acceso se vean del mismo remitente importa mas que la originalidad.
function Construir-Html {
    param([string]$Titular, [string]$Preheader, [string]$Cuerpo, [string]$Boton)

    # Sin -Boton no se pinta el bloque. A quien ya termino el curso no se le
    # manda un boton al aula: hoy lleva a la pantalla de mantenimiento, y de
    # todos modos ahi ya no le queda nada por hacer.
    $bloqueBoton = if ($Boton) { @"
  <p style="margin:0 0 24px">
    <!-- Blanco sobre marino, no marino sobre cian: el modo oscuro de Gmail
         invierte los textos oscuros y sobre el cian quedaban lavados. 14.4:1
         aguanta cualquier inversion. El cian se queda como acento, no como
         fondo de boton. -->
    <a href="$AULA"
       style="display:inline-block;background:#16294C;color:#FFFFFF;font-weight:600;
              font-size:16px;text-decoration:none;padding:14px 28px;border-radius:4px;
              border:2px solid #16294C">
      $Boton
    </a>
  </p>
"@ } else { "" }

    @"
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>$Titular</title>
</head>
<body style="margin:0;padding:0;background:#F4F6F4">
<div style="display:none;font-size:1px;color:#F4F6F4;max-height:0;overflow:hidden">$Preheader</div>
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;color:#16294C;background:#FFFFFF">

  <p style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#4D5F7C;margin:0 0 24px">
    CELEBIOS &middot; Aula virtual
  </p>

  <h1 style="font-size:24px;line-height:1.25;margin:0 0 16px;color:#16294C">
    $Titular
  </h1>

$Cuerpo

$bloqueBoton

  <p style="font-size:14px;line-height:1.6;color:#4D5F7C;margin:0 0 32px">
    Si algo no coincide con lo que recuerdas, responde este correo y lo revisamos.
  </p>

  <hr style="border:none;border-top:1px solid #C3CDC0;margin:0 0 16px">

  <p style="font-size:12px;line-height:1.5;color:#4D5F7C;margin:0">
    Centro Latinoamericano de Estudios en Ciencias Biol&oacute;gicas y de la Salud Animal<br>
    <a href="$PRIVACIDAD" style="color:#4D5F7C">Aviso de privacidad</a>
  </p>

</div>
</body>
</html>
"@
}

function P([string]$t) { "  <p style=`"font-size:16px;line-height:1.6;margin:0 0 16px;color:#16294C`">$t</p>" }

# ------------------------------------------------------------------ textos --
function Correo-ConAvance {
    param([string]$Nombre, [int]$Pct)
    $cuerpo = @(
        (P "Hola, ${Nombre}:"),
        (P "Movimos <strong>Lenguaje y Comunicaci&oacute;n de los Gatos</strong> a nuestra propia plataforma. Los once m&oacute;dulos y sus ex&aacute;menes est&aacute;n completos, y entrar es m&aacute;s simple que antes: escribes tu correo, te llega una liga y ya. No hay contrase&ntilde;a que recordar."),
        (P "Te debo una advertencia. <strong>Tu avance no se pudo traer.</strong> La plataforma anterior no permite exportar en qu&eacute; m&oacute;dulo iba cada quien, as&iacute; que el curso arranca en blanco."),
        (P "En el registro que alcanzamos a rescatar apareces con <strong>$Pct%</strong> del curso. El aula te deja abrir cualquier m&oacute;dulo desde el primer d&iacute;a, as&iacute; que puedes ir directo a donde te quedaste.")
    ) -join "`n"
    Construir-Html -Titular "Tu curso cambi&oacute; de casa" `
                   -Preheader "Ya no est&aacute; en Kajabi. As&iacute; entras ahora, y algo que se qued&oacute; en el camino." `
                   -Cuerpo $cuerpo -Boton "Entrar a mi curso"
}

# El que TERMINO no puede recibir "tu avance no se pudo traer": ya acabo. Lo que
# le debemos es su constancia, y esa decision es de Angel, asi que por defecto
# queda FUERA del lote y se manda a mano.
function Correo-Termino {
    param([string]$Nombre, [string]$Folio)
    $cuerpo = @(
        (P "Hola, ${Nombre}:"),
        (P "Terminaste el curso completo. De todas las personas que lo tomaron, muy pocas llegaron al final, as&iacute; que gracias por eso."),
        (P "<strong>Aqu&iacute; va tu constancia</strong>, adjunta a este correo, con folio <strong>$Folio</strong>."),
        (P "De paso: movimos el curso a nuestra propia plataforma. Tu acceso sigue ah&iacute; y puedes volver a cualquier m&oacute;dulo cuando quieras &mdash; ahora escribes tu correo, te llega una liga y entras. Ya no hay contrase&ntilde;a."),
        # OJO: el precio va como &#36; y no como $. PowerShell interpola "$200"
        # como variable y lo deja VACIO: el correo salia diciendo "Son  y te
        # queda la grabacion". Se cazo al renderizar el preview, no antes.
        (P "Y una cosa m&aacute;s. Estoy armando una <strong>sesi&oacute;n en vivo de una hora</strong> para resolver casos reales: los gatos de quienes tomaron el curso, con sus man&iacute;as y sus pleitos de verdad. Cupo chico, para que d&eacute; tiempo de ver el tuyo. Son <strong>&#36;200</strong> y te queda la grabaci&oacute;n."),
        (P "&iquest;Te aparto un lugar?")
    ) -join "`n"
    Construir-Html -Titular "Terminaste el curso" `
                   -Preheader "Va tu constancia adjunta. Y una propuesta." `
                   -Cuerpo $cuerpo -Boton "Volver al curso"
}

# Retira la oferta de sesion en vivo que salio por error el 14-ago. Se manda
# suelta, sin adjunto: la constancia ya la tiene.
function Correo-Correccion {
    param([string]$Nombre)
    $cuerpo = @(
        (P "Hola, ${Nombre}:"),
        (P "Te escribo para corregir algo de mi correo de hace un rato. Mencion&eacute; una sesi&oacute;n en vivo y <strong>me adelant&eacute;</strong>: todav&iacute;a no la tengo armada, as&iacute; que prefiero dec&iacute;rtelo hoy y no cuando me escribieras para apartar lugar."),
        (P "Tu constancia sigue en pie, es tuya y no cambia nada de eso."),
        (P "Estoy terminando otra cosa, y esa s&iacute; existe. Te escribo en unos d&iacute;as para ense&ntilde;&aacute;rtela. Perd&oacute;n por el ida y vuelta.")
    ) -join "`n"
    Construir-Html -Titular "Corrijo lo de la sesi&oacute;n" `
                   -Preheader "Me adelant&eacute;. Tu constancia sigue igual." `
                   -Cuerpo $cuerpo -Boton "Volver al curso"
}

# Manda la constancia sobre la plantilla oficial. No explica por que llega una
# segunda: al alumno se le dice cual se queda, no que paso con la anterior.
function Correo-Constancia {
    param([string]$Nombre)
    $cuerpo = @(
        (P "Hola, ${Nombre}:"),
        (P "Aqu&iacute; va <strong>tu constancia</strong>, adjunta en PDF."),
        (P "La emiten CELEBIOS y Etolog&iacute;aCH, y lleva el registro del Consejo Nacional de Certificaci&oacute;n en Medicina Veterinaria y Zootecnia (CONCERVET). Es la versi&oacute;n definitiva, as&iacute; que gu&aacute;rdate esta."),
        (P "Gracias por llegar al final. De todas las personas que empezaron el curso, muy pocas lo terminaron.")
    ) -join "`n"
    Construir-Html -Titular "Tu constancia" `
                   -Preheader "Va adjunta en PDF, con el registro de CONCERVET." `
                   -Cuerpo $cuerpo -Boton ""
}

function Correo-SinAvance {
    param([string]$Nombre)
    $cuerpo = @(
        (P "Hola, ${Nombre}:"),
        (P "Movimos <strong>Lenguaje y Comunicaci&oacute;n de los Gatos</strong> a nuestra propia plataforma. Los once m&oacute;dulos y sus ex&aacute;menes est&aacute;n completos y te siguen esperando."),
        (P "Lo que m&aacute;s cambia es entrar: escribes tu correo, te llega una liga y listo. <strong>Ya no hay contrase&ntilde;a.</strong> Si eso era lo que te frenaba, ese obst&aacute;culo desapareci&oacute;."),
        (P "Puedes empezar por el m&oacute;dulo que quieras y a tu ritmo. No hay fechas ni horarios.")
    ) -join "`n"
    Construir-Html -Titular "Tu curso cambi&oacute; de casa" `
                   -Preheader "Ya no est&aacute; en Kajabi, y ahora entrar es m&aacute;s f&aacute;cil." `
                   -Cuerpo $cuerpo -Boton "Empezar el curso"
}

# ---------------------------------------------------------------- preview --
if ($Preview) {
    $muestras = @(
        @{ t = "1 &middot; Con avance (11 personas)";  sub = "Tu curso de gatos cambi&oacute; de casa"; h = (Correo-ConAvance -Nombre "Luis" -Pct 69) },
        @{ t = "2 &middot; Sin avance (6 personas)";   sub = "Tu curso de gatos cambi&oacute; de casa"; h = (Correo-SinAvance -Nombre "Diana") },
        @{ t = "3 &middot; Termin&oacute; (1 persona, -Constancia)"; sub = "Tu constancia del curso de gatos"; h = (Correo-Constancia -Nombre "Ana") }
    )
    $secciones = foreach ($m in $muestras) {
        $srcdoc = $m.h -replace '"', '&quot;'
        @"
<section>
  <h2>$($m.t)</h2>
  <p class="asunto"><span>Asunto</span> $($m.sub)</p>
  <p class="asunto"><span>De</span> CELEBIOS &lt;contacto@celebios.com&gt;</p>
  <iframe srcdoc="$srcdoc"></iframe>
</section>
"@
    }
    $pagina = @"
<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Correos de migracion - CELEBIOS</title>
<style>
 body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#EEF1EE;margin:0;padding:32px;color:#16294C}
 h1{font-size:22px;margin:0 0 4px} .sub{color:#4D5F7C;margin:0 0 32px;font-size:14px}
 .grid{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}
 section{background:#fff;border:1px solid #C3CDC0;border-radius:8px;padding:16px;width:560px}
 h2{font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:#4D5F7C;margin:0 0 12px}
 .asunto{font-size:13px;margin:0 0 6px;color:#16294C}
 .asunto span{display:inline-block;width:52px;color:#4D5F7C;font-size:11px;text-transform:uppercase;letter-spacing:.08em}
 iframe{width:100%;height:640px;border:1px solid #E2E8E2;border-radius:4px;margin-top:12px;background:#F4F6F4}
</style></head><body>
<h1>Correos de migraci&oacute;n</h1>
<p class="sub">Lo que van a ver los 18 alumnos que vienen de Kajabi. Tal cual, sin retoques.</p>
<div class="grid">
$($secciones -join "`n")
</div></body></html>
"@
    $pagina | Set-Content -Path $Preview -Encoding utf8
    Write-Output "Preview escrito en: $Preview"
    exit 0
}

# ------------------------------------------------------------------ envio --
$todos = Import-Csv -Path $CSV -Encoding UTF8
# -Solo salta el filtro de internas a proposito: la prueba se manda a Angel,
# que esta marcado interna=si y si no, quedaria fuera y no se probaria nada.
if ($Solo) { $alumnos = $todos | Where-Object { $_.correo -eq $Solo } }
else       { $alumnos = $todos | Where-Object { $_.interna -ne 'si' } }

Write-Output ("Destinatarios: " + $alumnos.Count + "   Modo: " + $(if ($Aplicar) { "ENVIO REAL" } else { "ENSAYO" }))
Write-Output ""

$cliente = $null
if ($Aplicar) {
    # Dos de las tres plantillas del lote llevan un boton "Entrar a mi curso" que
    # apunta al aula. Si el aula esta en mantenimiento, ese boton lleva a
    # "Volvemos muy pronto": 17 personas invitadas a un muro. La regla ya estaba
    # escrita en este archivo -- por eso Correo-Constancia va sin boton -- pero
    # se habia aplicado solo a la plantilla de una persona. Aqui se comprueba
    # contra el aula DESPLEGADA, no contra lo que uno crea que esta desplegado.
    # Solo -Constancia esta exento: es la unica plantilla SIN boton al aula.
    # -Correccion tambien lleva uno, asi que tiene que pasar por el guard.
    if (-not $Constancia) {
        # OJO con el nombre de esta variable: NO puede llamarse $aula, porque
        # PowerShell no distingue mayusculas y pisaria la constante $AULA de
        # arriba con las 45 KB del HTML. El guard tapaba ese efecto al disparar
        # siempre; el dia que se arreglara solo la condicion, habrian salido 17
        # correos con la pagina entera metida dentro del href del boton.
        try {
            $htmlDelAula = (Invoke-WebRequest -Uri $AULA -UseBasicParsing -TimeoutSec 20).Content
        } catch {
            throw "No pude comprobar si el aula esta abierta ($($_.Exception.Message)). No mando nada a ciegas."
        }
        # Se lee el VALOR de la bandera, no la presencia del markup. La seccion
        # <section id="v-mantenimiento" hidden> y el titular "Volvemos muy
        # pronto" estan SIEMPRE en el HTML servido (aula/index.html:127 y 131):
        # lo que enciende esa pantalla es la constante de JS, y una descarga con
        # Invoke-WebRequest no ejecuta JS. Buscar el markup daba positivo con el
        # aula abierta, o sea que el gate no dejaba mandar nunca.
        $bandera = [regex]::Match($htmlDelAula, 'const\s+EN_MANTENIMIENTO\s*=\s*(true|false)')
        if (-not $bandera.Success) {
            throw "No encontre EN_MANTENIMIENTO en el aula desplegada. Cambio el codigo y este guard ya no sabe leerlo; revisalo antes de mandar nada."
        }
        if ($bandera.Groups[1].Value -eq 'true') {
            throw "El aula esta en mantenimiento: estos correos llevan boton al aula y mandarian a la gente a la pantalla de 'Volvemos muy pronto'. Reabre primero (EN_MANTENIMIENTO = false) o quita el -Boton de las plantillas."
        }
    }

    $linea = Get-Content $ENVFILE | Where-Object { $_ -like "SMTP_APP_PASSWORD=*" } | Select-Object -First 1
    if (-not $linea) { throw "Falta SMTP_APP_PASSWORD en $ENVFILE" }
    $pass = ($linea -replace '^SMTP_APP_PASSWORD=', '').Trim().Trim('"') -replace '\s', ''
    if ($pass.Length -ne 16) { throw "La contrasena de aplicacion debe tener 16 caracteres; tiene $($pass.Length)" }
    $cliente = New-Object System.Net.Mail.SmtpClient('smtp.gmail.com', 587)
    $cliente.EnableSsl = $true
    $cliente.Credentials = New-Object System.Net.NetworkCredential($REMITENTE, $pass)
    $pass = $null
}

$n = 0
foreach ($a in $alumnos) {
    $n++
    # Se limpia en CADA vuelta: si no, el adjunto de quien termino se le colaria
    # a todos los que vienen despues en el lote.
    $adjunto = $null
    $pct = [int]$a.progreso_pct
    $nombre = ($a.nombre -split ' ')[0]
    $nombre = $nombre.Substring(0,1).ToUpper() + $nombre.Substring(1).ToLower()

    if ($Constancia) {
        if ($pct -lt 100) { continue }   # la constancia es solo de quien acredito
        $slug = ($a.nombre -replace '[^\w]', '-') -replace '-+','-'
        $adjunto = "C:\Users\coche\Desktop\CELEBIOS-constancias\Constancia-$slug.pdf"
        if (-not (Test-Path $adjunto)) {
            Write-Output ("    NO existe la constancia en PDF: " + $adjunto)
            Write-Output "    Generala antes con generar-constancia.ps1. No mando nada."
            continue
        }
        $html = Correo-Constancia -Nombre $nombre
        $tipo = "constancia oficial (100%)"
        $asuntoTexto = "Tu constancia del curso de gatos"
    }
    elseif ($Correccion) {
        $html = Correo-Correccion -Nombre $nombre
        $tipo = "correccion (retira la sesion)"
        $asuntoTexto = "Corrijo lo de la sesi" + [char]0xF3 + "n"
    }
    elseif ($pct -ge 100) {
        # Correo-Termino quedo obsoleto: inventaba un folio propio y llevaba el
        # upsell que se retiro. Quien termina recibe -Constancia, no esto.
        Write-Output ("{0,2}. {1,-40} TERMINO (100%) -> usa -Constancia" -f $n, $a.correo)
        continue
    }
    elseif ($pct -gt 0) { $html = Correo-ConAvance -Nombre $nombre -Pct $pct; $tipo = "con avance ($pct%)"; $asuntoTexto = "Tu curso de gatos cambi" + [char]0xF3 + " de casa" }
    else                { $html = Correo-SinAvance -Nombre $nombre;          $tipo = "sin avance";          $asuntoTexto = "Tu curso de gatos cambi" + [char]0xF3 + " de casa" }

    Write-Output ("{0,2}. {1,-40} {2}" -f $n, $a.correo, $tipo)

    if ($Aplicar) {
        $msg = New-Object System.Net.Mail.MailMessage
        $msg.From = New-Object System.Net.Mail.MailAddress($REMITENTE, $NOMBRE_DE, [Text.Encoding]::UTF8)
        $msg.To.Add($a.correo)
        $msg.Subject = $asuntoTexto
        $msg.SubjectEncoding = [Text.Encoding]::UTF8
        $msg.Body = $html
        $msg.BodyEncoding = [Text.Encoding]::UTF8
        $msg.IsBodyHtml = $true
        if ($adjunto -and (Test-Path $adjunto)) {
            $msg.Attachments.Add((New-Object System.Net.Mail.Attachment($adjunto)))
        }
        try {
            $cliente.Send($msg)
            Write-Output "    -> enviado"
        } catch {
            Write-Output ("    -> FALLO: " + $_.Exception.Message)
            Write-Output "    Me detengo aqui para no repetir el error 17 veces mas."
            break
        } finally { $msg.Dispose() }
        if ($n -lt $alumnos.Count) { Start-Sleep -Seconds $PausaSegundos }
    }
}

if (-not $Aplicar) {
    Write-Output ""
    Write-Output "ENSAYO: no se mando nada. Para enviar de verdad, agrega -Aplicar"
}
