import msvcrt

def input_password(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        char = msvcrt.getch()
        if char == b'\r':  # Enter ditekan
            break
        elif char == b'\x08':  # Backspace ditekan
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        else:
            password += char.decode('utf-8')
            print('*', end='', flush=True)
    print()  # Pindah ke baris baru
    return password