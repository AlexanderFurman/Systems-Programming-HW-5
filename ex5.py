import json
import os

#literals used in the code
ASCII_A = 65
ASCII_Z = 90
ASCII_a = 97
ASCII_z = 122
SIZE_OF_ALPHABET = 26
FAIL = -1
DECRYPT_MULTIPLIER = -1
ENCRYPT_MULTIPLIER = 1
CONFIG_FILE = 'config.json'
ENCRYPT_SUFFIX = '.enc'
DECRYPT_SUFFIX = '.txt'
READ = 'r'
WRITE = 'w'
DICT_TYPE = 'type'
DICT_MODE = 'mode'
DICT_KEY = 'key'
ENCRYPT_MODE = 'encrypt'
CAESAR_TYPE = 'Caesar'


# function displaces a single char as described in instructions (abAB letter by disp, other chars stay as they were)
# letter: a string. expects to get a string of length 2
# displacement: the displacement of the returned letter (positive/negative/zero)
# return: the displaced letter
def displace_letter(letter, displacement):
    if len(letter) != 1:
        return FAIL
    elif not letter.isalpha():
        return letter
    else:
        is_upper_flag = False if letter.islower() else True
        letter = letter.lower()
        num_letter = ord(letter) - ASCII_a
        out_letter = chr((num_letter + displacement) % SIZE_OF_ALPHABET + ASCII_a)
        if is_upper_flag:
            out_letter = out_letter.upper()
        return out_letter


class CaesarCipher:
    # constructor to CaesarCipher taking the displacement
    def __init__(self, displacement):
        self.displacement = displacement

    # Caesar encryption of a string
    # gets a string, returns the encrypted string.
    def encrypt(self, plaintext: str) -> str:
        out_str = ""
        for i in range(len(plaintext)):
            out_str += displace_letter(plaintext[i], self.displacement)
        return out_str

    # Caesar decryption of a string
    # gets a Caesar encrypted string, returns the decrypted string.
    def decrypt(self, plaintext: str) -> str:
        self.displacement = -self.displacement
        out_str = self.encrypt(plaintext)
        self.displacement = -self.displacement
        return out_str


class VigenereCipher:
    # constructor of VigenereCipher, with array of displacements as an input argument
    def __init__(self, array):
        self.cypher = array
        self.current_index = 0

    # increments current index of cypher, taking into account reaching the end of the array
    def increment_index(self):
        if self.current_index < len(self.cypher) - 1:
            self.current_index += 1
        else:
            self.current_index = 0

    # uses string to produce new encrypted/decrypted string
    # string: initial string used
    # decrypt: bool indicating whether to decrypt or encrypt
    # returns: ans - changed string
    def update_string(self, string, decrypt=False):
        mode = DECRYPT_MULTIPLIER if decrypt else ENCRYPT_MULTIPLIER
        ans = ""

        for char in string:
            if char.isalpha():
                ans += displace_letter(char, mode * self.cypher[self.current_index])
                self.increment_index()
            else:
                ans += char

        self.current_index = 0
        return ans

    # encrypts a given string
    # returns new encrypted string
    def encrypt(self, string):
        return self.update_string(string)

    # decrypts a given string
    # returns new decrypted string
    def decrypt(self, string):
        return self.update_string(string, decrypt=True)

# function which creates new VigenereCipher object using a string for the cypher
# string: used and converted to create cypher array of integers
def getVigenereFromStr(string):
    array = []
    for char in string:
        if char.isalpha():
            if ord(char) >= ASCII_a:
                num = ord(char) - ASCII_a
            else:
                num = ord(char) - ASCII_A + SIZE_OF_ALPHABET

            array.append(num)

    return VigenereCipher(array)

#function which receives a directory, and encrypts/decrypts the appropriate files in the directory 
#creates new encrypted/decrypted files to complement the original files
def processDirectory(path):
    path = path.format(os.sep, os.sep)

    internal_files = os.listdir(path)

    with open(os.path.join(path, CONFIG_FILE), READ) as f:
        data = json.loads(f.read())
    cypher_type = data.get(DICT_TYPE)
    cypher_mode = data.get(DICT_MODE)
    cypher_key = data.get(DICT_KEY)

    if cypher_type == CAESAR_TYPE:
        cypher = CaesarCipher(cypher_key)
    else:
        if isinstance(cypher_key, str):
            cypher = getVigenereFromStr(cypher_key)
        else:
            cypher = VigenereCipher(cypher_key)

    if cypher_mode == ENCRYPT_MODE:
        suffix = ENCRYPT_SUFFIX
    else:
        suffix = DECRYPT_SUFFIX

    input_files = load_input_files(path, internal_files, opposite_suffix(suffix))

    for file in input_files:
        create_output_file(file, cypher, suffix)

# function which reads a file, and creates a matching encrypted/decrypted file
def create_output_file(file, cypher, suffix):
    with open(file, READ) as f:
        string = f.read()

    new_file = os.path.splitext(file)[0] + suffix
    with open(new_file, WRITE) as f:
        f.write(cypher.encrypt(string) if suffix == ENCRYPT_SUFFIX else cypher.decrypt(string))

# function which returns the correct files within a given directory which need to be encrypted/decrypted
def load_input_files(directory, file_list, suffix):
    input_files = []
    for file in file_list:
        if os.path.splitext(file)[1] == suffix:
            input_files.append(os.path.join(directory, file))

    return input_files

# function which receives a suffix '.enc' or '.txt', and returns the other suffix
# i.e. '.enc' --> '.txt'      ////    '.txt' --> '.enc'
def opposite_suffix(suffix):
    return DECRYPT_SUFFIX if suffix == ENCRYPT_SUFFIX else ENCRYPT_SUFFIX