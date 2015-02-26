import random
import os

from twitter import TwitterStream, OAuth, Twitter


class Markov(object):
    def __init__(self, chain_size=3):
        self.chain_size = chain_size
        self.cache = {}
        self.tweet_size = 0
        self.words = []

    def add_tweet(self, tweet):
        tweet = tweet.split()
        self.tweet_size += len(tweet)
        self.words += tweet
        self.database(tweet)

    def chains(self, tweet):
        if len(tweet) < self.chain_size:
            return

        for i in range(len(tweet) - (self.chain_size - 1)):
            yield tuple(self.tweet_at_position(i, tweet))

    def database(self, tweet):
        for chain_set in self.chains(tweet):
            key = chain_set[:self.chain_size - 1]
            next_word = chain_set[-1]
            if key in self.cache:
                self.cache[key].append(next_word)
            else:
                self.cache[key] = [next_word]

    def tweet_at_position(self, i, tweet):
        chain = []
        for chain_index in range(0, self.chain_size):
            chain.append(tweet[i + chain_index])
        return chain

    def words_at_position(self, i):
        chain = []
        for chain_index in range(0, self.chain_size):
            chain.append(self.words[i + chain_index])
        return chain

    def generate_markov_text(self, size=1):
        size = self.tweet_size
        seed = random.randint(0, self.tweet_size - self.chain_size)
        seed_words = self.words_at_position(seed)[:-1]
        gen_words = []
        for word in seed_words:
            gen_words.append(word)
        for i in xrange(size):
            last_word_len = self.chain_size - 1
            last_words = gen_words[-1 * last_word_len:]
            if tuple(last_words) in self.cache:
                next_word = random.choice(self.cache[tuple(last_words)])
                gen_words.append(next_word)
            else:
                seed = random.randint(0, self.tweet_size - self.chain_size)
                seed_words = self.words_at_position(seed)[:-1]
                for word in seed_words:
                    gen_words.append(word)

        return gen_words[:15]

auth = OAuth(
    consumer_key=os.environ['CONSUMER_KEY'],
    consumer_secret=os.environ['CONSUMER_SECRET'],
    token=os.environ['TOKEN'],
    token_secret=os.environ['TOKEN_SECRET']
)

markov = Markov()

tweet_count = 0

twitter_stream = TwitterStream(auth=auth)
t = Twitter(auth=auth)

for tweet in twitter_stream.statuses.sample():
    try:
        if tweet['lang'] == 'en' and tweet['text'][:2] != 'RT':
            tweet_count += 1
            markov.add_tweet(tweet['text'])
            if tweet_count == 10000:
                status = ' '.join(markov.generate_markov_text())[:140]
                t.statuses.update(status=status)
                tweet_count = 0
                markov = Markov()

    except KeyError as e:
        pass
