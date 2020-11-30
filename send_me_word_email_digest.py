#!/usr/bin/env python

import argparse
import json
import os
import ssl
import random

from collections import defaultdict

from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from markdown import Markdown
from smtplib import SMTP
from PyDictionary import PyDictionary

"""

"""
parser = argparse.ArgumentParser(
    description='Send an email digest of a random selection of words and their corresponding definitions.'
)
parser.add_argument(
    'num_words',
    type=int,
    help='The number of words to send a definition digest for.'
)
args = parser.parse_args()
num_requested_words = args.num_words

def load_words():
    with open('words_dictionary.json') as word_file:
        valid_words = word_file.read()
        valid_words = json.loads(valid_words)
    return valid_words


all_possible_words = list(load_words().keys())


def get_random_words(num_words):
    selected_words = []
    for i in range(num_words):
        word = random.choice(all_possible_words)
        if word[-2:] != "'s":
            selected_words.append(word)
    return selected_words


def format_definitions_into_email(definitions):
    words_header = """# Words: \n    * """ + '\n    * '.join(definitions.keys()) + '\n'
    body_content = [words_header]
    for word, definition_dict in definitions.items():
        definition_text = ''
        for definition in definition_dict:
            type_of_word = list(definition_dict.keys())
            def_list = list(definition_dict.values())
            for c, word_type in enumerate(type_of_word):
                definition_text += f'* {word_type} \n    - ' + '\n    - '.join(def_list[c]) + '\n'
        markdown_plaintext = f"""
---
## {word}
#### Definitions:
{definition_text}
        """
        body_content.append(markdown_plaintext)
    return ''.join(body_content)


def get_definitions(words, num_requested_definitions):
    dictionary = PyDictionary()
    definitions = defaultdict(str)
    def get_definition(word):
        definition = dictionary.meaning(word, disable_errors=True)
        if definition is not None:
            definitions[word] = definition
    for word in words:
        get_definition(word)
    while len(definitions) < num_requested_definitions:
        # Sometimes the response is empty from http://wordnetweb.princeton.edu/perl/webwn?s so we programatically retry
        new_word = random.choice(all_possible_words)
        get_definition(new_word)
    return definitions


password = os.getenv('SMTP_PASS')
host = os.getenv('SMTP_HOST')
from_email = os.getenv('EMAIL_FROM')
to_email = os.getenv('EMAIL_TO')
error_msg = 'Please add SMTP_PASS, SMTP_HOST, EMAIL_FROM, and EMAIL_TO as env vars'
assert all([password, host, from_email, to_email]), error_msg

random_words = get_random_words(num_words=num_requested_words)
definitions = get_definitions(random_words, num_requested_words)

message = MIMEMultipart("alternative")
message["Subject"] = f"{datetime.now().strftime('%Y-%m-%d')} Word Definition Digest"
message["From"] = from_email
message["To"] = to_email

# Create the plain-text and HTML version of your message
text = format_definitions_into_email(definitions)
markdowner = Markdown()
html = markdowner.convert(text)

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

context = ssl.create_default_context()
with SMTP(host=host, port=587) as server:
    server.starttls(context=context)
    server.login(from_email, password)
    server.sendmail(from_email, to_email, message.as_string())
