from os import listdir
from os.path import isfile, join
from datetime import datetime
from time import sleep

import crypto_handler

import requests

AUTHOR = "Sinipelto"

# Output file formats in tuples
txt = ("        ", ".txt")
csvf = (";", ".csv")
jsonf = (": ", ".json")


def parse_ip(fp):
    file_data = {}

    for line in fp:
        # Separator should be 4 spaces but may differ
        data = line.split(" ")

        ip = ""

        for i in range(len(data)):
            periods = 0

            for k in data[i]:
                if k == ".":
                    periods += 1

            if periods != 3:
                continue

            nums = data[i].split(".")

            if len(nums) != 4:
                continue

            success_count = 0

            for n in nums:
                try:
                    if 0 <= int(n) <= 255:
                        success_count += 1
                    else:
                        break
                except ValueError:
                    break

            if success_count == 4:
                ip = ".".join(nums)
                break

        # Check correct ip format
        periods = 0
        for x in ip:
            if x == ".":
                periods += 1

        if periods != 3:
            raise AssertionError("Invalid IP Address! Period count mismatch (not 3 !!!)")

        if ip not in file_data.keys():
            file_data[ip] = 1
        else:
            file_data[ip] += 1

    return file_data


def process_ip(apikey, ip):
    base_url = "http://api.ipstack.com/"
    api_url = "?access_key=" + apikey
    params = "&hostname=1&security=1"

    full_url = base_url + ip + api_url + params

    resp = requests.get(full_url)

    return resp.content.decode("utf-8").strip("'")


def parse_logs(srcdir, outdir, file_format, filenames=None, parse_all=False, write_info=True):
    if not parse_all and len(filenames) <= 0:
        raise AttributeError("No files to process.")

    if '/' not in srcdir[len(srcdir) - 1]:
        srcdir += "/"

    if filenames is None or len(filenames) <= 0:
        file_list = [f for f in listdir(srcdir) if isfile(join(srcdir, f))]

    else:
        file_list = [f for f in filenames]

    ip_data = {}
    results = []

    for f in file_list:
        ifp = open(srcdir + f, "r", encoding="utf-8")
        data = parse_ip(ifp)
        ifp.close()

        for key in dict(data).keys():
            if key not in ip_data.keys():
                ip_data[key] = data[key]
            else:
                ip_data[key] += data[key]

    if '/' not in outdir[len(outdir) - 1]:
        outdir += "/"

    api_key = crypto_handler.decrypt_apikey("apikey.enc")

    counter = 0
    processed = 0
    total = len(ip_data)

    # LIMIT: 150 ips / minute
    for ip in ip_data.keys():
        if counter >= 4:
            break

        if counter >= 149:
            print("Limit reached! Sleeping for 1 minute.")
            sleep(61)
            counter = 0

        results.append(process_ip(api_key, str(ip)))

        processed += 1
        counter += 1

        print("IPs Processed: [{0}]/[{1}]".format(processed, total))

    print("IP Processing Complete.")

    stamp = str(datetime.now().isoformat().replace("T", "_").replace(":", "-").split(".")[0])

    freq_fname_stub = stamp + "_frequencies"
    freq_header_stub = ["ip", "frequency"]

    res_fname = stamp + "_results.txt"

    if file_format == "txt":
        separator = txt[0]
        header = txt[0].join(freq_header_stub)
        proc_fname = freq_fname_stub + txt[1]

    elif file_format == "csv":
        separator = csvf[0]
        header = csvf[0].join(freq_header_stub)
        proc_fname = freq_fname_stub + csvf[1]

    elif file_format == "json":
        separator = jsonf[0]
        header = jsonf[0].join(freq_header_stub)
        proc_fname = freq_fname_stub + jsonf[1]

    else:
        raise AttributeError("Incorrect file format!")

    ofp = open(outdir + proc_fname, "w", encoding="utf-8")
    ofp2 = open(outdir + res_fname, "w", encoding="utf-8")

    if write_info:
        process_info = "Processed at: " + str(datetime.now().astimezone())
    else:
        process_info = ""

    lines = [process_info + "\n\n" + header]
    lines2 = process_info + "\n\n" + "TOTAL IP COUNT: " + str(len(results)) + "\n\n"

    for key in ip_data.keys():
        lines.append(str(key + separator + str(ip_data[key])))

    # [header, nl nl topic nl nl, json, ,  json, m json, copyright]

    raw_lines = ""
    raw_lines += "[\n"
    raw_lines += ",\n".join(results)
    raw_lines += "\n]"

    ofp.write("\n".join(lines))
    ofp2.write(lines2 + raw_lines)

    if write_info:
        cp_right = "\n\n" + "COPYRIGHT (c) 2019 " + AUTHOR + ". All rights reserved."

        ofp.write(cp_right)
        ofp2.write(cp_right)

    ofp.close()
    ofp2.close()
