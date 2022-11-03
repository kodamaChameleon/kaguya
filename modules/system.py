"""
KAGUYA -- system

Summary
-------

This feature handles the various interactions between
modules such as the main launch menu and other
features to include but not limited to manipulating
the environment file.
"""

# Import dependencies
import json

# Create environment class which stores data about how the application will behave
class environment:

    def __init__(self):
        self.fileName = "data/.env"
        self.env = self.read_env()
    
    # Read environment file, create if does not exist
    def read_env(self):
        try:
            with open(self.fileName, "r") as file:
                env = eval(file.read())
        except:
            env = {}
            self.write_env(env)
        
        return env

    # Write environment file to data directory
    def write_env(self, env):
        with open(self.fileName, 'w') as file:
            json.dump(env, file, indent=4, sort_keys=True)

    # Check for environmental variables, create if it does not exist
    def check_env(self, var_name):
        try:
            while not self.env[var_name]:
                self.env = self.update_env(var_name)
        except:
            self.env[var_name] = None
            self.env = self.update_env(var_name)

    # Edit environmental variables
    def update_env(self, key = None):
        
        # If no key specified, default option
        if key == None:
            keys = list(self.env.keys())

            # Display options
            print(
                "="*23 + "[UPDATE ENVIRONMENT]" + "="*23,
                "\nChoose from the following options:",
                *[str(n+1) + ") " + keys[n] for n in range(len(keys))],
                str(len(keys) + 1) + ") Cancel",
                "\nChoose from the following options:",
                sep = "\n"
            )

            # Select from the menu
            while True:
                try:
                    choice = int(input("\nSelect an option to continue: "))
                    if keys[choice] or choice == len(keys) +1:
                        if choice != len(keys) + 1:
                            key = keys[choice]
                        break
                except:
                    print("\nNot a valid option.")

        if key:
            # Set new value
            print("\n'" + str(key) + "' current value = " + str(self.env[key]))
            self.env[key] = input("Set new value for '" + str(key) + "'; ")
            self.write_env(self.env)
            print("\n'" + str(key) + "' set to value '" + str(self.env[key]) + "'")

        else:
            print("\nCancelled.")