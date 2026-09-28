import random
import datetime
import sys
import os
import json

# Ensure console output supports Unicode characters (like ₹) on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# File used for permanent storage
ACCOUNTS_FILE = "accounts.json"


def load_accounts():
    """Loads accounts from accounts.json if the file exists."""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not read {ACCOUNTS_FILE} ({e}). Starting with empty accounts.")
            return {}
    return {}


def save_accounts():
    """Saves the current accounts dictionary permanently to accounts.json."""
    try:
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4)
    except Exception as e:
        print(f"Error saving to {ACCOUNTS_FILE}: {e}")


# Load accounts from accounts.json at startup
accounts = load_accounts()

# Tracks the currently logged-in user (None if no user is logged in)
current_user = None


def generate_account_number():
    """Generates a unique 6-digit account number."""
    while True:
        acc_num = str(random.randint(100000, 999999))
        if acc_num not in accounts:
            return acc_num


def create_account():
    print("\n--- Create Account ---")
    while True:
        name = input("Enter your name: ").strip()
        if name:
            break
        print("Invalid name! Name cannot be empty. Please try again.")

    # Validate phone number (must be 10 numeric digits)
    while True:
        phone = input("Enter your phone number: ").strip()
        if len(phone) == 10 and phone.isdigit():
            break
        print("Invalid phone number! Please enter a valid 10-digit numeric phone number.")

    # Ensure the user enters a valid 4-digit PIN
    while True:
        pin = input("Create a 4-digit PIN: ").strip()
        if len(pin) == 4 and pin.isdigit():
            break
        print("Invalid PIN! The PIN must be exactly 4 digits. Please try again.")

    # Generate a unique 6-digit account number
    account_number = generate_account_number()

    # Create account dictionary
    new_account = {
        "name": name,
        "phone": phone,
        "pin": pin,
        "account_number": account_number,
        "balance": 0,
        "transaction_history": []
    }

    # Store the account in the accounts dictionary
    accounts[account_number] = new_account

    # Save immediately to accounts.json
    save_accounts()

    # Display confirmation and details to user
    print("\n Account Created Successfully!")
    print("========================================")
    print(f"Account Holder : {name}")
    print(f"Account Number : {account_number}")
    print(f"Current Balance: ₹{new_account['balance']}")
    print("========================================")
    print(" Please remember your Account Number and PIN! You will need them to log in.\n")


def check_balance(user):
    """Displays the current balance of the logged-in user."""
    print("\n--- Check Balance ---")
    print(f"Current Balance: ₹{user['balance']}\n")


def deposit(user):
    """Deposits money into the logged-in user's account and logs the transaction."""
    print("\n--- Deposit Money ---")
    try:
        amount_input = input("Enter deposit amount: ").strip()
        amount = float(amount_input)

        # Amount must be strictly greater than 0
        if amount <= 0:
            print("\nError: Deposit amount must be greater than 0.\n")
            return

        # Keep as int if it's a whole number for clean display
        if amount.is_integer():
            amount = int(amount)

        # Update balance
        user["balance"] += amount

        # Record transaction with type, amount, date, time, and description
        now = datetime.datetime.now()
        transaction = {
            "transaction_type": "Deposit",
            "amount": amount,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "description": f"Deposit of ₹{amount}"
        }
        user["transaction_history"].append(transaction)

        # Save the updated balance and transaction to accounts.json
        save_accounts()

        # Display success message and updated balance
        print("\nDeposit successful!")
        print(f"Current Balance: ₹{user['balance']}\n")

    except ValueError:
        print("\nError: Invalid amount! Please enter a valid numerical value.\n")


def withdraw(user):
    """Withdraws money from the logged-in user's account if balance is sufficient."""
    print("\n--- Withdraw ---")
    
    # 1. Read the current balance directly from the logged-in account data
    current_balance = user["balance"]
    print(f"Current Balance: ₹{current_balance}")

    try:
        # 2. Read and convert the entered withdrawal amount to numeric type
        amount_input = input("Enter withdrawal amount: ").strip()
        withdrawal_amount = float(amount_input)

        # Make sure the amount is greater than 0
        if withdrawal_amount <= 0:
            print("\nError: Withdrawal amount must be greater than 0.\n")
            return

        # Keep as int if it's a whole number for clean display
        if withdrawal_amount.is_integer():
            withdrawal_amount = int(withdrawal_amount)

        # Check if the withdrawal amount is greater than the available balance
        if withdrawal_amount > current_balance:
            print("\nInsufficient balance!\n")
            return

        # 3. Calculate remaining balance: remaining_balance = current_balance - withdrawal_amount
        remaining_balance = current_balance - withdrawal_amount

        # 4. Update ONLY the logged-in user's balance
        user["balance"] = remaining_balance

        # Add a Withdrawal transaction to the user's transaction history
        now = datetime.datetime.now()
        transaction = {
            "type": "Withdrawal",
            "transaction_type": "Withdrawal",
            "amount": withdrawal_amount,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "description": f"Withdrawal of ₹{withdrawal_amount}"
        }
        user["transaction_history"].append(transaction)

        # 5. Save the updated account data correctly to accounts.json
        save_accounts()

        # 6. Display the actual updated balance from the account data after saving
        print("\nWithdrawal successful!")
        print(f"Withdrawn Amount: ₹{withdrawal_amount}")
        print(f"Remaining Balance: ₹{user['balance']}\n")

    except ValueError:
        print("\nError: Invalid amount! Please enter a valid numerical value.\n")


def transfer(user):
    """Transfers money from the logged-in user to another account."""
    print("\n--- Transfer Money ---")
    receiver_account = input("Enter receiver account number: ").strip()

    # Check whether the receiver account exists in accounts.json
    if receiver_account not in accounts:
        print("\nReceiver account not found!\n")
        return

    # Check if sender tries to transfer to their own account
    if receiver_account == user["account_number"]:
        print("\nYou cannot transfer money to your own account!\n")
        return

    receiver = accounts[receiver_account]

    try:
        amount_input = input("Enter transfer amount: ").strip()
        amount = float(amount_input)

        # Make sure the amount is greater than 0
        if amount <= 0:
            print("\nEnter a valid transfer amount!\n")
            return

        # Keep as int if it's a whole number for clean display
        if amount.is_integer():
            amount = int(amount)

        # Check if the transfer amount is greater than the sender's balance
        if amount > user["balance"]:
            print("\nInsufficient balance!\n")
            return

        # Deduct from sender and add to receiver
        user["balance"] -= amount
        receiver["balance"] += amount

        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # Add transaction to sender's transaction history
        sender_tx = {
            "type": "Transfer",
            "amount": amount,
            "date": date_str,
            "time": time_str,
            "description": f"Transferred to Account {receiver_account}"
        }
        user["transaction_history"].append(sender_tx)

        # Add transaction to receiver's transaction history
        receiver_tx = {
            "type": "Transfer Received",
            "amount": amount,
            "date": date_str,
            "time": time_str,
            "description": f"Received from Account {user['account_number']}"
        }
        receiver["transaction_history"].append(receiver_tx)

        # Save both updated accounts to accounts.json
        save_accounts()

        # Display success message with transferred amount, receiver account number, and remaining balance
        print("\nTransfer successful!")
        print(f"Transferred Amount: ₹{amount}")
        print(f"Receiver Account: {receiver_account}")
        print(f"Remaining Balance: ₹{user['balance']}\n")

    except ValueError:
        print("\nEnter a valid transfer amount!\n")


def view_transaction_history(user):
    """Displays all transactions for the logged-in user."""
    print("\n--- Transaction History ---\n")
    history = user.get("transaction_history", [])

    if not history:
        print("No transactions found.\n")
        return

    for idx, tx in enumerate(history, 1):
        tx_type = tx.get("transaction_type") or tx.get("type", "Transaction")
        amount = tx.get("amount", 0)

        date = tx.get("date")
        time = tx.get("time")
        if not date or not time:
            dt = tx.get("date_time", "")
            if " " in dt:
                date, time = dt.split(" ", 1)
            else:
                date = dt or "N/A"
                time = "N/A"

        description = tx.get("description", f"{tx_type} of ₹{amount}")

        print(f"{idx}. {tx_type}")
        print(f"   Amount: ₹{amount}")
        print(f"   Date: {date}")
        print(f"   Time: {time}")
        print(f"   Description: {description}\n")


def change_pin(user):
    """Allows the logged-in user to change their 4-digit PIN."""
    print("\n--- Change PIN ---")
    current_pin = input("Enter current PIN: ").strip()

    # Check whether the current PIN matches
    if current_pin != user["pin"]:
        print("\nIncorrect current PIN.\n")
        return

    new_pin = input("Enter new PIN: ").strip()

    # Check whether the new PIN is exactly 4 digits
    if len(new_pin) != 4 or not new_pin.isdigit():
        print("\nPIN must be exactly 4 digits.\n")
        return

    confirm_pin = input("Confirm new PIN: ").strip()

    # Check whether the new PIN and confirmation match
    if confirm_pin != new_pin:
        print("\nPINs do not match.\n")
        return

    # Update PIN and save to accounts.json
    user["pin"] = new_pin
    save_accounts()

    print("\nPIN changed successfully!\n")


def account_menu(user):
    """Displays the Account Menu for a logged-in user."""
    print("========================================")
    print(f"      Account Menu - {user['name']}     ")
    print(f"      Account Number: {user['account_number']} ")
    print("========================================")

    while True:
        print("\nAccount Menu:")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Transaction History")
        print("6. Change PIN")
        print("7. Logout")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            check_balance(user)
        elif choice == "2":
            deposit(user)
        elif choice == "3":
            withdraw(user)
        elif choice == "4":
            transfer(user)
        elif choice == "5":
            view_transaction_history(user)
        elif choice == "6":
            change_pin(user)
        elif choice == "7":
            print("\nLogged out successfully!\n")
            break
        else:
            print("\nInvalid choice! Please select a valid option (1-7).")


def login():
    """Handles user login and opens the account menu upon success."""
    global current_user
    print("\n--- Login ---")

    while True:
        account_number = input("Enter Account Number: ").strip()
        pin = input("Enter PIN: ").strip()

        # Step 1: Check whether the Account Number exists
        if not account_number or account_number not in accounts:
            print("\nError: Account Number does not exist! Please check your account number or create an account first.")
        # Step 2: Check whether the entered PIN matches
        elif accounts[account_number]["pin"] != pin:
            print("\nError: Incorrect PIN! Access denied.")
        else:
            # Step 3: Login successful
            current_user = accounts[account_number]
            print("\nLogin Successful!")
            print(f"Welcome, {current_user['name']}!\n")

            # Open Account Menu
            account_menu(current_user)

            # When user logs out of Account Menu, clear current_user session
            current_user = None
            return

        # Offer another login attempt or return to main menu
        retry = input("\nWould you like to try logging in again? (y/n): ").strip().lower()
        if retry != "y":
            print("Returning to Main Menu...\n")
            return


def main():
    print("========================================")
    print("   Welcome to the Banking System!       ")
    print("========================================")

    while True:
        print("Main Menu:")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            login()
        elif choice == "3":
            print("\nThank you for using the Banking System. Goodbye!")
            break
        else:
            print("\nInvalid choice! Please select a valid option (1, 2, or 3).\n")


if __name__ == "__main__":
    main()
