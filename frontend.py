from zendesk_extract import ZendeskExtractor as Extractor
from zendesk_extract import ZendeskParser as Parser
from zendesk_extract import ZendeskSearcher as Searcher
from output import Output as Output
import pandas as pd
import json
import sys
import os

# TODO: Flow backwards through menus (Explore setting up "menu tiers" for future ease; Implement as stack?)
class Frontend():
    parser = Parser()
    extractor = Extractor()
    searcher = Searcher()

    output = Output()
    output.TextBlock = Output.TextBlock()
    output.Prompt = Output.Prompts()
    output.Error = Output.Errors()
    output.ToolUsage = Output.ToolUsage()

    def start(self, cmds):
        # TODO: evaluate commands
        isValid = ['--simple', '-s',
                 '--pull', '-p',
                 '--element', '-e',
                 '--help', '-h']
        if len(cmds) > 0:
            if self.verify_input(cmds[0], isValid):
                print(self.output.TextBlock.print_text('intro'))
                return self.usage(cmds, True)
            else:
                print(self.output.Error.print_error('badinput'))
                print(self.output.Prompt.print_prompt('help'))
                return 1
        else:
            print(self.output.TextBlock.print_text('intro'))
            return self.options()
        return 0

    def cmd_check(self, args, tool, offset=0): #SORT BASED ON TOOL PROVIDED
        print("Checking...\n tool choice is: " + str(tool))
        if len(args) <= 1+offset:
            print(self.output.Error.print_error('badinput'))
            print(self.output.Error.print_error('badargs'))
            return False
        if tool == "--simple" or tool == '-s':
            if args[0+offset] == "-t" or args[0+offset] == "--trim":
                #verify number of arguments
                if len(args) > 3+offset:
                    print(self.output.Error.print_error('badinput'))
                    print(self.output.Error.print_error('badargs'))
                #verify that file exists
                else:
                    try:
                        ft = open(args[1+offset], 'r')
                        ft.close()
                    except FileNotFoundError:
                        print("'" + args[1+offset] + "'" + str(print(self.output.Error.print_error('nofile'))))
                    except:
                        print(self.output.Error.print_error('errfile'))
                    else:
                        print("'" + args[1+offset] + "' has been verified")
                        return True
            return False

        elif tool == "--element" or tool == '-e':
            if (args[0+offset] == '-t' or args[0+offset] == "--tags" or
                args[0+offset] == '-f' or args[0+offset] == "--form" or
                args[0+offset] == '-r' or args[0+offset] == "--range" or
                args[0+offset] == '-s' or args[0+offset] == "--score" or
                args[0+offset] == '-b' or args[0+offset] == "--brand"):
                #verify number of arguments
                if len(args) > 4+offset:
                    print(self.output.Error.print_error('badinput'))
                    print(self.output.Error.print_error('badargs'))
                else:
                    #verify that file name is type CSV
                    if args[1+offset].lower().endswith('.csv'):
                        #verify that the file exists
                        try:
                            ft = open(args[1+offset], 'r')
                            ft.close()
                        except FileNotFoundError:
                            print("'" + args[1+offset] + "'" + str(print(self.output.Error.print_error('nofile'))))
                        except:
                            print(self.output.Error.print_error('errfile'))
                        else:
                            print("'" + args[1+offset] + "' has been verified")

                        #confirm parameter list format...
                        #if first character is: [ and last is: ]
                        if args[2+offset].startswith('[') and args[2+offset].endswith(']'):
                            print("Data contained in brackets.")
                            print(args[2+offset])
                            print("Brackets removed.")
                            print(args[2+offset].strip(',]['))
                            print("Splitting contents.")
                            print(args[2+offset].strip(',][').split(','))
                            return True

                    print(self.output.Error.print_error('filename'))


                    return False
            return False

        elif tool == "--pull" or tool == '-p':
            if (args[0+offset] == '-t' or args[0+offset] == "--tags" or
                args[0+offset] == '-u' or args[0+offset] == "--user" or
                args[0+offset] == '-c' or args[0+offset] == "--comt" or
                args[0+offset] == '-r' or args[0+offset] == "--email"):
                #verify number of arguments
                print("Correct options used for element")
                if len(args) > 3+offset:
                    print(self.output.Error.print_error('badinput'))
                    print(self.output.Error.print_error('badargs'))
                else:
                    #remove all fields except for the requested and date/brand information
                    return True
            return False
        else:
            return False

    # Return dataframe for rendering on page
    def usage(self, cmds=['--simple'], usercmd=False):
        #
        args = cmds # TODO: verify type for new users
        out = ''
        if args[0] == '--simple' or args[0] == '-s':
            self.output.ToolUsage.display_usage(args[0])
            args = self.verify_cmd(usercmd, args)

            print(self.output.Prompt.print_prompt('parse'))
            result = self.parser.parse_import(args[1])
            print(self.output.Prompt.print_prompt('extract'))
            result = self.parser.extract_essential(result)

            if len(args) == 3:
                out = self.parser.write_out(result, args[2])
            else:
                out = self.parser.write_out(result)
            return result, out

        elif args[0] == '--pull' or args[0] == '-p':
            self.output.ToolUsage.display_usage(args[0])
            args = self.verify_cmd(usercmd, args)

            extractorObj = self.extractor.generate_construct(args)
            result = self.extractor.filter_data(extractorObj)

            out = self.extractor.write_out(result, extractorObj)
            return result, out


        elif args[0] == '--element' or args[0] == '-e':
            self.output.ToolUsage.display_usage(args[0])
            args = self.verify_cmd(usercmd, args)

            #split the contents by comma and return in a new object
            searcherObj = self.searcher.generate_construct(args)
            #delete each ticket that doesn't contain list contents
            result = self.searcher.filter_data(searcherObj)

            #VISIT LATER
            out = self.searcher.write_out(result, searcherObj)
            print("Outfile: " + out)
            return result, out

        elif args[0] == '--help' or args[0] == '-h':
            self.output.ToolUsage.display_usage(args[0])

        else:
            print(self.output.Error.print_error('generr'))
        return 0


    def options(self):
        #
        isValid = ['1', '2', '3', '4']
        data = ''
        while True:
            print(self.output.TextBlock.print_text('menu'))
            data = input(self.output.Prompt.print_prompt('cmd'))
            if self.verify_input(data, isValid):
                break
            print(self.output.Error.print_error('badinput'))
        return self.option_selector(data)

    def option_selector(self, data):
        if data == '1':
            return self.simple_extract()
            #return 1
        elif data == '2':
            return self.elem_extract()
            #return 2
        elif data == '3':
            return self.data_extract()
            #return 3
        elif data == '4':
            self.output.ToolUsage.display_usage('--help')
            return 4
        else:
            self.exit(self.output.TextBlock.print_text('bye'))
            return 5

    def simple_extract(self):
        return self.usage()
        #return 1

    def elem_extract(self):
        return self.usage(['--element'])
        #return 2

    def data_extract(self):
        return self.usage(['--pull'])
        #return 3

# TODO: commandCheck (cmd_check) not working properly
#       currently, it takes the wrong argument (option instead of tool)
#       off by 1? or bad data?
    def verify_cmd(self, usercmd, args):
        print("Verifying Command")
        print(usercmd)
        tool = args[0]
        if usercmd:
            #args.pop(0)
            print(args)
            if not self.cmd_check(args, tool, 1):
                usercmd = False
                print(self.output.Error.print_error('badinput'))
            else:
                args.pop(0)

        while not usercmd:
            selection = input(self.output.Prompt.print_prompt('cmd'))
            args = selection.split()

            if self.cmd_check(args, tool, 0):
                break
            else:
                print(self.output.Error.print_error('badinput'))

        return args

    def verify_input(self, data, valid):
        return data in valid

    def exit(self, msg):
        print(msg)
        return 0
