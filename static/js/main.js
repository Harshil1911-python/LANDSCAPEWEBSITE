document.addEventListener("DOMContentLoaded",()=>{
  if(document.getElementById("hero-title")){
    gsap.to("#hero-title",{opacity:1,y:0,duration:1.2,ease:"power3.out",delay:.3});
    gsap.to("#hero-sub",{opacity:1,y:0,duration:1,ease:"power3.out",delay:.6});
    gsap.to("#hero-btns",{opacity:1,y:0,duration:1,ease:"power3.out",delay:.9});
  }
  const b=document.getElementById("mobile-menu-btn"),m=document.getElementById("mobile-menu");
  if(b&&m)b.onclick=()=>m.classList.toggle("hidden");
  const slides=document.querySelectorAll(".hero-slide");
  if(slides.length>1){let i=0;setInterval(()=>{slides[i].classList.remove("opacity-100");slides[i].classList.add("opacity-0");i=(i+1)%slides.length;slides[i].classList.remove("opacity-0");slides[i].classList.add("opacity-100");},1500);}
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

  // Infinite marquee: JS-driven so it always fills the row (even with 1-2 items),
  // scrolls at a constant fast speed, and supports real click-to-pause.
  function initMarquee(trackId, wrapId, speed){
    const track=document.getElementById(trackId);
    const wrap=document.getElementById(wrapId);
    if(!track||!wrap||!track.children.length)return;

    track.classList.add("marquee-track");
    const originalHTML=track.innerHTML;
    let unitWidth=0, paused=false, x=0, rafId=null, lastTs=null;

    function fill(){
      // Rebuild with enough copies so ONE "unit" is at least as wide as the wrap.
      track.innerHTML=originalHTML;
      let guard=0;
      while(track.scrollWidth<wrap.clientWidth && guard<25){
        track.innerHTML+=originalHTML;
        guard++;
      }
      unitWidth=track.scrollWidth;
      // Add a second copy of the unit so the loop is seamless.
      track.innerHTML+=track.innerHTML;
      x=0;
      track.style.transform="translateX(0px)";
    }

    function step(ts){
      if(!lastTs)lastTs=ts;
      const dt=(ts-lastTs)/1000;
      lastTs=ts;
      if(!paused&&unitWidth>0){
        x-=speed*dt;
        if(x<=-unitWidth)x+=unitWidth;
        track.style.transform="translateX("+x+"px)";
      }
      rafId=requestAnimationFrame(step);
    }

    function restart(){
      cancelAnimationFrame(rafId);
      lastTs=null;
      fill();
      rafId=requestAnimationFrame(step);
    }

    restart();
    // Recompute once images (logos etc.) finish loading, and on resize.
    track.querySelectorAll("img").forEach(img=>{
      if(!img.complete)img.addEventListener("load",restart,{once:true});
    });
    let resizeTimer;
    window.addEventListener("resize",()=>{
      clearTimeout(resizeTimer);
      resizeTimer=setTimeout(restart,200);
    });

    wrap.addEventListener("mouseenter",()=>paused=true);
    wrap.addEventListener("mouseleave",()=>paused=false);
    wrap.addEventListener("click",()=>{paused=!paused;});
    document.addEventListener("visibilitychange",()=>{
      if(document.hidden)cancelAnimationFrame(rafId);
      else{lastTs=null;rafId=requestAnimationFrame(step);}
    });
  }
  initMarquee("clients-track","clients-wrap",90);
  initMarquee("test-track","test-wrap",70);

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

  function hideLoader(){
    const L=document.getElementById("page-loader");
    if(L)L.classList.add("hide");
  }
  if(document.readyState==="complete")setTimeout(hideLoader,300);
  else window.addEventListener("load",()=>setTimeout(hideLoader,300));
  setTimeout(hideLoader,4000);

  // YouTube click-to-play (avoids embed "video unavailable" until user clicks)
  document.querySelectorAll(".yt-player").forEach(box=>{
    const btn=box.querySelector(".yt-play");
    if(!btn)return;
    btn.addEventListener("click",()=>{
      const id=(box.dataset.yt||"").trim();
      if(!id)return;
      const ifr=document.createElement("iframe");
      ifr.className="absolute inset-0 w-full h-full";
      ifr.src="https://www.youtube-nocookie.com/embed/"+id+"?autoplay=1&rel=0&modestbranding=1";
      ifr.title="Work video";
      ifr.setAttribute("allow","accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
      ifr.setAttribute("allowfullscreen","");
      ifr.setAttribute("referrerpolicy","strict-origin-when-cross-origin");
      box.innerHTML="";
      box.appendChild(ifr);
    });
  });

});
