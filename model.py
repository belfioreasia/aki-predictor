#!/usr/bin/env python3

import argparse
import csv
import random


def get_model_prediction():
    try:
        return random.choice(["y", "n"])
    except Exception as e:
        # Handle any potential exceptions
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="test.csv")
    parser.add_argument("--output", default="aki.csv")
    flags = parser.parse_args()
    r = csv.reader(open(flags.input))
    w = csv.writer(open(flags.output, "w"))
    w.writerow(("aki",))
    next(r) # skip headers
    for _ in r:
        # TODO: Implement a better model
        w.writerow((random.choice(["y", "n"]),))

if __name__ == "__main__":
    main()