(function() {
  "use strict";
  const buttons=Array.from(document.querySelectorAll("[data-mr-choice]"));
  const panels=Array.from(document.querySelectorAll("[data-mr-panel]"));
  const graphNodes=Array.from(document.querySelectorAll("[data-mr-node]"));
  const edges=Array.from(document.querySelectorAll("[data-mr-edge]"));
  const showAll=document.querySelector("[data-mr-show-all]");
  const status=document.getElementById("mr-selection-status");
  if(buttons.length!==7||panels.length!==7||graphNodes.length!==7||edges.length!==8||!showAll||!status)return;
  function choose(id){
    buttons.forEach(function(button){button.setAttribute("aria-pressed",String(button.dataset.mrChoice===id));});
    showAll.setAttribute("aria-pressed",String(id===null));
    graphNodes.forEach(function(node){node.setAttribute("aria-pressed",String(node.dataset.mrNode===id));});
    edges.forEach(function(edge){const pair=edge.dataset.mrEdge.split(":");edge.classList.toggle("mr-relevant",id!==null&&(pair[0]===id||pair[1]===id));});
    panels.forEach(function(panel){panel.hidden=(id!==null&&panel.dataset.mrPanel!==id);});
    status.textContent=id===null?"Showing all seven decisions.":"Showing decision "+id+".";
  }
  buttons.forEach(function(button){button.addEventListener("click",function(){choose(button.dataset.mrChoice);});});
  graphNodes.forEach(function(node){node.addEventListener("click",function(){choose(node.dataset.mrNode);});});
  showAll.addEventListener("click",function(){choose(null);});
  choose("D1");
})();
