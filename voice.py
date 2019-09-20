import dialogflow
from google.api_core.exceptions import InvalidArgument
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()

# Setting up the text to voice engine's properties
engine.setProperty('rate', 140)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Connect with the dialogflow account
DIALOGFLOW_PROJECT_ID = 'small-talk-ifssbd'
DIALOGFLOW_LANGUAGE_CODE = 'en-US'
GOOGLE_APPLICATION_CREDENTIALS = 'Small-Talk-6795c34619e1.json'
SESSION_ID = 'current-user-id'

r = sr.Recognizer()
mic = sr.Microphone()

# using mic to listen


def listening():
    with mic as source:
        print("Speak now!")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text_to_be_analyzed = r.recognize_google(audio)
        # engine.say(text_to_be_analyzed)
        return text_to_be_analyzed
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))


print("Hey how can I help you?")

while(True):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

    # text_to_be_analyzed = input("reply: ")
    text_to_be_analyzed = listening()

    text_input = dialogflow.types.TextInput(
        text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            session=session, query_input=query_input)
    except InvalidArgument:
        raise

    print("Query text:", response.query_result.query_text)
    # engine.say(response.query_result.query_text)

    print("Detected intent:", response.query_result.intent.display_name)
    print("Detected intent confidence:",
          response.query_result.intent_detection_confidence)
    print("Fulfillment text:", response.query_result.fulfillment_text)
    engine.say(response.query_result.fulfillment_text)

    engine.runAndWait()
    engine.stop()
    # set GOOGLE_APPLICATION_CREDENTIALS=F:\Project JEAN\JEAN-546c043a456f.json
