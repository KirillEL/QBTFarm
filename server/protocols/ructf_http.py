import requests

from server import app
from server.models import FlagStatus, SubmitResult

RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over', 'is not up',
                        'no such flag'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat', '200'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own',
                          'too old', 'not in database', 'already submitted', 'invalid flag', '400', '403'],
}
# The RuCTF checksystem adds a signature to all correct flags. It returns
# "invalid flag" verdict if the signature is invalid and "no such flag" verdict if
# the signature is correct but the flag was not found in the checksystem database.
#
# The latter situation happens if a checker puts the flag to the service before putting it
# to the checksystem database. We should resent the flag later in this case.


TIMEOUT = 5


def submit_flags(flags, config):
    for item in flags:

        r = requests.get(config['SYSTEM_URL'],
                         params={'teamid': 'qarabagteam', 'flag': item},
                         timeout=TIMEOUT)

        response_status = r.status_code
        if response_status == 200:
            found_status = FlagStatus.ACCEPTED
        elif response_status == 400 or response_status == 403:
            found_status = FlagStatus.REJECTED
        else:
            found_status = FlagStatus.QUEUED

        # unknown_responses = set()
        # for item in r.json():
        #     response = item['msg'].strip()
        #     response = response.replace('[{}] '.format(item['flag']), '')
        #
        #     response_lower = response.lower()
        #     for status, substrings in RESPONSES.items():
        #         if any(s in response_lower for s in substrings):
        #             found_status = status
        #             break
        #     else:
        #         found_status = FlagStatus.QUEUED
        #         if response not in unknown_responses:
        #             unknown_responses.add(response)
        #             app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)

        yield SubmitResult(item['flag'], found_status, response_status)
