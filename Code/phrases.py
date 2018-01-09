import random
import datetime
import yaml
import os


class Phrases(object):
    YAML_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + '/yaml/'

    def __init__(self):
        # make random more random by seeding with time
        random.seed(datetime.datetime.now())

    @staticmethod
    def add_phrases(file, phrases):
        stream_load = open(Phrases.YAML_DIRECTORY + file + '.yaml', 'r', encoding='utf-8')
        results = yaml.safe_load(stream_load)
        stream = open(Phrases.YAML_DIRECTORY + file + '.yaml', 'w', encoding='utf-8')
        results = results + phrases
        yaml.safe_dump(results, stream, encoding='utf-8', allow_unicode=True)

    @staticmethod
    def get_phrases(file):
        stream = open(Phrases.YAML_DIRECTORY + file + '.yaml', 'r', encoding='utf-8')
        results = yaml.safe_load(stream)
        if file == 'greetings_phrases':
            date = datetime.datetime.now()
            if date.hour < 6 or date.hour > 21:
                return random.choice(['Καλό βράδυ', random.choice(results)])
            elif 6 < date.hour < 12:
                return random.choice(['Καλημέρα', random.choice(results)])
            elif 12 <= date.hour <= 21:
                return random.choice(['Καλησπέρα', random.choice(results)])

        return random.choice(results)
