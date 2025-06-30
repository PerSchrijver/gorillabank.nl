// setTimeout(()=>{document.querySelectorAll('.flash').forEach(e=>e.remove());},4000);

if (window.location.origin.includes('dev.gorillabank.nl') || window.location.origin.includes(':6969')) {
    const script = document.createElement('script');
    script.src = '/static/js/debug.js';
    document.head.appendChild(script);
}
