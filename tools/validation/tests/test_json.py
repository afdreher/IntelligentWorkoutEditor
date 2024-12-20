import json
import unittest

import workout.steps

from .context import workout
from workout import WorkoutDecoder, Workout

class TestJSONParsing(unittest.TestCase):

    def test_single_step_workout(self):
        input = '[{\n        "type": "run",\n        "value": 600,\n        "unit": "seconds",\n        "notes": "marathon pace"\n      }\n]'
        parsed = json.loads(input, cls=WorkoutDecoder)
        self.assertEqual(type(parsed), Workout)
        self.assertEqual(len(parsed.steps), 1)

        parsed_step = parsed.steps[0]
        self.assertEqual(type(parsed_step), workout.steps.RunWorkoutStep)
        self.assertEqual(parsed_step.value, 600)
        self.assertEqual(parsed_step.unit, 'seconds')
        self.assertEqual(parsed_step.notes, 'marathon pace')

        self.assertTrue(
            parsed_step.similar(
                workout.steps.RunWorkoutStep(
                    value=600,
                    unit='seconds',
                    notes='marathon pace'
                )
            )
        )


    def test_basic_repetition(self):
        input = '[{\n    "type": "repetition",\n    "value": 4,\n    "steps": [\n      {\n        "type": "run",\n        "minimum": 300,\n        "maximum": 360,\n        "unit": "seconds",\n        "notes": "T pace"\n      },\n      {\n        "type": "rest",\n        "value": 60,\n        "unit": "seconds"\n      }\n    ]\n  }\n]'
        parsed = json.loads(input, cls=WorkoutDecoder)
        self.assertEqual(type(parsed), Workout)
        self.assertEqual(len(parsed.steps), 1)

        parsed_step = parsed.steps[0]
        self.assertEqual(type(parsed_step), workout.steps.RepetitionStep)
        self.assertEqual(parsed_step.value, 4)

        # Test each step
        expected_run = workout.steps.RunWorkoutStep(
                            minimum=300,
                            maximum=360,
                            unit='seconds',
                            notes='T pace'
                        )
        run = parsed_step.steps[0]

        self.assertEqual(run.value, expected_run.value)
        self.assertEqual(run.minimum, expected_run.minimum)
        self.assertEqual(run.maximum, expected_run.maximum)
        self.assertEqual(run.unit, expected_run.unit)
        self.assertEqual(run.notes, expected_run.notes)
        self.assertTrue(run.similar(expected_run))
        
        expected_rest = workout.steps.RestWorkoutStep(
                            value=60,
                            unit='seconds'
                        )
        rest = parsed_step.steps[1]

        self.assertEqual(rest.value, expected_rest.value)
        self.assertEqual(rest.minimum, expected_rest.minimum)
        self.assertEqual(rest.maximum, expected_rest.maximum)
        self.assertEqual(rest.unit, expected_rest.unit)
        self.assertTrue(rest.similar(expected_rest))
        
        # Test the repetition
        self.assertTrue(
            parsed_step.similar(
                workout.steps.RepetitionStep(
                    value=4,
                    steps=[
                        expected_run,
                        expected_rest,
                    ]
                )
            )
        )


    def test_jack_daniels_type_plan(self):
        input = '[\n  {\n    "type": "run",\n    "value": 2,\n    "unit": "miles",\n    "notes": "E pace"\n  },\n  {\n    "type": "repetition",\n    "value": 4,\n    "steps": [\n      {\n        "type": "run",\n        "minimum": 300,\n        "maximum": 360,\n        "unit": "seconds",\n        "notes": "T pace"\n      },\n      {\n        "type": "rest",\n        "value": 60,\n        "unit": "seconds"\n      }\n    ]\n  },\n  {\n    "type": "run",\n    "value": 3600,\n    "unit": "seconds",\n    "notes": "E pace"\n  },\n  {\n    "type": "run",\n    "minimum": 900,\n    "maximum": 1200,\n    "unit": "seconds",\n    "notes": "T pace"\n  },\n  {\n    "type": "run",\n    "value": 2,\n    "unit": "miles",\n    "notes": "E pace"\n  }\n]'
        parsed = json.loads(input, cls=WorkoutDecoder)
        self.assertEqual(type(parsed), Workout)
        self.assertEqual(len(parsed.steps), 5)

        self.assertTrue(
            parsed.similar(
                workout.Workout(
                    steps=[
                        workout.steps.RunWorkoutStep(
                            value=2,
                            unit='miles',
                            notes='E pace'
                        ),
                        workout.steps.RepetitionStep(
                            value=4,
                            steps=[
                                workout.steps.RunWorkoutStep(
                                    minimum=300,
                                    maximum=360,
                                    unit='seconds',
                                    notes='T pace'
                                ),
                                workout.steps.RestWorkoutStep(
                                    value=60,
                                    unit='seconds'
                                ),
                            ]
                        ),
                        workout.steps.RunWorkoutStep(
                            value=3600,
                            unit='seconds',
                            notes='E pace',
                        ),
                        workout.steps.RunWorkoutStep(
                            minimum=900,
                            maximum=1200,
                            unit='seconds',
                            notes='T pace'
                        ),
                        workout.steps.RunWorkoutStep(
                            value=2,
                            unit='miles',
                            notes='E pace'
                        )
                    ]
                )
            )
        )
    

if __name__ == '__main__':
    unittest.main()