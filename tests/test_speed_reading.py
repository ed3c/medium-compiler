"""Lossless formatting controls; these do not certify syntax or pronunciation."""
import copy
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reading_projection',ROOT/'scripts/alg_four_projection.py')
projection=importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)


class ReadingText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text=[]
        self.ignore=0
    def handle_starttag(self,tag,attrs):
        if tag=='span' and (self.ignore or dict(attrs).get('class') in {'alg-reading-mark','alg-minor-break','alg-major-break'}):
            self.ignore+=1
    def handle_endtag(self,tag):
        if tag=='span' and self.ignore: self.ignore-=1
    def handle_data(self,data):
        if not self.ignore: self.text.append(data)


class SpeedReadingTests(unittest.TestCase):
    def setUp(self):
        self.text='The algorithm returns a result. It preserves [a/b] without copying.'
        self.layout={'tokens':[
            {'text':'The algorithm returns ','stress':[{'start':4,'end':6,'word':'algorithm','pronunciation':'ˈæl.ɡər.ɪ.ðəm','source':'https://dictionary.cambridge.org/us/pronunciation/english/algorithm'}]},
            {'text':'a result.','bundle':True},
            {'text':' It preserves [a/b] without copying.','break_before':'major'}],
            'skeleton':'Algorithm → returns result → preserves original data without copying'}

    def test_added_marks_preserve_existing_brackets_slashes_and_complete_source(self):
        rendered=projection.render_speed_reading(self.layout,self.text)
        recovered=ReadingText();recovered.feed(rendered)
        self.assertEqual(''.join(recovered.text),self.text)
        self.assertIn('<strong class="alg-stress">al</strong>gorithm',rendered)
        self.assertIn('//</span><br>',rendered)
        self.assertIn('[a/b]',rendered)

    def test_source_drift_function_word_bolding_missing_evidence_and_long_skeleton_refuse(self):
        for failure in ('drift','function','evidence','skeleton'):
            layout=copy.deepcopy(self.layout)
            if failure=='drift': layout['tokens'][0]['text']='An algorithm returns '
            elif failure=='function': layout['tokens'][0]['stress'][0].update(start=0,end=3,word='The')
            elif failure=='evidence': layout['tokens'][0]['stress'][0]['source']=''
            else: layout['skeleton']='word '*16
            with self.subTest(failure=failure),self.assertRaises(ValueError):
                projection.render_speed_reading(layout,self.text)

    def test_unverified_words_stay_plain_and_source_html_is_escaped(self):
        text='Keep <script> and [literal] / path/a//b.'
        layout={'tokens':[{'text':text}],'skeleton':'Reader → preserves source → leaves unverified words plain'}
        rendered=projection.render_speed_reading(layout,text)
        self.assertEqual(rendered,'Keep &lt;script&gt; and [literal] / path/a//b.')
        self.assertNotIn('<strong',rendered)


if __name__=='__main__': unittest.main()
