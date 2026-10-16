import unittest, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parent.parent
D=json.loads((ROOT/'data/tasks.json').read_text(encoding='utf-8'))
class ContentTest(unittest.TestCase):
    def test_10_chapters_50_tasks(self):
        self.assertEqual(len(D['chapters']),10)
        self.assertEqual(len(D['tasks']),50)
    def test_action_proof_blocked(self):
        ids=[]
        for x in D['tasks']:
            ids.append(x['id'])
            for k in ('id','title','action','proof','blocked','phase','chapter'):
                self.assertGreaterEqual(len(str(x[k]).strip()),3,f'{x["id"]}:{k}')
            self.assertGreaterEqual(len(x['action']),20)
        self.assertEqual(len(ids),len(set(ids)))
    def test_chapter_files(self):
        for c in D['chapters']:
            p=(ROOT/'guides'/f"{c['code']}.md")
            self.assertTrue(p.exists())
            text=p.read_text(encoding='utf-8')
            for item in D['tasks']:
                if item['phase']==c['code']:
                    self.assertIn(item['title'],text)
    def test_templates_and_sops(self):
        self.assertGreaterEqual(len(list((ROOT/'templates').glob('*.md'))),8)
        self.assertGreaterEqual(len(list((ROOT/'templates').glob('*.csv'))),16)
        self.assertEqual(len(list((ROOT/'playbooks').glob('*.md'))),10)

    def test_deepdives_survive_rebuild(self):
        for c in D['chapters']:
            p=ROOT/'deepdives'/f"{c['code']}.md"
            text=p.read_text(encoding='utf-8')
            self.assertGreater(len(text),450,c['code'])
            self.assertIn('深入实操', (ROOT/'guides'/f"{c['code']}.md").read_text(encoding='utf-8'))
    def test_comprehensive_resources(self):
        for name in ('FAQ.md','CASES.md','AI_PROMPTS.md','START_HERE.md','SOURCES.md'):
            self.assertGreater((ROOT/name).stat().st_size,800,name)
    def test_all_markdown_links_resolve(self):
        for doc in [ROOT/'README.md',ROOT/'START_HERE.md']:
            body=doc.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)',body):
                if target.startswith(('http://','https://','#')): continue
                self.assertTrue((ROOT/target).exists(),f'{doc.name}: {target}')

    def test_seven_stage_roadmap_and_tracks(self):
        docs=[
            ROOT/'guides'/'10-roadmap.md',
            ROOT/'tracks'/'ai-product.md',
            ROOT/'tracks'/'product-operations.md',
            ROOT/'tracks'/'finance-hr-technology.md',
            ROOT/'REFERENCES.md',
            ROOT/'CONTENT_LICENSE.md',
        ]
        for doc in docs:
            self.assertGreater(doc.stat().st_size,500,doc.name)
            body=doc.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)',body):
                if target.startswith(('http://','https://','mailto:','#')):
                    continue
                path=target.split('#',1)[0]
                self.assertTrue((doc.parent/path).resolve().exists(),f'{doc.name}: {target}')
        roadmap=(ROOT/'guides'/'10-roadmap.md').read_text(encoding='utf-8')
        for phrase in ('别急着学管理，先弄清楚你想负责什么','七阶段','不能直接照搬的地方','三条细分路线'):
            self.assertIn(phrase,roadmap)
        self.assertEqual(len(list((ROOT/'tracks').glob('*.md'))),3)
        self.assertIn('CC BY 4.0',(ROOT/'CONTENT_LICENSE.md').read_text(encoding='utf-8'))
        self.assertIn('70-20-10',(ROOT/'REFERENCES.md').read_text(encoding='utf-8'))
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        read=(ROOT/'read.html').read_text(encoding='utf-8')
        for needle in ('guides/10-roadmap.html','tracks/ai-product.html','tracks/product-operations.html','tracks/finance-hr-technology.html','别急着学管理'):
            self.assertIn(needle,home,needle)
            self.assertIn(needle,read,needle)
        self.assertIn('href="10-roadmap.html"',(ROOT/'guides'/'00-start.html').read_text(encoding='utf-8'))
        self.assertIn('REFERENCES.html',read)
        self.assertIn('CONTENT_LICENSE.html',read)

    def test_links_and_html(self):
        self.assertTrue((ROOT/'index.html').exists())
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertEqual(home.count('class="card task-card"'),50)
        self.assertNotIn('https://cdn.',home)
        md=(ROOT/'README.md').read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',md):
            if not target.startswith(('http','#')):
                self.assertTrue((ROOT/target).exists(),target)
if __name__=='__main__':unittest.main()
