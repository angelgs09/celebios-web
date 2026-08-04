/* Auditor de contraste, para pegar en la consola del navegador.
 *
 * Por que existe: el analisis estatico del CSS se equivoco en los DOS sentidos.
 * Dio por malo el nav (medido contra el fondo del body, cuando el header es un
 * marino traslucido al 92%) y no vio que `.nav-cta` declaraba el color correcto
 * y PERDIA la cascada contra `.nav-links a`, pintandose casi blanco sobre cian.
 * Lo unico que dice la verdad es getComputedStyle sobre la pagina renderizada.
 *
 * Uso:  copiar y pegar en la consola, o desde Playwright con page.evaluate.
 * Devuelve solo lo que NO cumple AA (4.5:1 normal, 3:1 grande), con la regla
 * CSS que lo esta pintando, que es lo que hace falta para arreglarlo.
 */
(() => {
  const lum = (r, g, b) => {
    const f = [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
  };
  const parse = c => {
    const m = (c || '').match(/[\d.]+/g);
    return m ? m.slice(0, 3).map(Number).concat([m[3] !== undefined ? +m[3] : 1]) : null;
  };
  const sobre = (fg, bg) => fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3]));

  // Compone TODA la pila de ancestros respetando alfa. Cortar en el primer
  // fondo "casi opaco" es lo que hizo fallar la primera version: el header
  // esta al 92% y quedaba fuera.
  const fondoReal = el => {
    const capas = [];
    let n = el;
    while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0) capas.push(c);
      if (c && c[3] >= 1) break;
      n = n.parentElement;
    }
    let base = [255, 255, 255];
    for (let i = capas.length - 1; i >= 0; i--) base = sobre(capas[i], base);
    return base.map(Math.round);
  };

  const ratio = (a, b) => {
    const L = [lum(...a), lum(...b)];
    return (Math.max(...L) + 0.05) / (Math.min(...L) + 0.05);
  };

  const reglaQueGana = el => {
    let ultima = null;
    for (const hoja of document.styleSheets) {
      let reglas;
      try { reglas = hoja.cssRules; } catch (e) { continue; }
      for (const r of reglas) {
        if (!r.selectorText || !r.style || !r.style.color) continue;
        try { if (el.matches(r.selectorText)) ultima = r.selectorText + ' { color:' + r.style.color + ' }'; } catch (e) { }
      }
    }
    return ultima;
  };

  const fallos = [];
  document.querySelectorAll('body *').forEach(el => {
    // solo nodos con texto propio: si no, se cuenta el mismo texto N veces
    const txt = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('');
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    const caja = el.getBoundingClientRect();
    if (!caja.width || !caja.height) return;
    const fg = parse(cs.color);
    if (!fg) return;
    const bg = fondoReal(el);
    const efectivo = fg[3] < 1 ? sobre(fg, bg) : fg.slice(0, 3);
    const px = parseFloat(cs.fontSize);
    const minimo = (px >= 24 || (px >= 18.66 && +cs.fontWeight >= 700)) ? 3 : 4.5;
    const cr = ratio(efectivo, bg);
    if (cr < minimo) fallos.push({
      texto: txt.slice(0, 40), ratio: +cr.toFixed(2), minimo,
      color: cs.color, fondo: `rgb(${bg})`, px: Math.round(px), regla: reglaQueGana(el),
    });
  });

  const unicos = [...new Map(fallos.map(f => [f.regla + f.fondo, f])).values()];
  console.table(unicos.sort((a, b) => a.ratio - b.ratio));
  return { nodos: fallos.length, reglas: unicos.length };
})();
