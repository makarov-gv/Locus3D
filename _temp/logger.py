import gs_lps
import timeit
import time
import pandas as pd
import json


if __name__ == '__main__':
    gs_lps = gs_lps.us_nav()
    gs_lps.start()
    timer = timeit.default_timer()
    df0 = pd.DataFrame()
    while timeit.default_timer()-timer < 120:
        data = [list(gs_lps.get_position()), timeit.default_timer()-timer]
        df = pd.DataFrame(
            [data], columns=['Positions, meters', 'Time passed, seconds']
        )
        df0 = pd.concat([df0, df])
        print(data)
        # time.sleep(0.1)
    result = df0.to_json(orient='records')
    parsed = json.loads(result)
    with open('log.json', 'w') as f:
        json.dump(parsed, f, indent=2)
    gs_lps.stop()
    exit()
