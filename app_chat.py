import streamlit as st
from streamlit_chat import message
from streamlit_option_menu import option_menu
from utils import get_initial_message, get_chatgpt_response, update_chat
import os
from dotenv import load_dotenv
from jinja2 import Template
import openai
from io import StringIO

from dataclasses import dataclass

load_dotenv()


@dataclass
class ModelConst:
    model_name: str = "gpt-4"


# openai.api_key = os.getenv('OPENAI_API_KEY')


# For streamlit deployment, the api key is added to streamlit-secrets in the app settings (during/after delpoyment)
openai.api_key = st.secrets["OPENAI_API_KEY"]


def main():
    st.set_page_config(page_title="Chatbot Application", page_icon=":robot_face:", layout="centered")
    st.image('assets/big_ai.png', width=700)

    # st.image('path/to/your/header_image.png', width=700)

    selected_page = option_menu(None, ["Editor", "Chat"], icons=['edit', 'comments'], menu_icon="bars", default_index=0,
                                orientation="horizontal", styles={"nav-link-selected": {"background-color": "#7D9338"}})

    if selected_page == "Editor":
        editor()
    elif selected_page == "Chat":
        chat()


def chat():
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    if 'query' not in st.session_state:
        st.session_state.query = ''

    if st.session_state.bug_flag == 1:
        st.warning("Oops, your previous message was sent to the model again", icon="🤖")

    def submit():
        st.session_state.query = st.session_state.input
        st.session_state.input = ''

    # Uncomment the second line to have GPT4 option in the select box dropdown menu

    model = ModelConst.model_name

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    # if st.session_state['generated']:

    # for i in range(len(st.session_state['generated'])-1, -1, -1):
    #     message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    #     message(st.session_state["generated"][i], key=str(i))

    def display():

        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

        # with st.expander("Show Messages"):
        #   st.write(st.session_state['messages'])

    st.text_input("Query: ", key="input", on_change=submit)
    # st.text_input("Query: ", key="input", on_change=submit)

    if 'messages' not in st.session_state:
        st.session_state['messages'] = get_initial_message()
        st.session_state['messages'] = update_chat(st.session_state['messages'], "system", st.session_state['prompt'])

    if st.session_state.query:
        with st.spinner("generating..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", st.session_state.query)
            # st.write("Before  making the API call")
            # st.write(messages)
            response = get_chatgpt_response(messages, model)
            messages = update_chat(messages, "assistant", response)
            st.session_state.past.append(st.session_state.query)
            st.session_state.generated.append(response)
            display()
            # st.experimental_rerun()


def editor():
    def filename_display(filename: str):
        filename, ext = os.path.splitext(filename)
        split_filename = filename.split("_")
        mod_filename = ""
        for part in split_filename:
            mod_filename = mod_filename + part.capitalize() + " "

        mod_filename = mod_filename.strip()
        return mod_filename

    def update_text_area(rendered_text_here: str):
        st.session_state.text_widget = rendered_text_here
        st.session_state.prompt = st.session_state.text_widget
        print(st.session_state.prompt)

    if 'generated' in st.session_state:
        st.session_state.bug_flag = 1
        # st.warning("Oops, your previous message was sent to the model again", icon = "🤖")
    else:
        st.session_state.bug_flag = 0

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    if 'text_widget' in st.session_state:
        print(st.session_state['text_widget'])

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to /prompts subdirectory
    prompts_dir = os.path.join(script_dir, 'prompts')

    # List all files in the /prompts directory
    files = [f for f in os.listdir(prompts_dir) if os.path.isfile(os.path.join(prompts_dir, f))]

    # Add a select box for all files
    selected_file = st.selectbox('Select a file:', files, format_func=filename_display)
    selected_file_path = os.path.join(prompts_dir, selected_file)

    with open(selected_file_path, 'r') as template_file:
        template_file_content = template_file.read()
        template = Template(template_file_content)

    st.session_state.prompt = template_file_content

    # List all files in the /rules directory
    rules_dir = os.path.join(script_dir, 'rules')
    files = [f for f in os.listdir(rules_dir) if os.path.isfile(os.path.join(rules_dir, f))]

    with st.expander("Select data source"):
        selected_rag_file = st.selectbox('', files, format_func=filename_display, index=0)
        selected_rag_path = os.path.join(rules_dir, selected_rag_file)
        with open(selected_rag_path, "r") as file:
            selected_rag_contents = file.read()

    st.text_area(label="Write your prompt here:", height=200, value=st.session_state.prompt, key="text_widget")
    # Change here is the prompt - "assassins guild" placeholder name changes
    rendered_text = Template(st.session_state.prompt).render(
        killer_agency_guilds_rules_2023_v06_new=selected_rag_contents)

    if st.button("Save Prompt", on_click=update_text_area, args=(rendered_text,)):
        st.success("Prompt saved successfully!")

    st.markdown(
        'Like it? Want to talk? Get in touch! <a href="mailto:leonid.sokolov@big-picture.com">Leonid Sokolov !</a> // '
        '<a href="mailto:hello@streamlit.io">Imke Bewersdorf</a>',
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()
