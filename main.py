import crypto_handler
from log_handler import parse_logs


def main():
    src_dir = "input/"
    out_dir = "output/"

    try:
        open("apikey.enc", "rb")
    except FileNotFoundError:
        print("Api key file not found.")
        print("Creating new one..")

        crypto_handler.encrypt_apikey("apikey.enc")

    parse_logs(src_dir, out_dir, file_format="txt", parse_all=True, write_info=True)

    return 0


main()
