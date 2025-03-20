import db
import os
from app import app

console_commands = {
    "toggle-admin": 1,
    "ta": 1,
    "remove-user": 2,
    "ru": 2,
    "backup-database": 3,
    "bd": 3,
    "list-users": 4,
    "lu": 4
}

parameters = {
    "toggle-admin": "username",
    "ta": "username",
    "remove-user": "username",
    "ru": "username",
    "backup-database": "date/filename",
    "bd": "date/filename",
    "list-users": "amount",
    "lu": "amount"
}

def list_users(action):
    users = db.query("SELECT username, userID, isAdmin FROM users LIMIT ?", [action[1]])
    print("Found users:")
    for i in users:
        print(" -" + i["username"])

def toggle_admin(action):
    user = db.query("SELECT userID, isAdmin FROM users WHERE username = ?", [action[1]])
    if user:
        print("Toggle admin at: " + action[1] + " with userID: " + str(user[0]["userID"]) + ". isAdmin: " + str(user[0]["isAdmin"]) + ". Please confirm > 'YES'")
        choice = input(" > ")
        if choice == "YES":
            status = 1 if user[0]["isAdmin"] == 0 else 0
            db.execute("UPDATE users SET isAdmin = ? WHERE userID = ? AND username = ?", [status, str(user[0]["userID"]), action[1]])
            print("Admin status changed.")
            print()
        else:
            print("Admin toggle aborted.")
            print()
    else:
        print("Error: No such user " + action[1])
        print()

def remove_user(action):
    user = db.query("SELECT userID, isAdmin FROM users WHERE username = ?", [action[1]])
    if user:
        print("Remove user " + action[1] + " with userID: " + str(user[0]["userID"]) + ". Please confirm > 'YES'")
        choice = input(" > ")
        if choice == "YES":
            db.execute("DELETE FROM users WHERE userID = ? AND username = ?", [str(user[0]["userID"]), action[1]])
            print("User removed")
            print()
        else:
            print("User removal aborted.")
            print()
    else:
        print("Error: No such user " + action[1])
        print()

def backup_database(action):
    print("Backup database as " + action[1] + ". Please confirm > 'YES'")
    choice = input(" > ")
    if choice == "YES":
        db.db_backup(action[1])
        print("Database backup successful.")
        print()
    else:
        print("Database backup aborted.")
        print()


with app.app_context():
    while True:
        action = input("Enter command > ").split(" ")
        if len(action) > 1 and action[0] in console_commands:
            match console_commands[action[0]]:
                case 1:
                    toggle_admin(action)
                case 2:
                    remove_user(action)
                case 3:
                    backup_database(action)
                case 4:
                    list_users(action)
        else:
            print("Invalid console command. Remember to add parameters. Valid commands: ")
            for i in console_commands:
                print(" - " + i + " + Parameters: " + parameters[i])
            
