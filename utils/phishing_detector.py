import re
import numpy as np
import requests
import socket
from urllib.parse import urlparse, urlencode
import tldextract
from bs4 import BeautifulSoup
from whoisapi import *
from datetime import datetime, timezone
import tensorflow as tf


def tld_in_subdomain(tld, subdomain):
    """
    Check if tld is used in the subdomain
    Parameters:
        tld (str): the top level domain
        subdomain (str): the subdomain
    Returns:
        int: 1 if tld is used in the subdomain, 0 otherwise
    """
    if subdomain.count(tld) > 0:
        return 1
    return 0


def page_rank(key, domain):
    """
    Get the page rank of the given domain using the openpagerank.com API
    Parameters:
        key (str): the API key
        domain (str): the domain
    Returns:
        int: the page rank of the domain. -1 if the API call fails
    """

    url = "https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=" + domain
    try:
        request = requests.get(url, headers={"API-OPR": key})
        result = request.json()
        result = result["response"][0]["page_rank_integer"]
        if result:
            return result
        else:
            return 0
    except:
        return -1


def domain_age(domain, api_key=None):
    """
    Get the age of the given domain using the payapi.io API
    Parameters:
        domain (str): the domain
    Returns:
        int: the age of the domain in days. -2 if the domain does not exist, -1 if the API call fails
    """
    if api_key is None:
        return -1

    client = Client(api_key=api_key)
    whois = client.data(domain)

    input_date_str = whois.created_date_raw
    if input_date_str == "":
        input_date_str = whois.registry_data.created_date_raw

    if input_date_str is None:
        return -2

    # Convert to datetime object
    input_date = datetime.strptime(input_date_str, "%Y-%m-%dT%H:%M:%S%z")

    # Get the current UTC time
    now = datetime.now(timezone.utc)

    # Calculate the difference
    diff = now - input_date

    return diff.days


def google_index(url):
    """
    Check if the given url is indexed in google
    Parameters:
        url (str): the url
    Returns:
        int: 0 if the url is indexed, 1 if it is not indexed, -1 if the API call fails
    """
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"
    headers = {"User-Agent": user_agent}
    query = {"q": "site:" + url}
    google = "https://www.google.com/search?" + urlencode(query)
    data = requests.get(google, headers=headers)
    data.encoding = "ISO-8859-1"
    soup = BeautifulSoup(str(data.content), "html.parser")
    try:
        if (
            "Our systems have detected unusual traffic from your computer network."
            in str(soup)
        ):
            return -1
        check = soup.find(id="rso").find("div").find("div").find("a")
        if check and check["href"]:
            return 0
        else:
            return 1

    except AttributeError:
        return 1


def extract_features_from_url(url, opr_key=None, whoisapi_key=None):
    """
    Extract the following features from the URL:

    0. google_index: Retrieved via external_features.google_index(url)
    1. page_rank: Retrieved via external_features.page_rank(opr_key, domain)
    2. nb_www: Count of "www" occurrences in the URL
    3. ratio_digits_url: Ratio of digit characters to total characters in the URL
    4. domain_in_title: 1 if the domain appears in the page title, else 0
    5. nb_hyperlinks: Count of <a> tags in the HTML content
    6. phish_hints: 1 if an '@' is present in the URL, else 0
    7. domain_age: Retrieved via external_features.domain_age(domain)
    8. ip: 1 if the hostname is an IP address, else 0
    9. nb_qm: Count of "?" characters in the URL
    10. length_url: Total length of the URL string
    11. ratio_intHyperlinks: Ratio of internal hyperlinks to total hyperlinks in the page
    12. nb_slash: Count of "/" characters in the URL
    13. length_hostname: Length of the hostname portion of the URL
    14. nb_eq: Count of "=" characters in the URL
    15. ratio_digits_host: Ratio of digits in the hostname to its total length
    16. shortest_word_host: Length of the shortest word in the hostname (split by '.' and '-')
    17. prefix_suffix: 1 if the hostname contains a hyphen ("-"), else 0
    18. longest_word_path: Length of the longest word in the URL path (split by non-alphanumeric characters)
    19. tld_in_subdomain: 1 if the TLD is present in the subdomain, else 0

    Parameters:
        url (str): the URL to extract features from
        opr_key (str): an API key for page_rank lookup (if not provided, default to -1)

    Returns:
        np.array: a vector of 19 features extracted from the URL
    """
    parsed = urlparse(url)
    hostname = parsed.netloc
    path = parsed.path
    scheme = parsed.scheme

    # Use tldextract to get domain, subdomain, and tld
    extracted = tldextract.extract(url)
    domain = extracted.domain
    subdomain = extracted.subdomain
    tld = extracted.suffix

    # Feature 0: google_index (external lookup)
    g_index = google_index(url)

    # Feature 1: page_rank (requires an API key; if not provided, default to -1)
    p_rank = page_rank(opr_key, domain) if opr_key else -1

    # Feature 2: nb_www: count occurrences of "www" in URL
    nb_www = url.lower().count("www")

    # Feature 3: ratio_digits_url: ratio of digits in URL
    total_chars = len(url)
    digits_in_url = sum(c.isdigit() for c in url)
    ratio_digits_url = digits_in_url / total_chars if total_chars > 0 else 0.0

    # Initialize content-based features (5 & 11 & 4 & 6)
    try:
        resp = requests.get(url, timeout=5)
        content = resp.content
        soup = BeautifulSoup(content, "html.parser")

        # Feature 4: domain_in_title: 1 if the domain appears in the page title
        title = soup.title.string if soup.title else ""
        domain_in_title = 1.0 if domain.lower() in title.lower() else 0.0

        # Feature 5: nb_hyperlinks: count of <a> tags in the page
        a_tags = soup.find_all("a")
        nb_hyperlinks = float(len(a_tags))

        # Feature 11: ratio_intHyperlinks: ratio of internal links to total hyperlinks
        internal_links = 0
        for tag in a_tags:
            href = tag.get("href", "")
            if hostname in href:
                internal_links += 1
        ratio_intHyperlinks = (
            internal_links / nb_hyperlinks if nb_hyperlinks > 0 else 0.0
        )
    except Exception:
        domain_in_title = 0.0
        nb_hyperlinks = 0.0
        ratio_intHyperlinks = 0.0

    # Feature 6: phish_hints: simple check for '@' in the URL
    phish_hints = 1.0 if "@" in url else 0.0

    # Feature 7: domain_age: retrieved via external_features.domain_age
    d_age = domain_age(url, whoisapi_key)

    # Feature 8: ip: check if hostname is an IP address
    try:
        socket.inet_aton(hostname)
        ip_flag = 1.0
    except Exception:
        ip_flag = 0.0

    # Feature 9: nb_qm: count "?" characters in URL
    nb_qm = url.count("?")

    # Feature 10: length_url: total length of URL
    length_url = float(len(url))

    # Feature 12: nb_slash: count "/" characters in URL
    nb_slash = url.count("/")

    # Feature 13: length_hostname: length of hostname string
    length_hostname = float(len(hostname))

    # Feature 14: nb_eq: count "=" characters in URL
    nb_eq = url.count("=")

    # Feature 15: ratio_digits_host: ratio of digits in hostname to its length
    digits_in_host = sum(c.isdigit() for c in hostname)
    ratio_digits_host = digits_in_host / len(hostname) if len(hostname) > 0 else 0.0

    # Feature 16: shortest_word_host: length of the shortest word in hostname split by '.' and '-'
    host_parts = re.split(r"[.-]", hostname)
    host_parts = [p for p in host_parts if p]
    shortest_word_host = min([len(p) for p in host_parts]) if host_parts else 0.0

    # Feature 17: prefix_suffix: 1 if '-' exists in hostname, else 0
    prefix_suffix = 1.0 if "-" in hostname else 0.0

    # Feature 18: longest_word_path: length of the longest word in the URL path split by non-alphanumerics
    path_words = re.split(r"\W+", path)
    path_words = [w for w in path_words if w]
    longest_word_path = max([len(w) for w in path_words]) if path_words else 0.0

    # Feature 19: tld_in_subdomain: use url_features.tld_in_subdomain
    tld_in_subdomain_val = tld_in_subdomain(tld, subdomain)

    # Assemble features in the specified order
    features = [
        g_index,  # google_index
        p_rank,  # page_rank
        nb_www,  # nb_www
        ratio_digits_url,  # ratio_digits_url
        domain_in_title,  # domain_in_title
        nb_hyperlinks,  # nb_hyperlinks
        phish_hints,  # phish_hints
        d_age,  # domain_age
        ip_flag,  # ip
        nb_qm,  # nb_qm
        length_url,  # length_url
        ratio_intHyperlinks,  # ratio_intHyperlinks
        nb_slash,  # nb_slash
        length_hostname,  # length_hostname
        nb_eq,  # nb_eq
        ratio_digits_host,  # ratio_digits_host
        shortest_word_host,  # shortest_word_host
        prefix_suffix,  # prefix_suffix
        longest_word_path,  # longest_word_path
        tld_in_subdomain_val,  # tld_in_subdomain
    ]

    return np.array(features, dtype=np.float32)


def load_model(model_path):
    model = tf.keras.models.load_model(model_path)
    return model


def predict(model, url, opr_key=None, whoisapi_key=None):
    """
    Predict the output of a given URL
    Parameters:
        model (tf.keras.models.Model): the model to use for prediction
        url (str): the URL to predict the output for
        opr_key (str): an API key for page_rank lookup (if not provided, default to -1)
    Returns:
        np.ndarray: a numpy array of the prediction
    """
    features = extract_features_from_url(url, opr_key, whoisapi_key)
    features = features.reshape(1, -1)
    predictions = model.predict(features)
    return predictions
    # return 0

# Optionally provide your OPR API key for page_rank computation:
opr_key = "so0kwk4448ck8ggwsogwo8kswgs08kwc4gk8s844"  # Replace with your key or leave as None
whoisapi_key = (
    "at_NlbHgbJ1DvB5cHC4PJSaRy7pT38z9"  # Replace with your key or leave as None
)

def inference_phishing_dl(model_path, url):
    model = load_model(model_path)
    return predict(model, url)

def inference_phishing_rl(model_path, url):
    model = load_model(model_path)
    q_vals = predict(model, url)
    delta_q = float(q_vals[0, 0] - q_vals[0, 1])
    # is_phish = delta_q <= 1.0
    return delta_q

def inference_phishing(model_path, url):
    if "Reinforcement" in model_path:
        return inference_phishing_rl(model_path, url)
    else:
        return inference_phishing_dl(model_path, url)