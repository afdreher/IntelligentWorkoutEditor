import getpass
import os
import sys

from typing import Any, Iterator, List, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.globals import set_verbose
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph import MessagesState, START
from langgraph.prebuilt import ToolNode
from langchain_core.tools import StructuredTool

# Get absolute paths for ai-starter-kit. Your location may vary
current_dir = os.getcwd()
workout_dir = os.path.abspath(os.path.join(current_dir, '..'))
repo_dir = os.path.abspath(os.path.join(workout_dir, '..'))
ai_kit_dir = os.path.abspath(os.path.join(repo_dir, 'ai-starter-kit'))
env_dir = repo_dir
sys.path.append(workout_dir)
sys.path.append(ai_kit_dir)

from tools.extraction.json_extractor import JSONExtractor
from tools.extraction.image_extractor import ImageExtractor
from tools.validation.workout.workout import Workout

from utils.model_wrappers.langchain_chat_models import ChatSambaNovaCloud


# Argument schema
class ParseWorkoutSchema(BaseModel):
    """Parse a workout from a given input string"""

    input: str = Field(description='The input string representing the workout. It should have some combination of shorthand, such as E, L, T, R, ST, MP, HMP or describe steps, such as Run, Recover, Rest, Repeat, Warm-up and Cool-down.')

class GetNameSchema(BaseModel):
    """
    Gets the name of the workout.
    """

class SetNameSchema(BaseModel):
    """Set a workout's name using a given input string. The workout's name can be cleared by sending either an empty or whitespace only string."""

    name: str = Field(description="The new name for the workout. If the name is \"\" or whitespace only, then the workout's name will be deleted.")


class PrimaryAgent(object):

    def __init__(self, api_key: str, user_id: str = '13542'):
        """Create the primary agent"""

        #print("[DIAGNOSTIC] creating agent")
        # Create the extractor and validator objects. We'll wrap these in a moment.
        self.workout_agent = JSONExtractor(api_key)
        self.image_agent = ImageExtractor(api_key)

        self._workout = None

        model = self._create_model(api_key)
        self.tools = self._define_tools()

        # Bind the tools.
        self.model = model.bind_tools(self.tools, parallel_tool_calls=False)

        self.agent = self._create_workflow()
        
         # For the configuration, any thread id will work. Just invent something.
        self.config = {"configurable": {"thread_id": user_id}}
        
        chat_template = ChatPromptTemplate.from_messages([('system', self._DEFAULT_PROMPT)])
        _ =  self.agent.update_state(self.config, {"messages": chat_template.format_prompt().to_messages()})

    @property
    def workout(self) -> Workout | None:
        #print("[DIAGNOSTIC] Getting workout value")
        return self._workout

    @workout.setter
    def workout(self, value: Workout | None):
        #print(f"[DIAGNOSTIC] Setting workout to {value}...")
        self._workout = value

    # ------------------------------
    # PUBLICLY CALLABLE METHODS
    # ------------------------------

    def invoke(self, messages: List[BaseMessage]) -> (dict[str, Any] | Any):
        return self.agent.invoke({'messages': messages}, self.config)
    
    def stream(self, input, **kwargs: Any | None) -> Iterator:
        return self.agent.stream(input, self.config, **kwargs)

    # If you call the tool function directly without using 'invoke', the LLM
    # won't have a tool message in the history, which is bad.
    def parse_workout(self, input: str) -> str:
        """Get a workout from an input string"""
        return self.parse_workout_tool.invoke(input)
    

    # ------------------------------
    # SETUP
    # ------------------------------

    def _create_model(self, api_key: str) -> ChatSambaNovaCloud:
        """This creates the agent"""
        # Get the SambaNova chat client.
        # Here, I've chosen to use the 70B version to have more context
        return ChatSambaNovaCloud(
            base_url="https://api.sambanova.ai/v1/",  
            api_key=api_key,
            streaming=False,
            temperature=0.01,
            model="Meta-Llama-3.1-70B-Instruct",
        )

    def _define_tools(self) -> List[StructuredTool]:
        """Create the tool definitions"""

        # request_photo = StructuredTool.from_function(
        #     func=self.request_photo,
        #     response_format='content_and_artifact',
        #     return_direct=True
        # )

        self.parse_workout_tool = StructuredTool.from_function(
            func=self._parse_workout,
            name='parse_workout',
            args_schema=ParseWorkoutSchema,
            #response_format='content_and_artifact', #it should be and artifact...
            return_direct=True
        )

        self.get_workout_name_tool = StructuredTool.from_function(
            func=self._get_workout_name,
            name='get_name',
            args_schema=GetNameSchema,
            return_direct=True
        )

        self.set_workout_name_tool = StructuredTool.from_function(
            func=self._set_workout_name,
            name='set_name',
            args_schema=SetNameSchema,
            return_direct=True
        )

        tools = [
            self.get_workout_name_tool,
            self.set_workout_name_tool,
            self.parse_workout_tool
        ]
        return tools

    # ------------------------------
    # PRIMARY TOOLS
    # ------------------------------

    # def _request_photo() -> str: # Tuple[str, object | None]:
    #     """Request a photo from the user"""
    #     # This should interface w/ the system to request a photo from the user
    #     return "Requesting photo! Here's the photo."
    
    # @tool(args_schema=ParseWorkoutSchema)
    def _parse_workout(self, input: str) -> str: #Tuple[str, Workout | None]:
        """
        Returns a workout in JSON format parsed from the input string.

        Args:
            input(str): the user's input string representing a workout.
        
        Returns:
            str: JSON formatted version of the workout
        """
        try:
            workout = self.workout_agent.from_string(input)
            if workout is not None:
                #print(f"RESULT: {workout}")
                # So this is a dirty hack because I don't have time to figure
                # out the proper serialization / deserialization with LangGraph
                self.workout = workout
                return self._workout_success_message(input)
            else:
                return self._workout_failure_message(input)
        except:
            # TODO: better reason
            return self._workout_failure_message(input)
        
    def _workout_success_message(self, input: str) -> str:
        return f"Successfully created the workout from {input}"

    def _workout_failure_message(self, input: str, reason: str | None = None) -> str:
        # TODO: Add context here
        return f"Failed to create a workout from {input}"   

    _no_workout_message = "Failure. No workout available. Create a workout first."

    def _get_workout_name(self) -> str:
        """
        Gets the name of the workout.
        
        Returns:
            str: Acknowledgement of the whether the tool successfully retrieved the workout name.
        """
        #print(f"Calling get name")
        #print(f"Current workout is {self.workout}")
        if self.workout is None:
            return self._no_workout_message
        name = self.workout.name
        if name is None:
            name = 'unnamed workout'
        return f"Success. The workout's name is \"{name}\"."

    def _set_workout_name(self, name: str) -> str:
        """
        Set a workout's name using a given input string. The workout's name can be cleared by sending either an empty or whitespace only string.
    
        Args:
            name(str): the new name for the workout. If the name is "" or whitespace only, then the workout's name will be deleted.
        
        Returns:
            str: Acknowledgement of the whether the tool updated the workout name successfully.
        """
        #print(f"Calling set name with {name}")
        #print(f"Current workout is {self.workout}")
        if self.workout is None:
            return self._no_workout_message
        
        trimmed = name.strip()
        if len(trimmed) > 0:
            self.workout.name = trimmed
            return f"Success. Workout name set to {trimmed}."
        else:
            self.workout.name = None
            return "Success. Workout name was cleared."

        
    # ------------------------------
    # GRAPH
    # ------------------------------

    # Now we need to define the LangGraph components. This taken from the example
    # and modified slightly to provide better instrumentation and wrap the tool
    # call with an AIMessage, which is important for SambaNova's client.

    # Define the function that determines whether to continue or not
    @staticmethod
    def _should_continue(state) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there is a tool call, then we finish
        if isinstance(last_message, ToolMessage):
            return "end"
        # Otherwise if there is, we continue
        else:
            return "continue"
        
        # The values "end" and "continue" are condition names in the graph

    # Define the function that calls the model
    def _call_model(self, state):
        messages = state["messages"]
        if isinstance(messages[-1], ToolMessage):
            return None
        else:
            response = self.model.invoke(messages)
            
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    def _create_workflow(self):
        """Get a new LangGraph workflow"""

        # Define a new graph
        workflow = StateGraph(MessagesState)

        # Define the two nodes we will cycle between
        workflow.add_node("agent", self._call_model)

        tool_node = ToolNode(self.tools)
        workflow.add_node("action", tool_node)

        # Set the entrypoint as `agent`
        # This means that this node is the first one called
        workflow.add_edge(START, "agent")

        # We now add a conditional edge
        workflow.add_conditional_edges(
            # First, we define the start node. We use `agent`.
            # This means these are the edges taken after the `agent` node is called.
            "agent",
            # Next, we pass in the function that will determine which node is called next.
            self._should_continue,
            # Finally we pass in a mapping.
            # The keys are strings, and the values are other nodes.
            # END is a special node marking that the graph should finish.
            # What will happen is we will call `should_continue`, and then the output of that
            # will be matched against the keys in this mapping.
            # Based on which one it matches, that node will then be called.
            {
                # If `tools`, then we call the tool node.
                "continue": "action",
                # Otherwise we finish.
                "end": END,
            },
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        workflow.add_edge("action", "agent")

        # Set up memory
        memory = MemorySaver()

        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable

        # We add in `interrupt_before=["action"]`
        # This will add a breakpoint before the `action` node is called
        app = workflow.compile(checkpointer=memory)
        return app


    # ------------------------------
    # PROMPT
    # ------------------------------

    # This prompt is good enough. You can certainly use the more elaborate
    # prompt from the function calling 
    _DEFAULT_PROMPT = """
    Your answer should be in the same language as the initial query.
    Either call a tool or respond to the user.
    Use the full chat history when creating a response.
    You are a helpful assistant.
    """


if __name__ == '__main__':
    # load env variables from a .env file into Python environment 
    if load_dotenv(os.path.join(env_dir, '.env')):
        api_key = os.getenv('SAMBANOVA_API_KEY') 
    else:
        os.environ["SAMBANOVA_API_KEY"] = getpass.getpass()
        api_key = os.environ.get("SAMBANOVA_API_KEY")

    # Load and create an agent. Test it...
    agent = PrimaryAgent(api_key=api_key)

    # Instantiate the template
    message = HumanMessage(content="Hi! I'd like make this into a workout: Basically 4 mile warmup, then alternating 800m at MP, 800m easy for 5 miles, then finish at normal long run pace")

    # Call the system
    for event in agent.stream({"messages": message}, stream_mode="values"):
        event["messages"][-1].pretty_print()