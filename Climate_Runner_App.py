import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


# download html with the given filename given the url
def download(filename, url):
    # doesn't download if the file is already downloaded
    if os.path.exists(os.path.join("app", "city_html_files", filename)):
        return

    # initializing the response object through the requests module
    resp = requests.get(url)
    # checks if the specific url exists and if the request went through correctly
    resp.raise_for_status()

    if ".html" in filename:
        doc = BeautifulSoup(resp.text, "html.parser")
        f = open(os.path.join("app", "city_html_files", filename), "w", encoding="utf-8")
        f.write(str(doc))
        f.close()


# finding tables with the heading having the keyword and returns the soup table and the title of the table
def parse_html_tables(html_file, keyword):
    f_spec_city = open(os.path.join("app", "city_html_files", html_file), encoding="utf-8")
    html_text = f_spec_city.read()
    f_spec_city.close()
    doc = BeautifulSoup(html_text, "html.parser")
    tables = doc.find_all("table")
    title_plot = ""
    table_climate = None

    # finding the appropriate table according to the keyword
    for each_table in tables:
        table_climate = None
        th_list_each = each_table.find_all("th")
        if len(th_list_each) == 0:
            continue
        str_heading = th_list_each[0].get_text()
        if keyword.lower() in str_heading.lower():
            table_climate = each_table
            title_plot = str_heading
            break

    return table_climate, title_plot


# returns the list of months of the year
def ret_list_months(climate_table_city):
    doc_table_rows = climate_table_city.find_all("tr")
    doc_months = doc_table_rows[1]
    th_list_months = doc_months.find_all("th")
    th_list_months = th_list_months[1:-1]
    list_months = []
    for each_entry in th_list_months:
        list_months.append(each_entry.get_text().strip())
    return list_months


# returns a list of values of the specific type of stat in order of the months of the year
def ret_list_stat_values(climate_table_city, keyword):
    doc_table_rows = climate_table_city.find_all("tr")
    specific_row = None
    type_data = None
    # finding the row with given keyword within table
    for each_row in doc_table_rows:
        type_data = each_row.find("th")
        if type_data is None:
            continue
        if keyword.lower() in type_data.get_text().strip().lower():
            specific_row = each_row
            break

    if specific_row is None:
        raise ValueError("No " + keyword + " row found")

    td_list = specific_row.find_all("td")
    td_list = td_list[:-1]
    list_vals = []
    for each_td in td_list:
        parts_si = each_td.get_text().strip().split("(")
        str_val = parts_si[0]
        if "," in str_val:
            two_parts = str_val.split(",")
            thousands_place = int(two_parts[0])
            rest = float(two_parts[1])
            val = 1000 * thousands_place + rest
            list_vals.append(val)
        else:
            if str_val == "trace" or str_val == "—":
                str_val = "0.0"
            list_vals.append(float(str_val))
    name_y_axis = type_data.get_text().strip().split("(")[0]
    return list_vals, name_y_axis


# constructing the dataframe to construct a plot
def each_stat_plot_climate(climate_table_city, keyword):
    if climate_table_city is None:
        raise ValueError("No Climate Table Found")

    list_months = ret_list_months(climate_table_city)

    list_vals_titles = ret_list_stat_values(climate_table_city, keyword)
    list_vals = list_vals_titles[0]
    name_y_axis = list_vals_titles[1]
    # constructing the dataframe

    dict_val_plot = {"Month": list_months, name_y_axis: list_vals}
    df_data = pd.DataFrame(dict_val_plot, list_months)
    df_data = df_data.reset_index(drop=True)

    return df_data, name_y_axis


# function that plots the data given the table, type of stat and the title of the plot
def plot_screen(climate_table_city, keyword, title_plot):
    df_tuple = each_stat_plot_climate(climate_table_city, keyword)
    df_data = df_tuple[0]
    name_y_axis = df_tuple[1]
    figure(num=None, figsize=(16, 9), dpi=70, facecolor='w', edgecolor='k')
    plt.scatter(df_data["Month"], df_data[name_y_axis], marker='o')
    plt.xlabel("Month")
    plt.ylabel(name_y_axis)
    if "vte" in title_plot:
        parts = title_plot.split("vte")
        title_plot = parts[1]
    if "edit" in title_plot:
        part_edit = title_plot.split("edit")
        title_plot = part_edit[0].strip() + part_edit[1]
    plt.title(title_plot)


# function that returns the appropriate url for the city
def return_city_url(city_name):
    assert city_name is not None
    starting_letter = city_name[0]
    f_spec_html = open(os.path.join("app", "city_html_files", starting_letter.upper() + ".html"), encoding="utf-8")
    html_text = f_spec_html.read()
    f_spec_html.close()
    doc = BeautifulSoup(html_text, "html.parser")
    table = doc.find("table")
    rows = table.find_all("tr")
    find_url = ""
    for each_row in rows:

        data = each_row.find("td")
        if data is None:
            continue
        data_str = data.get_text()
        if "," in data_str:
            parts = data.get_text().split(",")
            data_str = parts[0] + parts[1]
        if data_str.lower() == city_name.lower():
            a_tag = data.find("a", href=True)
            link_val = a_tag["href"]
            find_url = "https://en.wikipedia.org/" + link_val
            break
    return find_url


# function that finds the table and plots a graph using that data
def city_stat_plot(name, stat_type, specific_stat):
    find_url = return_city_url(name)
    download(name + "_data.html", find_url)
    climate_table_city_title = parse_html_tables(name + "_data.html", stat_type)
    climate_table_city = climate_table_city_title[0]
    title = climate_table_city_title[1]
    if title[0:3].lower() == "vte":
        title = title[3:]
    return plot_screen(climate_table_city, specific_stat, title)


# generates a list of URLs of cities starting with each letter of the alphabet
def generating_city_files():
    list_urls = []
    base_url = "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_100,000_or_more_inhabitants/cityname:_"
    for i in range(26):
        val = 65 + i
        append_letter = str(chr(val))
        list_urls.append(base_url + append_letter)

    # downloading each html file so that extraction of all cities is possible
    for each_url in list_urls:
        download(each_url[-1] + ".html", each_url)


# collecting all cities in alphabetical order in a complete list
def ret_list_alpha(html_file):
    list_letter = []
    f = open(os.path.join("app", "city_html_files", html_file), encoding="utf-8")
    html_text = f.read()
    f.close()
    doc = BeautifulSoup(html_text, "html.parser")
    table = doc.find("table")
    rows = table.find_all("tr")
    for each_row in rows:
        data = each_row.find("td")
        if data is None:
            continue
        list_letter.append(data.get_text().lower())
    return list_letter


# creating a list of all cities in alphabetical order
# then, writing it into a file
def writing_list_cities():
    list_cities = []
    if not os.path.exists(os.path.join("app", "static", "list_of_cities.txt")):
        for i in range(26):
            val = 65 + i
            file_name = str(chr(val)) + ".html"
            list_each_letter = ret_list_alpha(file_name)
            list_cities.extend(list_each_letter)
        f_cities_list = open(os.path.join("app", "static", "list_of_cities.txt"), "w", encoding="utf-8")
        for each_city in list_cities:
            str_city = each_city
            if "," in str_city:
                two_parts = str_city.split(",")
                str_city = two_parts[0] + two_parts[1]
            if each_city == list_cities[-1]:
                f_cities_list.write(str_city)
            else:
                f_cities_list.write(str_city + "\n")

        f_cities_list.close()


# generates a list of all possible climate stats
def create_list_cities():
    # creating a list of cities to work with throughout the code
    writing_list_cities()
    f_read_cities = open(os.path.join("app", "static", "list_of_cities.txt"), encoding="utf-8")
    str_contents = f_read_cities.read()
    list_cities = str_contents.split("\n")

    return list_cities


# returns the list of cities from the string input
def num_city_grabber(list_cities, list_stats, str_input):
    # city1, city2, type_stat
    tuple_cities = assign_city_type_stat(list_cities, list_stats, str_input, True)[:-1]
    city1 = tuple_cities[0]
    city2 = tuple_cities[1]
    parts = str_input.split(" ")
    for each in parts:
        for each_stat in list_stats:
            if each in each_stat and (each in city1 or each in city2):
                return 1
    if tuple_cities[1] == "" or tuple_cities[1] is None:
        return 1
    elif city1 in city2 or city2 in city1:
        return 1
    else:
        return 2


def create_list_stats(list_cities, str_input):
    city = assign_city(list_cities, str_input)
    if city == "":
        return -1
    city_url = return_city_url(city)
    download(city + "_data.html", city_url)
    table_climate = parse_html_tables(city + "_data.html", "climate")[0]
    if table_climate is None:
        raise ValueError("No Climate Table found for the Given City!")
    table_rows = table_climate.find_all("tr")
    table_rows = table_rows[2:]  # ignoring the table heading and month row
    list_stats = []
    for each_row in table_rows:
        each_th = each_row.find("th")
        if each_th is None:
            continue
        list_stats.append(each_th.get_text().lower().strip())
    return list_stats


def assign_city(list_cities, str_input):
    str_input = str_input
    city = check_hyphen(str_input, list_cities)
    if city is not None:
        return city
    else:
        all_matches = []
        # here is where you check for the city in input
        for i in range(len(list_cities)):
            if list_cities[i] in str_input:
                all_matches.append(list_cities[i])

        flag = 1
        text = nltk.word_tokenize(str_input)
        for each_match in all_matches:
            if each_match in text:
                flag = 0
                break

        if flag == 1:
            all_matches = []
            for each_word in text:
                for i in range(len(list_cities)):
                    if each_word in list_cities[i]:
                        all_matches.append(list_cities[i])

        if len(all_matches) == 0:
            return None

        if len(all_matches) == 1:
            city = all_matches[0]
            return city
        else:
            max_len = len(all_matches[0])
            max_city = all_matches[0]
            for each_match in all_matches:
                if len(each_match) > max_len:
                    max_len = len(each_match)
                    max_city = each_match
            return max_city


def return_overlap_string(str1, str2):
    overlap_string = ""
    parts_str1 = str1.split(" ")
    parts_str2 = str2.split(" ")
    list_str1 = []
    list_str2 = []
    for each_section in parts_str1:
        list_str1.append(each_section)
    for each_section in parts_str2:
        list_str2.append(each_section)
    list_overlap = list(set(list_str1) & set(list_str2))
    if len(list_overlap) == 0:
        return None
    for each_entry in list_overlap:
        overlap_string += each_entry + " "
    return overlap_string.strip()


def ret_stat(list_stats, str_input):
    type_stat = ""
    stripped_list_stats = []
    for each_entry in list_stats:
        if "(" in each_entry:
            parts = each_entry.split("(")
            stripped_list_stats.append(parts[0].strip())
        else:
            stripped_list_stats.append(each_entry.strip())
    list_stats = stripped_list_stats

    for i in range(len(list_stats)):
        if list_stats[i] in str_input:
            type_stat = list_stats[i]

    if type_stat == "":
        for each_stat in list_stats:
            overlap_string = return_overlap_string(each_stat, str_input)
            if overlap_string is not None:
                break
        if overlap_string is not None:
            for each_stat in list_stats:
                if overlap_string in each_stat:
                    type_stat = each_stat

    if type_stat == "":
        text = nltk.word_tokenize(str_input)
        for each_word in text:
            for each_stat in list_stats:
                if each_word in each_stat:
                    type_stat = each_stat
                    break

    if "inches" in type_stat or "cm" in type_stat:
        part_unit = type_stat.split("inches")
        type_stat = part_unit[0]

    return type_stat


# given a string input, finds the required city and type of stat
def assign_city_type_stat(list_cities, list_stats, str_input, compare_bool=False):
    if not compare_bool:
        # here is where you check for the city in input
        given_city = assign_city(list_cities, str_input)
        type_stat = ret_stat(list_stats, str_input)
        return given_city, type_stat
    else:
        city2 = ""
        city1 = assign_city(list_cities, str_input)
        all_matches = []
        # here is where you check for the city in input
        for i in range(len(list_cities)):
            if list_cities[i] in str_input:
                if list_cities[i] == city1:
                    continue
                all_matches.append(list_cities[i])

        type_stat = ret_stat(list_stats, str_input)

        flag = 1
        text = nltk.word_tokenize(str_input)
        for each_match in all_matches:
            if each_match in text:
                flag = 0
                break

        if flag == 1:
            all_matches = []
            for each_word in text:
                list_word = [each_word]
                if nltk.pos_tag(list_word)[0][1] != 'NN':
                    continue

                for i in range(len(list_cities)):
                    if each_word in list_cities[i]:
                        all_matches.append(list_cities[i])

        if len(all_matches) == 0:
            return city1, city2, type_stat
        else:
            if len(all_matches) == 1:
                city2 = all_matches[0]
            else:
                max_len = len(all_matches[0])
                max_city = all_matches[0]
                for each_match in all_matches:
                    if len(each_match) > max_len and each_match != city1:
                        max_len = len(each_match)
                        max_city = each_match
                city2 = max_city
            type_stat = ret_stat(list_stats, str_input)
            return city1, city2, type_stat


# checks if there is a hyphenated city in input
def check_hyphen(str_input, list_cities):
    text = nltk.word_tokenize(str_input)
    for each_word in text:
        if "-" in each_word:
            parts = each_word.split("-")
            new_word = parts[0] + "–" + parts[1]
            if new_word in list_cities:
                given_city = each_word
                return given_city


# checks that the city or stat is non-empty
def check_empty_city_type(given_city, type_stat):
    assert given_city != "" and type_stat != ""


# checks if there are more than one city in input
def check_compare(list_cities, list_stats, str_input):
    if num_city_grabber(list_cities, list_stats, str_input) == 2:
        return True
    return False


# method that calls city_stat_plot() if there is only one city in the input
def single_plot(given_city, type_stat):
    city_stat_plot(given_city, "climate", type_stat)
    plt.savefig(os.path.join("app", "static", given_city + ".png"))


# method that handles plotting when there is comparison of ONE OR MORE CITIES
def double_city_plot(list_cities, list_stats, str_input):
    cities_stats = assign_city_type_stat(list_cities, list_stats, str_input, True)
    city1 = cities_stats[0]
    city2 = cities_stats[1]
    type_stat = cities_stats[2]
    assert city1 != "" and city1 is not None and city2 != "" and city2 is not None and type_stat != "" and type_stat is not None
    download(city1 + "_data.html", return_city_url(city1))
    download(city2 + "_data.html", return_city_url(city2))
    tuple_city1 = parse_html_tables((city1 + "_data.html"), "climate")
    table_city1 = tuple_city1[0]
    table_city1_title = tuple_city1[1]
    tuple_city2 = parse_html_tables((city2 + "_data.html"), "climate")
    table_city2 = tuple_city2[0]
    table_city2_title = tuple_city2[1]
    list_months = ret_list_months(table_city1)
    list_specs_city1_title = ret_list_stat_values(table_city1, type_stat)
    list_specs1 = list_specs_city1_title[0]
    y_axis_title = list_specs_city1_title[1]
    list_specs_city2_title = ret_list_stat_values(table_city2, type_stat)
    list_specs2 = list_specs_city2_title[0]
    figure(num=None, figsize=(16, 9), dpi=70, facecolor='w', edgecolor='k')
    plt.scatter(list_months, list_specs1, marker='x', label=city1.capitalize())
    plt.scatter(list_months, list_specs2, marker='s', label=city2.capitalize())
    if "Climate data for" in table_city1_title and "Climate data for" in table_city2_title:
        if "edit" in table_city1_title:
            parts = table_city1_title.split("edit")
            table_city1_title = parts[0] + parts[1]
            if table_city1_title[0:3].lower() == "vte":
                table_city1_title = table_city1_title[3:]
        if "edit" in table_city2_title:
            parts = table_city2_title.split("edit")
            table_city2_title = parts[0] + parts[1]
        combined_title = table_city1_title + " and" + table_city2_title.split("Climate data for")[1]
        if "vte" in combined_title:
            parts_vte = combined_title.split("vte")
            combined_title = parts_vte[1]
        plt.title(combined_title)
    plt.xlabel("Month")
    plt.ylabel(y_axis_title)
    plt.legend(loc='best')
    if city1 < city2:
        plt.savefig(os.path.join("app", "static", city1 + ".png"))
        return city1
    else:
        plt.savefig(os.path.join("app", "static", city2 + ".png"))
        return city2


def main(str_input):
    str_input = str_input.lower()
    plt.clf()
    generating_city_files()
    list_cities = create_list_cities()
    try:
        list_stats = create_list_stats(list_cities, str_input)
    except ValueError:
        raise ValueError("")
        print("No Climate Table found for the given city")
        return
    except AssertionError:
        print("Your sentence does not contain a city, or the city has a population lesser than 100k")
        return
    if list_stats == -1:
        print("Your sentence does not contain a city, or the city has a population lesser than 100k")
        return
    if not check_compare(list_cities, list_stats, str_input):
        given_city = check_hyphen(str_input, list_cities)
        tuple_city_stat = assign_city_type_stat(list_cities, list_stats, str_input)
        if given_city == "" or given_city is None:
            given_city = tuple_city_stat[0]
        type_stat = tuple_city_stat[1]
        try:
            check_empty_city_type(given_city, type_stat)
        except AssertionError:
            if given_city == "" or given_city is None:
                print("Your sentence does not contain a city, or the city has a population lesser than 100k")
            if type_stat == "" or type_stat is None:
                print("Your sentence does not contain a recognized climate statistic for this city")
            return
        single_plot(given_city, type_stat)
        return given_city
    else:
        try:
            return double_city_plot(list_cities, list_stats, str_input.lower())
        except AssertionError:
            print("Your sentence does not contain a city, or the city has a population lesser than 100k")
            print("or your sentence doesn't contain a recognized climate statistic for this city")


main("madison and chicago snow")