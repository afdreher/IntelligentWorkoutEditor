from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages.base import BaseMessage


class PoliteResponder(object):
    """
    A polite assistant LLM to generate responses to the user
    """

    def __init__(self, api_key: str):
        self.chain = self._create_chain(api_key)

    def _create_chain(self, api_key: str) -> ChatOpenAI:
        """Create a LangChain processing chain to generate polite feedback"""

        # 70B is more than enough for this task
        model = ChatOpenAI(
            base_url="https://api.sambanova.ai/v1/",  
            api_key=api_key,
            model="Meta-Llama-3.1-70B-Instruct", 
            temperature=0.15,
            streaming=False
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", self._DEFAULT_TEMPLATE), ("user", "{text}")]
        )

        parser = StrOutputParser()

        chain = prompt_template | model | parser
        return chain

    def call_llm(self, messages: List[BaseMessage]) -> str | None:
        """Call the LLM to generate a response"""

        try:
            return self.chain.invoke(messages)
            return 
        except Exception as e:
            return None
            #print(f"[CHAIN RESULT] is exception: {e}")
        return None

    # This template is a bit repetitive and verbose, but it currently passes
    # internal tests.
    _DEFAULT_TEMPLATE = """
You are a helpful and polite assistant who responds to the user. 
You do not ask questions.
You only provide helpful statements.

The user may talk about workouts using shorthand.  Here's some important abbreviations to know:
    1. "wu" and "w/u" mean "warm-up"
    2. "cd" and "c/d" mean "cool-down"
    3. A common encoding system comprised of with "E", "L", "I", "R", "T", "JG", "ST", "MP", and "HMP".  Convert abbreviations and enter the expanded value in "notes" field as:
        "E" => "easy pace", "L" => "long run pace", "I" => "interval pace", "R" => "repetition pace", "T" => "tempo pace", "JG" => "jog", "ST" => "stride", "MP" => "marathon pace", and "HMP" => "half marathon pace". If the units are not specified with these values, assume they are miles.

If the user has previously asked a question, try to summarize and answer the user's question.
"""