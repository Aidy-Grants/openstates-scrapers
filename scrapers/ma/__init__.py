import re
import requests
import lxml.html
from openstates.scrape import State
from .bills import MABillScraper
from .events import MAEventScraper


class Massachusetts(State):
    scrapers = {
        "bills": MABillScraper,
        "events": MAEventScraper,
    }
    legislative_sessions = [
        # {
        #     "_scraped_name": "186th",
        #     "classification": "primary",
        #     "identifier": "186th",
        #     "name": "186th Legislature (2009-2010)",
        #     "start_date": "2009-01-07",
        #     "end_date": "2010-07-31",
        # },
        # {
        #     "_scraped_name": "187th",
        #     "classification": "primary",
        #     "identifier": "187th",
        #     "name": "187th Legislature (2011-2012)",
        #     "start_date": "2011-01-05",
        #     "end_date": "2012-07-31",
        # },
        # {
        #     "_scraped_name": "188th",
        #     "classification": "primary",
        #     "identifier": "188th",
        #     "name": "188th Legislature (2013-2014)",
        #     "start_date": "2013-01-02",
        #     "end_date": "2014-08-01",
        # },
        # {
        #     "_scraped_name": "189th",
        #     "classification": "primary",
        #     "identifier": "189th",
        #     "name": "189th Legislature (2015-2016)",
        #     "start_date": "2015-01-07",
        #     "end_date": "2016-07-31",
        # },
        # {
        #     "_scraped_name": "190th",
        #     "classification": "primary",
        #     "identifier": "190th",
        #     "name": "190th Legislature (2017-2018)",
        #     "start_date": "2017-01-04",
        #     "end_date": "2018-12-31",
        # },
        # {
        #     "_scraped_name": "191st",
        #     "classification": "primary",
        #     "identifier": "191st",
        #     "name": "191st Legislature (2019-2020)",
        #     "start_date": "2019-01-02",
        #     "end_date": "2021-01-06",
        # },
        # {
        #     "_scraped_name": "192nd",
        #     "classification": "primary",
        #     "identifier": "192nd",
        #     "name": "192nd Legislature (2021-2022)",
        #     "start_date": "2021-01-06",
        #     "end_date": "2021-12-31",
        #     "active": False,
        # },
        {
            "_scraped_name": "193rd",
            "classification": "primary",
            "identifier": "193rd",
            "name": "193rd Legislature (2023-2024)",
            "start_date": "2023-01-04",
            "end_date": "2024-07-31",  # https://malegislature.gov/ClerksOffice/Senate/Deadlines
            "active": True,
        },
    ]
    ignored_scraped_sessions = [
        "192nd",
        "191st",
        "190th",
        "189th",
        "188th",
        "187th",
        "186th",
        "2022 Regular Session",
        "2021 Regular Session",
        "2020 Regular Session",
        "2019 Regular Session",
        "2018 Regular Session",
        "2017 Regular Session",
        "2016 Regular Session",
        "2015 Regular Session",
        "2014 Regular Session",
        "2013 Regular Session",
        "2012 Regular Session",
        "2011 Regular Session",
        "2010 Regular Session",
        "2009 Regular Session",
        "2008 Regular Session",
        "2007 Regular Session",
        "2006 Regular Session",
        "2005 Regular Session",
        "2004 Regular Session",
        "2003 Regular Session",
        "2002 Regular Session",
        "2001 Regular Session",
        "2000 Regular Session",
        "1999 Regular Session",
        "1998 Regular Session",
        "1997 Regular Session",
        "1996 Regular Session",
        "1995 Regular Session",
        "1994 Regular Session",
        "1993 Regular Session",
        "1992 Regular Session",
        "1991 Regular Session",
        "1990 Regular Session",
        "1989 Regular Session",
        "1988 Regular Session",
        "1987 Regular Session",
        "1986 Regular Session",
        "1985 Regular Session",
        "1984 Regular Session",
        "1983 Regular Session",
        "1982 Regular Session",
        "1981 Regular Session",
        "1980 Regular Session",
        "1979 Regular Session",
        "1978 Regular Session",
        "1977 Regular Session",
        "1976 Regular Session",
        "1975 Regular Session",
        "1974 Regular Session",
        "1973 Regular Session",
        "1972 Regular Session",
        "1971 Regular Session",
    ]

    def get_session_list(self):
        doc = lxml.html.fromstring(
            requests.get("https://malegislature.gov/Bills/Search", verify=False).text
        )
        sessions = doc.xpath(
            "//div[@data-refinername='lawsgeneralcourt']/div/label/text()"
        )

        # Remove all text between parens, like (Current) (7364)
        return list(
            filter(
                None,
                [re.sub(r"\([^)]*\)", "", session).strip() for session in sessions],
            )
        )
