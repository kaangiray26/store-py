#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import httpx
import argparse
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
from prettytable import PrettyTable

class Store:
    def __init__(self):
        self.pretty = False
        self.x = PrettyTable()
        self.x.align = "l"
        with open(os.path.join(os.path.expanduser('~'),'.config/store-py/config.json')) as f:
            self.config = json.load(f)
    
    def handle_args(self, args):        
        # Check for server
        if not self.config["server"]:
            raise Exception("Server not specified!")
        
        # Check for username
        if not self.config["username"]:
            raise Exception("Username not specified!")
        
        # Check for password
        if not self.config["password"]:
            raise Exception("Password not specified!")
        
        if args.pretty:
            self.pretty = True
        
        if args.get:
            self.get_file(args.get)
            return
        
        if args.add:
            self.add_file(args.add)
            return
        
        if args.delete:
            self.delete_file(args.delete)
            return
        
        if args.list:
            self.list_files()
            return
        
        if args.replace:
            self.replace_file(args.replace)
            return
        
        if args.search:
            self.search_file(args.search)
            return
        
    def get_file(self, filename):
        r = httpx.get(f"{self.config['server']}/{filename}")
        
        if r.status_code != 200:
            raise Exception("File not found!")
        
        # Save file
        with open(filename, 'wb') as f:
            f.write(r.content)
        
        print("File saved to: " + filename)
        
    def replace_file(self, args):        
        # Check if file exists
        if not os.path.isfile(args[1]):
            raise Exception("File does not exist!")
        
        # Put file to server
        server = f"{self.config['server']}/replace/{args[0]}"
        files = {'file': open(args[1], 'rb')}
        headers = {'username': self.config['username'], 'password': self.config['password']}
                
        r = httpx.put(server, files=files, headers=headers)
        if r.status_code != 200:
            raise Exception("Error replacing file!")
        
        print(r.json())
        
    def list_files(self):
        server = f"{self.config['server']}/list"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        # Get files from server
        r = httpx.get(server, headers=headers)
        if r.status_code != 200:
            raise Exception("Error listing files!")
        
        # Print files
        data = r.json()
        if not len(data['response']):
            print("No owned files!")
            return
        
        # Print response
        if not self.pretty:
            for object in r.json()['response']:
                print(object)
            return
        
        # Pretty print
        self.x.field_names = ["title", "id", "date", "owner"]
        self.x.add_rows([[object['title'], object['id'], object['date'], object['owner']] for object in data['response']])
        print(self.x)
        
    def delete_file(self, filename):
        # Delete file from server
        server = f"{self.config['server']}/delete/{filename}"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        r = httpx.delete(server, headers=headers)
        if r.status_code != 200:
            raise Exception("Error deleting file!")
        
        print(r.json())
            
    def add_file(self, args):
        # Check if file exists
        if not os.path.isfile(args[0]):
            raise Exception("File does not exist!")
        
        # Set data to send
        data = {}
        if len(args) == 2:
            data['title'] = args[1]
        
        # Put file to server
        server = f"{self.config['server']}/add"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        file_size = os.path.getsize(args[0])
        
        # Upload file with tqdm progress bar
        with open(args[0], 'rb') as f:
            with tqdm(desc=f"Uploading", total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as t:
                wrapper = CallbackIOWrapper(t.update, f, 'read')
                r = httpx.put(server, files={'file': wrapper}, headers=headers, data=data)
                
                # Clear progress bar
                t.close()
                
                if r.status_code != 200:
                    print(r.content)
                    raise Exception("Error adding file!")
                
                # Print response
                if not self.pretty:
                    print(r.json())
                    return
                
                # Pretty print
                self.x.field_names = ["file"]
                self.x.add_row([r.json()['file']])
                print(self.x)
                
    def search_file(self, query):
        server = f"{self.config['server']}/search"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        # Search files from server
        r = httpx.get(server, headers=headers, params={'title': query})
        if r.status_code != 200:
            raise Exception("Error replacing file!")
        
        data = r.json()
        
        # Print results
        if not self.pretty:
            print(data)
            return
        
        # Pretty print
        self.x.field_names = ["title", "id", "date", "owner"]
        self.x.add_rows([[object['title'], object['id'], object['date'], object['owner']] for object in data['response']])
        print(self.x)

if __name__ == "__main__":
    s = Store()
    parser = argparse.ArgumentParser(description='kaangiray26/store-py')
    parser.add_argument('-a', '--add', help='Add file to the store', nargs='+', metavar=('file_path', 'title'))
    parser.add_argument('-d', '--delete', help='Delete file from the store', metavar='file_id')
    parser.add_argument('-l', '--list', help='List files in the store', action='store_true')
    parser.add_argument('-r', '--replace', help='Replace file in the store', nargs=2, metavar=('file_id', 'file_path'))
    parser.add_argument('-g', '--get', help='Get file from the store', metavar='file_id')
    parser.add_argument('-s', '--search', help='Search file from the store', metavar='query')
    parser.add_argument('-p', '--pretty', help='Pretty print json response', action='store_true')
    
    args = parser.parse_args()
    s.handle_args(args)