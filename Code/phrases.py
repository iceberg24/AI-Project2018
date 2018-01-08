import random
import datetime
import yaml


class Phrases(object):
    def __init__(self):
        # make random more random by seeding with time
        random.seed(datetime.datetime.now())

    @staticmethod
    def add_phrases(file, phrases):
        stream = open('yaml/' + file + '.yaml', 'a')
        yaml.safe_dump(phrases, stream)

    @staticmethod
    def get_phrases(file):
        stream = open('yaml/' + file + '.yaml', 'r')
        results = yaml.load(stream)
        if file == 'greetings_phrases':
            date = datetime.datetime.now()
            if date.hour < 6 or date.hour > 21:
                return random.choice(['Καλό βράδυ', random.choice(results)])
            elif 6 < date.hour < 12:
                return random.choice(['Καλημέρα', random.choice(results)])
            elif 12 <= date.hour <= 21:
                return random.choice(['Καλησπέρα', random.choice(results)])

        return random.choice(results)
