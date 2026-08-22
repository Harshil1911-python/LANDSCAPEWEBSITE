document.addEventListener("DOMContentLoaded",()=>{
  if(document.getElementById("hero-title")){
    gsap.to("#hero-title",{opacity:1,y:0,duration:1.2,ease:"power3.out",delay:.3});
    gsap.to("#hero-sub",{opacity:1,y:0,duration:1,ease:"power3.out",delay:.6});
    gsap.to("#hero-btns",{opacity:1,y:0,duration:1,ease:"power3.out",delay:.9});
  }
  const b=document.getElementById("mobile-menu-btn"),m=document.getElementById("mobile-menu");
  if(b&&m)b.onclick=()=>m.classList.toggle("hidden");
  const slides=document.querySelectorAll(".hero-slide");
  if(slides.length>1){let i=0;setInterval(()=>{slides[i].classList.remove("opacity-100");slides[i].classList.add("opacity-0");i=(i+1)%slides.length;slides[i].classList.remove("opacity-0");slides[i].classList.add("opacity-100");},4000);}
  document.addEventListener("keydown",e=>{if(e.key==="F12"||(e.ctrlKey&&e.shiftKey&&["I","J","C"].includes(e.key))||(e.ctrlKey&&e.key==="u"))e.preventDefault();});

  const counters=document.querySelectorAll(".counter");
  let counted=false;
  function runCounters(){
    if(counted)return;counted=true;
    counters.forEach(el=>{
      const target=parseInt(String(el.dataset.target).replace(/\D/g),10)||0;
      const dur=1500,start=performance.now();
      (function tick(now){const p=Math.min((now-start)/dur,1);el.textContent=Math.floor(target*(.5-Math.cos(Math.PI*p)/2));if(p<1)requestAnimationFrame(tick);else el.textContent=target;})(start);
    });
  }
  const box=document.getElementById("counters");
  if(box&&counters.length){const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){runCounters();io.disconnect();}},{threshold:.2});io.observe(box);}

  // Infinite marquee: duplicate content exactly once so -50% is seamless
  function prep(id){
    const el=document.getElementById(id);
    if(!el||!el.children.length)return;
    el.innerHTML=el.innerHTML+el.innerHTML;
    el.classList.add("marquee-track");
  }
  prep("clients-track");
  prep("test-track");

  if("serviceWorker" in navigator)navigator.serviceWorker.getRegistrations().then(r=>r.forEach(x=>x.update()));

  const modal=document.getElementById("quote-modal");
  function openM(e){if(e)e.preventDefault();if(modal){modal.classList.remove("hidden");modal.classList.add("flex");}}
  function closeM(){if(modal){modal.classList.add("hidden");modal.classList.remove("flex");}}
  ["open-quote","open-quote-2","open-quote-faq"].forEach(id=>{const el=document.getElementById(id);if(el)el.onclick=openM;});
  const cq=document.getElementById("close-quote");if(cq)cq.onclick=closeM;
  if(modal)modal.onclick=e=>{if(e.target===modal)closeM();};
  async function sendQuote(form,status){
    const data=Object.fromEntries(new FormData(form).entries());
    if(status){status.classList.remove("hidden");status.textContent="Sending...";status.className="text-sm text-center text-slate-500 mt-2";}
    try{
      const r=await fetch("/api/quote",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
      const j=await r.json();
      if(j.ok){if(status){status.textContent="Sent!";status.className="text-sm text-center text-green-600 mt-2";}form.reset();}
      else if(status){status.textContent=j.error||"Failed";status.className="text-sm text-center text-red-600 mt-2";}
    }catch{if(status){status.textContent="Network error";status.className="text-sm text-center text-red-600 mt-2";}}
  }
  const form=document.getElementById("quote-form"),status=document.getElementById("quote-status");
  if(form)form.onsubmit=e=>{e.preventDefault();sendQuote(form,status);};
  const form2=document.getElementById("consult-form"),st2=document.getElementById("consult-status");
  if(form2)form2.onsubmit=e=>{e.preventDefault();sendQuote(form2,st2);};
});
