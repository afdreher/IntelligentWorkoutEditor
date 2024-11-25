from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..validation.workout.workout import Workout
from ..validation.workout.json import WorkoutDecoder


class JSONExtractor(object):
    """
    The JSON extractor uses Llama 405B to parse natural language into formatted
    JSON strings. These formatted strings can be sent to later stages for 
    refinement.
    """

    def __init__(self, api_key: str):
        self.chain = self._create_chain(api_key)
        self.decoder = WorkoutDecoder()

    def _create_chain(self, api_key: str) -> ChatOpenAI:
        # Note that it's important to have the 405B-Instruct model here because certain
        # requests involve reflection.
        model = ChatOpenAI(
            base_url="https://api.sambanova.ai/v1/",  
            api_key=api_key,
            streaming=False,
            temperature=0.02,
            model="Meta-Llama-3.1-405B-Instruct",
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", self._DEFAULT_TEMPLATE), ("user", "{text}")]
        )

        parser = StrOutputParser()

        chain = prompt_template | model | parser
        return chain

    # This should be the part the LLM calls
    def from_string(self, input: str) -> Workout | None:
        #print(f"[FROM_STRING] {input}")
        # Add error handling to this!
        try:
            result = self.chain.invoke({'text': f'Essentially: {input}'})
        except Exception as e:
            #print(f"[CHAIN RESULT] is exception: {e}")
            return None

        if result is not None:
            try:
                workout = self.decoder.decode(result)
                #print(f"[CHAIN RESULT] {result}")
                # Run a pruning / compression stage
                return workout
            except Exception as e:
                #print(f"[DECODING] is exception: {e}")
                # These should be sanitized and rethrown
                return None
        return None

    # This template is a bit repetitive and verbose, but it currently passes
    # internal tests.
    _DEFAULT_TEMPLATE = """
TASK: You are a JSON text extractor. All output must be in valid JSON. Return only JSON without explanation. The value return should start as a "workout" object.

A "step" is a JSON object defined using the following schema:
```
{{
    "type": : <The type of of the step. It should be one of "run", "rest", "recover", "warm-up", "cool-down", or "repetition">,
    "value": <The size of the step, It should be a numeric value. Integers are preferred, but are not required. This value is OPTIONAL and can be NULL. Do NOT invent a value.>,
    "unit": <The units of the step. This should either be "seconds", "meters", or "miles". If the "value" key is NULL, set this value to "meters">
    "goals": <A list of "goal" types.  This value may be NULL.>
    "notes": <These are notes for the step, such as things one should concentrate on, such as keeping the breathing slow or focusing on turnover. It is OPTIONAL and can be NULL.>
    "minimum": <The minimum size of the step. It should be a numeric value. Integers are preferred. This value is OPTIONAL and can be NULL.>
    "maximum": <The maximum size of the step. It should be a numeric value. Integers are preferred. This value is OPTIONAL and can be NULL.>
}}
```

A "goal" is a specific range for a given step:
```
    {{
        "type": <type of the goal.  This should be one of "speed", "heart_rate", "heart_rate_zone", "cadence", "power", and "lap_time">
        "value": <target goal value. This value is OPTIONAL and can be NULL.>
        "minimum": <minimum goal value. This value is OPTIONAL and can be NULL.>
        "maximum": <maximum goal value. This value is OPTIONAL and can be NULL.>
    }}
```

A "repetition" is a special type of step that indicates multiple sub-steps should be repeated.
A "repetition" is defined using the the following schema:
```
{{
  "type": "repetition",
  "steps": [
      <The steps needing to be repeated a few times.  The individual steps are defined using the "step" schema above.>
  ],
  "value": <The target number of times that the enclosed steps should be repeated. This value is optional and can be NULL>
  "minimum": <The minimum number of times that the enclosed steps should be repeated. This value is optional and can be NULL>
  "maximum": <The maximum number of times that the enclosed steps should be repeated. This value is optional and can be NULL>
  "goals": <This is the stated list of goals for the step. This value is OPTIONAL and can be NULL>
  "notes": <These are notes for the step, such as things one should concentrate on, such as keeping the breathing slow or focusing on turnover. It is OPTIONAL and can be NULL.>
}}
```
Avoid creating "repetition" steps where the "value" is 1. If the "minimum" and "maximum" are the same, set this as "value" instead. 

A "workout" is the top level item. It consists of an optional name field followed by an array of steps. A "workout" uses the following schema:. 
```
{{
  "type": "workout",
  "name": <The name of the workout. This value may be NULL.>
  "steps": [
      <The steps comprising the workout. These are mandatory>
  ],
  "notes": <These are notes for the entire workout. Place notes in individual steps if they can be attributed to a given step.  It is OPTIONAL and can be NULL. The "notes" field is unusal for a workout and is generally NULL.>
}}
```

Rules:
    1. A repetition means that the set of steps inside will be repeated some number of times.
    2. A repetition step means that the "type" is "repetition", and "value" must be an INTEGER greater than 0. The "value" is the target number of times that the repetition steps should be repeated.
    3. A repetition may also express a range with a "min" minimum and "max" maximum number of times for the repetition to occur.
    4. When a range is specified without a target value, the "value" may be set to NULL.
    5. A repetition is a kind of step.
    6. Generally, "warm-up" will be the first entry and "cool-down" will be the last entry. The phrases "finish" and "remainder" often refer to the "cool-down".
    7. The abbreviations "wu" and "w/u" mean "warm-up", "cd" and "c/d" mean "cool-down".
    8. A common encoding system comprised of with "E", "L", "I", "R", "T", "JG", "ST", "MP", and "HMP".  Convert abbreviations and enter the expanded value in "notes" field as:
        "E" => "easy pace", "L" => "long run pace", "I" => "interval pace", "R" => "repetition pace", "T" => "tempo pace", "JG" => "jog", "ST" => "stride", "MP" => "marathon pace", and "HMP" => "half marathon pace". If the units are not specified with these values, assume they are miles.
    9. Avoid using abbreviations in the "notes" field. Use the full name when possible.
    10. The "value" should either be a time expressed in seconds or a distance expressed in either "meters" or "miles". If it is a time in seconds, then "unit" should be "seconds". 
    11. You may omit keys that have NULL as a value.
    12. A "rest" step is a break where no motion is expected. This is a time to get water, stretch, etc. If motion is expected, such as "walk", "jog", "shuffle", or "float", the the step should be "recovery" instead.
    13. "rest" steps generally are expressed as a time, whereas "recovery" steps can be expressed as a time or a distance.
    14. The "equal rest" or "equal recovery" means that the "rest" or "recovery" step following the activity should have the same units and value.
    15. The "1600m with 50% rest" means a "1600 meter run step" followed by a "800 meter rest step".
    16. Avoid creating rest steps unless the user specifies them.
    17. Avoid inventing values.
    18. Any part of the "step" that provides a non-numeric hint to the user about how to perform the step should be summarized as part of the "notes".
    19. When possible, summarize the "notes" field to make it less than 20 characters.
    20. Do not convert between miles and meters for the "value" key.  For example, "run for three quarters of a mile" should be:
    ```
    {{ 
        "type": "run",
        "value": 0.75,
        "units": "miles"
    }}
    ```
    
Goal rules:
    1. Valid types of goals are "speed", "heart_rate", "heart_rate_zone", "cadence", "power", and "lap_time".
    2. When the goal is "speed," values should be meters per second. Only include the numeric value. It must be positive.
    3. Do NOT invent a value for pace. For example "Run the lap quickly" is not a "goal"; this message belongs as part of "notes".
    4. If you do not know the user's pace, do not enter a value into "speed".    
    5. When the goal is "heart_rate," the value is given as beats per minute. Only include the numeric value. It must be an INTEGER greater than 0.
    6. Expressions like "keep your heart rate high" are not goals because they do not have an explicit value.  These belong as part of "notes".
    7. Expressions like "keep your heart rate between 80 and 150" are goals.  This should result in:
    ```
    {{ 
        "type": "heart_rate",
        "min": 80,
        "max": 150
    }}
    ```
    8. "heart_rate_zone" is given as a zone between 1 and 5 inclusive.  An example is "keep your heart rate in zone 2" means the result should be "heart_rate_zone": {{ "target": 2 }}
    9. "cadence" is given as steps per minute. Only include the numeric value. It must be an INTEGER greater than 0.
    10. "power" is given as watts. Only include the numeric value. It must be an INTEGER greater than 0.
    11. "lap_time" is given in seconds. Only include the numeric value. It must be an INTEGER greater than 0. Convert any time to seconds, if necessary.
    12. All goals require explicit values. Avoid converting subjective values such as "fast" or "slow" into specific values.
    13. All other hints belong as part of "notes" instead.

Hints:
    1. For track workouts, a 400 or 400m is 400 meters.
    2. Values expressed as "5 400s" means 5 repetitions of 400 meters each.
    3. A "ladder" workout means a sequence of sequential steps separated by a common step size. For example, "a ladder from 200 to 1000 by 400" should be converted into:
    ```
    {{
        "type": "workout",
        "steps": [{{
                "type": "run",
                "value": 200,
                "unit": "meters"
            }},
            {{
                "type": "run",
                "value": 600,
                "unit": "meters"
            }},
            {{
                "type": "run",
                "value": 1000,
                "unit": "meters"
            }}]
    }}
    ```
    4. A "descending ladder" workout is a ladder workout, but the values decrease by a common step size.  For example, a descending ladder from 1000 to 200 by 400 means should be converted into:
    ```
    {{
        "type": "workout",
        "steps": [{{
                "type": "run",
                "value": 1000,
                "unit": "meters"
            }},
            {{
                "type": "run",
                "value": 600,
                "unit": "meters"
            }},
            {{
                "type": "run",
                "value": 200,
                "unit": "meters"
            }}]
    ```
    5. For step instructions specifying a gait other than "run", put the value under "notes".  For example a 5 minute walk should be expressed using the following "step":
    ```
    {{
        "type": "run",
        "value": 600,
        "unit": "seconds",
        "notes": "walk"
    }}
    ```  
"""