// Lightweight shooting-stars background appended into .stars-bg
(function () {
  function spawn() {
    const wrap = document.querySelector('.stars-bg');
    if (!wrap) return;

    const star = document.createElement('div');
    star.className = 'shoot';
    const startX = Math.random() * window.innerWidth;
    const startY = Math.random() * window.innerHeight * 0.6;
    const length = 160 + Math.random() * 160;
    const angle = -Math.PI/8 + (Math.random()-0.5) * 0.4;

    star.style.position = 'absolute';
    star.style.left = startX + 'px';
    star.style.top = startY + 'px';
    star.style.width = length + 'px';
    star.style.height = '2px';
    star.style.background = 'linear-gradient(90deg, rgba(255,255,255,0.9), rgba(192,132,252,0.9), transparent)';
    star.style.transform = `rotate(${angle}rad)`;
    star.style.opacity = '0.0';
    star.style.transition = 'transform 900ms linear, opacity 900ms linear';
    star.style.pointerEvents = 'none'; // so stars never block clicks
    star.style.zIndex = 0; // ensure stars are always behind content

    wrap.appendChild(star);

    // fade-in then translate
    requestAnimationFrame(() => {
      star.style.opacity = '1';
      star.style.transform = `translateX(${(-length*0.8)}px) rotate(${angle}rad)`;
    });

    setTimeout(() => {
      star.style.opacity = '0';
      setTimeout(() => star.remove(), 1000);
    }, 900 + Math.random()*1200);
  }

  // initial gentle stars as dots (non-moving)
  function createStaticDots() {
    const wrap = document.querySelector('.stars-bg');
    if (!wrap) return;
    for (let i = 0; i < 100; i++) {
      const dot = document.createElement('div');
      dot.className = 'star-dot';
      dot.style.position = 'absolute';
      dot.style.width = '2px';
      dot.style.height = '2px';
      dot.style.background = 'rgba(255,255,255,' + (0.2 + Math.random()*0.6) + ')';
      dot.style.left = Math.random()*window.innerWidth + 'px';
      dot.style.top = Math.random()*window.innerHeight + 'px';
      dot.style.borderRadius = '50%';
      dot.style.filter = 'blur(0.6px)';
      dot.style.pointerEvents = 'none';
      wrap.appendChild(dot);

      // twinkle effect
      dot.animate(
        [
          { opacity: dot.style.backgroundOpacity || 0.3 },
          { opacity: 1 },
          { opacity: dot.style.backgroundOpacity || 0.3 }
        ],
        {
          duration: 4000 + Math.random() * 4000,
          iterations: Infinity
        }
      );
    }
  }

  window.addEventListener('load', function() {
    createStaticDots();
    setInterval(spawn, 1800 + Math.random()*1200);
    window.addEventListener('resize', function() {
      document.querySelectorAll('.stars-bg > div').forEach(el => el.remove());
      createStaticDots();
    });
  });
})();
