from pathlib import Path
p=Path(__file__).parent
text=(p/'article.first.en.md').read_text()
text=text.replace('That observation leads to an algorithm that either constructs a legal completion sequence or explains why progress has stopped.','')
text=text.replace('the courses it can unlock','the courses it can release').replace('Course 0 unlocks 1 and 2','Course 0 releases 1 and 2').replace('it unlocks nothing','it releases nothing').replace('without unlocking anything','without releasing anything')
text=text.replace('**Why use indegree?**','Why use indegree?').replace('**Why can each edge be handled once?**','Why can each edge be handled once?').replace('**Why does an empty queue sometimes mean failure?**','Why does an empty queue sometimes mean failure?').replace('**What are the bounds?**','What are the bounds?')
text=text.replace('zero. \n','zero.\n')
(p/'article.en.md').write_text(text)
