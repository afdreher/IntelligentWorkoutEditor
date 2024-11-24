import base64
import json

from openai import OpenAI
from typing import List


class ImageExtractor(object):
    """
    The image extractor uses Llama Vision to perform OCR and text extraction.
    The results from the image extractor are natural language text strings.
    These strings are then passed to a processor, such as the JSONExtractor to
    convert from natural language into something machine parsable.
    """

    def __init__(self, api_key: str):
        self.model = self._create_model(api_key)

    def _create_model(self, api_key: str) -> OpenAI:
        # Note that it's important to have the 405B-Instruct model here because certain
        # requests involve reflection.
        return OpenAI(
            base_url="https://api.sambanova.ai/v1/",  
            api_key=api_key,
        )

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def from_image(self, image_path) -> List[str] | None:
        # Getting the base64 string
        base64_image = self.encode_image(image_path)
        return self.from_base64(base64_image)

    def from_base64(self, base64_image) -> List[str] | None:
        # SambaNova currently does to support system messages with vision
        response = self.model.chat.completions.create(
            model="Llama-3.2-11B-Vision-Instruct",
            messages=[
                {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': 'You are a text extractor.\nYou only respond by returning an array containing a list of strings representing workouts.\nIf there are no discernible workouts in the image, return a single string with all of the extracted text.\nDiscard any irrelevant text.\nRespond with a valid JSON array only.\nDo not add a preamble or discussion.\nWhat are the workouts in this image?',
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            "url":  f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
                }
            ],
        )

        try:
            # Response should be either a string or an array
            resp = json.loads(response.choices[0].message.content)
            #print(f"Response {resp}")
            if isinstance(resp, str):
                return [resp]
            return resp
        except Exception as e:
            #print(f"Exception {e}")
            return None  # Figure out why later.
