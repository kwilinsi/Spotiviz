GET_RECENT_PROJECTS = 'SELECT * FROM Projects ' \
                      'ORDER BY created_at desc LIMIT ?;'
