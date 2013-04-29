#!/usr/bin/env python

"""
Idea: generate a URL pointer.data which form a linked-list. We store each link
in the list in a URL shortener. The head is just a pointer and can be retrieved
at will.

TODO: take a public key on the command line to encrypt it with
"""

import os, sys, getopt, requests
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64encode, b64decode

def enum(**enums):
    return type('Enum', (), enums)
Directions = enum(UPLOAD=1, DOWNLOAD=-1)

def readFile(file):
    return open(file, "r").read()
def writeFile(file, data):
    open(file, "w").write(data)

alt = ".-"
separator = ':'
def encode(s):
    return b64encode(s, alt)
def decode(s):
    return b64decode(s, alt)

# Might change depending on the shortener
max_step = 32768
def toChunks(data):
    data = encode(data)
    chunks = []
    for i in xrange(0, len(data), max_step):
        chunks.append(data[i:i + max_step])
    return chunks

def fromChunks(chunks):
    data = str()
    for chunk in chunks:
        data += chunk
    return decode(data)

def store(url):
    r = requests.get(service + "/api-create.php?url=" + url, allow_redirects=False)
    if r.status_code == 200:
        # skip over "http://tinyurl.com/"
        return r.text[19:]
    print >> sys.stderr, "Something terrible happened"
    os.exit(1)

def push(file):
    def reverse(s):
        return s[::-1]

    chunks = reverse(toChunks(readFile(file)))
    prev = str()
    for chunk in chunks:
        url = prev + separator + chunk
        prev = store(url)
    return prev

# start: c6em4sp, or crdr8g8
service = "http://tinyurl.com"
def retrieve(key):
    r = requests.get(service + "/" + key, allow_redirects=False)
    data = r.headers['location']
    # skip over "http://blah/" if it's present
    if data[:7] == "http://":
        data = data[7:]
    return data

def pull(key):
    chunks = []
    next = key
    i = 0
    while next:
        [next, chunk] = retrieve(next).split(separator)
        chunks.append(chunk)
        i += 1
    return fromChunks(chunks)

def usage():
    text = """
usage: ./a.out [options] [file]

options:
    -p, --put           upload a file
    -g, --get=<key>     download a file
    -f, --file=<file>   use <file> as the file

    -h, --help          this message
"""
    print >> sys.stderr, text
    sys.exit(1)

# Make it read from stdin
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hpg:f:", ["help", "put", "get=", "file="])
    except getopt.GetoptError as err:
        print >> sys.stderr, str(err)
        usage()

    direction = file = key = None

    for opt, arg in opts:
        if opt == "-h":
            usage()
        if opt == "-p":
            direction = Directions.UPLOAD
        elif opt in ["-g", "--get"]:
            direction = Directions.DOWNLOAD
            key = arg
        elif opt in ["-f", "--file"]:
            file = arg
        else:
            usage()

    if not direction:
        usage()
    elif direction == Directions.UPLOAD and not file:
        print >> sys.stderr, "What file do you want to upload, chief?"
        sys.exit(1)
    elif direction == Directions.DOWNLOAD and not key:
        print >> sys.stderr, "What file do you want to download, champ?"
        sys.exit(1)

    if direction == Directions.UPLOAD:
        print "retrieval key:", push(file)
    elif direction == Directions.DOWNLOAD:
        data = pull(key)
        if not file or file == "-":
            print data
        else:
            writeFile(file, data)


if __name__ == "__main__":
    main(sys.argv[1:])
