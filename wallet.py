"""This is going to be your wallet. Here you can do several things:
- Generate a new address (public and private key). You are going
to use this address (public key) to send or receive any transactions. You can
have as many addresses as you wish, but keep in mind that if you
lose its credential data, you will not be able to retrieve it.

- Send coins to another address
- Retrieve the entire blockchain and check your balance

If this is your first time using this script don't forget to generate
a new address and edit miner config file with it (only if you are
going to mine).

Timestamp in hashed message. When you send your transaction it will be received
by several nodes. If any node mine a block, your transaction will get added to the
blockchain but other nodes still will have it pending. If any node see that your
transaction with same timestamp was added, they should remove it from the
node_pending_transactions list to avoid it get processed more than 1 time.
"""

import requests
import time
import base64
import ecdsa


def wallet():
    response = None
    while response not in ["1", "2", "3","4"]:
        response = input("""Was wollen sie machen?
        1. Neues Wallet erstellen.
        2. Wuefficoins zu einem anderen Wallet senden.
        3. Transaktionen überprüfen.
        4. Verlassen.\n""")
    if response == "1":
        # Generate new wallet
        print("""=========================================\n
WICHTIG: Speichern sie diese Keys gut ab. Sie erden sonst nicht an ihr Wallet kommen.
=========================================\n""")
        generate_ECDSA_keys()
    elif response == "2":
        addr_from = input("Von: Trage deine Adresse ein. (public key)\n")
        private_key = input("Trage deinen private key ein.\n")
        addr_to = input("Nach: Trage die Walletadresse deines Empfängers ein.\n")
        amount = input("Menge: wieviel willst du an das Wallet des Empfängers senden?\n")
        print("=========================================\n\n")
        print("Ist alles korrekt?\n")
        print(F"From: {addr_from}\nPrivate Key: {private_key}\nTo: {addr_to}\nAmount: {amount}\n")
        response = input("y/n\n")
        if response.lower() == "y":
            send_transaction(addr_from, private_key, addr_to, amount)
        elif response.lower() == "n":
            return wallet()  # return to menu
    elif response == "3":  # Will always occur when response == 3.
        check_transactions()
    else:
        quit()


def send_transaction(addr_from, private_key, addr_to, amount):
    """Sends your transaction to different nodes. Once any of the nodes manage
    to mine a block, your transaction will be added to the blockchain. Despite
    that, there is a low chance your transaction gets canceled due to other nodes
    having a longer chain. So make sure your transaction is deep into the chain
    before claiming it as approved!
    """
    # For fast debugging REMOVE LATER
    # private_key="181f2448fa4636315032e15bb9cbc3053e10ed062ab0b2680a37cd8cb51f53f2"
    # amount="3000"
    # addr_from="SD5IZAuFixM3PTmkm5ShvLm1tbDNOmVlG7tg6F5r7VHxPNWkNKbzZfa+JdKmfBAIhWs9UKnQLOOL1U+R3WxcsQ=="
    # addr_to="SD5IZAuFixM3PTmkm5ShvLm1tbDNOmVlG7tg6F5r7VHxPNWkNKbzZfa+JdKmfBAIhWs9UKnQLOOL1U+R3WxcsQ=="

    if len(private_key) == 64:
        signature, message = sign_ECDSA_msg(private_key)
        url = 'http://localhost:5000/txion'
        payload = {"from": addr_from,
                   "to": addr_to,
                   "amount": amount,
                   "signature": signature.decode(),
                   "message": message}
        headers = {"Content-Type": "application/json"}

        res = requests.post(url, json=payload, headers=headers)
        print(res.text)
    else:
        print("Falsche Walletadresse oder Keylänge. Bitte überprüfe deine Angaben und versuche es erneut.")


def check_transactions():
    """Retrieve the entire blockchain. With this you can check your
    wallets balance. If the blockchain is to long, it may take some time to load.
    """
    try:
        res = requests.get('http://localhost:5000/blocks')
        print(res.text)
    except requests.ConnectionError:
        print('Verbindungserror. Stelle sicher das Miner.py in einem anderm Terminal läuft.')

    

def generate_ECDSA_keys():
    """This function takes care of creating your private and public (your address) keys.
    It's very important you don't lose any of them or those wallets will be lost
    forever. If someone else get access to your private key, you risk losing your coins.

    private_key: str
    public_ley: base64 (to make it shorter)
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) #this is your sign (private key)
    private_key = sk.to_string().hex() #convert your private key to hex
    vk = sk.get_verifying_key() #this is your verification key (public key)
    public_key = vk.to_string().hex()
    #we are going to encode the public key to make it shorter
    public_key = base64.b64encode(bytes.fromhex(public_key))

    filename = input("Schreibe deine Wunschadresse deines Wallets auf. ") + ".txt"
    with open(filename, "w") as f:
        f.write(F"Private key: {private_key}\nWallet address / Public key: {public_key.decode()}")
    print(F"Dein Private key, sowie dein public key sind in der Datei: {filename}")

def sign_ECDSA_msg(private_key):
    """Sign the message to be sent
    private_key: must be hex

    return
    signature: base64 (to make it shorter)
    message: str
    """
    # Get timestamp, round it, make it into a string and encode it to bytes
    message = str(round(time.time()))
    bmessage = message.encode()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    signature = base64.b64encode(sk.sign(bmessage))
    return signature, message


if __name__ == '__main__':
    print("""       =========================================\n
        Wueffi COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        Falls du Hilfe brauchst: https://github.com/cosme12/SimpleCoin\n
        Du musst die letzte Version benutzen, sonst buggt das Programm.\n\n\n""")
    wallet()
    input("Drücke ENTER um das Programm zu verlassen.")
