import asyncio
import random
import json
import streamlit as st
from dotenv import load_dotenv
from ragbase.chain import ask_question, create_chain
from ragbase.config import Config
from ragbase.ingestor import Ingestor
from ragbase.model import create_llm
from ragbase.retriever import create_retriever
import base64
# from ragbase.uploader import upload_files

first_prompt = False

load_dotenv()

logo = (Config.Path.IMAGES_DIR / "logo.png")
st.set_page_config(page_title="AhriBot", page_icon=str(logo)) 

CHATBOT_NAME = "Ahri"
if "chatbot_name" not in st.session_state:
    st.session_state.chatbot_name = CHATBOT_NAME

LOADING_MESSAGES = [
    "Summoning the champions... Prepare for battle!",
    "Channeling Summoner's Rift energies... almost there!",
    "Upgrading boots... this might take a while!",
    "Securing Baron... hold tight!",
    "Charging your ultimate... ready soon!",
    "Gearing up for a Pentakill... one moment!",
    "Checking runes... making sure they’re perfect!",
    "Reviving after respawn... coming back stronger!",
    "Boosting the jungle... clearing the path!",
    "Gathering vision from wards... stay tuned!"
]


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_font_as_base64(font):
    with open(font, "rb") as f:
        data = f.read()
        e_font = base64.b64encode(data).decode('utf-8')
    return e_font

img = get_img_as_base64("images/backg.png")
img2 = get_img_as_base64("images/assistant-avatar.png")
headerfont = get_font_as_base64("images/MBFManata.ttf")

st.markdown("""
    <header data-testid="stHeader" class="st-emotion-cache-1atd71m">
        <p class="strategem">STRATEGEM</p>
    </header>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
        @font-face {{
            font-family: 'MANATA';
            src: url('data:font/ttf;base64,{headerfont}') format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        
        .strategem {{
            font-family: 'MANATA';
            background: linear-gradient(45deg, rgb(234, 255, 43), rgb(7, 165, 204), rgb(48, 189, 255));
            animation: gradientAnimation 4s ease infinite;
            background-clip: text;
            background-size:300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: clamp(1rem, 2.5vw, 1.5rem);
            margin: 30px 0 0 30px;
        }}
        
        @keyframes gradientAnimation {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}
        
    </style>
""", unsafe_allow_html=True)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img}");
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
    min-height: 100vh; 
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    @import url('https://fonts.cdnfonts.com/css/sk-concretica');
    @import url('https://fonts.cdnfonts.com/css/pp-neue-montreal');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    
    .st-emotion-cache-1atd71m {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    height: 3.75rem;
    outline: none;
    z-index: 999990;
    display: block;
    }
    
    .warning {
        font-family: 'Poppins', sans-serif;
        font-weight: lighter;
        color: white;
        font-size: 9px;
        letter-spacing: 0.5px;
        position: fixed;
        z-index: 100;
        text-align: center;
        width: 100%;  
        left: 50%;
        bottom: 0%;
        transform: translate(-50%, -50%); 
    }

    
    .st-emotion-cache-1sno8jx, .st-bp {
        font-family: 'SK Concretica', sans-serif;
        font-weight: 'lighter';                                           
    }
    
    .st-emotion-cache-janbn0 {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 1rem;
        border-radius: 1rem;
        background-color: rgba(0, 0, 0, 0);
    }
    
    .st-emotion-cache-4oy321 {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 1rem 1rem 1rem 1rem;
        border-radius: 1rem;
        background-color: rgba(51, 198, 187, 0.3);
    }
    
    .st-emotion-cache-1htpkgr {
        position: relative;
        bottom: 0px;
        width: 100%;
        padding-bottom: -10px;
        min-width: 100%;
        background-color: rgba(0, 0, 0, 0);
        display: flex;
        flex-direction: column;
        -webkit-box-align: center;  
        align-items: center;  
        z-index: 99;
    }
    
    .st-emotion-cache-arzcut {
        width: 100%;
        padding: 1rem 1rem 55px;
        max-width: 46rem;
        position: sticky;
        background-color: field;
        border-radius: 1rem;
        height: 90px;
        min-height: 90px;
    }
        
    </style>
    """, unsafe_allow_html=True
)

@st.cache_resource(show_spinner=False)
def build_qa_chain(files):
    file_paths = files
    # file_paths = upload_files(files)
    vector_store = Ingestor().ingest(file_paths)
    llm = create_llm()
    retriever = create_retriever(llm, vector_store=vector_store)
    return create_chain(llm, retriever)

async def ask_chain(question: str, chain):
    full_response = ""
    assistant = st.chat_message("assistant", avatar=str(Config.Path.IMAGES_DIR / "assistant-avatar.png"))
    
    with assistant:
        message_placeholder = st.empty()
        message_placeholder.status(random.choice(LOADING_MESSAGES), state="running")
        documents = []
        async for event in ask_question(chain, question, session_id="session-id-42"):
            if type(event) is str:
                full_response += event
                message_placeholder.markdown(full_response)
            if type(event) is list:
                documents.extend(event)
                
    st.session_state.messages.append({"role": "assistant", "content": full_response})

def show_upload_documents():
    holder = st.empty()
    uploaded_files = list(Config.Path.PDF_DIR.glob("*.pdf"))
    with st.spinner("Summoning Ahri... Prepare for battle!"):
        holder.empty()
        return build_qa_chain(uploaded_files)

# def show_upload_documents():
#     holder = st.empty()
#     with holder.container():
#         st.header("RagBase")
#         st.subheader("Get answers from your documents")
#         uploaded_files = st.file_uploader(
#             label="Upload PDF files", type=["pdf"], accept_multiple_files=True
#         )
#     if not uploaded_files:
#         st.warning("Please upload PDF documents to continue!")
#         st.stop()

#     with st.spinner("Analyzing your document(s)..."):
#         holder.empty()
#         return build_qa_chain(uploaded_files)

def show_message_history():
    for message in st.session_state.messages:
        role = message["role"]
        avatar_path = (
            Config.Path.IMAGES_DIR / "assistant-avatar.png"
            if role == "assistant"
            else Config.Path.IMAGES_DIR / "user-avatar.png"
        )
        with st.chat_message(role, avatar=str(avatar_path)):
            st.markdown(message["content"])

def show_chat_input(chain):

    if prompt := st.chat_input("Summoner, what’s your next move? ⚔️"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=str(Config.Path.IMAGES_DIR / "user-avatar.png")):
            st.markdown(prompt)
            
        asyncio.run(ask_chain(prompt, chain))
    
    st.markdown(
        """
        <style>
            .streamlit-expanderHeader {
                position: relative;
            }
            .stTextInput > div {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background: rgba(0,0,0,0;
                z-index: 10;
                padding: 10px;
            }
            
            .stChatInputTextArea > div {
                background-color: rgb(51, 198, 187);
            }

        </style>
        """, unsafe_allow_html=True
    )

    st.markdown("<div style='height: 70px'></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Greetings! I'm {CHATBOT_NAME}, how can I help you today?"}
    ]

if Config.CONVERSATION_MESSAGES_LIMIT > 0 and Config.CONVERSATION_MESSAGES_LIMIT <= len(st.session_state.messages):
    st.warning("You have reached the conversation limit. Refresh the page to start a new conversation.")
    st.stop()
    
with st.container():
    st.markdown(
        "<div class='warning'>Strategem may commit mistakes. Please verify its response.</div>", 
        unsafe_allow_html=True
    )

chain=show_upload_documents()
show_message_history()
show_chat_input(chain)


