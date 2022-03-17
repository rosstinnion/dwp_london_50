import requests     # http module
import math         # math module needed for distance calculations sin / cos etc
import re           # regular expressions module

# base url for api
api_user_details_url = "https://bpdts-test-app.herokuapp.com/user/"

# longitude / latitude of London
london_latitude = 51.5072
london_longitude = -0.1276


# convert degrees to radians
def to_radians(degree):
    one_degree = math.pi / 180
    return one_degree * float(degree)


# calculate distance between two point
# wiki page here https://en.wikipedia.org/wiki/Haversine_formula although I didn't use this formula
def distance_between_two_points(long1, lat1, long2, lat2):
    latitude1 = to_radians(float(lat1))
    longitude1 = to_radians(float(long1))
    latitude2 = to_radians(float(lat2))
    longitude2 = to_radians(float(long2))

    # Haversine Formula
    long = longitude2 - longitude1
    lat = latitude2 - latitude1
    answer = pow(math.sin(lat / 2), 2) + math.cos(latitude1) * math.cos(latitude2) * pow(math.sin(long / 2), 2)
    answer = 2 * math.asin(math.sqrt(answer))

    # Radius of Earth in Miles = 3956
    radius_of_earth = 3956

    # Calculate the result
    answer = answer * radius_of_earth

    return answer


# call endpoint to get users by city
def get_user_by_city(city):
    api_city_users_url = f"https://bpdts-test-app.herokuapp.com/city/{city}/users"
    city_response = requests.get(api_city_users_url)
    return city_response.json()


# call endpoint to get user by id
def get_user_by_id(user_id):
    api_single_user_url = f"{api_user_details_url}{['user_id']}"
    user_id_response = requests.get(api_single_user_url)
    return user_id_response.json()


# call endpoint to find all users
def get_all_users():
    api_all_users_url = "https://bpdts-test-app.herokuapp.com/users"
    all_users_response = requests.get(api_all_users_url)
    return all_users_response.json()


# get the reported city for a given IP address
def get_city_by_ip(ip_address):
    ip_city = "unknown"

    if validate_ip(str(ip_address)) == 0:
        return ip_city

    api_ip_lookup_url = "https://ip-api.io/json/"
    response = requests.get(f"{api_ip_lookup_url}{ip_address}")

    # If good response, city will be found in response, else return unknown as call failed
    if "city" in response:
        ip_city = str.lower(response["city"])

    return ip_city


# format the output of the user object
def user_object_friendly_output_string(user_parameter):
    distance = distance_between_two_points(london_longitude, london_latitude, user_parameter["longitude"], user_parameter["latitude"])
    return f"name:{user_parameter['first_name']} {user_parameter['last_name']} " \
           f"longitude:{user_parameter['longitude']} latitude:{user_parameter['latitude']} Distance from London:{distance:.2f} miles"


def validate_ip(ip_address):
    regex = '^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'

    if re.search(regex, ip_address):
        return 1

    return 0


london_users = get_user_by_city('London')

# print out all users found by city of London search, ignoring longitude and latitude

print('Output from User by City')

for user in london_users:
    print(f'London User found by City Search:{user_object_friendly_output_string(user)}')


print("Output from longitude/latitude calculation")

all_users = get_all_users()

# loop through all users and calculate distance from London using longitude and latitude
for user in all_users:

    # call endpoint to get user by id
    user_details = ""
    # This call can be implemented if we want to check by user id if their city is London
    # user_details = get_user_by_id(user["id"])

    # get city reported for user
    user_details_city = "unknown"
    if "city" in user_details:
        user_details_city = str(user_details['city'])

    ip = str(user['ip_address'])

    # This call can be implemented if we want to check if the IP address reports back as London, not reliable but possible
    # get the city associated with IP
    user_city_by_ip = ""
    # user_city_by_ip = get_city_by_ip(ip)

    # get geographic distance of user from London using longitude and latitude
    distance_from_london = distance_between_two_points(london_longitude, london_latitude, user["longitude"], user["latitude"])

    # if user is less than or equal to 50 miles from the centre of London, print out the result
    if distance_from_london <= 50:
        print("\rLongitude and latitude indicate user is within 50 miles of London : ", end="")
        print(user_object_friendly_output_string(user))

print('\rEND')
