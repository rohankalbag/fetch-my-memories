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
from constants import BLACK_COVER_IMG, BLACK_GRP_IMAGE

class YearBook:

    def __init__(self, username, password, include_friends=False, dark_mode=False):
        """Initialize the YearBook generator.
        
        Args:
            username (str): Username for authentication
            password (str): Password for authentication
            include_friends (bool): Whether to include friends' messages
            dark_mode (bool): Whether to use dark mode color scheme
        """
        self.progress_callback = None
        self.include_friends = include_friends
        self.dark_mode = dark_mode
        
        # Set up colors based on mode
        if dark_mode:
            self.bg_color = colors.HexColor('#2C2C2C')  # Slate gray
            self.text_color = colors.HexColor('#E4E4E4')  # Light gray
            self.accent_color = colors.HexColor('#B39CD0')
        else :
            self.text_color = colors.black  
            self.accent_color = colors.purple  # Keep purple as accent color

        auth_url = "https://yearbook.sarc-iitb.org/api/authenticate/token/"
        auth_payload = {"username": username, "password": password}

        response = requests.post(auth_url, json=auth_payload, headers={"Content-Type": "application/json"})
        try:
            access_token = response.json()['access']
        except:
            raise Exception("Invalid credentials. Please check your email and password.")
        
        self.auth_header = {"Authorization": f"Bearer {access_token}"}
        self.userId = requests.get("https://yearbook.sarc-iitb.org/api/authenticate/current_user/", headers=self.auth_header).json()['id']
        
        # Get your messages
        self.messagesForYou = requests.get(f"https://yearbook.sarc-iitb.org/api/posts/others/{self.userId}",headers=self.auth_header).json()
        self.messagesByYou = requests.get(f"https://yearbook.sarc-iitb.org/api/posts/my/{self.userId}",headers=self.auth_header).json()
        self.userPhotos = requests.get(f"https://yearbook.sarc-iitb.org/api/authenticate/profile/{self.userId}/gallery/", headers=self.auth_header).json()
        
        # Get friend messages only if include_friends is True
        self.friendMessages = self.get_friend_messages() if include_friends else []
        
        self.progress = 0
        pdfmetrics.registerFont(TTFont('Symbola', 'Symbola.ttf'))

    def add_message_block(self, c, message, y_position):
        width, height = letter

        c.setStrokeColor(self.accent_color)
        c.setLineWidth(1)
        c.line(50, y_position, width - 50, y_position)

        # Left Profile
        try: 
            profile_image_url = message['written_by_profile']['profile_image']
            if profile_image_url:
                response = requests.get("https://yearbook.sarc-iitb.org" + profile_image_url, headers=self.auth_header)
                profile_img = ImageReader(BytesIO(response.content))
                c.drawImage(profile_img, 60, y_position - 60, 50, 50)
        except:
            # skip for messages from anonymous users
            time.sleep(0)

        # Right Profile
        profile_image_url = message['written_for_profile']['profile_image']
        if profile_image_url:
            response = requests.get("https://yearbook.sarc-iitb.org" + profile_image_url, headers=self.auth_header)
            profile_img = ImageReader(BytesIO(response.content))
            c.drawImage(profile_img, width - 260, y_position - 60, 50, 50)

        # Names and details
        written_by = "From: " + message['written_by']
        written_for = "To: " + message['written_for']
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.accent_color)
        c.drawString(120, y_position - 20, f"{written_by}")
        c.drawString(width - 200, y_position - 20, f"{written_for}")

        c.setFont("Helvetica", 10)
        c.setFillColor(self.text_color)
        if message['written_by_dept'] != "None" and message['written_by_year'] != "None":
            # for anonymous users, these fields are not present
            if '&' in message["written_by_dept"]:
                p = message["written_by_dept"].split('&')
                c.drawString(120, y_position - 40, f"{p[0]}")
                c.drawString(120, y_position - 55, f"{'&' + p[1]}")
                c.drawString(120, y_position - 70, f"{message['written_by_year']}")
            elif 'and' in message["written_by_dept"]:
                p = message["written_by_dept"].split('and')
                c.drawString(120, y_position - 40, f"{p[0]}")
                c.drawString(120, y_position - 55, f"{'and' + p[1]}")
                c.drawString(120, y_position - 70, f"{message['written_by_year']}")
            else:
                c.drawString(120, y_position - 40, f"{message['written_by_dept']}")
                c.drawString(120, y_position - 55, f"{message['written_by_year']}")
        
        if '&' in message["written_for_dept"]:
            p = message["written_for_dept"].split('&')
            c.drawString(width - 200, y_position - 40, f"{p[0]}")
            c.drawString(width - 200, y_position - 55, f"{'&' + p[1]}")
            c.drawString(width - 200, y_position - 70, f"{message['written_for_year']}")
        elif ' and ' in message["written_for_dept"]:
            p = message["written_for_dept"].split('and')
            c.drawString(width - 200, y_position - 40, f"{p[0]}")
            c.drawString(width - 200, y_position - 55, f"{'and' + p[1]}")
            c.drawString(width - 200, y_position - 70, f"{message['written_for_year']}")
        else:
            c.drawString(width - 200, y_position - 40, f"{message['written_for_dept']}")
            c.drawString(width - 200, y_position - 55, f"{message['written_for_year']}")


        # Written Content
        c.setFont("Symbola",12)
        content = message['content']
        text_object = c.beginText(60, y_position - 85)
        text_object.setFont("Symbola", 12)
        text_object.setFillColor(self.text_color)
        max_width = width - 120
        content_height = 0 
        current_y_position = y_position - 85

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
                        if self.dark_mode:
                            c.setFillColor(self.bg_color)
                            c.rect(0, 0, width, height, fill=1)
                        text_object = c.beginText(60, height - 50)
                        text_object.setFont("Symbola", 12)
                        text_object.setFillColor(self.text_color)
                        current_y_position = height - 50

                    current_line = word + " "

            if current_line:
                text_object.textLine(current_line.strip())
                content_height += 12
                current_y_position -= 12

                if current_y_position < 50:
                    c.drawText(text_object)
                    c.showPage()
                    if self.dark_mode:
                        c.setFillColor(self.bg_color)
                        c.rect(0, 0, width, height, fill=1)
                    text_object = c.beginText(60, height - 50)
                    text_object.setFont("Symbola", 12)
                    text_object.setFillColor(self.text_color)
                    current_y_position = height - 50

        c.drawText(text_object)

        return current_y_position - 50

    def get_friend_ids(self):
        """Get unique IDs of friends (people who have written to you or you have written to)."""
        friend_ids = set()
        
        # Add people who have written to you
        for message in self.messagesForYou:
            try:
                # The profile ID is directly in the profile object
                friend_id = message['written_by_profile']['user']
                friend_ids.add(friend_id)
            except (KeyError, IndexError) as e:
                print(f"Warning: Could not get friend ID from message. Error: {str(e)}")
                continue
        
        # Add people you have written to
        for message in self.messagesByYou:
            try:
                # The profile ID is directly in the profile object
                friend_id = message['written_for_profile']['user']
                friend_ids.add(friend_id)
            except (KeyError, IndexError) as e:
                print(f"Warning: Could not get friend ID from message. Error: {str(e)}")
                continue
        
        print(f"Found {len(friend_ids)} unique friends")
        # print(f"Returning only first two for now")
        return list(friend_ids)

    def get_friend_messages(self):
        """Get messages written by and for each friend."""
        friend_ids = self.get_friend_ids()
        friend_messages = []
        
        for friend_id in friend_ids:
            try:
                # Get messages written by the friend
                messages_by_friend = requests.get(f"https://yearbook.sarc-iitb.org/api/posts/my/{friend_id}", 
                                               headers=self.auth_header).json()
                
                # Get messages written for the friend
                messages_for_friend = requests.get(f"https://yearbook.sarc-iitb.org/api/posts/others/{friend_id}", 
                                                headers=self.auth_header).json()
                
                # Add friend's profile info to each message
                friend_profile = None
                friend_name = None
                
                if messages_by_friend:
                    friend_profile = messages_by_friend[0]['written_by_profile']
                    friend_name = friend_profile.get('name', 'Unknown')
                elif messages_for_friend:
                    friend_profile = messages_for_friend[0]['written_for_profile']
                    friend_name = friend_profile.get('name', 'Unknown')
                
                if friend_name:
                    friend_messages.append({
                        'friend_id': friend_id,
                        'friend_name': friend_name,
                        'messages_by': messages_by_friend,
                        'messages_for': messages_for_friend
                    })
            except Exception as e:
                print(f"Warning: Error processing friend {friend_id}: {str(e)}")
                continue
        
        return friend_messages

    def add_friend_intro_page(self, c, friend_data):
        """Add an introduction page - just a centered title."""
        width, height = letter
        
        # Start a new page
        c.showPage()
        
        # Add dark background if in dark mode
        if self.dark_mode:
            c.setFillColor(self.bg_color)
            c.rect(0, 0, width, height, fill=1)
        
        # Add centered title
        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(self.accent_color)
        
        # First line
        first_line = "Messages written by and for"
        text_width = c.stringWidth(first_line, "Helvetica-Bold", 30)
        x_position = (width - text_width) / 2
        c.drawString(x_position, height/2 + 20, first_line)
        
        # Second line - friend's name
        second_line = friend_data['friend_name']
        text_width = c.stringWidth(second_line, "Helvetica-Bold", 30)
        x_position = (width - text_width) / 2
        c.drawString(x_position, height/2 - 20, second_line)
        
        # Add a decorative line
        c.setStrokeColor(self.accent_color)
        c.setLineWidth(1)
        c.line(50, height/2 - 50, width - 50, height/2 - 50)

    def generate_pdf(self, output_file):
        """Generate the yearbook PDF.
        
        Args:
            output_file (str): Path to save the PDF file
        """
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter

        # cover page
        c.drawImage('iitb_bg.jpg', 0, -2, width=width+3, height=height+2,mask='auto')
        c.drawImage('iitb-logo.png', width-77, height-77, 70, 70, mask='auto')

        c.setFillColor(colors.white)
        c.setFillAlpha(0.3)
        c.rect(80, 360, 450, 70, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 25)
        # c.setFillColor(self.accent_color)
        c.setFillColor(self.accent_color)
        c.drawString(100, 396, "Yearbook - Your College Memories")
        c.setFont("Helvetica-Bold", 15)
        c.drawString(100, 376, "Late Nights, Deadlines, and Dreams - A Stroll through time")
        c.showPage()

        # Add dark background if in dark mode
        if self.dark_mode:
            c.setFillColor(self.bg_color)
            c.rect(0, 0, width, height, fill=1)

        imagesInserted = False
        coverPhotoInserted = False
        groupPhotosInserted = False
        userPhotos = self.userPhotos

        try:
            coverImageURL = "https://yearbook.sarc-iitb.org" + userPhotos["cover"]
            response = requests.get(coverImageURL, headers=self.auth_header)
            if response.content != BLACK_COVER_IMG:
                coverImage = ImageReader(BytesIO(response.content))
                c.drawImage(coverImage, 50, 545, width - 100, (width - 100)*0.3) # 10:3 aspect ratio
                coverPhotoInserted = True
            groupImageRawData = [requests.get("https://yearbook.sarc-iitb.org" + userPhotos[t], headers=self.auth_header).content for t in userPhotos if t.startswith("img")]
            groupImages = [ImageReader(BytesIO(t)) for t in groupImageRawData if t != BLACK_GRP_IMAGE]
            if len(groupImages) > 0:
                c.setFillColor(self.accent_color)
                c.setFont("Helvetica-Bold", 15)
                c.drawString(90, 510, "Group Photos: A Timeless Reminder of Cherished Friendships !")
                c.setFont("Helvetica-Bold", 12)
                c.drawString(155, 495, "Smiles That Speak of Shared Journeys and Lasting Bonds")
                groupPhotosInserted = True
            for i in range(len(groupImages)):
                c.drawImage(groupImages[i], 50 + (i % 2) * 265, 310 - (i // 2) * 200, (width - 110)/2, (width - 110)/2 * (2/3)) # 3:2 aspect ratio
            imagesInserted = coverPhotoInserted or groupPhotosInserted
        except:
            time.sleep(0)

        if imagesInserted:
            c.showPage()
            if self.dark_mode:
                c.setFillColor(self.bg_color)
                c.rect(0, 0, width, height, fill=1)
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(self.accent_color)
            c.drawString(175, 750, "What people wrote for you")
            y_position = 720
        else:
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(self.accent_color)
            c.drawString(175, 690, "What people wrote for you")
            y_position = 670

        # Calculate total messages for progress bar
        total_messages = len(self.messagesForYou) + len(self.messagesByYou)
        if self.include_friends:
            for friend_data in self.friendMessages:
                total_messages += len(friend_data['messages_by']) + len(friend_data['messages_for'])
        
        progressBar = tqdm(total=total_messages)

        # Your messages
        for message in self.messagesForYou:
            if y_position < 150: 
                c.showPage()
                if self.dark_mode:
                    c.setFillColor(self.bg_color)
                    c.rect(0, 0, width, height, fill=1)
                y_position = 750
            y_position = self.add_message_block(c, message, y_position)
            progressBar.update(1)
            self.progress += 1
            if self.progress_callback:
                self.progress_callback(self.progress)
        
        c.showPage()
        if self.dark_mode:
            c.setFillColor(self.bg_color)
            c.rect(0, 0, width, height, fill=1)
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(self.accent_color)
        c.drawString(175, 750, "What you wrote for others")
        y_position = 720
        
        for message in self.messagesByYou:
            if y_position < 150: 
                c.showPage()
                if self.dark_mode:
                    c.setFillColor(self.bg_color)
                    c.rect(0, 0, width, height, fill=1)
                y_position = 750
            y_position = self.add_message_block(c, message, y_position)
            progressBar.update(1)
            self.progress += 1
            if self.progress_callback:
                self.progress_callback(self.progress)

        # Friends' messages (only if include_friends is True)
        if self.include_friends:
            for friend_data in self.friendMessages:
                if not friend_data['messages_by'] and not friend_data['messages_for'] : continue
                # Add friend introduction page
                self.add_friend_intro_page(c, friend_data)
                
                # Messages written by the friend
                if friend_data['messages_by']:
                    c.showPage()
                    if self.dark_mode:
                        c.setFillColor(self.bg_color)
                        c.rect(0, 0, width, height, fill=1)
                    c.setFont("Helvetica-Bold", 16)
                    c.setFillColor(self.accent_color)
                    c.drawString(175, 750, f"Messages written by {friend_data['friend_name']}")
                    y_position = 720

                    for message in friend_data['messages_by']:
                        if y_position < 150:
                            c.showPage()
                            if self.dark_mode:
                                c.setFillColor(self.bg_color)
                                c.rect(0, 0, width, height, fill=1)
                            y_position = 750
                        y_position = self.add_message_block(c, message, y_position)
                        progressBar.update(1)
                        self.progress += 1
                        if self.progress_callback:
                            self.progress_callback(self.progress)

                # Messages written for the friend
                if friend_data['messages_for']:
                    c.showPage()
                    if self.dark_mode:
                        c.setFillColor(self.bg_color)
                        c.rect(0, 0, width, height, fill=1)
                    c.setFont("Helvetica-Bold", 16)
                    c.setFillColor(self.accent_color)
                    c.drawString(175, 750, f"Messages written for {friend_data['friend_name']}")
                    y_position = 720

                    for message in friend_data['messages_for']:
                        if y_position < 150:
                            c.showPage()
                            if self.dark_mode:
                                c.setFillColor(self.bg_color)
                                c.rect(0, 0, width, height, fill=1)
                            y_position = 750
                        y_position = self.add_message_block(c, message, y_position)
                        progressBar.update(1)
                        self.progress += 1
                        if self.progress_callback:
                            self.progress_callback(self.progress)

        c.save()

if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        print("Usage: python generateYearBook.py <username> <password> [wfriends] [dark]")
        print("Options:")
        print("  wfriends  - Include friends' messages")
        print("  dark      - Use dark mode color scheme")
        sys.exit(1)

    param1 = sys.argv[1]
    param2 = sys.argv[2]
    include_friends = 'wfriends' in sys.argv
    dark_mode = 'dark' in sys.argv
    
    yb = YearBook(param1, param2, include_friends, dark_mode)
    yb.generate_pdf("yearbook.pdf")
