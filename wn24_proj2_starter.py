from bs4 import BeautifulSoup as bs
import re
import os
import csv
import unittest
import requests

# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"

An example of that within the function would be:
    open("filename", "r", encoding="utf-8-sig")

There are a few special characters present from Airbnb that aren't defined in standard UTF-8 (which is what Python runs by default). This is beyond the scope of what you have learned so far in this class, so we have provided this for you just in case it happens to you. Good luck!
"""
def extract_host(div_text):
    return re.search(r'(\w+$)|\w+\sAnd\s\w+$', div_text).group()
def extract_place_type(div_text):
    text = div_text.lower()
    if text.find("shared") == -1:
        if text.find("private") == -1:
            return "Entire Room"
        else:
            return "Private Room"
    else:
        return "Shared Room"

def retrieve_listings(html_file): 
    """
    retrieve_listings(html_file) -> list 

    TODO Write a function that takes file data from the variable html_file, reads it, and loads it into a BeautifulSoup object 

    Parse through the object, and return a list of tuples that includes the listing title and the listing id. 
        
        The listing id is found in the url of a listing. For example, for https://www.airbnb.com/rooms/1944564 the listing id is 1944564.

    Example output: 
        [('Loft in Mission District', '1944564'), ('Home in Mission District', '49043049'), ...]

    """
    lst = []
    with open(html_file, 'r') as file:
        html_content = file.read()
    soup = bs(html_content, 'html.parser')

    div_lst = soup.find_all('div', class_='t1jojoys dir dir-ltr')
    for div in div_lst:
        home_id = div.get('id')
        home_data = div.text.strip()
        home_id = re.search(r'\d+', home_id)
        lst.append((home_data, home_id.group()))
    return lst


def listing_details(listing_id): 
    """
    listing_details(listing_id) -> tuple

    TODO Write a function that takes a string containing the listing id of an Airbnb and returns a tuple that includes the policy number, the host name(s), the place type, the average review score, and the nightly price of the listing. 

        Policy number (data type: str) - either a string of the policy number, "Pending", or "Exempt". 
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word "Pending" or "Exempt" or many others. Look at the raw data, decide how to categorize them into the three categories.

        Host name(s) (data type: str) - either the host name or  "missing". 
            Beware some listings have multiple hosts– please make sure to capture both names (e.g. "Seth And Alexa")


        Place type (data type: str) - either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it

        Average Review Score (data type: float)
            Do not forget to account for listings which have no reviews 

        Nightly price of listing (data type: int)

    Example output: 
        ('2022-004088STR', 'Brian', 'Entire Room', 4.98, 181)
    """
    html_file  = f"html_files/listing_{listing_id}.html"
    with open(html_file, 'r') as file:
        html_content = file.read()
    soup = bs(html_content, 'html.parser')
    host_div = soup.find('div', class_='tehcqxo dir dir-ltr')
    host_div = host_div.find('h2')
    host = extract_host(host_div.text) # host name
    place_type_div = soup.find('h2', class_='_14i3z6h')
    place_type = extract_place_type(place_type_div.text) #place type
    policy_ul = soup.find('ul', class_='fhhmddr dir dir-ltr')
    policy = policy_ul.find('li').find('span', class_= 'll4r2nl dir dir-ltr').text
    policy = re.search(r'(STR-\d+\w+)|(pending)|(\d+-\d+STR)|(exempt)|(\d+)', policy).group()
    if policy == 'pending' or policy == 'exempt':
       policy=  policy.capitalize()
    price = soup.find('span' , class_= '_tyxjp1').text
    price = int(re.search(r'(\d)+' , price).group())

    if soup.find('span', class_='_12si43g') is not None:
        rev_span = soup.find('span', class_='_12si43g').string
        rev_str = re.search(r'\d\.\d{0,2}', rev_span).group()
        avg_review = float(rev_str)

    else:
        avg_review = 0


    return (policy, host, place_type, avg_review , price)






def make_listing_database(html_file): 
    """
    make_listing_database(html_file) -> list

    TODO Write a function that takes in a variable representing the path of the search_results.html file then calls the functions retrieve_listings() and listing_details() in order to create and return the complete listing information. 
    
    This function will use retrieve_listings() to create an initial list of Airbnb listings. Then use listing_details() to obtain additional information about the listing to create a complete listing, and return this information in the structure: 

        [
        (Listing Title 1,Listing ID 1,Policy Number 1, Host Name(s) 1, Place Type 1, Average Review Score 1, Nightly Rate 1),
        (Listing Title 2,Listing ID 2,Policy Number 2, Host Name(s) 2, Place Type 2, Average Review Score 2, Nightly Rate 2), 
        ... 
        ]

    NOTE: retrieve_listings() returns a list of tuples where the tuples are of length 2, listing_details() returns just a tuple of length 5, and THIS FUNCTION returns a list of tuples where the tuples are of length 7. 

    Example output: 
        [('Loft in Mission District', '1944564', '2022-004088STR', 'Brian', 'Entire Room', 4.98, 181), ('Home in Mission District', '49043049', 'Cherry', 'Pending', 'Entire Room', 4.93, 147), ...]    
    """
    lst = []
    listing_tup = retrieve_listings(html_file)
    for tup in listing_tup:
        id = tup[1]
        lst.append(tup + (listing_details(id)))
    return lst



def write_csv(data, filename): 
    """
    TODO Write a function that takes in a list of tuples called data, (i.e. the one that is returned by make_listing_database()), sorts the tuples in ascending order by average review score, writes the data to a csv file, and saves it to the passed filename. 
    
    The first row of the csv should contain "Listing Title", "Listing ID", "Policy Number", "Host Name(s)", "Place Type", "Average Review Score", "Nightly Rate", respectively as column headers. 
    
    For each tuple in the data, write a new row to the csv, placing each element of the tuple in the correct column. The data should be written in the csv in ascending order by average review score.

    Example output in csv file: 
        Listing Title,Listing ID,Policy Number,Host Name(s),Place Type,Average Review Score,Nightly Rate
        Apartment in Noe Valley,824047084487341932,2022-008652STR,Eileen,Entire Room,0.0,176
        Home in Mission District,11442567,STR-0005421,Bernat,Entire Room,4.79,164
        ...


    """
    sorted_data = sorted(data, key=lambda x: x[5])
    
    headers = ["Listing Title", "Listing ID", "Policy Number", "Host Name(s)", "Place Type", "Average Review Score", "Nightly Rate"]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(sorted_data)


def find_invalid_policy_numbers(data):
    """
    find_invalid_policy_numbers(data) -> list

    TODO Write a function that takes in a list of tuples called data, (i.e. the one that is returned by make_listing_database()), and parses through the policy number of each, validating that the policy number matches the policy number format. Ignore any pending or exempt listings. 

    Return a list of tuples that contains the listing id, host name(s), and invalid policy number for listings whose respective policy numbers that do not match the correct format.
        
        Policy numbers are a reference to the business license San Francisco requires to operate a short-term rental. These come in two forms below. # means any digit 0-9.

            20##-00####STR
            STR-000####

    Example output: 
    [('1944564', 'Brian', '2022-004088STR'), ...]

    """
    lst = []
    for tup in data:
        if re.search(r'20\d{2}-\d{6}STR|STR-\d{7}', tup[2]) is None and tup[2] != "Pending" and tup[2] != "Exempt":
            lst.append(tup)
    return lst



# EXTRA CREDIT 
def goodreads_searcher(query): 
    """
    goodreads_searcher(query) -> list
    TODO Write a function that imports requests library of Python
    and sends a request to good reads with the passed query.
    Using BeautifulSoup, find all titles and return the list of titles you see on page 1. 
    (that means, you do not need to scrape results on other pages)
    You do not need to write test cases for this question.
    Example output using 'airbnb' as query: 
        ['The Upstarts: How Uber, Airbnb, and the Killer Companies of the New Silicon Valley Are Changing the World', 
        'The Airbnb Story: How Three Ordinary Guys Disrupted an Industry, Made Billions . . . and Created Plenty of Controversy', 
        'Extreme Teams: Why Pixar, Netflix, Airbnb, and Other Cutting-Edge Companies Succeed Where Most Fail', 
        'Optimize YOUR Bnb: The Definitive Guide to Ranking #1 in Airbnb Search by a Prior Employee', 
        'How to Start a Successful Airbnb Business: Quit Your Day Job and Earn Full-time Income on Autopilot With a 
         Profitable Airbnb Business Even if You’re an Absolute Beginner (2023)', 
        "You, Me, and Airbnb: The Savvy Couple's Guide to Turning Midterm Rentals into Big-Time Profits", 
        'Get Paid For Your Pad: How to Maximize Profit From Your Airbnb Listing', 
        'How To Invest in Airbnb Properties: Create Wealth and Passive Income Through Smart Vacation Rentals Investing', 
        'Airbnb Listing Hacks - The Complete Guide To Maximizing Your Bookings And Profits', 
        'Work From Home: 50 Ways to Make Money Online Analyzed']
    * see PDF instructions for more details
    """
    response = requests.get(query)
    soup = bs.find(response, 'html.parser')
    table = soup.find('tr', itemtype='http://schema.org/Book')
    table.find_all()


# TODO: Don't forget to write your test cases! 
class TestCases(unittest.TestCase):
    def setUp(self):
        self.listings = retrieve_listings("html_files/search_results.html")
        self.listing_1944564 = listing_details(1944564)
        self.listing_database = make_listing_database("html_files/search_results.html")
        self.goodread = goodreads_searcher('airbnb')

    def test_retrieve_listings(self):
        # call retrieve_listings("html_files/search_results.html")
        # and save to a local variable

         # check that the number of listings extracted is correct (18 listings)
        self.assertEqual(len(self.listings), 18)

        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(self.listings), list)

        # check that each item in the list is a tuple

        # check that the first title and listing id tuple is correct (open the search results html and find it)

        # check that the last title and listing id tuple is correct (open the search results html and find it)

    def test_listing_details(self):
        html_list = ["467507",
                     "1550913",
                     "1944564",
                     "4614763",
                     "6092596"]
        
        # call listing_details for i in html_list:
        listing_information = [listing_details(id) for id in html_list]

        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_information), 5)
        for info in listing_information:
            # check that each item in the list is a tuple
            self.assertEqual(type(info), tuple)
            # check that each tuple has 5 elements
            self.assertEqual(len(info), 5)
            # check that the first three elements in the tuple are string
            self.assertEqual(type(info[0]), str)
            self.assertEqual(type(info[1]), str)
            self.assertEqual(type(info[2]), str)
            # check that the fourth element in the tuple is a float
            self.assertEqual(type(info[3]), float)
            # check that the fifth element in the tuple is an int
            self.assertEqual(type(info[4]), int)

        # check that the first listing in the html_list has the correct policy number

        # check that the last listing in the html_list has the correct place type

        # check that the third listing has the correct cost

    def test_make_listing_database(self):
        # call make_listing_database on "html_files/search_results.html"
        # and save it to a variable
        detailed_data = make_listing_database("html_files/search_results.html")

        # check that we have the right number of listings (18)
        self.assertEqual(len(detailed_data), 18)

        for item in detailed_data:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 7

        # check that the first tuple is made up of the following:
        # ('Loft in Mission District', '1944564', '2022-004088STR', 'Brian', 'Entire Room', 4.98, 181)

        # check that the last tuple is made up of the following:
        # ('Guest suite in Mission District', '467507', 'STR-0005349', 'Jennifer', 'Entire Room', 4.95, 165)

    def test_write_csv(self):
        # call make_listing_database on "html_files/search_results.html"
        # and save the result to a variable
        detailed_data = make_listing_database("html_files/search_results.html")

        # call write_csv() on the variable you saved
        write_csv(detailed_data, "test.csv")

        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)

        # check that there are 19 lines in the csv
        self.assertEqual(len(csv_lines), 19)

        # check that the header row is correct

        # check that the next row is Apartment in Noe Valley,824047084487341932,2022-008652STR,Eileen,Entire Room,0.0,176

        # check that the last row is Guest suite in Mission District,755957132088408739,STR-0000315,HostWell,Entire Room,5.0,125

    def test_find_invalid_policy_numbers(self):
        # call make_listing_database on "html_files/search_results.html"
        # and save the result to a variable
        detailed_data = make_listing_database("html_files/search_results.html")

        # call find_invalid_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = find_invalid_policy_numbers(detailed_data)

        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)

        # check that the elements in the list are tuples
        # and that there are exactly three element in each tuple

def main (): 
    detailed_data = make_listing_database("html_files/search_results.html")
    write_csv(detailed_data, "airbnb_dataset.csv")

if __name__ == '__main__':
    # main()
    unittest.main(verbosity=2)