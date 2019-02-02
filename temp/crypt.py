import pyAesCrypt.crypto
import io

"""Custom module to encrypt and decrypt data.
Decryption module also included in parser."""


def decrypt_data(filename):
    sIn = io.BytesIO()
    sOut = io.BytesIO()

    with open(filename, "rb") as f:
        sIn.write(f.read())

    while True:
        key = str(input("Enter file password: "))

        try:
            sIn.seek(0)
            sOut.seek(0)

            # Decrypt file with 4K buffer, using stream value size
            pyAesCrypt.decryptStream(sIn, sOut, key, 4 * 1024, len(sIn.getvalue()))
            break

        except ValueError:
            print("Wrong password or invalid input file! (Ctrl + C) to quit.")

    print("File decrypted.")
    print(sOut.getvalue().decode("utf-8"))


def encrypt_data(filename):
    ok = False

    secret = None
    passwd = None

    while not ok:
        secret = str(input("Enter secret to encrypt: "))
        passwd = str(input("Enter password: "))

        ans = str(input("Are values correct?(y/n) ")).lower()

        if ans == "y" or ans == "yes":
            ok = True

    sIn = io.BytesIO(secret.encode("utf-8"))
    sOut = io.BytesIO()

    # Enc to file with 4K buffer
    pyAesCrypt.crypto.encryptStream(sIn, sOut, passwd, 4 * 1024)

    print("Writing data to file...")

    sOut.seek(0)
    with open(filename, "wb") as f:
        f.write(sOut.getvalue())

    print("Encryption done.")

# decrypt_data("testfile.enc")
# encrypt_data("testfile.enc")
