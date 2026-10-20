(function() {
  "use strict";
  const buttons=Array.from(document.querySelectorAll("[data-mr-choice]"));
  const panels=Array.from(document.querySelectorAll("[data-mr-panel]"));
  const showAll=document.querySelector("[data-mr-show-all]");
  const status=document.getElementById("mr-selection-status");
  if(buttons.length!==7||panels.length!==7||!showAll||!status)return;
  function choose(id){
    buttons.forEach(function(button){button.setAttribute("aria-pressed",String(button.dataset.mrChoice===id));});
    showAll.setAttribute("aria-pressed",String(id===null));
    panels.forEach(function(panel){panel.hidden=(id!==null&&panel.dataset.mrPanel!==id);});
    status.textContent=id===null?"Showing all seven decisions.":"Showing decision "+id+".";
  }
  buttons.forEach(function(button){button.addEventListener("click",function(){choose(button.dataset.mrChoice);});});
  showAll.addEventListener("click",function(){choose(null);});
  choose("D1");
})();
