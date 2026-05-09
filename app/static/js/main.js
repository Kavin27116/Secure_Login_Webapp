/* Password strength meter logic */
(function () {
  const pwdInput = document.getElementById('password');
  if (!pwdInput) return;

  const fill  = document.getElementById('strength-fill');
  const label = document.getElementById('strength-label');
  if (!fill || !label) return;

  const levels = [
    { label: '',        cls: '' },
    { label: 'Weak',   cls: 'weak' },
    { label: 'Fair',   cls: 'fair' },
    { label: 'Good',   cls: 'good' },
    { label: 'Strong', cls: 'strong' },
  ];

  function score(p) {
    let s = 0;
    if (p.length >= 8)  s++;
    if (p.length >= 12) s++;
    if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s++;
    if (/\d/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    return Math.min(4, Math.ceil(s * 4 / 5));
  }

  pwdInput.addEventListener('input', function () {
    const v = pwdInput.value;
    if (!v) { fill.className = 'strength-fill'; label.textContent = ''; return; }
    const lvl = score(v);
    fill.className = 'strength-fill ' + levels[lvl].cls;
    label.textContent = 'Strength: ' + levels[lvl].label;
  });

  /* Toggle show/hide password */
  const toggleBtns = document.querySelectorAll('.input-toggle');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const target = document.getElementById(this.dataset.target);
      if (!target) return;
      if (target.type === 'password') {
        target.type = 'text';
        this.textContent = '🙈';
      } else {
        target.type = 'password';
        this.textContent = '👁️';
      }
    });
  });
})();

/* Auto-dismiss flash messages */
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s ease, transform .4s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    setTimeout(() => el.remove(), 400);
  }, 4500);
  el.addEventListener('click', () => el.remove());
});
