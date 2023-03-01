import json
import sys
import qrcode
import zlib
import PySimpleGUI as sg

SPLITTER = "$"


def import_file(path):
    """
    file import
    :param path: path of the json file
    :return:
    """
    file = open(path, encoding="utf8")
    data = json.load(file)
    file.close()
    return data


def validate(data):
    """
    this is a sample function doing basic validation on the imported json
    :param dict data: dict of json to be imported.
    :return: data as is if it passes validation.
    """
    if isinstance(data, dict):
        for internal_key in data.keys():
            if internal_key[0] != "K":
                raise Exception("data is incorrectly formatted")
    else:
        raise Exception("data is incorrectly formatted")
    return data


def clean_string(data):
    """
    :param dict data: json to beqred
    :return:
    """
    capsule_value = str(data).replace('{', "").replace('}', "").replace("'", "")
    return capsule_value


def string_to_bytes(str):
    str_encoded = bytes(str, "utf-8")
    return str_encoded


def append_calculate_crc32(data):
    if isinstance(data, str):
        encoded_data = string_to_bytes(data)
    else:
        encoded_data = data
    checksum = zlib.crc32(encoded_data)
    encoded_checksum = string_to_bytes(str(checksum))
    split_char = string_to_bytes(SPLITTER)
    complete_data = encoded_data + split_char + encoded_checksum

    return complete_data


def split(string, size):
    size = size - 33 - 15
    return [string[i:i + size] for i in range(0, len(string), size)]


def write_to_qr(message, index):
    """

    :param str message:
    :param index:
    :return:
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    print(f'total qr size = {sys.getsizeof(message)}')
    qr.add_data(message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"qr{index}.png")



def list_to_qr(test):
    for chunk in range(len(test)):
        id = string_to_bytes(f'{SPLITTER}id{str(chunk)}')
        write_to_qr(test[chunk]+id, chunk)


def sign_list(test):
    new_list = []
    for chunk in test:
        chunk = append_calculate_crc32(chunk)
        new_list.append(chunk)
    return new_list


def main(file_path):
    text = validate(import_file(file_path))
    text = clean_string(text)
    text = append_calculate_crc32(text)
    print(f' total size = {sys.getsizeof(text)}')
    text = split(text, 1000)
    text = sign_list(text)
    list_to_qr(text)
    print(f' last string size = {sys.getsizeof(text[-1])}')


main("test_capsule.json")
