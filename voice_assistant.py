import speech_recognition as sr
import pyttsx3

from ai_tutor import AITutor


# Speech recognition
recognizer = sr.Recognizer()

# Voice output
engine = pyttsx3.init()

# AI Tutor
tutor = AITutor()

def speak(text):

    print()
    print("--------------------------------")
    print("AI VOICE ANSWER")
    print("--------------------------------")
    print(text)
    print("--------------------------------")

    try:

        # Convert answer into one clean sentence
        speech_text = " ".join(
            text.split()
        )

        engine.stop()

        engine.say(
            speech_text
        )

        engine.runAndWait()

        print("Voice response completed.")

    except Exception as error:

        print(
            "Voice output error:",
            error
        )

def listen():

    print()
    print("--------------------------------")
    print("VOICE ASSISTANT")
    print("--------------------------------")
    print("Listening... Speak clearly.")

    try:

        with sr.Microphone(device_index=1) as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=2
            )

            recognizer.energy_threshold = 300

            print("Speak now...")

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )

        print("Processing speech...")

        question = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You said:", question)

        return question


    except sr.WaitTimeoutError:

        print("No speech detected.")
        return ""


    except sr.UnknownValueError:

        print("Could not understand the speech.")
        return ""


    except sr.RequestError as error:

        print("Speech recognition error:", error)
        return ""


    except Exception as error:

        print("Voice Assistant Error:", error)
        return ""


def voice_ai_tutor():

    # Get voice question
    question = listen()

    if not question:
        return

    print()
    print("Sending question to AI Tutor...")

    # Get AI Tutor answer
    answer = tutor.get_response(question)

    # Display answer
    print()
    print("--------------------------------")
    print("AI TUTOR")
    print("--------------------------------")
    print(answer)
    print("--------------------------------")

    # Speak answer
    speak(answer)


if __name__ == "__main__":

    voice_ai_tutor()
