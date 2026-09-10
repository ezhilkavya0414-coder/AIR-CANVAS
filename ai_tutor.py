import re


class AITutor:

    def __init__(self):
        pass

    def get_response(self, question):

        # Remove extra spaces
        question = question.strip()

        # Remove "solve" from beginning
        question = re.sub(
            r"^\s*solve\s+",
            "",
            question,
            flags=re.IGNORECASE
        )

        # ==========================================
        # LINEAR EQUATION
        # Example: 3x - 7 = 14
        # ==========================================

        match = re.match(
            r"^\s*(-?\d*)x\s*([+-])\s*(\d+)\s*=\s*(-?\d+)\s*$",
            question,
            re.IGNORECASE
        )

        if match:

            a_text = match.group(1)
            operator = match.group(2)
            b = int(match.group(3))
            c = int(match.group(4))

            # Find coefficient of x
            if a_text == "" or a_text == "+":
                a = 1
            elif a_text == "-":
                a = -1
            else:
                a = int(a_text)

            # Convert + / - term
            if operator == "+":
                b_value = b
            else:
                b_value = -b

            # ax + b = c
            x = (c - b_value) / a

            if x.is_integer():
                x = int(x)

            return (
                f"Equation: {question}\n\n"
                f"Step 1:\n"
                f"Move {b_value} to the other side.\n\n"
                f"{a}x = {c - b_value}\n\n"
                f"Step 2:\n"
                f"Divide both sides by {a}.\n\n"
                f"x = {x}"
            )

        # ==========================================
        # ADDITION
        # ==========================================

        match = re.match(
            r"^\s*(-?\d+)\s*\+\s*(-?\d+)\s*$",
            question
        )

        if match:

            a = int(match.group(1))
            b = int(match.group(2))

            return (
                f"Question: {question}\n\n"
                f"{a} + {b} = {a + b}\n\n"
                f"Answer: {a + b}"
            )

        # ==========================================
        # SUBTRACTION
        # ==========================================

        match = re.match(
            r"^\s*(-?\d+)\s*-\s*(-?\d+)\s*$",
            question
        )

        if match:

            a = int(match.group(1))
            b = int(match.group(2))

            return (
                f"Question: {question}\n\n"
                f"{a} - {b} = {a - b}\n\n"
                f"Answer: {a - b}"
            )

        # ==========================================
        # MULTIPLICATION
        # ==========================================

        match = re.match(
            r"^\s*(-?\d+)\s*(?:\*|x|×)\s*(-?\d+)\s*$",
            question,
            re.IGNORECASE
        )

        if match:

            a = int(match.group(1))
            b = int(match.group(2))

            return (
                f"Question: {question}\n\n"
                f"{a} × {b} = {a * b}\n\n"
                f"Answer: {a * b}"
            )

        # ==========================================
        # DIVISION
        # ==========================================

        match = re.match(
            r"^\s*(-?\d+)\s*/\s*(-?\d+)\s*$",
            question
        )

        if match:

            a = int(match.group(1))
            b = int(match.group(2))

            if b == 0:
                return "Cannot divide by zero."

            answer = a / b

            if answer.is_integer():
                answer = int(answer)

            return (
                f"Question: {question}\n\n"
                f"{a} ÷ {b} = {answer}\n\n"
                f"Answer: {answer}"
            )

        # ==========================================
        # BASIC QUESTIONS
        # ==========================================

        lower = question.lower()

        if "what is ai" in lower:

            return (
                "AI stands for Artificial Intelligence.\n\n"
                "AI enables computers to perform tasks "
                "that normally require human intelligence."
            )

        if "what is python" in lower:

            return (
                "Python is a high-level programming language "
                "widely used in AI, Machine Learning and Data Science."
            )

        if "photosynthesis" in lower:

            return (
                "Photosynthesis is the process by which "
                "green plants prepare food using sunlight, "
                "water and carbon dioxide."
            )

        # ==========================================
        # UNKNOWN
        # ==========================================

        return (
            "I could not understand the question.\n\n"
            "Try:\n"
            "Solve 3x - 7 = 14\n"
            "25 + 35\n"
            "50 - 20\n"
            "10 * 5\n"
            "100 / 4"
        )
