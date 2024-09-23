import json
from datetime import datetime, timezone
import statistics
import argparse


def parse_time_data_to_matrix(file_path, limit_time_ns=None):
    matrix = []

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()

            if parts[0] == '*' or all(ts == '0' for ts in parts[2:7]):
                continue

            try:
                option_emm_id = int(parts[0])
                timestamps = [int(ts) for ts in parts[2:7]]
                t2 = timestamps[0]

                t2_readable = datetime.fromtimestamp(t2 / 1_000_000_000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f UTC')
                print(f"t2 (human-readable): {t2_readable}")

                if limit_time_ns is not None and t2 > limit_time_ns:
                    break

            except ValueError:
                continue

            matrix.append([option_emm_id] + timestamps)

    return matrix


def compute_latencies(matrix):
    decode_latencies = []
    write_latencies_inserts = []
    write_latencies_updates = []
    jdl_latencies = []
    seen_keys = set()

    for event in matrix:
        option_emm_id = event[0]
        t2, t3, t4, t5 = event[2], event[3], event[4], event[5]

        jdl_latency = t5 - t2
        decode_latency = t4 - t3
        write_latency = t5 - t4

        jdl_latencies.append(jdl_latency)
        decode_latencies.append(decode_latency)

        if option_emm_id not in seen_keys:
            write_latencies_inserts.append(write_latency)
            seen_keys.add(option_emm_id)
        else:
            write_latencies_updates.append(write_latency)

    return {
        "jdl_latencies": jdl_latencies,
        "decode_latencies": decode_latencies,
        "write_latencies_inserts": write_latencies_inserts,
        "write_latencies_updates": write_latencies_updates,
    }


def calculate_statistics(latencies):
    if latencies:
        return {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
        }
    return {"min": None, "max": None, "mean": None, "median": None}


def extract_date_from_t2(t2_ns):
    date_obj = datetime.fromtimestamp(t2_ns / 1_000_000_000, tz=timezone.utc)
    return date_obj.strftime('%Y-%m-%d')


def convert_time_to_ns(time_str, reference_date):
    datetime_str = f"{reference_date} {time_str} UTC"
    time_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %Z")

    epoch_ns = int(time_obj.replace(tzinfo=timezone.utc).timestamp() * 1_000_000_000)
    return epoch_ns


def get_first_valid_t2(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()

            if parts[0] == '*' or all(ts == '0' for ts in parts[2:7]):
                continue

            try:
                t2 = int(parts[2])
                return t2
            except ValueError:
                continue

    return None


def main(input_file, time_limit=None):
    limit_time_ns = None

    first_t2 = get_first_valid_t2(input_file)

    if first_t2 is not None and time_limit is not None:
        reference_date = extract_date_from_t2(first_t2)
        limit_time_ns = convert_time_to_ns(time_limit, reference_date)

    matrix = parse_time_data_to_matrix(input_file, limit_time_ns)

    latency_data = compute_latencies(matrix)

    stats = {
        "jdl_latencies": calculate_statistics(latency_data["jdl_latencies"]),
        "decode_latencies": calculate_statistics(latency_data["decode_latencies"]),
        "write_latencies_inserts": calculate_statistics(latency_data["write_latencies_inserts"]),
        "write_latencies_updates": calculate_statistics(latency_data["write_latencies_updates"]),
    }

    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file = f"{current_date}.json"

    with open(output_file, 'w') as json_file:
        json.dump(stats, json_file, indent=4)

    print(f"Statistics saved to {output_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process time data file.')
    parser.add_argument('input_file', type=str, help='Path to the input data file')
    parser.add_argument('-t', '--time', type=str, help='Time limit in HH:MM:SS format (UTC)', default=None)
    args = parser.parse_args()

    main(args.input_file, args.time)
