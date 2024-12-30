import aiohttp
import asyncio
import certifi
import csv
import dns.resolver
import random
import ssl
from urllib.parse import urlparse
from tabulate import tabulate
from typing import Union


proxy_list = []

def get_ip(domain):
    """Resolve IP addresses for a domain."""
    try:
        result = dns.resolver.resolve(domain, 'A')
        return [ip.to_text() for ip in result]
    except Exception:
        return []

def read_subdomains_file(subdomains_file):
    """Read the subdomains from the file. """
    try:
        with open(subdomains_file, 'r') as file:
            subdomains = [line.strip() for line in file.readlines() if line.strip()]

        return subdomains
    except FileNotFoundError:
        print(f"[ERROR] File not found: {subdomains_file}")
        return

def write_csv(filename, data, headers):
    """Write data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"CSV file '{filename}' created successfully.")
    except Exception as e:
        print(f"[ERROR] writing to CSV file '{filename}': {e}")

def filter(lst):
    """
    Method that filters list
    :param lst: list to be filtered
    :return: new filtered list
    """
    if lst is None:
        return []
    new_lst = []
    for item in lst:
        item = str(item)
        if (item[0].isalpha() or item[0].isdigit()) and ('xxx' not in item) and ('..' not in item):
            item = item.replace('252f', '').replace('2F', '').replace('2f', '').replace('u003d', '').replace('x3e', '')
            new_lst.append(item.lower())

    new_lst = set(new_lst)  # Remove duplicates.
    return new_lst

def get_delay() -> float:
    """Method that is used to generate a random delay"""
    return random.randint(1, 3) - .5

async def check_google(text: str) -> bool:
    """Helper function to check if Google has blocked traffic.
    :param text: See if certain text is returned which means Google is blocking us
    :return bool:
    """
    for line in text.strip().splitlines():
        if 'This page appears when Google automatically detects requests coming from your computer network' in line \
                or 'http://www.google.com/sorry/index' in line or 'https://www.google.com/sorry/index' in line:
            print('[-] Google is blocking your IP due to too many automated requests, wait or change your IP')
            return True
    return False


async def post_fetch(url, headers='', data='', params='', json=False, proxy=False):
    """
    Perform a POST request to the specified URL.

    Parameters
    ---
    :param url: The URL to send the POST request to.
    :param headers: Headers to include in the request. Defaults to an empty string.
    :param data: The data to send in the body of the POST request. Defaults to an empty string.
    :param params: Query parameters to include in the request URL. Defaults to an empty string.
    :param json: If True, send the data as JSON. Defaults to False.
    :param proxy: Proxy server to use for the request. Defaults to False.

    Returns
    ---
    :return: The response from the POST request, which can be a string, dictionary, list, or a boolean indicating success.
    """
    if len(headers) == 0:
        headers = {'User-Agent': get_user_agent()}
    timeout = aiohttp.ClientTimeout(total=720)
    # by default timeout is 5 minutes, changed to 12 minutes
    # results are well worth the wait
    try:
        if proxy:
            proxy = str(random.choice(proxy_list))
            if params != "":
                async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                    async with session.get(url, params=params, proxy=proxy) as response:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
            else:
                async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                    async with session.get(url, proxy=proxy) as response:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
        elif params == '':
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.post(url, data=data) as resp:
                    await asyncio.sleep(3)
                    return await resp.text() if json is False else await resp.json()
        else:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                sslcontext = ssl.create_default_context(cafile=certifi.where())
                async with session.post(url, data=data, ssl=sslcontext, params=params) as resp:
                    await asyncio.sleep(3)
                    return await resp.text() if json is False else await resp.json()
    except Exception as e:
        print(f'An exception has occurred: {e}')
        return ''

async def fetch(session, url, params='', json=False, proxy="") -> Union[str, dict, list, bool]:
    """
    This fetch method solely focuses on GET requests.

    Parameters
    ---
    :param session: An active session object for making requests.
    :param url: The URL to send the GET request to.
    :param params: (optional) Query parameters to include in the request. Defaults to an empty string.
    :param json: (optional) If True, parse the response as JSON. Defaults to False.
    :param proxy: (optional) Proxy server to use for the request. Defaults to an empty string.

    Return
    ---
    :return: The response content, which can be a string, dictionary, list, or a boolean indicating success.
    """
    try:
        # Wrap in try except due to 0x89 png/jpg files
        # TODO determine if method for post requests is necessary
        if proxy != "":
            if params != "":
                sslcontext = ssl.create_default_context(cafile=certifi.where())
                async with session.get(url, ssl=sslcontext, params=params, proxy=proxy) as response:
                    return await response.text() if json is False else await response.json()
            else:
                sslcontext = ssl.create_default_context(cafile=certifi.where())
                async with session.get(url, ssl=sslcontext, proxy=proxy) as response:
                    await asyncio.sleep(2)
                    return await response.text() if json is False else await response.json()

        if params != '':
            sslcontext = ssl.create_default_context(cafile=certifi.where())
            async with session.get(url, ssl=sslcontext, params=params) as response:
                await asyncio.sleep(2)
                return await response.text() if json is False else await response.json()

        else:
            sslcontext = ssl.create_default_context(cafile=certifi.where())
            async with session.get(url, ssl=sslcontext) as response:
                await asyncio.sleep(2)
                return await response.text() if json is False else await response.json()
    except Exception as e:
        print(f'An exception has occurred: {e}')
        return ''

async def fetch_all(urls, headers='', params='', json=False, proxy=False) -> list:
    """
    Perform GET requests to multiple URLs and return their responses.

    Parameters
    ---
    :param urls: A list of URLs to send GET requests to.
    :param headers: (optional) Headers to include in the requests. Defaults to an empty string.
    :param params: (optional) Query parameters to include in the requests. Defaults to an empty string.
    :param json: (optional) If True, parse the responses as JSON. Defaults to False.
    :param proxy: (optional) Proxy server to use for the requests. Defaults to False.

    Return
    ---
    :return: A list of responses from the GET requests.
    """



    # By default timeout is 5 minutes, 60 seconds should suffice
    timeout = aiohttp.ClientTimeout(total=60)


    if len(headers) == 0:
        headers = {'User-Agent': get_user_agent()}

    if len(params) == 0:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            if proxy:
                texts = await asyncio.gather(
                    *[fetch(session, url, json=json, proxy=random.choice(proxy_list)) for url in
                        urls])
                return texts
            else:
                texts = await asyncio.gather(*[fetch(session, url, json=json) for url in urls])
                return texts
    else:
        # Indicates the request has certain params
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            if proxy:
                texts = await asyncio.gather(*[fetch(session, url, params, json, proxy=random.choice(proxy_list)) for url in urls])
                return texts
            else:
                texts = await asyncio.gather(*[fetch(session, url, params, json) for url in urls])
                return texts

def get_user_agent() -> str:
    """
    Returns a random user agent from a list of user agents.
    """
    # User-Agents from https://github.com/microlinkhq/top-user-agents/blob/master/src/desktop.json
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36 Hutool",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.6.5 Chrome/124.0.6367.243 Electron/30.1.2 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.4.14 Chrome/114.0.5735.289 Electron/25.8.1 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "NetworkingExtension/8619.2.8.10.9 Network/4277.42.2 iOS/18.1.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Mozilla/5.0 (compatible; Cloudinary/1.0)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.7.7 Chrome/128.0.6613.186 Electron/32.2.5 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.6.7 Chrome/124.0.6367.243 Electron/30.1.2 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.6.7 Chrome/124.0.6367.243 Electron/30.1.2 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.4.16 Chrome/114.0.5735.289 Electron/25.8.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.6.5 Chrome/124.0.6367.243 Electron/30.1.2 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.4.16 Chrome/114.0.5735.289 Electron/25.8.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "NetworkingExtension/8620.1.16.10.11 Network/4277.60.255 iOS/18.2",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.5.3 Chrome/114.0.5735.289 Electron/25.8.1 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "NetworkingExtension/8619.1.26.30.5 Network/4277.2.5 iOS/18.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.4.13 Chrome/114.0.5735.289 Electron/25.8.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) obsidian/1.5.12 Chrome/120.0.6099.283 Electron/28.2.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"
    ]
    return random.choice(user_agents)

async def google_workaround(visit_url: str) -> Union[bool, str]:
    """
    Function that makes a request on our behalf, if Google starts to block us
    :param visit_url: Url to scrape
    :return: Correct html that can be parsed by BS4
    """
    url = 'https://websniffer.cc/'
    data = {
        'Cookie': '',
        'url': visit_url,
        'submit': 'Submit',
        'type': 'GET&http=1.1',
        'uak': str(random.randint(4, 8))  # select random UA to send to Google
    }

    print("[*] Trying to bypass Google IP block...")
    returned_html = await post_fetch(url, headers={'User-Agent': get_user_agent()}, data=data)
    returned_html = "This page appears when Google automatically detects requests coming from your computer network" \
        if returned_html == "" else returned_html[0]

    returned_html = "" if 'Please Wait... | Cloudflare' in returned_html else returned_html

    if len(returned_html) == 0 or await search(returned_html) or '&lt;html' not in returned_html:
        # indicates that google is serving workaround a captcha
        # That means we will try out second option which will utilize proxies
        return True
    # the html we get is malformed for BS4 as there are no greater than or less than signs
    if '&lt;html&gt;' in returned_html:
        start_index = returned_html.index('&lt;html&gt;')
    else:
        start_index = returned_html.index('&lt;html')

    end_index = returned_html.index('&lt;/html&gt;') + 1
    correct_html = returned_html[start_index:end_index]
    # Slice list to get the response's html
    correct_html = ''.join([ch.strip().replace('&lt;', '<').replace('&gt;', '>') for ch in correct_html])
    return correct_html