#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import argparse

class Store:
    def __init__(self):
        # Check for config file
        if not os.path.isfile("config.json"):
            with open("config.json", "w") as f:
                json.dump({}, f, indent=4)
            print("Empty config file created!")
        
        with open("config.json") as f:
            self.config = json.load(f)
    
    def handle_args(self, args):
        # Override config with args
        if args.server:
            self.config["server"] = args.server
        if args.username:
            self.config["username"] = args.username
        if args.password:
            self.config["password"] = args.password
        
        # Check for server
        if not self.config["server"]:
            raise Exception("Server not specified!")
        
        # Check for username
        if not self.config["username"]:
            raise Exception("Username not specified!")
        
        # Check for password
        if not self.config["password"]:
            raise Exception("Password not specified!")
        
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
        
    def get_file(self, filename):
        r = requests.get(f"{self.config['server']}/get/{filename}")
        if r.status_code != 200:
            raise Exception("File not found!")
        
        with open(filename, 'wb') as f:
            f.write(r.content)
        
        print("File saved to: " + filename)
        
    def replace_file(self, args):
        print("Replacing file: " + args[0] + " with " + args[1])
        
        # Check if file exists
        if not os.path.isfile(args[1]):
            raise Exception("File does not exist!")
        
        # Put file to server
        server = f"{self.config['server']}/replace/{args[0]}"
        files = {'file': open(args[1], 'rb')}
        headers = {'username': self.config['username'], 'password': self.config['password']}
                
        r = requests.put(server, files=files, headers=headers)
        print(r.status_code, r.json())
        
    def list_files(self):
        print("Listing files")
        
        # List files from server
        server = f"{self.config['server']}/list"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        r = requests.get(server, headers=headers)
        print(r.status_code, r.json())
        
    def delete_file(self, filename):
        print("Deleting file: "+ filename)
        
        # Delete file from server
        server = f"{self.config['server']}/delete/{filename}"
        headers = {'username': self.config['username'], 'password': self.config['password']}
        
        r = requests.delete(server, headers=headers)
        print(r.status_code, r.json())
            
    def add_file(self, filepath):
        print("Adding file: " + filepath)
        
        # Check if file exists
        if not os.path.isfile(filepath):
            raise Exception("File does not exist!")
        
        # Put file to server
        server = f"{self.config['server']}/add"
        files = {'file': open(filepath, 'rb')}
        headers = {'username': self.config['username'], 'password': self.config['password']}
                
        r = requests.put(server, files=files, headers=headers)
        print(r.status_code, r.json())

if __name__ == "__main__":
    s = Store()
    parser = argparse.ArgumentParser(description='kaangiray26/store-py')
    parser.add_argument('-a', '--add', help='Add file to the store', metavar='file_path')
    parser.add_argument('-d', '--delete', help='Delete file from the store', metavar='file_id')
    parser.add_argument('-l', '--list', help='List files in the store', action='store_true')
    parser.add_argument('-r', '--replace', help='Replace file in the store', nargs=2, metavar=('file_id', 'file_path'))
    parser.add_argument('-g', '--get', help='Get file from the store', metavar='file_id')
    parser.add_argument('-s', '--server', help='Server', metavar='server_url')
    parser.add_argument('-u', '--username', help='Username', metavar='username')
    parser.add_argument('-p', '--password', help='Password', metavar='password')
    
    args = parser.parse_args()
    s.handle_args(args)