# coding: utf-8

import re
import requests
import time
import tqdm
import argparse
import os

regex_1 = re.compile('meta  property="og:description"')
regex_2 = re.compile('content="“(.*)”"')


def clean_tweet(text):
    return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", '-i',
                        default=r"..\datasets\riloff\riloff.txt",
                        # required=True,
                        help="Input file path with each line containing a tweet ID")

    parser.add_argument('--delay',
                        default=0.1,
                        help='Delay between requests, in seconds. Default: 0.3')

    args = parser.parse_args()

    input_file_path = args.input

    assert args.input.endswith('.txt')

    output_file_path = args.input.replace('.txt', '.tweets.tsv')

    with open(input_file_path) as in_file:
        tids = [line.strip().split("\t")[0] for line in in_file.readlines()]

    cached_tids = []
    if os.path.exists(output_file_path):
        with open(output_file_path, encoding="utf-8") as out_file:
            cached_tids = [line.strip().split('\t')[0]
                           for line in out_file.readlines()]

    last_cached_id = cached_tids[-1]
    last_index = tids.index(last_cached_id)

    with open(output_file_path, 'a', encoding="utf-8") as out_file:
        for tid in tqdm.tqdm(tids[last_index + 1:]):

            if cached_tids and tid in cached_tids:
                continue

            url = 'https://twitter.com/globglogabgalab/status/{0}'.format(tid)
            r = requests.get(url)
            # print(r.status_code)

            if r.status_code == 200:
                url_lines = r.content.decode('utf-8').splitlines()
                for url_line in url_lines:
                    if regex_1.search(url_line):
                        match = regex_2.findall(url_line)[0]
                        tweet = clean_tweet(match)
                        out_file.write('{0}\t{1}\n'.format(tid, tweet))
                        # print(tweet)
                        out_file.flush()
                        if args.delay:
                            time.sleep(eval(args.delay))
