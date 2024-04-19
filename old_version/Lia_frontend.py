#AIzaSyBqxzLuXaUp6kT4k-qpFKvwkC3qGrCr1M0


import os
import io
import streamlit as st
import requests
import google.generativeai as genai
from google.cloud import speech
from st_audiorec import st_audiorec
from streamlit.components.v1 import html
import plotly.graph_objs as go

# Securely accessing the API key
API_KEY = 'AIzaSyBqxzLuXaUp6kT4k-qpFKvwkC3qGrCr1M0'


# Assuming GOOGLE_API_KEY is set as an environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = API_KEY
if API_KEY is None:
    st.error("Please set the GOOGLE_API_KEY environment variable before using this app.")
    st.stop()
else:
    genai.configure(api_key=API_KEY)


# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'recognition_state' not in st.session_state:
    st.session_state.recognition_state = None


def draw_roadmap():
    # Define the positions of the nodes (tasks)
    nodes_x = [0, -1, 1, -1.5, -0.5, 1.5, 0.5, -1.75, -1.25, 1.25, 1.75]
    nodes_y = [2, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1]
    node_text = ['Start', 'Task 1', 'Task 2', 'Task 6', 'Task 3', 'Task 5', 'Task 4', 'Task 7', 'Task 8', 'Task 9', 'Task 10']

    # Define the edge connections
    edges_x = [0, -1, 0, 1, -1, -1.5, -1, -0.5, 1, 1.5, 1, 0.5, -1.5, -1.75, -1.5, -1.25, 1.5, 1.25, 1.5, 1.75]
    edges_y = [2, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, -1, 0, -1, 0, -1]

    # Create the Plotly figure
    fig = go.Figure()

    # Add edges as lines
    fig.add_trace(go.Scatter(x=edges_x, y=edges_y,
                             mode='lines',
                             line=dict(width=2, color='RoyalBlue'),
                             hoverinfo='none'))

    # Add nodes as scatter points
    fig.add_trace(go.Scatter(x=nodes_x, y=nodes_y,
                             mode='markers+text',
                             text=node_text,
                             textfont=dict(size=18, color='Black'),
                             marker=dict(size=70, color='LightSkyBlue'),
                             hoverinfo='text'))

    # Update figure layout for a better fit
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      showlegend=False,
                      margin=dict(t=0, l=0, r=0, b=0))

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

# Define page content functions
def main_page():
    #center the title
    st.markdown("<h1 style='text-align: center; color: #FFF;'>Welcome to Interview Prep Helper</h1>", unsafe_allow_html=True)
    #st.subheader("Welcome to Interview Prep Helper")
    #place to upload resume
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
        st.write(file_details)
    #read the file
    if st.button("Assess Resume"):
        file = uploaded_file.read()

    #add in textboxes for user to input their information
    st.write("Tell Us About Yourself in A Few Sentences")
    prof_exp = st.text_input("Describe your educational and professional experience. ")
    #Add in textbox to see What is the most impressive project you have done?
    impressive_project = st.text_input("What is the most impressive project you have done? ")
    #Add in textbox to see What is something you want to improve the most?
    improve = st.text_input("What is something you want to improve the most? ")
    #select the industry you are interested in with a company website link to add in next to it
    col = st.columns(2)
    with col[0]:
        industry = st.selectbox("Select the industry you are interested in: ", ["Technology", "Finance", "Healthcare", "Education", "Other"])
    with col[1]:
      company_website = st.text_input("Company Website: ")
    

def technical_interview():
    st.subheader("Go back and submit your resume to get started!")

def road_map():
    #create a Initial Assessment title and center it
    st.markdown("<h1 style='text-align: center; color: #FFF;'>Initial Assessment</h1>", unsafe_allow_html=True)
    #create a subheader for Here is where you stand
    st.subheader("Here is where you stand")

    # Progress bars with labels and percentages
    clarity_score = 70
    st.write(f"Clarity: {clarity_score}%")
    st.progress(clarity_score)

    relevance_score = 50
    st.write(f"Relevance: {relevance_score}%")
    st.progress(relevance_score)

    star_score = 80
    st.write(f"STAR: {star_score}%")
    st.progress(star_score)

    friendliness_score = 60
    st.write(f"Friendliness: {friendliness_score}%")
    st.progress(friendliness_score)

    #create a Road Map title and center it
    st.markdown("<h1 style='text-align: center; color: #FFF;'>Road Map</h1>", unsafe_allow_html=True)

    draw_roadmap()



# JavaScript for Web Speech API integration
WEB_SPEECH_API_JS = """
<div>
    <button id="start_button" onclick="startRecognition()">Start Recognition</button>
    <p id="transcript">Transcription will appear here...</p>
</div>
<script>
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;  // Change to true if you want the recognition to continue even after the user stops speaking
    recognition.interimResults = false;  // Set to true if you want to get results while the user is speaking

    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript;
        document.getElementById("transcript").innerText = "Transcription: " + transcript;
        // Use Streamlit's setComponentValue to send the transcript back to Python
        window.parent.postMessage({transcript: transcript}, "*");
    };

    function startRecognition() {
        recognition.start();
    }
</script>
"""

# Function to handle the transcript
def process_transcript(transcript):
    # Placeholder for processing the transcript
    # For example, updating session state or displaying the text
    st.session_state['transcript'] = transcript
    st.write(f"Transcript: {transcript}")

# Injecting the HTML and JavaScript into the Streamlit app
# def display_web_speech_api():
#     st.markdown("Click the button below to start voice recognition:", unsafe_allow_html=True)
#     st.components.v1.html(WEB_SPEECH_API_JS, height=150)
#     # Display the transcript if available
#     if st.session_state.get('transcript'):
#         process_transcript(st.session_state.transcript)
#     else:
#         st.write("No transcript available yet.")


# Define the send_message function
def send_message(user_input):
    # Here you would have your code to send the message to the chatbot and receive a response
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(user_input)
    return response.text if response else "Sorry, I couldn't get a response."

# Display chat history function
def display_chat_history():
    # Display chat history before and after the form
    for sender, message in st.session_state.chat_history:  # Reversed for bottom-up display
        #Differentiate the sender with color
        if sender == "You":
            st.markdown(f"<div style='float: right; color: #FFF; padding: 10px; display: inline-block;'> 🕺 You</div>",
                        unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style='width: 100%;'>
                    <div style='float: right;'>
                        <div style='text-align: right; background-color: #FFF; color: #000; 
                                    border-radius: 10px; padding: 10px; display: inline-block; 
                                    margin: 5px 0; clear: both;'>
                            {message}
                        </div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:  # sender == "Tutor"
            st.markdown(f"<div style='text-align: right; color: #FFF; padding: 10px; display: inline-block;'> 💃 LiA</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: left; background-color: #DBE6F6; color: #000; "
                        f"border-radius: 10px; padding: 10px; display: inline-block;'>{message}</div>",
                        unsafe_allow_html=True)

def process_user_input(user_input):
    if user_input:  # Check if the input is not empty
        # Send the user's message and get the response from the chatbot
        response = send_message(user_input)
        
        # Append both user's message and tutor's response to the chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Tutor", response))

# Chatbot UI function
def chatbot_ui():
    st.subheader("LiA (Connects to Gemini API)")

    # Initial chatbot greeting and chat history display
    if len(st.session_state.chat_history) == 0:
        initial_greeting = "Hi, I'm LiA, your interview assistant. How can I help you today?"
        st.session_state.chat_history.append(("Tutor", initial_greeting))

    # Chat history display
    display_chat_history()

    #display_web_speech_api()

    #MAYBE split into another function

    # Start and Stop buttons for Web Speech API
    # st.markdown("Click the button below to start voice recognition:", unsafe_allow_html=True)
    # # Add Start and Stop buttons with callbacks to start/stop the speech recognition
    #  # Start and Stop buttons for Web Speech API
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button('Start Recognition', key='start'):
    #         st.session_state.recognition_state = 'start'
    # with col2:
    #     if st.button('Stop Recognition', key='stop'):
    #         st.session_state.recognition_state = 'stop'


    # If recognition state is set, trigger the corresponding JavaScript function
    if st.session_state.get('recognition_state') == 'start':
        display_web_speech_api()
        st.session_state.recognition_state = None  # Reset the recognition state
    elif st.session_state.get('recognition_state') == 'stop':
        st.session_state.recognition_state = None  # Reset the recognition state

    # Handle incoming transcription from JavaScript
    if st.session_state.get('transcript'):
        process_user_input(st.session_state.transcript)
    
    # Input box with the last transcript
    user_input = st.text_input("Ask me anything about your interview preparation:",
                               key="chat_input",
                               value=st.session_state.get('transcript', ''))
    st.button('Send', on_click=process_user_input, args=(user_input,))


# Chatbot UI function
# def chatbot_ui():
#     st.subheader("LiA (Connects to Gemini API)")

#     # Initial chatbot greeting
#     if len(st.session_state.chat_history) == 0:
#         initial_greeting = "Hi, I'm LiA, your interview assistant. How can I help you today?"
#         st.session_state.chat_history.append(("Tutor", initial_greeting))
  
#     # Chat history display
#     display_chat_history()

#     display_web_speech_api()

#     # Display the transcript if available
#     if 'transcript' in st.session_state:
#         st.write("Last transcript:", st.session_state['transcript'])


#     # wav_audio_data = st_audiorec()

#     # transcript = ""
#     # if wav_audio_data is not None:
#     #     # If there's audio data, transcribe it
#     #     transcript = transcribe_audio(wav_audio_data)
#     #     if transcript:
#     #         # Use the transcript as if it was text input
#     #         st.session_state.chat_history.append(("You", transcript))
#     #         response = send_message(transcript)
#     #         st.session_state.chat_history.append(("Tutor", response))
#     #     else:
#     #         st.error("Could not transcribe the audio.")
    
#     #send st.session_state['transcript'] to the input box
#     st.text_input("Ask me anything about your interview preparation:", key="chat_input2", value=str(st.session_state['transcript']))

#     # User input form
#     user_input = st.text_input("Ask me anything about your interview preparation:", key="chat_input")

#     # When 'Send' or the key enter is pressed, the message is processed and the input box is cleared
#     st.button('Send', on_click=process_user_input, args=(user_input,))

# Define page navigation function
def load_page(page_func):
    st.session_state['current_page'] = page_func

# Button styles
button_style = """
    <style>
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            margin: 5px;
        }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# Main application layout
st.title("LiA (Large Interview Advisor)")
st.markdown(button_style, unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("About You"):
        load_page(main_page)
with col2:
    if st.button("Assessment"):
        load_page(technical_interview)
with col3:
    if st.button("Road Map"):
        load_page(road_map)
with col4:
    if st.button("Improvement Chatbot"):
        load_page(chatbot_ui)
    

# Load the current page
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = main_page
st.session_state['current_page']()

# # Initialize session state for chat history
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []
# if 'input_counter' not in st.session_state:
#     st.session_state.input_counter = 0

# # Define page content functions
# def main_page():
#     st.subheader("Welcome to Interview Prep Helper")

# def technical_interview():
#     st.subheader("Technical Interview Preparation")

# def road_map():
#     st.subheader("Behavioral Interview Preparation")

# def road_map():
#     st.subheader("Case Study Preparation")

# def resources_and_tips():
#     st.subheader("Resources and Tips")

# def chat_history():
#     st.write("Chat History: " + str(st.session_state.input_counter))
    
#     # Display chat history before and after the form
#     for sender, message in st.session_state.chat_history:  # Reversed for bottom-up display
#         #Differentiate the sender with color
#         if sender == "You":
#             st.markdown(f"<div style='float: right; color: #FFF; padding: 10px; display: inline-block;'> 🕺 You</div>",
#                         unsafe_allow_html=True)
#             st.markdown(
#                 f"""
#                 <div style='width: 100%;'>
#                     <div style='float: right;'>
#                         <div style='text-align: right; background-color: #FFF; color: #000; 
#                                     border-radius: 10px; padding: 10px; display: inline-block; 
#                                     margin: 5px 0; clear: both;'>
#                             {message}
#                         </div>
#                     </div>
#                 </div>
#                 """, 
#                 unsafe_allow_html=True
#             )
#         else:  # sender == "Tutor"
#             st.markdown(f"<div style='text-align: right; color: #FFF; padding: 10px; display: inline-block;'> 💃 LiA</div>",
#                         unsafe_allow_html=True)
#             st.markdown(f"<div style='text-align: left; background-color: #DBE6F6; color: #000; "
#                         f"border-radius: 10px; padding: 10px; display: inline-block;'>{message}</div>",
#                         unsafe_allow_html=True)
            
      
# def chatbot_ui():
#     st.subheader("LiA (Connects to Gemini API)")

#     #make an annitial call to the chatbot where the user says hi
#     if len(st.session_state.chat_history) == 0:
#         response = send_message("hi your name is LiA and interview assistant give me a greeting with your name - keep it brief but be welcoming")
#         st.session_state['chat_history'].append(("Tutor", response))
#         st.session_state.input_counter += 1

#     chat_history()

#     st.subheader("")

#     # Form for user input
#     with st.form(key='chat_form'):
#         user_input = st.text_input("Ask me anything about your interview preparation:", key="chat_input")
#         submit_button = st.form_submit_button(label='Send')

#     st.write("User input:", user_input)
#     st.write("Submit button:", submit_button)

#     # Process user input
#     if submit_button and user_input:
#         st.write("YO")
#         # Simulate sending the user message and getting a response from the chatbot
#         response = send_message(user_input)
#         st.session_state['chat_history'].append(("You", user_input))
#         st.session_state['chat_history'].append(("Tutor", response))
#         st.session_state.input_counter += 1  # Increment the input_counter to refresh the input field

# def send_message(user_input=None):
#     #sending the message and getting a response from the chatbot
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content(user_input)
#     return response.text if response else "Sorry, I couldn't get a response."

# # Page navigation
# def load_page(page_func):
#     # Function to load a page content function
#     st.session_state['current_page'] = page_func

# # Top navigation bar
# st.title("LIA (Large Interview Advisor)")

# # Button styles
# button_style = """
#     <style>
#         div.stButton > button {
#             width: 100%;
#             border-radius: 10px;
#             margin: 5px;
#         }
#     </style>
# """
# st.markdown(button_style, unsafe_allow_html=True)

# # Top icon buttons for navigation
# col1, col2, col3, col4, col5, col6 = st.columns(6)
# with col1:
#     if st.button("🏠 Home"):
#         load_page(main_page)
# with col2:
#     if st.button("💻 Technical"):
#         load_page(technical_interview)
# with col3:
#     if st.button("🗣️ Behavioral"):
#         load_page(road_map)
# with col4:
#     if st.button("📊 Case Study"):
#         load_page(road_map)
# with col5:
#     if st.button("📚 Resources"):
#         load_page(resources_and_tips)
# with col6:
#     if st.button("💬 Chatbot"):
#         st.write("In")
#         load_page(chatbot_ui)

# # Load the selected page
# if 'current_page' not in st.session_state:
#     st.session_state['current_page'] = main_page
# st.session_state['current_page']()
# st.write("Out")


# def chatbot_ui():
#     st.subheader("Interview Prep Chatbot (Connects to Gemini API)")

#     with st.form(key='chat_form'):
#         user_input = st.text_input("Ask me anything about your interview preparation:", key="chat_input")
#         submit_button = st.form_submit_button(label='Send')

#     if submit_button and user_input:
#         # Simulate sending the user message and getting a response from the chatbot
#         response = send_message(user_input)
#         st.session_state.chat_history.append(("You", user_input))
#         st.session_state.chat_history.append(("Tutor", response))

#         st.session_state.input_counter += 1  # Increment the input_counter to refresh the input field

#     # Display chat history
#     for sender, message in st.session_state.chat_history:
#         # Differentiate the sender with color
#         if sender == "You":
#             st.markdown(f"<div style='float: right; color: #FFF; padding: 10px; display: inline-block;'> 🕺 You</div>",
#                         unsafe_allow_html=True)
#             st.markdown(
#                 f"""
#                 <div style='width: 100%;'>
#                     <div style='float: right;'>
#                         <div style='text-align: right; background-color: #FFF; color: #000; 
#                                     border-radius: 10px; padding: 10px; display: inline-block; 
#                                     margin: 5px 0; clear: both;'>
#                             {message}
#                         </div>
#                     </div>
#                 </div>
#                 """, 
#                 unsafe_allow_html=True
#             )
#         else:  # sender == "Tutor"
#             st.markdown(f"<div style='text-align: right; color: #FFF; padding: 10px; display: inline-block;'> 💃 LiA</div>",
#                         unsafe_allow_html=True)
#             st.markdown(f"<div style='text-align: left; background-color: #DBE6F6; color: #000; "
#                         f"border-radius: 10px; padding: 10px; display: inline-block;'>{message}</div>",
#                         unsafe_allow_html=True)
            
    # with st.form(key='chat_form'):
    #   user_input = st.text_input("Ask me anything about your interview preparation:", key="chat_input")
    #   submit_button = st.form_submit_button(label='Send')

