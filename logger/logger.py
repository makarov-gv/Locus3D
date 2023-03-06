import gs_lps
import timeit
import pandas as pd
import json


if __name__ == '__main__':
    gs_lps = gs_lps.us_nav()
    gs_lps.start()
    timer = timeit.default_timer()
    df0 = pd.DataFrame()
    while timeit.default_timer()-timer < 120:
        data = [gs_lps.get_position(), gs_lps.get_angles(), timeit.default_timer()-timer]
        df = pd.DataFrame(
            [data], columns=['Position', 'Angles', 'Time']
        )
        df0 = pd.concat([df0, df])
    result = df0.to_json(orient='records')
    parsed = json.loads(result)
    with open('log.json', 'w') as f:
        json.dump(parsed, f, indent=2)
    gs_lps.stop()
    exit()
