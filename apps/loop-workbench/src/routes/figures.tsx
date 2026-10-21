import {createFileRoute} from '@tanstack/react-router'
import '../learning.css'
export const Route=createFileRoute('/figures')({component:FigureLab})
function FigureLab(){
 return <main className="learn-shell">
  <header className="learn-top"><a href="/">← LOOP WORKBENCH</a><span>MODULAR FIGURE LAB</span><a href="/learning">LOCAL LEARNING ↗</a></header>
  <section className="learn-intro">
   <span className="learn-overline">AI ENGINEERING FROM SCRATCH · SOURCE-PRESERVED</span>
   <h1>Explore real mechanisms.<br/><em>Reuse, don't rewrite.</em></h1>
   <p>Selected upstream Math / Engineering figures run in a restricted iframe without same-origin privileges. Original computational source is pinned, with no native Agent or grading authority.</p>
  </section>
  <iframe title="AIFS source-preserved interactive figures" src="/aifs/figure-lab.html"
   sandbox="allow-scripts" referrerPolicy="no-referrer"
   style={{display:'block',border:'1px solid #dedbd2',width:'100%',height:'min(1160px,130vh)',background:'#fafaf5'}}/>
  <footer className="learn-footer">MIT THIRD-PARTY MODULES · SOURCE-BOUND DEMONSTRATION · NO PROVIDER EFFECTS</footer>
 </main>
}
