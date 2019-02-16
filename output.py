class Output():
    #def __init__(self):

    class Errors():
        error_key = {'badinput': 'Invalid input provided.',
                    'badargs': 'Invalid number of arguments.',
                    'badkey': 'No Error Message Found Matching the Key: ',
                    'badform': 'Incorrect command format.',
                    'nofile': 'File Not Found.',
                    'errfile': 'There has been an error handling your input file.',
                    'errofile': 'An Error Occured when writing to the file',
                    'filename': 'The filename provided is incorrect.',
                    'generr': 'An Error Has Occured.'}
        def print_error(self, key):
            if key in self.error_key:
                return self.error_key[key]
            outmsg = self.error_key['badkey'] + key
            return outmsg


    class Prompts():
        prompt_key = {'cmd': 'Command: ',
                     'parse': '********** Parsing the Data',
                     'extract': '********** Extracting the requested elements',
                     'help': "For usage information, type 'frontend.py --help'"}
        def print_prompt(self, key):
            if key in self.prompt_key:
                return self.prompt_key[key]
            outmsg = self.prompt_key['badkey'] + key
            return outmsg


    class TextBlock():
        text_key = {'intro': 'Welcome to the thing.',
                   'menu': '\nOptions: \n\t1. Simple Extraction\n\t2. Extract by Element\n\t3. Pull from Dataframe\n\t4. View Help\n\t5. Exit',
                   'badkey': 'No Text Block Found Matching the Key: ',
                   'bye': 'Thanks for using the tool!\n'}
        def print_text(self, key):
            if key in self.text_key:
                return self.text_key[key]
            outmsg = self.text_key['badkey'] + key
            return outmsg


    class ToolUsage():
        def display_usage(self, cmd):
            if cmd == '--help':
                self.print_description(cmd)
                #iterate over the other options to display them all..
                return
            self.print_description(cmd)
            self.print_usage(cmd)
            self.print_options(cmd)

        def print_description(self, cmd):
            if cmd == '--help':
                print("Description: ")
                print("    This tool is a collection of scripts designed to simplify the process of formatting and analyzing json data exported from the Zendesk platform.")
                print("    If this program is run without any arguments, on-screen instructions will be provided for navigating to the desired functions.")
                print("    Advanced commands for more quickly navigating the tool are listed below.")
            if cmd == '--element' or cmd == '-e':
                print("Summary: ")
                print("    This script takes either a CSV file or Zendesk's ticket logs as input and parses it into a succinct record")
                print("    User specified exclusion rules are used and output to a CSV and dataframe.")
            if cmd == '--simple' or cmd == '-s':
                print("Summary: ")
                print("    This script takes Zendesk's ticket logs as input, parses them into a record, and removes unnecessary fields.")
                print("    The output is formatted to CSV for use in language processing classification models.")
                print("    Additionally, the CSV output can be used in the other options (Extract by Element and Pull from Dataframe).")
            if cmd == '--pull' or cmd == '-p':
                print("Summary: ")
                print("    This script takes a formatted CSV or Dataframe as input and allows for the extraction of data.")
                print("    The output is formatted to CSV for use in data reporting")

        def print_usage(self, cmd):
            if cmd == '--element' or cmd == '-e':
                print("\nUsage: ")
                print("    --option <input-file.csv> [comma,separated,params] [<output-file.csv>]")
            if cmd == '--simple' or cmd == '-s':
                print("\nUsage: ")
                print("    --option <input-file.json> [<output-file.csv>]")
            if cmd == '--pull' or cmd == '-p':
                print("\nUsage: ")
                print("    --option <input-file.csv> [<output-file.csv>]")

        def print_options(self, cmd):
            if cmd == '--element' or cmd == '-e':
                print("\nOptions: ")
                print("    --tags, -t \t\t Pull only tickets with the matching tag(s)")
                print("    --score, -s \t\t Pull only tickets with the matching score (good, bad, offered, unoffered)")
                print("    --range, -r \t\t Pull only tickets within a range of dates [yyyy-mm-dd,yyyy-mm-dd]")
                print("    --form, -f \t\t Pull only tickets with the matching form name")
                print("    --brand, -b \t\t Pull only tickets with the matching brand name")
            if cmd == '--simple' or cmd == '-s':
                print("\nOptions: ")
                print("    --trim, -t \t\t Parse and trim the input file")
            if cmd == '--pull' or cmd == '-p':
                print("\nOptions: ")
                print("    --tags, -t \t\t Extract only ticket tags")
                print("    --user, -u \t\t Extract only user information")
                print("    --email, -e \t\t Extract only email information")
                print("    --comt, -c \t\t Extract only comment information")
