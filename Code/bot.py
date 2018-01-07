import re
import traceback
import wikipedia
from wit import Wit
from speech import Speech
from knowledge import Knowledge
from phrases import Phrases
from fatsecret import Fatsecret
from googletrans import Translator
import time

weather_api_token = "73995c4fbf4f6cd3fe31eb7ca4b3bdec"
fat_secret_oauth = "90fe184a283449ed8a83e35790c04d65"


class Bot(object):
    def __init__(self, speech_input=False, facebook_input=False):
        self.phrases = Phrases()
        self.speech = Speech()
        self.knowledge = Knowledge()
        self.facebook_input = facebook_input
        if self.facebook_input:
            self.facebook_response = []
        self.speech_input = speech_input
        self.witai = Wit("S73IKQDWJ22OJMOSD6AOT4CSJOWXIPX6")
        self.fs = Fatsecret("90fe184a283449ed8a83e35790c04d65", "054e80b2be154337af191be2c9e11c28")
        self.translator = Translator()

    def gr_to_en(self, text):
        return self.translator.translate(text, 'en', 'el').text

    def en_to_gr(self, text):
        return self.translator.translate(text, 'el', 'en').text

    def start(self):
        if self.speech_input or self.facebook_input:
            self.decide_action()
        else:
            print("Γεία σου! Πως θα μπορούσα να σε βοηθήσω;")
            while 1:
                self.decide_action()

    def decide_action(self, facebook_input=None):

        if self.speech_input or self.facebook_input:
            if self.speech_input:
                recognizer, audio = self.speech.listen_for_audio()
                # received audio data, now we'll recognize it using Google Speech Recognition
                bot_input = self.speech.google_speech_recognition(recognizer, audio)
            if self.facebook_input:
                bot_input = facebook_input
        else:
            bot_input = input()

        if bot_input is not None:
            self.facebook_response = []
            try:
                resp = self.witai.message(bot_input)
                entities = None
                intent = None
                if 'entities' in resp and 'intent' in resp['entities']:
                    entities = resp['entities']
                    intent = resp['entities']['intent'][0]["value"]
                    # print('Intent: {intent}'.format(intent=intent))
                if intent == 'greeting':
                    self.__text_action(self.phrases.greet())
                elif intent == 'tutorial':
                    self.__tutorial_action()
                elif intent == 'personal_status':
                    self.__personal_status()
                elif intent == 'beatbox':
                    self.__beatbox_action()
                elif intent == 'joke':
                    self.__joke_action()
                elif intent == 'datetime':
                    # print(resp)
                    self.__datetime_action(entities)
                elif intent == 'weather':
                    self.__weather_action()
                elif intent == 'search':
                    self.__search_action(entities)
                elif intent == 'food_det':
                    self.__food_action(entities)
                elif intent == 'recipe':
                    self.__recipe_action(entities)
                else:  # No recognized intent
                    # print('Intent not recognized')
                    self.__text_action(self.phrases.unrecognized_intent())
                    return

            except Exception as e:
                print("Exception occured")
                print(e)
                traceback.print_exc()
                self.__text_action("Έγινε κάποιο λάθος")
                return

    def __text_action(self, text=None):
        if text is not None:
            if self.speech_input:
                self.speech.synthesize_text(text)
            if self.facebook_input:
                self.facebook_response.append(text)
            else:
                print(text)

    def __tutorial_action(self):
        self.__text_action(self.phrases.tutorial())

    def __personal_status(self):
        self.__text_action(self.phrases.personal_status())

    def __joke_action(self):
        joke = self.phrases.joke()
        for j in joke:
            time.sleep(1)
            self.__text_action(j)

    def __datetime_action(self, entities):
        dt = None
        if 'datetime' in entities:
            dt = entities['datetime'][0]['grain']
            print('Datetime: {dt}'.format(dt=dt))
        if str(dt) == 'second':
            self.__text_action('Η ώρα είναι {time}'.format(time=self.knowledge.get_time()))
        elif str(dt) == 'day':
            self.__text_action('Σήμερα είναι {weekday}'.format(weekday=self.knowledge.get_weekday()))
        elif str(dt) == 'ημερομηνία':
            self.__text_action('Σήμερα είναι {date}'.format(date=self.knowledge.get_date()))

    def __weather_action(self):
        weather_obj = self.knowledge.find_weather()
        self.__text_action('Η θερμοκρασία είναι ' + str(weather_obj['temperature']) + '° Κελσίου.')

    def __search_action(self, entities=None):
        self.__text_action(self.phrases.searching())
        if 'wikipedia_search_query' in entities:
            query = entities['wikipedia_search_query'][0]['value']
            print('wikipedia query: {query}'.format(query=query))
            wikipedia.set_lang("el")
            try:
                self.__text_action(re.sub(r'\([^)]*\)', '', wikipedia.summary(query, sentences=1)))
            except wikipedia.PageError as e:
                print(e)
                self.__text_action('Δεν βρήκα κάποιο αποτέλεσμα')
        else:
            self.__text_action('Δεν μου είπες τί να ψάξω')

    def __food_action(self, entities):
        self.__text_action(self.phrases.searching())
        inp = self.gr_to_en(entities['wikipedia_search_query'][0]['value'])
        try:
            resp = self.fs.foods_search(inp)
            # self.__text_action(self.en_to_gr(resp[0]["food_name"] + "\n" + resp[0]["food_description"]))
            food = self.fs.food_get(resp[0]['food_id'])
            if 'nutrient_type' in entities.keys():
                self.__text_action(self.en_to_gr('1 {serving}'.format(serving=food['servings']['serving'][0]['measurement_description'])))
                for nutrient in entities['nutrient_type']:
                    self.__text_action(self.en_to_gr('{nutrient}: {value}'.format(nutrient=nutrient['value'],
                                                   value=food['servings']['serving'][0][nutrient['value']])))
        except Exception as e:
            print(e)
            self.__search_action(entities)

    def __recipe_action(self, entities):
        self.__text_action(self.phrases.searching())
        inp = self.gr_to_en(entities['wikipedia_search_query'][0]['value'])
        try:
            resp = self.fs.recipes_search(inp)
            recipe = self.fs.recipe_get(resp[0]['recipe_id'])
            self.__text_action(self.en_to_gr(recipe['recipe_name'] + "\n"))
            self.__text_action("Οδηγίες")
            for dir in recipe['directions']['direction']:
                self.__text_action(self.en_to_gr(dir['direction_description']))
            self.__text_action("Συστατικά")
            for ing in recipe['ingredients']['ingredient']:
                self.__text_action(self.en_to_gr(ing['ingredient_description']))
        except Exception as e:
            self.__text_action("Δεν υπάρχει διαθέσιμη συνταγή για " + entities['wikipedia_search_query'][0]['value'])
            self.__search_action(entities)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
