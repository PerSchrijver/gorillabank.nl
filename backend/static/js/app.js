setTimeout(()=>{document.querySelectorAll('.flash').forEach(e=>e.remove());},4000);

/*  TODO: remove before prod 🫣
    fetch('/debug/users')
      .then(r=>r.json()).then(console.table);
*/
