import speech_recognition as sr

r = sr.Recognizer()

print("--------------------------------")
print("MICROPHONE TEST")
print("--------------------------------")

print("Available microphones:")

for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(i, ":", name)

print("--------------------------------")

with sr.Microphone() as source:

    print("Adjusting for background noise...")
    r.adjust_for_ambient_noise(source, duration=2)

    print("Speak LOUDLY now...")
    audio = r.listen(source, timeout=10, phrase_time_limit=8)

print("Audio captured!")
print("Trying to recognize...")

try:

    text = r.recognize_google(
        audio,
        language="en-IN"
    )

    print("--------------------------------")
    print("SUCCESS!")
    print("You said:", text)
    print("--------------------------------")

except sr.UnknownValueError:

    print("--------------------------------")
    print("VOICE RECEIVED BUT NOT UNDERSTOOD")
    print("--------------------------------")

except sr.RequestError as e:

    print("--------------------------------")
    print("INTERNET / GOOGLE ERROR")
    print(e)
    print("--------------------------------")
