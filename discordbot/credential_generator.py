import string
import random

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_nickname(length=8):
    letters = string.ascii_lowercase
    nickname = ''.join(random.choice(letters) for _ in range(length))
    return nickname

def write_credentials_to_file(filename, num_credentials=10, password_length=12, nickname_length=8):
    with open(filename, 'w') as file:
        for _ in range(num_credentials):
            nickname = generate_nickname(nickname_length)
            password = generate_password(password_length)
            file.write(f"Nickname: {nickname}\tPassword: {password}\n")

if __name__ == "__main__":
    # You can customize these values as needed
    file_name = "credentials.txt"
    num_credentials_to_generate = 1
    password_length = 12
    nickname_length = 8

    write_credentials_to_file(file_name, num_credentials_to_generate, password_length, nickname_length)
    print(f"{num_credentials_to_generate} credentials (nicknames and passwords) generated and saved to {file_name}")
