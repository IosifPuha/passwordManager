import os
import pickle
from cryptography.fernet import Fernet
from tkinter import filedialog, Tk, Button, Label, Entry, StringVar, messagebox, Listbox, SINGLE, END
from colorama import init, Fore, Style

init(autoreset=True)

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    messagebox.showinfo("Key Generated", "The new key was generated in the current directory as 'secret.key'. STORE IT SOMEWHERE ONLY YOU CAN ACCESS IT!")

def load_key():
    file_path = filedialog.askopenfilename(title="Select the key file")
    with open(file_path, "rb") as key_file:
        key = key_file.read()
    return key

def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

def save_passwords(passwords, key):
    with open("passwords.dat", "wb") as password_file:
        encrypted_data = []
        for service, username, password in passwords:
            encrypted_service = encrypt_password(service, key)
            encrypted_username = encrypt_password(username, key)
            encrypted_password = encrypt_password(password, key)
            encrypted_data.append((encrypted_service, encrypted_username, encrypted_password))
        pickle.dump(encrypted_data, password_file)

def load_passwords(key):
    passwords = []
    if os.path.exists("passwords.dat"):
        with open("passwords.dat", "rb") as password_file:
            encrypted_data = pickle.load(password_file)
            for encrypted_service, encrypted_username, encrypted_password in encrypted_data:
                service = decrypt_password(encrypted_service, key)
                username = decrypt_password(encrypted_username, key)
                password = decrypt_password(encrypted_password, key)
                passwords.append((service, username, password))
    return passwords

def add_password():
    if key is None:
        messagebox.showerror("Error", "You must load a key first!")
        return

    service = service_var.get()
    username = username_var.get()
    password = password_var.get()

    if service and username and password:

        # Check if the service already exists
        for s, _, _ in passwords:
            if s == service:
                messagebox.showerror("Error", f"The service '{service}' already exists. Select it from the list and use 'Change Password' to modify the existing password.")
                return

        passwords.append((service, username, password))
        save_passwords(passwords, key)
        list_services()
        messagebox.showinfo("Success", "Password successfully saved!")
    else:
        messagebox.showerror("Error", "You should fill in all fields!")

def view_password():
    if key is None:
        messagebox.showerror("Error", "You must load a key first!")
        return

    selected_indices = service_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Error", "You must select a service first!")
        return

    selected_service = service_listbox.get(selected_indices)
    for service, username, password in passwords:
        if service == selected_service:
            messagebox.showinfo(f"Password for {service}",
                                f"Service: {service}\nUsername: {username}\nPassword: {password}")
            break

def change_password():
    if key is None:
        messagebox.showerror("Error", "You must load a key first!")
        return

    selected_indices = service_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Error", "You must select a service first!")
        return

    selected_service = service_listbox.get(selected_indices)
    new_password = password_var.get()
    if new_password:
        for i, (service, username, password) in enumerate(passwords):
            if service == selected_service:
                passwords[i] = (service, username, new_password)
                save_passwords(passwords, key)
                list_services()
                messagebox.showinfo("Success", "Password successfully changed!")
                break
    else:
        messagebox.showerror("Error", "The new password can't be empty!")


def list_services():
    if key is None:
        messagebox.showerror("Error", "You must load a key first!")
        return

    service_listbox.delete(0, END)
    for service, _, _ in passwords:
        service_listbox.insert(END, service)

def load_existing_key():
    global key
    key = load_key()
    global passwords
    passwords = load_passwords(key)
    list_services()

def generate_and_load_key():
    generate_key()
    load_existing_key()




# Inizializza la finestra principale di Tkinter
root = Tk()
root.title("Password Manager")

key = None
passwords = []

# Creazione dei widget
service_var = StringVar()
username_var = StringVar()
password_var = StringVar()

Label(root, text="Service:").grid(row=0, column=0, sticky='e')
Entry(root, textvariable=service_var).grid(row=0, column=1, padx=10, pady=5)

Label(root, text="Username:").grid(row=1, column=0, sticky='e')
Entry(root, textvariable=username_var).grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Password:").grid(row=2, column=0, sticky='e')
Entry(root, textvariable=password_var).grid(row=2, column=1, padx=10, pady=5)

Button(root, text="Add Password", command=add_password).grid(row=3, column=1, pady=10)


Label(root, text="Your Services:").grid(row=0, column=2, padx=10, pady=5)

service_listbox = Listbox(root, selectmode=SINGLE)
service_listbox.grid(row=0, column=2, rowspan=6, padx=10)

Button(root, text="View Password", command=view_password).grid(row=4, column=1, pady=5)
Button(root, text="Change Password", command=change_password).grid(row=5, column=1, pady=5)

Button(root, text="Load Existing Key", command=load_existing_key).grid(row=6, column=0, pady=5)
Button(root, text="Generate and Load Key", command=generate_and_load_key).grid(row=6, column=1, pady=5)

# Avvia il loop principale della GUI
root.mainloop()
