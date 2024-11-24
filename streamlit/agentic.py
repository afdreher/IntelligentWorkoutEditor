import streamlit as st

import os
import sys
import base64

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, BaseMessage

# Get absolute paths for ai-starter-kit. Your location may vary
current_dir = os.getcwd()
sys.path.append(current_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(parent_dir)
repo_dir = os.path.abspath(os.path.join(parent_dir, '..'))
ai_kit_dir = os.path.abspath(os.path.join(repo_dir, 'ai-starter-kit'))
sys.path.append(ai_kit_dir)

from agents.polite_responder import PoliteResponder
from agents.primary_agent import PrimaryAgent

from tools.extraction.json_extractor import JSONExtractor
from tools.extraction.image_extractor import ImageExtractor
from tools.validation.workout.htmlwriter import HTMLWriter

# api_key = st.sidebar.text_input("SambaNova API Key", type="password")

# Set SambaNova API key from Streamlit secrets
api_key = st.secrets["SAMBANOVA_API_KEY"]


# Introduce statefulness and caching
def agent():
    if 'primary_agent' not in st.session_state:
        st.session_state['primary_agent'] = PrimaryAgent(api_key=api_key)
    return st.session_state['primary_agent']

def polite_responder():
    if 'polite_responder' not in st.session_state:
        st.session_state['polite_responder'] = PoliteResponder(api_key)
    return st.session_state['polite_responder']

def image_extractor():
    if 'image_extractor().' not in st.session_state:
        st.session_state['image_extractor().'] = ImageExtractor(api_key)
    return st.session_state['image_extractor().'] 

def html_writer():
    if 'html_writer' not in st.session_state:
        # Decode and write to HTML for visualization
        st.session_state['html_writer'] = HTMLWriter() 
    return st.session_state['html_writer']

# Load the style for the workout HTML
external = '<link href="https://fonts.googleapis.com/css?family=Montserrat:400,500,600,700" rel="stylesheet">'
style = '<style> .workout { font-family: "Montserrat", sans-serif; } .workout ol, .workout ul { margin: 0px; padding: 0px; } .workout li { list-style-type: none; margin: 10px 0px; } .workout .step { position: relative; min-width: 200px; background-color: #f3f3f3; display: flex; color: #ccc; -webkit-border-radius: 6px; -moz-border-radius: 6px; border-radius: 6px; padding: 10px; box-shadow: 2px 3px; border: 1px solid #ccc; } .workout .step .level_1 { background-color: #e3e3e3; } .workout .step.level_2 { background-color: #f3f3f3; } .workout .step .color-bar { position:absolute; width: 5px; height: 100%; /* background-image: linear-gradient(to right, blue, #EEE); background-color: blue; */ left: 0px; top: 0px; -webkit-border-radius: 6px 0 0 6px; -moz-border-radius: 6px 0 0 6px ; border-radius: 6px 0 0 6px; z-index: 0; } .workout .step .badge { text-transform: uppercase; font-weight: 600; z-index: 2; background-color: white; display: inline-block; position: absolute; bottom: 0; top: 0; left: 10px; right: 0; margin: 5px 0px; width: 120px; text-align: center; -webkit-border-radius: 15px; -moz-border-radius: 15px; border-style: solid; border-width: 1px; border-radius: 15px; border-color: #ccc; height: 30px; line-height: 25px; } .workout .step.run > .color-bar, .workout .step.run > .badge { background-color: #D13728; } .workout .step.warm-up > .color-bar, .workout .step.warm-up > .badge { background-color: #EE923C; } .workout .step.recover > .color-bar, .workout .step.recover > .badge { background-color: #e4ae1c; } .workout .step.cool-down > .color-bar, .workout .step.cool-down > .badge { background-color: #0C7339FF; } .workout .step.repetition > .color-bar, .workout .step.repetition > .badge { background-color: #59098e; } .workout .step.rest > .color-bar, .workout .step.rest > .badge { background-color: #145381; } .workout .step .badge span { color: #efefef; display: inline-block; vertical-align: middle; line-height: normal; } .workout .step .details { color: #333; position: relative; margin-left: 130px; width: 100%; } /* .step .details .notes { background-color: red; } */ .workout .step .details .notes{ color: #444; } .workout .step .details .notes .text { font-style: italic; } </style>' 
st.html(f'{external}{style}')

st.title("Intelligent Workout Editor - Demo")

def get_response_for_user(message: BaseMessage) -> str | None:
    """Generate a polite message using the PoliteResponder LLM"""
    messages = [message, AIMessage(content="Generate a response for the user")]
    return polite_responder().call_llm(messages)

def finish_prompt_response(assistant_message, extra):           
    # Add assistant response to chat history
    with st.chat_message("assistant"):
        st.markdown(assistant_message)
        if extra is not None:
            #print(f"HTML: {extra}")
            st.html(extra)
    if extra is None:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    else:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message, 'extra': extra})


def invoke_text_path(prompt):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt['text'])
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    llm_response =  agent().invoke([HumanMessage(prompt['text'])])
    extra = None

    # This is very fragile right now!
    last_message = llm_response['messages'][-1]
    assistant_message = ''
 
    if isinstance(last_message, ToolMessage):
        content = last_message.content
        #print(f'[DIAGNOSTIC] tool message: {content}')
        if content.startswith("Successfully created the workout"):
            assistant_message = get_response_for_user(last_message)
            if assistant_message is None:
                assistant_message = "Successfully created workout." 
            extra = html_writer().to_html( agent().workout)
            #print("Creating HTML version")
        elif content.startswith("Success"):
            assistant_message = get_response_for_user(last_message)
            if assistant_message is None:
                assistant_message = "Success."
        elif content.startswith("Failure"):
            assistant_message = get_response_for_user(last_message)
            if assistant_message is None:
                assistant_message = "Failure."
        else:
            assistant_message = "FAILURE :(" # Use LLM later
    else:
        assistant_message = llm_response['messages'][-1].content
            
    finish_prompt_response(assistant_message, extra)

def invoke_image_path(prompt):
    # Try to work with the image...
    uploaded_file = prompt['files'][0]
    bytes_data = uploaded_file.getvalue()
    with st.chat_message("user"):
        st.image(uploaded_file)

    encoded = base64.b64encode(bytes_data).decode('utf-8')
    strings = image_extractor().from_base64(encoded)
    #print(strings)

    ai_message = AIMessage(content=f"Inform the user that the following possible items have been discovered in the image: {strings}")
    assistant_message = get_response_for_user(ai_message)

    for string in strings:
        result =  agent().parse_workout(string)
        if result.startswith("Successfully created the workout"):
            message = AIMessage(content=f"Successfully created workout for {string}.")
            assistant_message = get_response_for_user(message)
            if assistant_message is None:
                assistant_message = "Successfully created workout." 
            extra = html_writer().to_html( agent().workout)
            #print("Creating HTML version")
            break
        else:
            assistant_message = "FAILURE :(" # Use LLM later

    finish_prompt_response(assistant_message, extra)


def handle_prompt(prompt):
    extra = None
    if len(prompt['files']) > 0:
        invoke_image_path(prompt)
    else:
        invoke_text_path(prompt)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    #print("Displaying from history")

    if message['role'] == 'user':
        # This is because I'm using a prompt that can be either image or text
        content = message['content']
        if content['text'] is not None:
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(content['text'])
    else:
        # It's the assistant
        #print(message)
        with st.chat_message("assistant"):
            keys = message.keys()
            if 'content' in keys and message["content"] is not None:
                st.markdown(message["content"])
            if 'extra' in keys and message["extra"] is not None:
                 st.html(message["extra"])

# Accept user input
if prompt := st.chat_input(
    "Ask for a workout or upload an image",
    # accept_file : bool | str
    # Whether the chat input should accept files. 
    # True to accept a single file, "multiple" to accept multiple files.
    accept_file=True,
    # # file_type : str | list[str] | None
    # # Array of allowed extensions, e.g. ['png', 'jpg']
    # # The default is None, which means all extensions are allowed.
    file_type=["png", "jpg"],
):
    handle_prompt(prompt)
