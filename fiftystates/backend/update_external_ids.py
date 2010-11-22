#!/usr/bin/env python

from fiftystates import settings
from fiftystates.backend import db

import re
import datetime

import argparse
import name_tools
import pymongo

from votesmart import votesmart, VotesmartApiError
votesmart.apikey = getattr(settings, 'VOTESMART_API_KEY', '')

def update_votesmart_legislators(state):
    current_term = state['terms'][-1]['name']

    query = {'roles': {'$elemMatch':
                       {'type': 'member',
                        'state': state['abbreviation'],
                        'term': current_term}
                      },
             'votesmart_id': None,
            }

    updated = 0
    initial_count = db.legislators.find(query).count()

    # get officials
    abbrev = state['_id'].upper()
    upper_officials = votesmart.officials.getByOfficeState(9, abbrev)
    try:
        lower_officials = votesmart.officials.getByOfficeState(8, abbrev)
    except VotesmartApiError:
        lower_officials = votesmart.officials.getByOfficeState(7, abbrev)

    def _match(chamber, vsofficials):
        updated = 0
        for unmatched in db.legislators.find(dict(query, chamber=chamber)):
            for vso in vsofficials:
                if (unmatched['district'] == vso.officeDistrictName and
                    unmatched['last_name'] == vso.lastName):
                    unmatched['votesmart_id'] = vso.candidateId
                    db.legislators.save(unmatched, safe=True)
                    updated += 1
        return updated

    updated += _match('upper', upper_officials)
    updated += _match('lower', lower_officials)

    print 'Updated %s of %s missing votesmart ids' % (updated, initial_count)



def update_missing_ids(state_abbrev):
    state = db.metadata.find_one({'_id': state_abbrev.lower()})
    if not state:
        print "State '%s' does not exist in the database." % (
            state_abbrev)
        sys.exit(1)

    print "Updating PVS legislator ids..."
    update_votesmart_legislators(state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        add_help=False,
        description=('attempt to match legislators with ids in other'
                     'relevant APIs'))

    parser.add_argument('states', metavar='STATE', type=str, nargs='+',
                        help='states to update')
    parser.add_argument('--votesmart_key', type=str,
                        help='the Project Vote Smart API key to use')

    args = parser.parse_args()

    if args.votesmart_key:
        votesmart.apikey = args.votesmart_key

    for state in args.states:
        update_missing_ids(state)

