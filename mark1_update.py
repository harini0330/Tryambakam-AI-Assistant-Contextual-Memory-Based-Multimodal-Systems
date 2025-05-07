# Import the intelligence experts system
import intelligence_experts

def print_chat_commands():
    print("\nAvailable commands:")
    print("1. new <title> - Create new chat")
    print("2. switch <chat_id> - Switch to existing chat")
    print("3. upload <file_path> - Upload a file to current chat")
    print("4. list - Show all available chat pages")
    print("5. back - Return to main menu")
    print("6. exit - Exit the program")
    print("7. vision - Activate webcam vision analysis")
    print("8. image upload - Analyze an uploaded image")
    print("9. experts - Access Intelligence Experts")

def chat_interface():
    # ... existing code ...
    
    while True:
        # ... existing code ...
        
        elif user_input.lower() == 'experts':
            # Call the experts system
            if intelligence_experts.start_experts_system(client):
                return True
            print_chat_commands()
            
        # ... rest of the existing code ...

def main_interface():
    while True:
        print("\nWelcome to Tryambakam. Intelligence System")
        print("1. Overall Intelligence (Memory Lanes)")
        print("2. General Intelligence (Chat Pages)")
        print("3. Intelligence Experts")
        print("4. Exit")
        
        choice = input("\nPlease select an option (1-4): ").strip()
        
        if choice == "1":
            if overall_interface():
                break
        elif choice == "2":
            print("\nSwitching to General Intelligence")
            if chat_interface():
                break
        elif choice == "3":
            print("\nSwitching to Intelligence Experts")
            if intelligence_experts.start_experts_system(client):
                break
        elif choice == "4":
            print("\nTryambakam.: Shutting down, sir. Have a good day.")
            break
        else:
            print("Invalid option. Please try again.") 