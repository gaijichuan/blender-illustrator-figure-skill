import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/blender-illustrator-figure-workflow/scripts/render_preserving_scene.py'
spec = importlib.util.spec_from_file_location('render_helper', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / 'source.blend').write_bytes(b'manifest-only fixture')
        self.job = {'source': 'source.blend', 'output': 'out/image.png', 'resolution': [64, 48]}

    def load(self, jobs):
        p = self.root / 'jobs.json'
        p.write_text(json.dumps({'jobs': jobs}), encoding='utf-8')
        return module.load_jobs(p)

    def test_resolves_relative_to_manifest(self):
        jobs = self.load([self.job])
        self.assertEqual(jobs[0]['source'], self.root / 'source.blend')
        self.assertEqual(jobs[0]['output'], self.root / 'out/image.png')
        self.assertIsNone(jobs[0]['samples'])

    def test_rejects_duplicate_output(self):
        with self.assertRaises(ValueError):
            self.load([self.job, dict(self.job)])

    def test_rejects_overwrite(self):
        (self.root / 'out').mkdir()
        p = self.root / 'out/image.png'
        p.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            self.load([self.job])
        self.assertEqual(p.read_bytes(), b'keep')

    def test_rejects_invalid_resolution(self):
        for dims in ([0, 10], [-1, 10], [True, 10], [10.5, 10]):
            with self.subTest(dims=dims), self.assertRaises(ValueError):
                self.load([dict(self.job, resolution=dims)])

    def test_rejects_missing_source_and_invalid_samples(self):
        with self.assertRaises(ValueError):
            self.load([dict(self.job, source='absent.blend')])
        with self.assertRaises(ValueError):
            self.load([dict(self.job, samples=0)])


if __name__ == '__main__':
    unittest.main()
