from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
import os


def save_pdf(image_path):

    pdf_name = "air_canvas_output.pdf"

    # Check PNG exists
    if not os.path.exists(image_path):

        print("--------------------------------")
        print("PDF ERROR")
        print("Image file not found:", image_path)
        print("--------------------------------")

        return None


    try:

        # Create PDF
        pdf = canvas.Canvas(
            pdf_name,
            pagesize=A4
        )

        page_width, page_height = A4


        # Open image
        image = Image.open(image_path)

        image_width, image_height = image.size


        # Keep image inside A4 page
        scale = min(
            page_width / image_width,
            page_height / image_height
        )


        new_width = image_width * scale
        new_height = image_height * scale


        # Center image
        x = (page_width - new_width) / 2

        y = (page_height - new_height) / 2


        # Title
        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 40,
            "AIR CANVAS - Virtual Whiteboard"
        )


        # Draw image
        pdf.drawImage(
            ImageReader(image),
            x,
            y,
            width=new_width,
            height=new_height,
            preserveAspectRatio=True,
            mask="auto"
        )


        # Save PDF
        pdf.save()


        print("--------------------------------")
        print("PDF EXPORTED SUCCESSFULLY")
        print("File:", pdf_name)
        print("--------------------------------")


        return pdf_name


    except Exception as error:

        print("--------------------------------")
        print("PDF EXPORT ERROR")
        print(error)
        print("--------------------------------")

        return None
