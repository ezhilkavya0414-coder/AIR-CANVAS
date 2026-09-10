import cv2
import numpy as np
import copy

from modules.hand_tracking import HandTracker
from modules.drawing import Drawing
from modules.gesture_detection import detect_gesture

from pdf_export import save_pdf
from ai_tutor import AITutor
from modules.ocr import read_text_from_canvas
from voice_assistant import voice_ai_tutor


# =========================================================
# SETTINGS
# =========================================================

WINDOW_NAME = "AIR CANVAS"

ERASER_SIZE = 35
BRUSH_THICKNESS = 5

THICKNESS_OPTIONS = {
    1: 2,
    2: 5,
    3: 10,
    4: 15
}

COLORS = [
    ("RED", (0, 0, 255)),
    ("GREEN", (0, 255, 0)),
    ("BLUE", (255, 0, 0)),
    ("YELLOW", (0, 255, 255)),
    ("WHITE", (255, 255, 255))
]


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()


# =========================================================
# OBJECTS
# =========================================================

tracker = HandTracker()

drawer = Drawing(
    color=(0, 0, 255),
    thickness=BRUSH_THICKNESS
)

ai_tutor = AITutor()


# =========================================================
# CANVAS
# =========================================================

canvas = None


# =========================================================
# STROKE DATA + UNDO / REDO
# =========================================================

strokes = []
undo_stack = []
redo_stack = []
current_stroke = None


def render_strokes():

    global canvas

    if canvas is None:
        return

    canvas[:] = 0

    for stroke in strokes:

        points = stroke["points"]
        color = stroke["color"]
        thickness = stroke["thickness"]

        if len(points) == 1:

            cv2.circle(
                canvas,
                tuple(points[0]),
                max(1, thickness // 2),
                color,
                -1
            )

        else:

            for i in range(1, len(points)):

                cv2.line(
                    canvas,
                    tuple(points[i - 1]),
                    tuple(points[i]),
                    color,
                    thickness,
                    cv2.LINE_AA
                )


def save_canvas_state():

    undo_stack.append(
        copy.deepcopy(strokes)
    )

    if len(undo_stack) > 20:
        undo_stack.pop(0)

    redo_stack.clear()


def undo_canvas():

    global strokes, current_stroke

    if len(undo_stack) == 0:

        print("Nothing to undo.")
        return

    redo_stack.append(
        copy.deepcopy(strokes)
    )

    strokes = undo_stack.pop()
    current_stroke = None

    drawer.reset()
    render_strokes()

    print("UNDO successful.")


def redo_canvas():

    global strokes, current_stroke

    if len(redo_stack) == 0:

        print("Nothing to redo.")
        return

    undo_stack.append(
        copy.deepcopy(strokes)
    )

    strokes = redo_stack.pop()
    current_stroke = None

    drawer.reset()
    render_strokes()

    print("REDO successful.")


def distance_to_stroke(point, stroke):

    px, py = point
    best = float("inf")

    for sx, sy in stroke["points"]:

        distance = ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5
        if distance < best:
            best = distance

    return best


def erase_stroke_at(point):

    global strokes

    if not strokes:
        return False

    nearest_index = -1
    nearest_distance = float("inf")

    for index, stroke in enumerate(strokes):

        distance = distance_to_stroke(
            point,
            stroke
        )

        allowed = ERASER_SIZE + stroke["thickness"]

        if distance <= allowed and distance < nearest_distance:

            nearest_distance = distance
            nearest_index = index

    if nearest_index != -1:

        strokes.pop(nearest_index)
        render_strokes()
        print("Stroke erased.")
        return True

    return False


# =========================================================
# SAVE PNG
# =========================================================

def save_png():

    if canvas is None:
        return

    filename = "air_canvas_output.png"

    success = cv2.imwrite(
        filename,
        canvas
    )

    if success:

        print("--------------------------------")
        print("PNG EXPORTED SUCCESSFULLY")
        print("File:", filename)
        print("--------------------------------")

    else:

        print("ERROR: PNG could not be saved.")


# =========================================================
# THICKNESS SELECTION
# =========================================================

def set_thickness(level):

    global BRUSH_THICKNESS

    if level in THICKNESS_OPTIONS:

        BRUSH_THICKNESS = THICKNESS_OPTIONS[level]
        drawer.thickness = BRUSH_THICKNESS
        drawer.reset()

        print(
            "Thickness selected:",
            BRUSH_THICKNESS
        )


def draw_thickness_info(frame):

    cv2.putText(
        frame,
        f"Thickness: {BRUSH_THICKNESS}px  (1:2  2:5  3:10  4:15)",
        (20, 425),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


# =========================================================
# COLOR PALETTE
# =========================================================

def draw_palette(frame):

    x_start = 20
    y_start = 100

    box_width = 75
    box_height = 40

    for i, (name, color) in enumerate(COLORS):

        x1 = x_start + i * box_width
        y1 = y_start

        x2 = x1 + box_width - 5
        y2 = y1 + box_height

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            -1
        )

        cv2.putText(
            frame,
            name,
            (x1 + 5, y2 + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1
        )


def choose_color(x):

    index = int(
        (x - 20) / 75
    )

    if 0 <= index < len(COLORS):

        name, color = COLORS[index]

        drawer.color = color

        print(
            "Selected color:",
            name
        )


# =========================================================
# AI TUTOR DISPLAY
# =========================================================

def show_ai_tutor(question, response):

    height = 500
    width = 800

    tutor_window = np.ones(
        (height, width, 3),
        dtype=np.uint8
    ) * 255


    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    cv2.putText(
        tutor_window,
        "AI TUTOR",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.1,
        (0, 0, 255),
        3
    )


    # -----------------------------------------------------
    # QUESTION
    # -----------------------------------------------------

    cv2.putText(
        tutor_window,
        "Question:",
        (30, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2
    )


    y = 125

    for line in question.split("\n"):

        if y > 180:
            break

        cv2.putText(
            tutor_window,
            line[:80],
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1
        )

        y += 25


    # -----------------------------------------------------
    # ANSWER
    # -----------------------------------------------------

    cv2.putText(
        tutor_window,
        "Answer:",
        (30, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2
    )


    y = 255

    for line in response.split("\n"):

        if y > 470:
            break

        cv2.putText(
            tutor_window,
            line[:80],
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1
        )

        y += 25


    cv2.imshow(
        "AI TUTOR",
        tutor_window
    )


# =========================================================
# OCR + AI TUTOR
# =========================================================

def run_ocr():

    global canvas

    if canvas is None:

        print("Canvas is not ready.")
        return


    print()
    print("--------------------------------")
    print("READING WHITEBOARD...")
    print("--------------------------------")


    try:

        text = read_text_from_canvas(
            canvas
        )

    except Exception as error:

        print(
            "OCR ERROR:",
            error
        )

        return


    text = text.strip()


    print(
        "OCR Result:",
        text
    )


    if text == "":

        print(
            "No text detected on the whiteboard."
        )

        show_ai_tutor(
            "No text detected",
            "Please write a clear equation or question."
        )

        return


    # -----------------------------------------------------
    # SEND OCR TEXT TO AI TUTOR
    # -----------------------------------------------------

    try:

        response = ai_tutor.get_response(
            text
        )

    except Exception as error:

        print(
            "AI TUTOR ERROR:",
            error
        )

        response = (
            "AI Tutor could not process the question."
        )


    print()
    print("--------------------------------")
    print("AI TUTOR RESPONSE")
    print("--------------------------------")
    print(response)
    print("--------------------------------")


    show_ai_tutor(
        text,
        response
    )


# =========================================================
# TYPE QUESTION TO AI TUTOR
# =========================================================

def type_ai_question():

    print()
    print("--------------------------------")
    print("AI TUTOR")
    print("--------------------------------")


    question = input(
        "Enter your question: "
    ).strip()


    if question == "":

        print("No question entered.")
        return


    try:

        response = ai_tutor.get_response(
            question
        )

    except Exception as error:

        print(
            "AI TUTOR ERROR:",
            error
        )

        response = (
            "AI Tutor could not process the question."
        )


    print()
    print("AI Tutor:")
    print(response)


    show_ai_tutor(
        question,
        response
    )


# =========================================================
# START MESSAGE
# =========================================================

print("--------------------------------")
print("          AIR CANVAS")
print("--------------------------------")

print("INDEX FINGER  = DRAW")
print("FIST          = ERASE")
print("OPEN PALM     = CLEAR")
print("PINCH         = COLOR")
print("1 / 2 / 3 / 4 = THICKNESS")

print("--------------------------------")

print("O = OCR + AI TUTOR")
print("T = TYPE AI QUESTION")
print("U = UNDO")
print("R = REDO")
print("S = SAVE PNG")
print("P = SAVE PDF")
print("Q = QUIT")

print("--------------------------------")


# =========================================================
# VARIABLES
# =========================================================

last_gesture = "NONE"
erase_action_started = False


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # -----------------------------------------------------
    # CAMERA FRAME
    # -----------------------------------------------------

    success, frame = cap.read()


    if not success:

        print(
            "ERROR: Camera frame could not be read."
        )

        break


    # -----------------------------------------------------
    # MIRROR
    # -----------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # -----------------------------------------------------
    # CREATE CANVAS
    # -----------------------------------------------------

    if canvas is None:

        canvas = np.zeros_like(
            frame
        )


    # -----------------------------------------------------
    # HAND LANDMARKS
    # -----------------------------------------------------

    landmarks = tracker.get_landmarks(
        frame
    )


    # =====================================================
    # HAND DETECTED
    # =====================================================

    if landmarks:

        # -------------------------------------------------
        # GESTURE
        # -------------------------------------------------

        gesture = detect_gesture(
            landmarks
        )


        # -------------------------------------------------
        # INDEX FINGER
        # -------------------------------------------------

        x, y = landmarks[8]

        current_point = (
            x,
            y
        )


        # -------------------------------------------------
        # FINGERTIP
        # -------------------------------------------------

        cv2.circle(
            frame,
            current_point,
            8,
            (0, 0, 255),
            -1
        )


        # =================================================
        # DRAW
        # =================================================

        if gesture == "DRAW":

            if drawer.previous_point is None:

                save_canvas_state()

                current_stroke = {
                    "points": [current_point],
                    "color": drawer.color,
                    "thickness": BRUSH_THICKNESS
                }

                strokes.append(current_stroke)

            else:

                if current_stroke is not None:
                    current_stroke["points"].append(current_point)

            drawer.thickness = BRUSH_THICKNESS

            drawer.draw_line(
                canvas,
                current_point
            )


        # =================================================
        # ERASE
        # =================================================

        elif gesture == "ERASE":

            drawer.reset()

            if last_gesture != "ERASE":
                save_canvas_state()

            erase_stroke_at(current_point)

            cv2.circle(
                frame,
                current_point,
                ERASER_SIZE,
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                "STROKE ERASE MODE",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )


        # =================================================
        # CLEAR
        # =================================================

        elif gesture == "CLEAR":

            drawer.reset()


            if last_gesture != "CLEAR":

                save_canvas_state()

                strokes.clear()
                current_stroke = None
                render_strokes()

                print(
                    "Canvas cleared."
                )


        # =================================================
        # COLOR
        # =================================================

        elif gesture == "COLOR":

            drawer.reset()
            current_stroke = None


            draw_palette(
                frame
            )


            cv2.putText(
                frame,
                "PINCH TO SELECT COLOR",
                (20, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )


            if last_gesture != "COLOR":

                if 20 <= x <= 395:

                    choose_color(x)


        # =================================================
        # NONE
        # =================================================

        else:

            drawer.reset()
            current_stroke = None


        # -------------------------------------------------
        # GESTURE DISPLAY
        # -------------------------------------------------

        cv2.putText(
            frame,
            "Gesture: " + gesture,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        last_gesture = gesture


    # =====================================================
    # NO HAND
    # =====================================================

    else:

        drawer.reset()
        current_stroke = None

        last_gesture = "NONE"


        cv2.putText(
            frame,
            "No Hand Detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # =====================================================
    # KEYBOARD HELP
    # =====================================================

    draw_thickness_info(frame)

    cv2.putText(
        frame,
        "O:OCR T:AI U:Undo R:Redo S:PNG P:PDF Q:Quit",
        (20, 475),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # COMBINE CAMERA + CANVAS
    # =====================================================

    output = cv2.add(
        frame,
        canvas
    )


    # =====================================================
    # SHOW AIR CANVAS
    # =====================================================

    cv2.imshow(
        WINDOW_NAME,
        output
    )


    # =====================================================
    # KEYBOARD
    # =====================================================

    key = cv2.waitKey(1) & 0xFF


    # -----------------------------------------------------
    # 1-4 = THICKNESS
    # -----------------------------------------------------

    if key in [ord("1"), ord("2"), ord("3"), ord("4")]:

        set_thickness(
            int(chr(key))
        )

    # -----------------------------------------------------
    # O = OCR
    # -----------------------------------------------------

    elif key == ord("o"):

        run_ocr()


    # -----------------------------------------------------
    # T = AI TUTOR
    # -----------------------------------------------------

    elif key == ord("t"):

        type_ai_question()


    # -----------------------------------------------------
    # U = UNDO
    # -----------------------------------------------------

    elif key == ord("u"):

        undo_canvas()


    # -----------------------------------------------------
    # R = REDO
    # -----------------------------------------------------

    elif key == ord("r"):

        redo_canvas()


    # -----------------------------------------------------
    # S = SAVE PNG
    # -----------------------------------------------------

    elif key == ord("s"):

        save_png()


    # -----------------------------------------------------
    # P = SAVE PDF
    # -----------------------------------------------------

    elif key == ord("p"):

        save_png()

        try:

            save_pdf(
                "air_canvas_output.png"
            )

        except Exception as error:

            print(
                "PDF ERROR:",
                error
            )

    elif key == ord("v"):
      print("V KEY PRESSED")
      voice_ai_tutor()



    # -----------------------------------------------------
    # Q = QUIT
    # -----------------------------------------------------

    elif key == ord("q"):

        break


# =========================================================
# CLOSE
# =========================================================

cap.release()

cv2.destroyAllWindows()

print()
print("--------------------------------")
print("AIR CANVAS CLOSED")
print("--------------------------------")
