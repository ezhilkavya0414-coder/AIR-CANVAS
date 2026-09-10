from voice_assistant import listen, speak


question = listen()


if question:

    speak(
        "You said " + question
    )
