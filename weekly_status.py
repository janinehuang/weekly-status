from datetime import datetime
from email.message import EmailMessage
import argparse
import smtplib
import subprocess
import time
import os
from config import *


def get_previous_week_number():
    current_date = datetime.now() # Default assumption is to generate the previous week's status
    week_number = current_date.isocalendar()[1]
    if week_number == 1:
        return 52
    return week_number - 1

def start_ollama_instance():
    subprocess.run(["ollama", "pull", "llama3:latest"], check=True)
    process = subprocess.Popen(["ollama", "run", "llama3:latest"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    return process

def send_prompt(prompt):
    # Send a prompt to the running Ollama instance
    result = subprocess.run(
        ["ollama", "run", "llama3:latest", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode()


def find_markdown_file_path(base_path, folder_prefix, previous_week, file_type):
    # Find target folder inside Obsidian directory
    target_folder = ''
    for item in os.listdir(base_path):
        # Check if the item is a directory and starts with "0." (working notes directory)
        if os.path.isdir(os.path.join(base_path, item)) and item.startswith(folder_prefix):
            target_folder = os.path.join(base_path, item)
            print("target_folder is:", target_folder)
    
    if not target_folder:
        print("No target folder found.")
        return None

    # List items in the target folder
    for item in os.listdir(target_folder):
        # Look for file. Example: "2024 - WK 41.md"
        if item.endswith(previous_week + file_type):
            markdown_file_path = os.path.join(target_folder, item)
            print("Found markdown file:", item)
            if os.path.isfile(markdown_file_path):
                return os.path.join(target_folder, item)  # Return the full path to the file
            else:
                print("File does not exist:", item)
            return None
    
    print("No markdown file found for week:", previous_week)
    return None

def read_markdown_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_prompt(active_projects_str, markdown_contents):
    return f"""You are a senior software engineer creating a short weekly status report for your manager.

    CONTEXT:
    - Projects: {active_projects_str}
    - DM is not the same as DOM
    - Goal: Persuade your manager you deserve a promotion
    - Style: Professional, concise, achievement-focused

    TASK:
    Analyze the following weekly notes and create a status update with:
    - 1-3 bullet points per project maximum
    - Focus on the most significant completed work, progress, and achievements
    - Use action verbs and quantifiable results when possible
    - Keep each bullet point under 2 lines
    - Maintain professional tone
    - Keep in mind the context notes are full of unorganized notes, so you need to extract only the most important information.

    NOTES TO ANALYZE:
    {markdown_contents}

    FORMAT YOUR RESPONSE AS:
    DOM:
    - [achievement/progress point]

    MRO:  
    - [achievement/progress point]

    M20 OCS:
    - [achievement/progress point]

    DM:
    - [achievement/progress point]

    Other Projects and Activities:
    - [achievement/progress point]

    Focus on what was accomplished, not what was planned, troubleshooting notes, or in progress tasks.
    If there are no significant accomplishments for a project, skip that section.
    Do not add any other text to the response not in the format above."""

def get_cache_filename(week_str):
    """Generate cache filename for a given week"""
    return f"week_{week_str}_cached_response.txt"

def save_to_cache(week_str, response):
    """Save response to cache file"""
    cache_file = get_cache_filename(week_str)
    with open(cache_file, 'w') as f:
        f.write(response)
    print(f"Response saved to cache: {cache_file}")

def load_from_cache(week_str):
    """Load response from cache file if it exists"""
    cache_file = get_cache_filename(week_str)
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read()
    return None

def show_email_preview(sender_email, recipient, week_str, response):
    print("\n" + "="*60)
    print("EMAIL PREVIEW")
    print("="*60)
    print(f"From: {sender_email}")
    print(f"To: {recipient}")
    print(f"Cc: {sender_email}")
    print(f"Subject: {NAME} Week {week_str} Status")
    print("-"*60)
    print(response)
    print("="*60)

def send_email(recipient, week, status):
    msg = EmailMessage()
    msg.set_content(status)

    # Get sender email from environment variable, fallback to default
    sender_email = os.getenv('EMAIL_SENDER', DEFAULT_SENDER)
    
    msg['Subject'] = f"{NAME} Week {week} Status"
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Cc'] = sender_email

    try:
        # Create SMTP session with TLS
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()  # Enable TLS encryption
        
        # Get email credentials from environment variables
        email_password = os.getenv('EMAIL_PASSWORD')
        if not email_password:
            print("Error: EMAIL_PASSWORD environment variable not set")
            print("Please set your email password: export EMAIL_PASSWORD='your_password'")
            return False
        
        # Login to the server
        s.login(sender_email, email_password)
        
        # Send the email
        s.send_message(msg)
        s.quit()
        print(f"Email sent successfully to {recipient}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Error: Authentication failed. Please check your email and password.")
        return False
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a status update for a specific week.')
    parser.add_argument('--week', type=int, help='The week number to generate a status update for (ISO week number).')
    parser.add_argument('--email', nargs='?', const='default', metavar='EMAIL', help="Send an email. If no email address provided, uses default recipient.")

    args = parser.parse_args()
    
    # Determine the previous week if no week number is provided
    if args.week:
        week_str = str(args.week)
    else:
        week_str = str(get_previous_week_number())
    

    active_projects_str = ACTIVE_PROJECTS
    recipient = ""

    print("generating weekly report for week", week_str)
    instance_process = start_ollama_instance()
    markdown_file_path = find_markdown_file_path(OBSIDIAN_DIR, FOLDER_PREFIX, week_str, FILE_TYPE)

    print("markdown file path located at:", markdown_file_path)

    if markdown_file_path:
        # Check for cached response first
        cached_response = load_from_cache(week_str)
        
        if cached_response and args.email:
            print(f"\nFound cached response for week {week_str}")
            print("-"*60)
            print("CACHED RESPONSE:")
            print("-"*60)
            print(cached_response)
            print("-"*60)
            
            use_cached = input("\nDo you want to use this cached response? (y/n): ").lower().strip()
            if use_cached in ['y', 'yes']:
                response = cached_response
            else:
                # Generate new response
                markdown_contents = read_markdown_file(markdown_file_path)
                prompt = create_prompt(active_projects_str, markdown_contents)
                response = send_prompt(prompt)
                response = response + DISCLAIMER
        else:
            # Generate new response
            markdown_contents = read_markdown_file(markdown_file_path)
            prompt = create_prompt(active_projects_str, markdown_contents)
            response = send_prompt(prompt)
            response = response + DISCLAIMER

        # Get sender email for potential use
        sender_email = os.getenv('EMAIL_SENDER', DEFAULT_SENDER)
        
        if args.email:
            # Set recipient based on whether an email address was provided
            if args.email == 'default':
                recipient = DEFAULT_RECIPIENT
            else:
                recipient = args.email
            
            # Preview the email content
            show_email_preview(sender_email, recipient, week_str, response)
            
            # Ask for confirmation
            email_sent = False
            email_cancelled = False
            while True:
                confirm = input(f"\nDo you want to send this email to {recipient}? (y/n): ").lower().strip()
                if confirm in ['y', 'yes']:
                    email_sent = send_email(recipient, week_str, response)
                    if not email_sent:
                        print("Failed to send email. Check the error messages above.")
                    break
                elif confirm in ['n', 'no']:
                    print("Email cancelled.")
                    save_to_cache(week_str, response)
                    edit_choice = input("Would you like to suggest edits to regenerate the response? (y/n): ").lower().strip()
                    if edit_choice in ['y', 'yes']:
                        print("\nPlease provide your suggested edits or feedback:")
                        print("(e.g., 'Add more details about DOM project', 'Make it more concise', 'Focus on achievements')")
                        user_edits = input("Your suggestions: ").strip()
                        if user_edits:
                            # Add user feedback to the prompt and regenerate
                            prompt += f"\n\nUSER FEEDBACK:\n{user_edits}"
                            
                            print("\nRegenerating response with your suggestions...")
                            response = send_prompt(prompt)
                            response = response + DISCLAIMER
                            
                            # Show updated content
                            print("\n" + "-"*60)
                            print("UPDATED CONTENT:")
                            print("-"*60)
                            print(response)
                            print("-"*60)
                            
                            # Ask for confirmation again
                            while True:
                                confirm = input(f"\nDo you want to send this updated email to {recipient}? (y/n): ").lower().strip()
                                if confirm in ['y', 'yes']:
                                    email_sent = send_email(recipient, week_str, response)
                                    if not email_sent:
                                        print("Failed to send email. Check the error messages above.")
                                    break
                                elif confirm in ['n', 'no']:
                                    print("Email cancelled.")
                                    save_to_cache(week_str, response)
                                    email_cancelled = True
                                    break
                                else:
                                    print("Please enter 'y' or 'n'.")
                            break
                        else:
                            print("No edits provided. Email cancelled.")
                            save_to_cache(week_str, response)
                            email_cancelled = True
                            break
                    else:
                        print("Email cancelled.")
                        save_to_cache(week_str, response)
                        email_cancelled = True
                        break
                else:
                    print("Please enter 'y' or 'n'.")
        
        # Only print response if email was not sent and not cancelled (so user can still see it if they didn't use --email flag)
        if not args.email or (not email_sent and not email_cancelled):
            print("Response:", response)
            
    else:
        print("Invalid file path, no prompt submitted.")

    instance_process.terminate()