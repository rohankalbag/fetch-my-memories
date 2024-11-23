from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from io import BytesIO
import sys
import requests
from tqdm import tqdm
import time

pdfmetrics.registerFont(TTFont('Symbola', 'Symbola.ttf'))

def add_message_block(c, message, y_position):
    width, height = letter

    c.setStrokeColor(colors.purple)
    c.setLineWidth(1)
    c.line(50, y_position, width - 50, y_position)

    # Left Profile
    try: 
        profile_image_url = message['written_by_profile']['profile_image']
        if profile_image_url:
            response = requests.get("https://centralised.sarc-iitb.org" + profile_image_url, headers=auth_header)
            profile_img = ImageReader(BytesIO(response.content))
            c.drawImage(profile_img, 60, y_position - 60, 50, 50)
    except:
        # skip for messages from anonymous users
        time.sleep(0) #DoNothing #ForRealThough

    # Right Profile
    profile_image_url = message['written_for_profile']['profile_image']
    if profile_image_url:
        response = requests.get("https://centralised.sarc-iitb.org" + profile_image_url, headers=auth_header)
        profile_img = ImageReader(BytesIO(response.content))
        c.drawImage(profile_img, width - 110, y_position - 60, 50, 50)

    # Names and details
    written_by = "From: " + message['written_by']
    written_for = "To: " + message['written_for']
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.purple)
    c.drawString(120, y_position - 20, f"{written_by}")
    c.drawString(width - 280, y_position - 20, f"{written_for}")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    if message['written_by_dept'] != "None" and message['written_by_year'] != "None":
        # for anonymous users, these fields are not present
        c.drawString(120, y_position - 40, f"{message['written_by_dept']} | {message['written_by_year']}")
    c.drawString(width - 280, y_position - 40, f"{message['written_for_dept']} | {message['written_for_year']}")

    # Written Content
    c.setFont("Symbola",12)
    content = message['content']
    text_object = c.beginText(60, y_position - 80)
    text_object.setFont("Symbola", 12)
    max_width = width - 120
    content_height = 0 
    current_y_position = y_position - 80

    for line in content.splitlines():
        words = line.split()
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if c.stringWidth(test_line) <= max_width:
                current_line = test_line
            else:
                text_object.textLine(current_line.strip())
                content_height += 12
                current_y_position -= 12

                if current_y_position < 50:
                    c.drawText(text_object)
                    c.showPage()
                    text_object = c.beginText(60, height - 50)
                    text_object.setFont("Symbola", 12)
                    current_y_position = height - 50

                current_line = word + " "

        if current_line:
            text_object.textLine(current_line.strip())
            content_height += 12
            current_y_position -= 12

            if current_y_position < 50:
                c.drawText(text_object)
                c.showPage()
                text_object = c.beginText(60, height - 50)
                text_object.setFont("Symbola", 12)
                current_y_position = height - 50

    c.drawText(text_object)

    return current_y_position - 50

def generate_pdf(messagesForYou, messagesByYou, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.purple)
    c.drawString(50, 750, "Yearbook - Your College Memories")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "Cherish the messages written for you and by you.")

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.purple)
    c.drawString(50, 700, "What people wrote for you")

    y_position = 680
    progressBar = tqdm(total=len(messagesForYou) + len(messagesByYou))

    for message in messagesForYou:
        if y_position < 150: 
            c.showPage()
            y_position = 750
        y_position = add_message_block(c, message, y_position)
        progressBar.update(1)
    
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.purple)
    c.drawString(50, y_position, "What you wrote for others")

    y_position -= 30
    
    for message in messagesByYou:
        if y_position < 150: 
            c.showPage()
            y_position = 750
        y_position = add_message_block(c, message, y_position)
        progressBar.update(1)
    c.save()

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments. Expected 2, got", len(sys.argv) - 1)
        sys.exit(1)

    param1 = sys.argv[1]
    param2 = sys.argv[2]

    auth_url = "https://centralised.sarc-iitb.org/api/authenticate/token/"
    auth_payload = {"username": param1, "password": param2}

    response = requests.post(auth_url, json=auth_payload, headers={"Content-Type": "application/json"})
    access_token = response.json()['access']
    auth_header = {"Authorization": f"Bearer {access_token}"}
    userId = requests.get("https://centralised.sarc-iitb.org/api/authenticate/current_user/", headers=auth_header).json()['id']
    messagesForYou = requests.get(f"https://centralised.sarc-iitb.org/api/posts/others/{userId}",headers=auth_header).json()
    messagesByYou = requests.get(f"https://centralised.sarc-iitb.org/api/posts/my/{userId}",headers=auth_header).json()
    generate_pdf(messagesForYou, messagesByYou, "yearbook.pdf")
