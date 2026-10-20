import json
import unittest
from pathlib import Path
from pipeline_schema.models import PipelineConfig
from backend.app.main import build_runner

class TestSmokePipeline(unittest.TestCase):
    def test_pipeline_execution(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        pipeline_path = project_root / "test_pipeline.json"

        with open(pipeline_path, "r") as f:
            config_dict = json.load(f)

        config = PipelineConfig.model_validate(config_dict)
        self.assertEqual(config.pipeline_id, "pipeline_1")

        runner = build_runner()
        result = runner.run(config)

        self.assertIsNone(result.stopped_at)
        self.assertEqual(result.errors, [])
        self.assertIsNotNone(result.validation)
        self.assertTrue(result.validation.passed)
        self.assertIsNotNone(result.evaluation)
        self.assertTrue(result.evaluation.passed)
        self.assertIsNotNone(result.registry)
        self.assertTrue(result.registry.registered)

if __name__ == "__main__":
    unittest.main()
