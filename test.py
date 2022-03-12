import asyncio
import ht_parser


async def main():
    search_filter = {'country_id': '18', 'region_id': '',
                     'departy_city_id': '2',
                     'month': 3, 'year': 2022, 'day': 13,
                     'adult': 3, 'child': 1,
                     'child_ages': 11}

    await ht_parser.parse_tours(search_filter)


if __name__ == "__main__":
    asyncio.run(main())
