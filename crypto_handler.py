from io import BytesIO
from pyAesCrypt.crypto import decryptStream
from pyAesCrypt.crypto import encryptStream


def decrypt_apikey(filename):
    sIn = BytesIO()
    sOut = BytesIO()

    with open(filename, "rb") as f:
        sIn.write(f.read())

    while True:
        key = str(input("Enter apikey password ('q' or 'exit' to stop): "))

        if key.lower() == "exit" or key.lower() == "q":
            exit(1)

        try:
            # Reset file pointers
            sIn.seek(0)
            sOut.seek(0)

            # Decrypt file with 4K buffer, using stream value size
            decryptStream(sIn, sOut, key, 4 * 1024, len(sIn.getvalue()))
            break

        except ValueError:
            print("Wrong password or input file corrupted.")

    print("Unlock successful.")
    return sOut.getvalue().decode("utf-8")


def encrypt_apikey(filename):
    ok = False

    apikey = None
    passwd = None

    while not ok:
        apikey = str(input("Enter apikey to encrypt: "))
        passwd = str(input("Enter password for apikey file: "))

        ans = str(input("Are values correct? (y/n): ")).lower()

        if ans == "y" or ans == "yes":
            ok = True

    sIn = BytesIO(apikey.encode("utf-8"))
    sOut = BytesIO()

    # Enc to file with 4K buffer
    encryptStream(sIn, sOut, passwd, 4 * 1024)

    print("Writing key to file...")

    sOut.seek(0)
    with open(filename, "wb") as f:
        f.write(sOut.getvalue())

    print("Encryption done. Apikey file ready.")
