CONFIG = {
    'TEAMS': {'Team #{}'.format(i): '10.0.{}.1'.format(i)
              for i in range(1, 20)},
    'FLAG_FORMAT': r'[A-Z0-9]{31}=',

    # 'SYSTEM_PROTOCOL': 'ructf_tcp',
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,

    'SYSTEM_PROTOCOL': 'ructf_http',
    'SYSTEM_URL': 'http://10.20.0.2:8080/flags',
    'SYSTEM_TOKEN': '14_cbdcb7fbc607f88d',

    # 'SYSTEM_PROTOCOL': 'volgactf',
    # 'SYSTEM_HOST': '127.0.0.1',

    # 'SYSTEM_PROTOCOL': 'forcad_tcp',
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,
    # 'TEAM_TOKEN': 'your_secret_token',

    # The server will submit not more than SUBMIT_FLAG_LIMIT flags
    # every SUBMIT_PERIOD seconds. Flags received more than
    # FLAG_LIFETIME seconds ago will be skipped.
    'SUBMIT_FLAG_LIMIT': 20,
    'SUBMIT_PERIOD': 15,
    'FLAG_LIFETIME': 15 * 60,

    
    'SERVER_USERNAME': 'qarabag69',    
    'SERVER_PASSWORD': '$ra01vz&q10',

    # Use authorization for API requests (хуйня не понимаю что это такое вообще)
    'ENABLE_API_AUTH': False,
    'API_TOKEN': '00000000000000000000'
}
