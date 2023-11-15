import argparse
import sys


class CLIArgumentsParserHelper:
    @staticmethod
    def get():
        parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
        parser.add_argument("--bulk_scrape", nargs='?', type=str, default="False",
                            help="Boolean variable to bulk scrape companies. Default False. If set to True, save_to_db will also be set to True")
        parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
        parser.add_argument("--save_to_db", nargs='?', type=str, default="False",
                            help="Boolean variable to save to db. Default False")
        parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
        parser.add_argument("--log_file", nargs='?', type=str, default=None,
                            help="Path for log file. If not given, output will be printed on stdout.")
        parser.add_argument("--urls_from_file", nargs='?', type=str, default=None, help="Load urls from file")
        parser.add_argument("--grabber-bbb-mustansir", nargs='?', type=bool, default=False,
                            help="Only mark to kill all")
        parser.add_argument("--proxy", nargs='?', type=str, default=None, help="Set proxy for scan")

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        return parser.parse_args()
