# IntelligentWorkoutEditor
A Llama (Large Language Model) powered editor for structured workouts.

## Installation

1. Clone the repository into a suitable location
2. Clone [SambaNova ai-starter-kit](https://github.com/sambanova/ai-starter-kit/tree/main) into an adjacent folder. 

    One can also modify the files under `/agents` instead to provide the proper location of the `ChatSambaNovaCloud` class, upon which this code depends.

3. Install the requisite packages in `requirements.txt` using `pip`

    ```
    pip install -r requirements.txt
    ```

The code is built and tested using Python 3 (3.11 and 3.12) on Mac OS Sequoia (15.1).


### Installing and running the Streamlit demonstration application

The demonstration application is written using Streamlit, although most of the development used Jupyter Notebooks.

---
**NOTE**

The application requires a version of the chat text that accepts images as well as text. This feature is currently under development. You can read more about the issue here: https://github.com/streamlit/streamlit/issues/7409

You can download the development wheel file from: https://core-previews.s3-us-west-2.amazonaws.com/pr-9491/streamlit-1.39.0-py2.py3-none-any.whl

This link is already included in the `requirements.txt` file.

---

After installing Streamlit, you need to create a Streamlit secrets file, `.streamlit/secrets.toml`.

Add your SambaNova API key to .streamlit/secrets.toml file:
```
SAMBANOVA_API_KEY = "YOUR_API_KEY"
```

## Usage

Currently, the agent does three primary tasks:

1. Creates workouts from natural language
2. Creates a workout from an image containing a textural description of a workout.
3. Gets and sets the name of the current workout.

For creating a workout or getting/updating the name, the process is a straightforward chat inside the Streamlit box. To use the image recognition feature:

1. Click on the attach (paperclip) icon at the left side of the chat box to select an image.
2. Hit send. Do not add any text to accompany the image or the system will process the text instead.

The extraction module supports additional features, such as parsing of step goals, that are currently not displayed in the HTML / CSS version. I'm just not enough of a web specialist to make that all behave.


### Example queries

The system is capable of handling natural language construction as well as some commonly used shorthand.  The following are some fun queries to try, not all of which will do *exactly* what you'd hope, although they are certainly able to be improved with work on the intermediate representation.

1. Do the following 3 times with 5 minute breaks between sets: 10 minutes of tempo at marathon pace, run 2 800s at HMP, 10 minutes of tempo at 5K

    *This is the example used in the introduction video. This workout is typical of a reasonably complicated structured workout with timed tempos. Creating this type of workout inside a visual programming system, such as Garmin Connect, is challenging because it involves multiple repetitions.*

2. Do 5 by 400m with equal jogging rest

    *This is an example of a commonly used track workout. The challenge for the model is understanding that "equal rest" means adding a similar step. I will note that, typically, the term "equal rest" means that the time of the interval should match even if the interval step itself is given as a distance, but that's beyond the scope of the output format and would require additional support on the part of the wearable*

3. Do 5 by 400m with 75% jogging rest

    *This is a slightly more complicated version of the above example. The LLM does not always calculate the percentages correctly, so production systems would probably need to handle this in the intermediate representation instead*

4. Warm-up; Pyramid workout (400m, 800m, 1-2x1200m, 800m, 400m); Cool down

    *Example of a classic Pyramid workout, which is where the distances / time progress in one direction before reversing*

5. Do a warm-up pyramid workout 400 m 800 m one to two 1200 meters 800 m 400 m and a cooldown

6. Warm Up, 12-16 x300M, Cool down

7. Warm up. 4-6 x 1000m. Cool down

8. Do a ladder from 100 to 1600m by 100m

    *Ladder workouts are quite difficult to program visually because most systems do not have a "ladder" node. This means that one has to create a new run step for each interval in the workout. Here, we use the LLM to calculate the change. The LLM handles this task much better than the percentage calculation above, but for a "real" system, it would probably be best to just stick this as a specialized node in the intermediate representation.*

9. Do a ladder from 100 to 1600 m x 100 m

10. Warm-up; ladder from 200 to 1800 by 400, cool down

11. Do a 5 minute warm-up. Try to keep the heart rate as low as possible and breathe easily. Follow this with 10 400s fast. Keep the turnover up, but don't stress it too much. Target 70 to 80s per lap. Float 200 meters between reps.  Cool down with a 2 mile easy run. This should be as relaxed as you possibly can run it.

    *This example demonstrates using the goals. To see that the LLM and the intermediate representation properly handle these tasks, I'd recommend uncommenting some of the logging `print` statements. I wanted to get around to displaying them in the Streamlit app, but I didn't get to building the HTML output*

12. Warm up by heading to South Picnic Lane. 2x200, 400, 4x800, 400, 2x200; Cool down when you're done.

    *This is an example of using summarized notes. The LLM is instructed to make the notes field concise and to summarize long note strings, which is necessary for display on a wearable device.*

13. Warm up by heading to the picnic lane then do 2 x 200 400 m 4 x 800 400 2 x 200 cool down when you’re done

    *This example shows a mix of repetition steps with run steps. These kinds of workouts are laborious to create using traditional approaches.*

14. Warm up. 400-800-1200-1200-800-400; cool down.

15. one mile warm up, 10 x 400m with, one mile cool down.

16. 10 mins wu; 12x3min perceived 70.3 effort with 1min walk recovery; 12mins easy run or walk

17. The tempo can be 2 x (4 x mile @ marathon pace (with 1 minute jog between the 4)) and 5 minute jog between the 2 sets.  

18. 2 miles E pace + 4 x (1 mile T pace with 1-min rest) + 5 min E pace + 3 x (1 mile T pace with 1-min rest) + 2 miles E pace

    *Example using shorthand code*

19. 2 miles E pace + 4 x (5 to 6 min T pace with 1-min rest)  + 1 hr E pace + 15 to 20 min T pace + 2 miles E pace

20. 4 mile warmup, then alternating 800m at MP, 800m easy for 5 miles, then finish at normal long run pace

    *This is an example of a complicated query that the `Llama-405B-instruct` model properly handles. It is interesting because the model has to discern that the "alternating 800m at MP, 800m easy" means that there needs to be a repetition step. Unlike most examples shown here, the number of repetitions is not provided directly; instead, the model must calculate the total distance in the step and then use the "for 5 miles" to find the proper number of repetitions. Smaller models such as the `Llama-70B-instruct` generally insert an incorrect value for the number of repetitions. I will comment, however, that even with the 405B model, this is still a fragile operation. As with many examples here, a more robust intermediate operation would probably be the better choice than relying on the LLM to "do the right thing," but it is amazing to see the capability nonetheless.*

21. 8x 500m / 300m float recovery

22. 6E+5×(4 min I w/3 min jg recoveries)+2E

23. 8E+5×(3 min I w/2 min jg)+6×(1 min R w/2 min jg)+2E

You can also ask for the name to be created simultaneously:

```
Create a workout named "easy track workout" with 8x 500m / 300m float recovery
```

### Limitations

The agent currently has limited tool use capabilities because I haven't fleshed out enough of the intermediate representation and associated manipulation tools to allow for more flexible queries.

Additionally, the tool calling mechanism for the `PrimaryAgent` is currently a bit touchy. There is a difference in how OpenAI and SambaNova respond to LangChain messages. I am, unfortunately, not yet enough of an expert to properly diagnose the issue so I've mostly just tried to work around some of the rough spots.

One glaring issue is that if a tool call is unavailable or if the LLM makes something up, SambaNova will respond with an empty message, for which `ChatSambaNovaCloud` will throw an exception. Although this is easy to catch, I have not yet figured out how this should be handled inside the LangGraph system. Consequently, you may encounter this problem.


### Model discussion

The primary agent and the polite responder both use the `Llama-70B-instruct` model because this model provides support for the tool calls and nicely summarizes the messages. I assume the agents can be run using the`Llama-3B-instruct` model, but since the `Llama-70B-instruct` version is already very quick, I have not explored this option.

The workout parser agent uses the `Llama-405B-instruct` model. This is because queries such as #20 above in the example do not correctly calculate the number of repetitions with the smaller models.

The image extraction agent uses the `Llama-90B-vision-instruct` model. This model proved very capable of isolating the important text blocks, which usually appear as tables.
