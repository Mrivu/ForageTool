import db
from app import app

console_commands = {
    "grant-admin": 1,
    "ga": 1
}

parameters = {
    "grant-admin": "username",
    "ga": "username"
}

with app.app_context():
    while True:
        action = input("Enter command > ").split(" ")
        if len(action) > 1:
            if action[0] in console_commands:
                match console_commands[action[0]]:
                    case 1:
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
        else: 
            print("Invalid console command. Remember to add parameters. Valid commands: ")
            for i in console_commands:
                print(" - " + i + " + Parameters: " + parameters[i])
            
