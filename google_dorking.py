import asyncio
from tabulate import tabulate
import os

import parser
from utils import check_google, filter, fetch_all, get_delay, write_csv, google_workaround

async def perform_google_dorking(domain, output_dir):
    results = []
    google_search = SearchGoogle(domain, 500, 0)

    await google_search.googledork()

    host_names = [host for host in filter(await google_search.get_hostnames()) if f'.{domain}' in host]
    email_list = filter(await google_search.get_emails())

    results.append([domain, "\n".join(host_names), "\n".join(email_list)])
    table_headers = ["No.", "Domain", "Hosts", "Emails"]

    if len(results[0][1]) != 0 or len(results[0][2]) != 0:
        results = [[i + 1, result[0], result[1], result[2]] for i, result in enumerate(results)]
        table = tabulate(results, headers=table_headers, tablefmt="pretty", colalign=("left","left", "left", "left"))
        print("\nGoogle Dork Results:")
        print(table)

    # Save the results to a CSV file
    output_to_file(output_dir, results, table_headers)


def output_to_file(output_dir, results, table_headers):
    dork_output_dir = "dork_results"
    try:
        os.makedirs(dork_output_dir, exist_ok=True)

        print(f"Saving google dork results in {output_dir}/{dork_output_dir}")
    except Exception as e:
        print(f"An error occured when making directory: {e}")
        return

    try:
        output_file = f"{dork_output_dir}/google_dork.csv"
        write_csv(output_file, results, table_headers)
        print()
    except Exception as e:
        print(f"An error occured when writing google dork output: {e}")



class SearchGoogle:
    googleUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 ' \
           'Safari/537.36 '


    def __init__(self, word, limit, start, proxy=False):
        self.word = word
        self.results = ""
        self.totalresults = ""
        self.server = 'www.google.com'
        self.dorks = []
        self.links = []
        self.database = 'https://www.google.com/search?q='
        self.quantity = '100'
        self.limit = limit
        self.counter = start
        self.proxy = proxy

    async def get_emails(self):
        rawres = parser.Parser(self.totalresults, self.word)
        return await rawres.emails()

    async def get_hostnames(self):
        rawres = parser.Parser(self.totalresults, self.word)
        return await rawres.hostnames()

    async def append_dorks(self):
        # Wrap in try-except in case filepaths are messed up.
        try:
            with open('wordlists/dorks.txt', 'r') as fp:
                self.dorks = [dork.strip() for dork in fp]
        except FileNotFoundError as error:
            print(error)


    async def construct_dorks(self):
        # Format is: site:targetwebsite.com + space + inurl:admindork
        colon = '%3A'
        plus = '%2B'
        space = '+'
        period = '%2E'
        double_quote = '%22'
        asterick = '%2A'
        left_bracket = '%5B'
        right_bracket = '%5D'
        question_mark = '%3F'
        slash = '%2F'
        single_quote = '%27'
        ampersand = '%26'
        left_peren = '%28'
        right_peren = '%29'
        pipe = '%7C'
        # Format is google.com/search?q=dork+space+self.word
        self.links = tuple(
            self.database + str(dork).replace(':', colon).replace('+', plus).replace('.', period).replace('"',
                                                                                                          double_quote)
            .replace('*', asterick).replace('[', left_bracket).replace(']', right_bracket)
            .replace('?', question_mark).replace(' ', space).replace('/', slash).replace("'", single_quote)
            .replace('&', ampersand).replace('(', left_peren).replace(')', right_peren).replace('|',
                                                                                                pipe) + space + self.word
            for dork in self.dorks)


    async def send_dorks(self):  # Helper function to minimize code reusability.
        headers = {'User-Agent': self.googleUA}
        # Get random user agent to try and prevent google from blocking IP.
        for num in range(len(self.links)):
            try:
                if num % 10 == 0 and num > 0:
                    print(f'[*] Searching through {num} results')
                link = self.links[num]
                req = await fetch_all([link], headers=headers, proxy=self.proxy)
                self.results = req[0]
                if await check_google(self.results):
                    try:
                        self.results = await google_workaround(link)
                        if isinstance(self.results, bool):
                            print('[-] Google is blocking your ip and the workaround, returning')
                            return
                    except Exception:
                        # google blocked, no useful result
                        return
                await asyncio.sleep(get_delay())
                self.totalresults += self.results
            except Exception as e:
                print(f'\tException Occurred {e}')

    async def googledork(self):
        await self.append_dorks()  # Call functions to create list.
        await self.construct_dorks()
        await self.send_dorks()


