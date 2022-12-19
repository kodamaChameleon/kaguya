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

        return self.read_env()

    # Edit environmental variables
    def update_env(self, key = None):
        
        # If no key specified, default option
        if key == None:
            keys = list(self.env.keys()) + ['Cancel']

            # Display options
            print(
                "="*23 + "[UPDATE ENVIRONMENT]" + "="*23,
                "\nChoose from the following options:",
                *[str(n+1) + ") " + keys[n] for n in range(len(keys))],
                "\nChoose from the following options:",
                sep = "\n"
            )

            # Select from the menu
            while True:
                try:
                    choice = int(input("\nSelect an option to continue: "))
                    if keys[choice - 1]:
                        key = keys[choice - 1]
                        break
                except:
                    print("\nNot a valid option.")

        if key in self.env:

            # Temporary placeholder for previous value
            oldValue = self.env[key]

            # Create default environment variables
            defaults = {
                'STIG Repository Path': 'exports',
            }

            # Set new value
            print("\n'" + str(key) + "' current value = " + str(self.env[key]))
            if key in defaults:
                newValue = input("Set new value for '" + str(key) + "' (leave empty for default value '" + defaults[key] + "'); ")
                if newValue == '':
                    self.env[key] = defaults[key]
                else:
                    self.env[key] = newValue
            else:
                self.env[key] = input("Set new value for '" + str(key) + "'; ")
            self.write_env(self.env)
            print("\n'" + str(key) + "' set to value '" + str(self.env[key]) + "'")

        else:
            print("\nCancelled.")