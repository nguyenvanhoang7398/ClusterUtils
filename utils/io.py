import csv
import json


def read_json(path):
    return json.load(open(path, 'rb'))


def write_json(content, path):
    json.dump(content, open(path, 'w'))


def write_csv(content, header, path, delimiter=","):
    with open(path, 'w', encoding="utf-8", newline='') as f:
        csv_writer = csv.writer(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header)

        for row in content:
            csv_writer.writerow(row)
