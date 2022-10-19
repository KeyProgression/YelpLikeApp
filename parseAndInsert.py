#!/usr/bin/env python
import json
import os
import psycopg2


def main():
    # Parsing JSON data and loading corresponding data into the database
    insert2BusinessTable()
    #parse_checkin()

    # Loading association tables
    load_hascategory()
    load_hashours()


def clean_sql_string(string):
    return string.replace("'", "`").replace("\n", " ")


def split_date_time(string):
    current = ""

    date = None

    for char in string:
        if char != " ":
            current += char
        else:
            date = current
            current = ""

    time = current
    current = ""
    split_times = []

    for char in date:
        if char != "-":
            current += char
        else:
            split_times.append(current)
            current = ""

    split_times.append(current)

    return split_times[0], split_times[1], split_times[2], time  # year, month, day, time


def split_categories(category_string):
    categories = []
    clean_categories = []
    current = ""

    for char in category_string:
        if char != ",":
            current += char
        else:
            categories.append(current)
            current = ""

    categories.append(current)

    # Removing spaces following commas for each item except the first
    clean_categories.append(categories[0])

    for i in range(1, len(categories), 1):
        category = categories[i][1:len(categories[i])]
        clean_categories.append(category)

    return clean_categories


def insert2BusinessTable():
    # Specifying file names
    json_file = "yelp_business.JSON"
    output_file = "output/business.txt"

    # Printing current process to console
    print("Loading table: business\n"
          "Input file: {}".format(json_file))

    # Creating folder to store output files if it doesn't already exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Opening JSON file
    with open(json_file, 'r') as f:
        out_file = open(output_file, 'w')
        line = f.readline()
        line_count = 0
        error_count = 0

        content = json.loads(line)
        headers = []

        for key in content:
            headers.append(key)

        headers.pop()
        out_file.write("Headers: {}\n\n".format(headers))

        # Connecting to database
        try:
            conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password=''")
        except:
            print("ERROR - Unable to connect to database.")

        cur = conn.cursor()

        # Reading and extracting data from each JSON object
        while line:
            # Extracting data from the current JSON object
            data = json.loads(line)

            business_id = data["business_id"]
            name = data["name"]
            address = data["address"]
            city = data["city"]
            state = data["state"]
            postal_code = data["postal_code"]
            latitude = str(data["latitude"])
            longitude = str(data["longitude"])
            stars = str(data["stars"])
            review_count = str(data["review_count"])
            is_open = str(data["is_open"])
            attributes = str(data["attributes"])
           # categories = str(data["categories"])
          #  for c in categories:
           #     pass

            # Inserting record into database
            sql_str = "INSERT INTO business(business_id, " \
                      "business_name, " \
                      "address, " \
                      "city, " \
                      "state_name, " \
                      "zip_code, " \
                      "latitude, " \
                      "longitude, " \
                      "business_avg_star, " \
                      "review_count, " \
                      "is_open, " \
                      "num_of_tips, " \
                      "num_of_checkins) " \
                      "VALUES('" + data['business_id'] + "', '" +\
                      clean_sql_string(data["name"]) + "', '" + \
                      clean_sql_string(data["address"]) + "', '" + \
                      clean_sql_string(data["city"]) + "', '" + \
                      clean_sql_string(data["state"]) + "', " + \
                      data["postal_code"] + ", " + \
                      str(data["latitude"]) + ", " + \
                      str(data["longitude"]) + ", " + \
                      str(data["stars"]) + ", " + \
                      str(data["review_count"]) + ", '" + \
                      str(is_open) + "', 0, 0);"

            try:
                cur.execute(sql_str)
            except:
                error_count += 1
                print("ERROR - Insert statement failed on business table.")
                print(sql_str)
                print("")

            conn.commit()

            # Writing parsed data to file
            out_file.write("Business:\t\t{}, {}\n".format(name, business_id))
            out_file.write("Location:\t\t{} {} {} {}, ({}, {})\n".format(address,
                                                                         city,
                                                                         state,
                                                                         postal_code,
                                                                         latitude,
                                                                         longitude))
            out_file.write("Reviews:\t\t{}, {}\n".format(stars, review_count))
            out_file.write("Open:\t\t\t{}\n".format(is_open))
            out_file.write("Attributes:\t\t{}\n".format(attributes))
            # out_file.write("Categories:\t\t{}\n".format(categories))

            out_file.write('\n')

            # Reading next line and incrementing line counter
            line = f.readline()
            line_count += 1

    # Display number of records processed
    out_file.write("Processed {} records.".format(line_count))

    # Closing file
    out_file.close()
    f.close()

    # Printing results
    print("Processed: {}, Errors: {}, Lines: {}, Output: {}\n".format(json_file, error_count, line_count, output_file))

"""
def parse_checkin():
    # Specifying file names
    json_file = "yelp_checkin.JSON"
    output_file = "output/checkin.txt"

    # Printing current process to console
    print("Loading table: yelpcheckin\n"
          "Input file: {}".format(json_file))

    # Creating folder to store output files if it doesn't already exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Opening JSON file
    with open(json_file, 'r') as f:
        out_file = open(output_file, 'w')
        line = f.readline()
        line_count = 0
        error_count = 0

        content = json.loads(line)
        headers = []

        for key in content:
            headers.append(key)

        out_file.write("Headers: {}\n\n".format(headers))

        # Connecting to database
        try:
            conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password=''")
        except:
            print("ERROR - Unable to connect to database.")

        cur = conn.cursor()

        # Reading and extracting data from each JSON object
        while line:
            data = json.loads(line)
            out_file.write("Business:\t{}\n".format(data["business_id"]))
            out_file.write("Check-ins:\t")

            date = data["time"]
            current = ""
            split_dates = []
            tuples = []

            for char in date:
                if char != ",":
                    current += char
                else:
                    split_dates.append(current)
                    current = ""

            split_dates.append(current)

            for date in split_dates:
                year = date[0:4]
                month = date[5:7]
                day = date[8:10]
                time = date[11:19]

                tuples.append((year, month, day, time))

            # Inserting records into database and generating text output.
            for item in tuples:
                sql_str = "INSERT INTO yelpcheckin(business_id, " \
                          "checkin_year, " \
                          "checkin_month, " \
                          "checkin_day, " \
                          "checkin_time) " \
                          "VALUES('" + data['business_id'] + "', " + \
                          item[0] + ", " + \
                          item[1] + ", " + \
                          item[2] + ", '" + \
                          item[3] + "'" \
                          ");"

                try:
                    cur.execute(sql_str)
                except:
                    error_count += 1
                    print("ERROR - Insert statement failed on checkin table.")
                    print(sql_str)
                    print("")

                conn.commit()

                out_file.write(str(item))

            out_file.write('\n\n')

            line = f.readline()
            line_count += 1

    # Display number of records processed
    out_file.write("Processed {} records.".format(line_count))

    # Closing file
    out_file.close()
    f.close()

    # Printing results
    print("Processed: {}, Errors: {}, Lines: {}, Output: {}\n".format(json_file, error_count, line_count, output_file))
"""

def load_hascategory():
    # Specifying file names
    json_file = "yelp_business.JSON"
    output_file = "output/hascategory.txt"

    # Printing current process to console
    print("Loading table: hascategory\n"
          "Input file: {}".format(json_file))

    # Creating folder to store output files if it doesn't already exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Opening JSON file
    with open(json_file, 'r') as f:
        out_file = open(output_file, 'w')
        line = f.readline()
        line_count = 0
        error_count = 0

        content = json.loads(line)
        headers = []

        for key in content:
            headers.append(key)

        out_file.write("Headers: {}\n\n".format(headers))

        # Connecting to database
        try:
            conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password=''")
        except:
            print("ERROR - Unable to connect to database.")

        cur = conn.cursor()

        # Reading and extracting data from each JSON object
        while line:
            data = json.loads(line)

            business_id = data["business_id"]
            categories = data["categories"]

            out_file.write("Business:\t\t{}\n".format(business_id))
            out_file.write("Categories:\t\t\t{}\n".format(categories))

            # Splitting categories for database insertion
            business_categories = split_categories(categories)

            # Inserting records into database and generating text output.
            for category in business_categories:
                clean_category = clean_sql_string(category)

                sql_str = "INSERT INTO hascategory(business_id, " \
                          "category_type) " \
                          "VALUES('" + data['business_id'] + "', '" + \
                          clean_category + "'" \
                          ");"

                try:
                    cur.execute(sql_str)
                except:
                    error_count += 1
                    print("ERROR - Insert statement failed on tip table.")
                    print(sql_str)
                    print("")

            conn.commit()

            out_file.write('\n')

            line = f.readline()
            line_count += 1

    # Display number of records processed
    out_file.write("Processed {} records.".format(line_count))

    # Closing file
    out_file.close()
    f.close()

    # Printing results
    print("Processed: {}, Errors: {}, Lines: {}, Output: {}\n".format(json_file, error_count, line_count, output_file))


def load_hashours():
    # Specifying file names
    json_file = "yelp_business.JSON"
    output_file = "output/hashours.txt"

    # Printing current process to console
    print("Loading table: hashours\n"
          "Input file: {}".format(json_file))

    # Creating folder to store output files if it doesn't already exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Opening JSON file
    with open(json_file, 'r') as f:
        out_file = open(output_file, 'w')
        line = f.readline()
        line_count = 0

        content = json.loads(line)
        headers = []
        error_count = 0

        for key in content:
            headers.append(key)

        headers.pop()
        out_file.write("Headers: {}\n\n".format(headers))

        # Connecting to database
        try:
            conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password=''")
        except:
            print("ERROR - Unable to connect to database.")

        cur = conn.cursor()

        # Reading and extracting data from each JSON object
        while line:
            data = json.loads(line)
            out_file.write("Business:\t{}\n".format(data["business_id"]))
            tuples2 = []
            hours = data["hours"]

            for key, value in hours.items():
                time = value.split("-")
                open_hour = time[0]
                close_hour = time[1]

                tuples2.append((key, open_hour, close_hour))

            for item in tuples2:
                sql_str = "INSERT INTO hashours(business_id, " \
                          "dayofweek, " \
                          "open_hour, " \
                          "close_hour) " \
                          "VALUES('" + clean_sql_string(data['business_id']) + "', '" + \
                           item[0] + "', '" + \
                           item[1] + "', '" + \
                           item[2] + "'" \
                           ");"

                try:
                    cur.execute(sql_str)
                except:
                    error_count += 1
                    print("ERROR - Insert statement failed on hashours table.")
                    print(sql_str)
                    print("")

                conn.commit()

                out_file.write("day_of_week:\t{}\n".format(key))
                out_file.write("hours:\t open {} \t close {}\n".format(item[1],item[2]))

                out_file.write('\n\n')

            line = f.readline()
            line_count += 1

    # Display number of records processed
    out_file.write("Processed {} records.".format(line_count))

    # Closing file
    out_file.close()
    f.close()

    # Printing results
    print("Processed: {}, Errors: {}, Lines: {}, Output: {}\n".format(json_file, error_count, line_count, output_file))


if __name__ == "__main__":
    main()
