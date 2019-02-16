from enum import Enum
import output as Output
import pandas as pd
import configparser
import time
import json
import sys
import ast
import os
import re

# TODO:
# NOTE FOR LATER: This is how you handle new Zendesk downloaded tickets format: { "tickets": [{},{},{}], next_page, previous_page, count}
# df = pd.read_json(exported_file_name)
# with open(new_file_name, 'a+') as myFile:
#     for tick in df['tickets']:
#         json.dump(tick, myFile)

# TODO: Searcher.filter_scores
# **TODO: Functionality to pass buffer between classes before saving
# **TODO: Documentation!!!
# TODO: Error handling
# TODO: Complete sortby function
# TODO: Flowchart for finding values
class Globals():
    nonspace = re.compile(r'\S')
    progress_mod = 128
    error = Output.Output.Errors()
    config_filename = 'config.ini'

    @staticmethod
    def getTime():
        return int(time.time())

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_filename)

    def update_progress(self, p):
        if p >= self.progress_mod:
            print('.', end='', flush=True)
            p = 0
        return p + 1

    def iterparse(self, j):
        decoder = json.JSONDecoder()
        pos = 0
        while True:
            matched = self.nonspace.search(j, pos)
            if not matched:
                break
            pos = matched.start()
            decoded, pos = decoder.raw_decode(j, pos)
            yield decoded

class ZendeskParser():
    globals = Globals()

    def parse_import(self, fileName):
        tickets_list = []

        with open(fileName) as inFile:
            data = inFile.read()
            tickets_list = list(self.globals.iterparse(data))
        dataframe = pd.DataFrame(tickets_list)
        return dataframe

    #remove key:value pairs from dictioary
    @staticmethod
    def delete_keys(keys, dic):
            newDict = dic.copy()
            for key in keys:
                try:
                    newDict.pop(key)
                except KeyError:
                    print("Key not found")
            return newDict

    #simply removes the fields that we believe won't be useful for our data mining
    def extract_essential(self, src):
        dropped = []
        progress = 0
        print('Removing unwanted columns...')
        #remove unwanted columns
        results = src.drop(ast.literal_eval(self.globals.config['COLUMNS']['Undesired']), axis=1)

        results.reset_index(drop=True, inplace=True)
        N = len(results.index)
        rows = results.iterrows()

        # For each row in the dataframe...
        for index, row in rows:

            # print(f'Row {index}: ', end='', flush=True)
            print(f'Row {index}/{N} ')

            # if row['recipient'] not in ast.literal_eval(self.globals.config['EMAILS']['Desired']):
            #     print(f'{row["recipient"]} is not in {self.globals.config["EMAILS"]["Desired"]}')
            #     results = results.drop(index)
            #     print(f'Dropping Row: {index}')
            #     continue
            # elif 'english' not in row['tags']:
            #     print("English not in this row's tags")
            #     results = results.drop(index)
            #     print(f'Dropping Row: {index}')
            #     continue



            # Remove redundant fields...
            # print('Removing redundant fields from the requester...', end='', flush=True)
            #remove unecessary fields from the requester
            keys = ast.literal_eval(self.globals.config['REQUESTER']['Undesired'])
            results["requester"][index] = self.delete_keys(keys, row['requester'])

            # print('and comments...')
            #trimming redundant fields from the comments
            #for allComments in results['comments']:
            new_comment = []
            for index2, comment in enumerate(row['comments']):
                keys = ast.literal_eval(self.globals.config['COMMENTS']['Undesired']) #remove these keys from the dict
                new_comment.append(self.delete_keys(keys, comment))
            results['comments'][index] = new_comment
            progress = self.globals.update_progress(progress)
        results.reset_index(drop=True, inplace=True)
        # print('\n')

        return results

    #sorts the dataframe by the provided column name
    def sortBy(self, src, param):
        results = src
        return results


    def valid_closed(self, obj):
        print(obj)
        return obj.status is "closed"

    def write_out(self, records, outFile="out.csv"):
        try:
            out = open(outFile, 'w+')
        except:
            print(self.globals.error.print_error('errfile'))
            return 'NONE'

        #write contents to file
        try:
            records.to_csv(outFile, encoding='utf-8', index='false')
        except:
            print(self.globals.error.print_error('errofile'))
            return 2
        #confirm that file writing was successful
        print("Records were successfully written to " + outFile + "!")
        return outFile

    def reset_json(self):
        obj = ast.literal_eval(self.globals.config['COLUMNS']['Desired'])
        return obj


# reads in a CSV or pandas dataframe and returns only the specified data
class ZendeskExtractor():

    globals = Globals()

    @staticmethod
    def categorize_function(func):
        if func == '--tags' or func == '-t':
            return 'TAGS'
        if func == '--user' or func == '-u':
            return 'USER'
        if func == '--email' or func == '-e':
            return 'EMAIL'
        if func == '--comt' or func == '-c':
            return 'COMMENT'

    def generate_construct(self, args):
        n = str(self.globals.getTime())[-6:]
        search_construct = {'function': '',
                            'inFile': '',
                            'outFile': f'out{n}.csv'}

        search_construct['function'] = self.categorize_function(args[0])
        search_construct['inFile'] = args[1]
        if len(args) == 3:
            search_construct['outFile'] = args[2]

        return search_construct

    def filter_data(self, construct):
        # TODO:
        # read the file and convert to pandas dataframe
        dataframe = pd.read_csv(construct['inFile'])
        # iterate over dataframe and delete rows that don't match criteria
        if construct['function'] == 'TAGS':
            dataframe = self.extract_tags(dataframe, construct)
        if construct['function'] == 'USER':
            dataframe = self.extract_user(dataframe, construct)
        if construct['function'] == 'COMMENT':
            dataframe = self.extract_comment(dataframe, construct)
        if construct['function'] == 'EMAIL':
            dataframe = self.extract_email(dataframe, construct)

        return dataframe

    @staticmethod
    def extract_tags(df, cons):
        df = df.loc[:, ['id', 'created_at', 'tags']]
        return df

    @staticmethod
    def extract_user(df, cons):
        df = df.loc[:, ['id', 'created_at', 'requester']]
        return df

    @staticmethod
    def extract_email(df, cons):
        df = df.loc[:, ['id', 'created_at', 'requester']]
        for index,row in enumerate(df.requester):
            row = ast.literal_eval(row)
            df.requester[index] = row['email']
            print(str(index) + ": " + str(row['email']))
        return df

    @staticmethod
    def extract_comment(df, cons):
        df = df.loc[:, ['id', 'created_at', 'description', 'comments']]
        return df

    @staticmethod
    def get_elements(argsList):
        return argsList.strip(',][').split(',')

    def write_out(self, df, cons):
        try:
            out = open(cons['outFile'], 'w+')
        except:
            print(self.globals.error.print_error('errfile'))
            return 1

        #write contents to file
        try:
            df.to_csv(cons['outFile'], encoding='utf-8', index='false')
        except:
            print(self.globals.error.print_error('errofile'))
            print(str(sys.exc_info()[1]))
            return 2
        #confirm that file writing was successful
        print("Records were successfully written to " + cons['outFile'] + "!")
        return cons['outFile']


# TODO:
#   Additional filtering criteria
# reads in a CSV, pandas dataframe, or Zendesk ticket log and returns all tickets which match a criteria
class ZendeskSearcher():

    globals = Globals()

    @staticmethod
    def categorize_function(func):
        if func == '--tags' or func == '-t':
            return 'TAGS'
        if func == '--score' or func == '-s':
            return 'SCORE'
        if func == '--range' or func == '-r':
            return 'RANGE'
        if func == '--form' or func == '-f':
            return 'FORM'
        if func == '--brand' or func == '-b':
            return 'BRAND'

    def filter_data(self, construct):
        print("filtering data")
        # TODO:
        # read the file and convert to pandas dataframe
        print('reading from: ' + construct['file'])
        dataframe = pd.read_csv(construct['file'])
        print('...successfully read!')
        # iterate over dataframe and delete rows that don't match criteria
        if construct['function'] == 'TAGS':
            print("WE MAKE IT THIS FAR")
            dataframe = self.filter_tags(dataframe, construct)
            print("THE TAGAS FILTERED")
        if construct['function'] == 'SCORE':
            dataframe = self.filter_scores(dataframe, construct)
        if construct['function'] == 'RANGE':
            print("Function is range...")
            dataframe = self.filter_range(dataframe, construct)
        if construct['function'] == 'FORM':
            dataframe = self.filter_forms(dataframe, construct)
        if construct['function'] == 'BRAND':
            dataframe = self.filter_brands(dataframe, construct)

        print("RETURNING DF")

        return dataframe

    def generate_construct(self, args):
        n = str(self.globals.getTime())[-6:]
        search_construct = {'function': '',
                            'arguments': [],
                            'file': '',
                            'outFile': f'out{n}.csv'}

        search_construct['function'] = self.categorize_function(args[0])
        search_construct['arguments'] = self.get_elements(args[2])
        if search_construct['function'] == 'FORM' or search_construct['function'] == 'BRAND':
            for index, form in enumerate(search_construct['arguments']):
                search_construct['arguments'][index] = '_'.join([f.capitalize() for f in form.split('_')])
            print(f'Search_Construct arguments are now: {search_construct["arguments"]}')
        search_construct['file'] = args[1]
        if len(args) == 4:
            search_construct['outFile'] = args[3]

        return search_construct

    @staticmethod
    def get_elements(argsList):
        return argsList.strip(',][').split(',')

    @staticmethod
    def filter_tags(df, cons):
        for index,row in df.iterrows():
            tagList = ast.literal_eval(row.tags)
            if not set(cons['arguments']).issubset(tagList):
                print(str(index) + " does not contain: " + str(cons['arguments']))
                df = df.drop(index)
        return df

    @staticmethod
    def filter_scores(df, cons):
        return df

    @staticmethod
    def filter_range(df, cons):
        omit = []
        for index,row in df.iterrows():
            if row['created_at'] < cons['arguments'][0] or row['created_at'] > cons['arguments'][1]:
                omit.append(index)
        df = df.drop(df.index[omit])
        return df

    def filter_forms(self, df, cons):
        # remove any rows that don't match the forms provided by the construct
        form_keys = ast.literal_eval(self.globals.config['FORMS']['form_key'])
        forms = []
        omit = []
        for form_name in form_keys:
            if form_name in cons['arguments']:
                print(f'{form_name} found in {cons["arguments"]}')
                forms.append(form_keys[form_name])

        for index, row in df.iterrows():
            if row['ticket_form_id'] not in forms:
                print('row: {0} not in forms: {1}'.format(row['ticket_form_id'], forms))
                omit.append(index)
                print(index)

        df = df.drop(df.index[omit])
        return df

    def filter_brands(self, df, cons):
        # remove any rows that don't match the given brand
        brand_keys = ast.literal_eval(self.globals.config['BRANDS']['brand_key'])
        brands = []
        omit = []
        for brand_name in brand_keys:
            if brand_name in cons['arguments']:
                print(f'{brand_name} found in {cons["arguments"]}')
                brands.append(brand_keys[brand_name])

        for index, row in df.iterrows():
            if row['brand_id'] not in brands:
                print('row: {0} not in brands: {1}'.format(row['brand_id'], brands))
                omit.append(index)
                print(index)

        df = df.drop(df.index[omit])

        return df

    def write_out(self, df, cons):
        try:
            out = open(cons['outFile'], 'w+')
        except:
            print(self.globals.error.print_error('errfile'))
            return 1

        #write contents to file
        try:
            df.to_csv(cons['outFile'], encoding='utf-8', index='false')
        except:
            print(self.globals.error.print_error('errofile'))
            print(str(sys.exc_info()[1]))
            return 2
        #confirm that file writing was successful
        print("Records were successfully written to " + cons['outFile'] + "!")
        return cons['outFile']










#EOF
