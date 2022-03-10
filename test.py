import ht_parser

# countries = ht_parser.get_countries()
# print(countries['1'])

regions = ht_parser.get_depart_cities()
# print(regions)

search_filter = {'country_id': '18', 'region_id': '', 'departy_city_id': '2',
                 'month': 3, 'year': 2022, 'day': 11, 'adult': 3, 'child': 1,
                 'child_ages': 11}

ht_parser.parse_tours(search_filter)
