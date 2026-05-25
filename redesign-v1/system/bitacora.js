/* CELEBIOS — bitácora.js · interacciones compartidas.
   1) nav móvil (hamburguesa, aria + Escape)  2) preview que sigue al cursor en .dip
   3) parallax sutil nativo scroll() con fallback rAF. Respeta prefers-reduced-motion. */
(function(){
  "use strict";
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  function reduced(){ return RM && RM.matches; }

  /* ---- 1. NAV móvil ---- */
  (function(){
    var t=document.getElementById('nav-toggle'),m=document.getElementById('nav-menu');
    if(!t||!m)return;
    function set(open){
      t.setAttribute('aria-expanded',open?'true':'false');
      t.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');
      m.classList.toggle('open',open);
    }
    t.addEventListener('click',function(){set(t.getAttribute('aria-expanded')!=='true');});
    m.addEventListener('click',function(e){if(e.target.tagName==='A')set(false);});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&t.getAttribute('aria-expanded')==='true'){set(false);t.focus();}});
  })();

  if (reduced()) return;

  /* ---- 2. Preview de diplomado que sigue al cursor (solo hover/fine) ---- */
  if (window.matchMedia('(hover:hover) and (pointer:fine)').matches){
    document.querySelectorAll('.dip').forEach(function(row){
      var img = row.querySelector('.dip__img');
      if (!img) return;
      var raf = 0, mx = 0, my = 0;
      function apply(){ raf = 0; img.style.setProperty('--mx', mx+'px'); img.style.setProperty('--my', my+'px'); }
      row.addEventListener('pointermove', function(e){
        var r = row.getBoundingClientRect();
        mx = e.clientX - r.left; my = e.clientY - r.top;
        if (!raf) raf = requestAnimationFrame(apply);
      });
      row.addEventListener('pointerenter', function(){ img.classList.add('is-tracking'); });
      row.addEventListener('pointerleave', function(){ img.classList.remove('is-tracking'); });
    });
  }

  /* ---- 3. Parallax sutil (máx ~6%, transform/translate only) ---- */
  var pl = document.querySelectorAll('[data-parallax]');
  if (pl.length){
    var nativeOK = window.CSS && CSS.supports && CSS.supports('animation-timeline','scroll()');
    if (nativeOK){
      var s = document.createElement('style');
      s.textContent =
        '@supports (animation-timeline: scroll()){' +
        '.cta .bg[data-parallax]{animation:plx-cta linear both;animation-timeline:view();animation-range:entry cover exit}' +
        '@keyframes plx-cta{from{transform:translateY(-6%)}to{transform:translateY(6%)}}' +
        '}';
      document.head.appendChild(s);
      var hero = document.querySelector('.hero__bg[data-parallax]');
      if (hero){
        var hp = document.createElement('style');
        hp.textContent =
          '@supports (animation-timeline: scroll()){' +
          '.hero__bg[data-parallax]{animation:plx-hero linear both;animation-timeline:scroll(root block);animation-range:0 100vh;translate:0 0}' +
          '@keyframes plx-hero{to{translate:0 6%}}' +
          '}';
        document.head.appendChild(hp);
      }
    } else {
      var ticking = false;
      function onScroll(){
        if (ticking) return; ticking = true;
        requestAnimationFrame(function(){
          var vh = window.innerHeight;
          pl.forEach(function(el){
            var r = el.getBoundingClientRect();
            var p = ((r.top + r.height/2) - vh/2) / vh;
            p = Math.max(-1, Math.min(1, p));
            el.style.transform = 'translateY(' + (p * 6) + '%)' + (el.classList.contains('hero__bg') ? ' scale(1)' : '');
          });
          ticking = false;
        });
      }
      window.addEventListener('scroll', onScroll, {passive:true});
      onScroll();
    }
  }
})();
