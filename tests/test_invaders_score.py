"""Independent atomic high scores for the space game and runner."""
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import runner_score
class InvadersScoreTests(unittest.TestCase):
    def test_independent_scores_and_validation(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(runner_score,'SCORE_FILE',Path(directory)/'runner.json'):
            self.assertEqual(runner_score.read_best_score('invaders'),0)
            runner_score.save_best_score(123)
            self.assertEqual(runner_score.save_best_score(400,'invaders'),400)
            self.assertEqual(runner_score.save_best_score(200,'invaders'),400)
            self.assertEqual(runner_score.read_best_score(),123)
            runner_score.save_best_score(999,'asteroids')
            self.assertEqual(runner_score.read_best_score('asteroids'),999)
            self.assertEqual(runner_score.read_best_score('invaders'),400)
            self.assertEqual((Path(directory)/'invaders.json').stat().st_mode&0o777,0o600)
            for score in (-1,True,1.5,2147483648):
                with self.assertRaises(ValueError):runner_score.save_best_score(score,'invaders')
            for game in ('breaker','lander','maze'):
                runner_score.save_best_score(321,game)
                self.assertEqual(runner_score.read_best_score(game),321)
            with self.assertRaises(ValueError):runner_score.read_best_score('../invalid')
