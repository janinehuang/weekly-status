#!/usr/bin/env python3
"""
Setup script for email configuration
"""
import os
import getpass

def setup_email():
    print("Email Setup for Weekly Status Report")
    print("=" * 40)
    
    # Check if EMAIL_SENDER is already set
    current_sender = os.getenv('EMAIL_SENDER')
    if current_sender:
        print(f"✓ EMAIL_SENDER is currently set to: {current_sender}")
    else:
        print("✗ EMAIL_SENDER is not set")
    
    # Check if EMAIL_PASSWORD is already set
    if os.getenv('EMAIL_PASSWORD'):
        print("✓ EMAIL_PASSWORD environment variable is already set")
    else:
        print("✗ EMAIL_PASSWORD is not set")
    
    choice = input("\nDo you want to update email settings? (y/n): ").lower()
    if choice != 'y':
        print("Setup complete!")
        return
    
    # Get sender email
    if current_sender:
        new_sender = input(f"Enter sender email (current: {current_sender}): ").strip()
        if not new_sender:
            new_sender = current_sender
    else:
        new_sender = input("Enter sender email: ").strip()
    

    password = getpass.getpass("Enter your JPL email password (this will only be saved in your shell profile): ")
    
    if new_sender and password:
        # Add to shell profile
        shell_profile = os.path.expanduser("~/.zshrc")  # If you're using zsh
        
        # Remove existing email configuration lines
        with open(shell_profile, 'r') as f:
            lines = f.readlines()
        
        with open(shell_profile, 'w') as f:
            for line in lines:
                if not line.startswith('# Weekly Status Email Configuration') and not line.startswith('export EMAIL_'):
                    f.write(line)
        
        # Add new configuration
        with open(shell_profile, 'a') as f:
            f.write(f'\n# Weekly Status Email Configuration\nexport EMAIL_SENDER="{new_sender}"\nexport EMAIL_PASSWORD="{password}"\n')
        
        print(f"\n✓ Email configuration added to {shell_profile}")
        print(f"✓ Sender: {new_sender}")
        print("✓ Please restart your terminal or run: source ~/.zshrc")
        print("\nTo test the email functionality, run:")
        print("python weekly_status.py --email")
        print("\nNote: Update your projects in config.py as needed.")
    else:
        print("Missing email or password. Setup cancelled.")

if __name__ == "__main__":
    setup_email()
