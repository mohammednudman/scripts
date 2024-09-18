import pandas as pd
from datetime import datetime, timedelta

file_path = 'time.data'
current_date = datetime.now().strftime('%Y-%m-%d')
output_file = f'{current_date}.csv'
chunk_size = 10_000

def nanoseconds_to_readable(ns):
    seconds = ns // 1_000_000_000
    nanoseconds = ns % 1_000_000_000
    timestamp = datetime(1970, 1, 1) + timedelta(seconds=seconds)
    return f"{timestamp.strftime('%H:%M:%S')}.{nanoseconds:09d}"

def nanoseconds_to_seconds(ns):
    return ns / 1_000_000_000

def process_event_data(df):
    df['T2-T1'] = nanoseconds_to_seconds(df['ts_tcp_recv'] - df['ts_amps'])
    df['T3-T2'] = nanoseconds_to_seconds(df['ts_thr_recv'] - df['ts_tcp_recv'])
    df['T4-T3'] = nanoseconds_to_seconds(df['ts_converted'] - df['ts_thr_recv'])
    df['T5-T4'] = nanoseconds_to_seconds(df['ts_written'] - df['ts_converted'])
    df['T5-T2'] = nanoseconds_to_seconds(df['ts_written'] - df['ts_tcp_recv'])
    return df

def main():
    df_all = pd.DataFrame()

    for chunk in pd.read_csv(file_path, sep=' ', header=None,
                             names=['option_emm_id', 'underlying_emm_id',
                                    'ts_amps', 'ts_tcp_recv', 'ts_thr_recv',
                                    'ts_converted', 'ts_written'],
                             chunksize=chunk_size, dtype='int64'):
        chunk_processed = process_event_data(chunk)

        df_all = pd.concat([df_all, chunk_processed], ignore_index=True)

    df_all.to_csv(output_file, index=False, float_format='%.9f')

    print(f"Data written to {output_file}")

if __name__ == "__main__":
    main()
