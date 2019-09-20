import dialogflow
from google.api_core.exceptions import InvalidArgument
import pyttsx3
import speech_recognition as sr


class voice():

    def __init__(self):
        self.engine = pyttsx3.init()

        # self.engine.setProperty('rate', 140)
        # voices = self.engine.getProperty('voice')
        # self.engine.setProperty('voice', voice[1].id)

        self.DIALOGFLOW_PROJECT_ID = 'jean-skgnmu'
        self.DIALOGFLOW_LANGUAGE_CODE = 'en-US'
        self.GOOGLE_APPLICATION_CREDENTIALS = 'JEAN-546c043a456f.json'
        self.SESSION_ID = 'current-user-id'

        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

    def listening(self):
        with self.mic as source:
            print("Speak! ")
            self.r.adjust_for_ambient_noise(source)
            audio = self.r.listen(source)

        try:
            self.text_to_be_analysed = self.r.recognize_google(audio)
            return self.text_to_be_analysed
        except sr.UnknownValueError:
            print("Could not understand audio!")
        except sr.RequestError as e:
            print("Could nit request result; {}".format(e))

    def connection(self):

        print("How can I help you?")

        while(True):
            session_client = dialogflow.SessionsClient()

            session = session_client.session_path(
                self.DIALOGFLOW_PROJECT_ID, self.SESSION_ID)

            self.text_to_be_analysed = self.listening()

            text_input = dialogflow.types.TextInput(
                text=self.text_to_be_analysed, language_code=self.DIALOGFLOW_LANGUAGE_CODE)
            query_input = dialogflow.types.QueryInput(text=text_input)

            try:
                response = session_client.detect_intent(
                    session=session, query_input=query_input)
            except InvalidArgument:
                raise

            print("Query text:", response.query_result.query_text)
            print("Query text:", response.query_result.query_text)
            # engine.say(response.query_result.query_text)

            print("Detected intent:", response.query_result.intent.display_name)
            print("Detected intent confidence:",
                  response.query_result.intent_detection_confidence)
            print("Fulfillment text:", response.query_result.fulfillment_text)
            self.engine.say(response.query_result.fulfillment_text)

            self.engine.runAndWait()
            self.engine.stop()


testVoice = voice()
testVoice.connection()
