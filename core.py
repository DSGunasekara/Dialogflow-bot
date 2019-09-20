# This is the core module for PILLIP
# Functions are controlled using threads and work independently.
# Import this module and use required instances to use functions
#
# When adding new classes please follow OOP design and PEP8.

import _thread

# for EyeHandler
import socket
import time

# for CameraHandler
import cv2
import numpy

# for voice
import dialogflow
from google.api_core.exceptions import InvalidArgument
import pyttsx3
import speech_recognition as sr


class EyeHandler:

    # Merged to master: 18/07/19
    # Author: hddananjaya
    """
    Send animation codes to mobile device.

    Communicates with mobile device using sockets, this instance acts as the client.
    use send_anim_code() for sending codes.
    This is a forever thread and checks connectivity with 1sec time interval,
    If connection is dropped, reconnect it back ;)
    """

    def __init__(self, host_addr, host_port):
        self.host_addr = host_addr
        self.host_port = host_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _thread.start_new_thread(self.connect, ())

    def connect(self):
        while True:
            try:
                self.sock.sendall(b"SYN")
            except:
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect_ex((self.host_addr, self.host_port))
                print(
                    "-- trying to connect {}:{} --".format(self.host_addr, self.host_port))
            time.sleep(1)

    def send_anim_code(self, anim_code):
        try:
            self.sock.sendall(anim_code)
            return 0
        except:
            return -1


class CameraHandler():

    # Merged to master: 18/07/19
    # author: hddananjaya
    """
    Detect face and eyes..

    Use get_position() to retrive the current location of detected face,
    If not found will return (0,0) or latest location
    """

    def __init__(self, detect_eyes=False):
        self.detect_eyes = detect_eyes
        self.face_x = 0
        self.face_y = 0
        _thread.start_new_thread(self.detect_face, ())

    def detect_face(self):
        face_cascade = cv2.CascadeClassifier(
            r'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(r'haarcascade_eye.xml')
        camera = cv2.VideoCapture(0)

        while (True):
            ret, frame = camera.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            self.face_x = 0
            self.face_y = 0

            for (x, y, w, h) in faces:
                self.face_x = x
                self.face_y = y
                img = cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # detect eyes if only required
                if (self.detect_eyes):
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(
                        roi_gray, 1.03, 5, 0, (40, 40))
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(img, (x+ex, y+ey),
                                      (x+ex+ew, y+ey+eh), (0, 255, 0), 2)

            cv2.imshow("camera", frame)
            if cv2.waitKey(1000 // 12) & 0xff == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()

    def get_position(self):
        return ((self.face_x, self.face_y))


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
        _thread.start_new_thread(self.connection, ())

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
        self.engine.say("How can I help you?")

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
