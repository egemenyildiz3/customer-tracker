
# Mini desktop app using tkinter
import csv
import smtplib
from email.mime.text import MIMEText
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog


CSV_FILE = 'users.csv'
TEMPLATE_DIR = '.'
LOG_FILE = 'user_action_log.txt'

def log_action(user, action):
	with open(LOG_FILE, 'a', encoding='utf-8') as f:
		f.write(f"{user['name']} {user['surname']} ({user['email']}): {action} at {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def read_users(csv_file):
	users = []
	with open(csv_file, newline='', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		for row in reader:
			row['age'] = int(row['age'])
			row['process'] = int(row['process'])
			row['isProcessEmailSent'] = row['isProcessEmailSent'].lower() == 'true'
			users.append(row)
	return users

def write_users(csv_file, users):
	with open(csv_file, 'w', newline='', encoding='utf-8') as f:
		fieldnames = ['name', 'surname', 'email', 'age', 'job', 'process', 'isProcessEmailSent']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for user in users:
			user_copy = user.copy()
			user_copy['isProcessEmailSent'] = str(user_copy['isProcessEmailSent'])
			writer.writerow(user_copy)

def load_template(process):
    template_file = os.path.join(TEMPLATE_DIR, 'templates', f'template_{process}.txt')
    if not os.path.exists(template_file):
        return None
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()

def save_template(process, content):
    template_file = os.path.join(TEMPLATE_DIR, 'templates', f'template_{process}.txt')
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)

def send_email(to_email, subject, body):
	# Update these with your SMTP server details
	smtp_server = 'smtp.example.com'
	smtp_port = 587
	smtp_user = 'your_email@example.com'
	smtp_password = 'your_password'

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = smtp_user
	msg['To'] = to_email

	with smtplib.SMTP(smtp_server, smtp_port) as server:
		server.starttls()
		server.login(smtp_user, smtp_password)
		server.send_message(msg)

class MailSenderApp(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Mail Sender App')
		self.minsize(1100, 750)
		self.geometry('1100x750')
		self.configure(bg='#f5f6fa')
		self.style = ttk.Style(self)
		self.style.theme_use('clam')
		self.style.configure('Treeview', font=('Segoe UI', 12), rowheight=28, background='#f5f6fa', fieldbackground='#f5f6fa')
		self.style.configure('Treeview.Heading', font=('Segoe UI', 13, 'bold'), background='#273c75', foreground='white')
		self.style.map('Treeview', background=[('selected', '#dff9fb')])
		self.users = read_users(CSV_FILE)
		self.create_widgets()

	def create_widgets(self):
		# Title Label
		title_lbl = tk.Label(self, text='Mail Sender Dashboard', font=('Segoe UI', 22, 'bold'), bg='#f5f6fa', fg='#273c75')
		title_lbl.pack(pady=(20, 10))

		# Users Table Section
		table_frame = tk.Frame(self, bg='#f5f6fa')
		table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))
		table_frame.grid_propagate(False)
		table_lbl = tk.Label(table_frame, text='User List', font=('Segoe UI', 15, 'bold'), bg='#f5f6fa', fg='#353b48')
		table_lbl.pack(anchor='w', pady=(0, 5))
		self.tree = ttk.Treeview(table_frame, columns=('name', 'surname', 'email', 'age', 'job', 'process', 'isProcessEmailSent'), show='headings')
		for col in self.tree['columns']:
			self.tree.heading(col, text=col)
			self.tree.column(col, width=120)
		self.tree.pack(fill=tk.BOTH, expand=True)
		self.refresh_table()

		# Buttons Section
		btn_frame = tk.Frame(self, bg='#f5f6fa')
		btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
		btn_frame.grid_propagate(False)
		tk.Label(btn_frame, text='Actions:', font=('Segoe UI', 13, 'bold'), bg='#f5f6fa', fg='#353b48').pack(side=tk.LEFT, padx=(0, 10))
		button_style = {'font': ('Segoe UI', 11, 'bold'), 'bg': '#273c75', 'fg': 'white', 'activebackground': '#40739e', 'activeforeground': 'white', 'bd': 0, 'relief': tk.FLAT, 'padx': 10, 'pady': 7}
		tk.Button(btn_frame, text='Edit Selected', command=self.edit_selected, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Add User', command=self.add_user, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Delete Selected', command=self.delete_selected, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Edit Template', command=self.edit_template, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Send Emails', command=self.send_emails, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Send Selected Email', command=self.send_selected_email, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Save CSV', command=self.save_csv, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='Refresh', command=self.refresh_from_csv, **button_style).pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text='See History', command=self.see_history, **button_style).pack(side=tk.LEFT, padx=5)
	def refresh_from_csv(self):
		self.users = read_users(CSV_FILE)
		self.refresh_table()

	def refresh_table(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		for user in self.users:
			self.tree.insert('', tk.END, values=(user['name'], user['surname'], user['email'], user['age'], user['job'], user['process'], user['isProcessEmailSent']))

	def edit_selected(self):
		selected = self.tree.selection()
		if not selected:
			messagebox.showinfo('Info', 'No user selected.')
			return
		idx = self.tree.index(selected[0])
		user = self.users[idx]
		edit_win = tk.Toplevel(self)
		edit_win.title('Edit User')
		edit_win.configure(bg='#f5f6fa')
		entries = {}
		for i, key in enumerate(['name', 'surname', 'email', 'age', 'job', 'process', 'isProcessEmailSent']):
			tk.Label(edit_win, text=key, font=('Segoe UI', 11), bg='#f5f6fa', fg='#353b48').grid(row=i, column=0, padx=10, pady=7, sticky='e')
			val = tk.StringVar(value=str(user[key]))
			ent = tk.Entry(edit_win, textvariable=val, font=('Segoe UI', 11), bg='white', fg='#353b48', relief=tk.GROOVE, bd=2)
			ent.grid(row=i, column=1, padx=10, pady=7, sticky='w')
			entries[key] = val
		def save():
			process_before = user['process']
			for key in entries:
				v = entries[key].get()
				if key == 'age' or key == 'process':
					user[key] = int(v)
				elif key == 'isProcessEmailSent':
					user[key] = v.lower() == 'true'
				else:
					user[key] = v
			# If process changed, set isProcessEmailSent to False
			if user['process'] != process_before:
				user['isProcessEmailSent'] = False
				log_action(user, f'Process updated from {process_before} to {user["process"]}')
			else:
				log_action(user, 'User edited')
			self.refresh_table()
			write_users(CSV_FILE, self.users)
			edit_win.destroy()
		tk.Button(edit_win, text='Save', command=save, font=('Segoe UI', 11, 'bold'), bg='#273c75', fg='white', activebackground='#40739e', activeforeground='white', bd=0, relief=tk.FLAT, padx=10, pady=7).grid(row=7, column=0, columnspan=2, pady=10)

	def add_user(self):
		new_user = {'name': '', 'surname': '', 'email': '', 'age': 0, 'job': '', 'process': 10, 'isProcessEmailSent': False}
		self.users.append(new_user)
		log_action(new_user, 'User added')
		self.refresh_table()
		messagebox.showinfo('Info', 'New user added. Edit details and save.')

	def delete_selected(self):
		selected = self.tree.selection()
		if not selected:
			messagebox.showinfo('Info', 'No user selected.')
			return
		idx = self.tree.index(selected[0])
		user = self.users[idx]
		if messagebox.askyesno('Confirm', 'Are you sure you want to delete this user?'):
			log_action(user, 'User deleted')
			del self.users[idx]
			self.refresh_table()

	def edit_template(self):
		process = simpledialog.askinteger('Template', 'Enter process value (10, 20, 30, ...):', parent=self)
		if not process:
			return
		content = load_template(process) or 'Subject: Your Process is at {process}%\n\nDear {name} {surname},\n\nYour current process is at {process}%.\n\nBest regards,\nTeam'
		edit_win = tk.Toplevel(self)
		edit_win.title(f'Edit Template {process}%')
		edit_win.configure(bg='#f5f6fa')
		tk.Label(edit_win, text=f'Editing Template for {process}%', font=('Segoe UI', 13, 'bold'), bg='#f5f6fa', fg='#353b48').pack(pady=(10, 5))
		txt = tk.Text(edit_win, width=80, height=20, font=('Segoe UI', 11), bg='white', fg='#353b48', relief=tk.GROOVE, bd=2)
		txt.insert('1.0', content)
		txt.pack(padx=10, pady=10)
		def save():
			save_template(process, txt.get('1.0', tk.END))
			edit_win.destroy()
		tk.Button(edit_win, text='Save', command=save, font=('Segoe UI', 11, 'bold'), bg='#273c75', fg='white', activebackground='#40739e', activeforeground='white', bd=0, relief=tk.FLAT, padx=10, pady=7).pack(pady=(0, 10))

	def send_emails(self):
		count = 0
		for user in self.users:
			if not user['isProcessEmailSent']:
				template = load_template(user['process'])
				if template:
					body = template.format(**user)
					subject = body.split('\n')[0].replace('Subject: ', '')
					body = '\n'.join(body.split('\n')[1:])
					try:
						# Uncomment to actually send emails
						# send_email(user['email'], subject, body)
						user['isProcessEmailSent'] = True
						log_action(user, f'Email sent for process {user["process"]}%')
						count += 1
					except Exception as e:
						messagebox.showerror('Error', f'Failed to send email to {user["email"]}: {e}')
				else:
					messagebox.showwarning('Warning', f'No template for process {user["process"]}%')
		self.refresh_table()
		write_users(CSV_FILE, self.users)
		messagebox.showinfo('Info', f'Sent {count} emails.')

	def send_selected_email(self):
		selected = self.tree.selection()
		if not selected:
			messagebox.showinfo('Info', 'No user selected.')
			return
		idx = self.tree.index(selected[0])
		user = self.users[idx]
		if user['isProcessEmailSent']:
			if not messagebox.askyesno('Confirm', 'Email already sent for this process. Send again?'):
				return
		template = load_template(user['process'])
		if template:
			body = template.format(**user)
			subject = body.split('\n')[0].replace('Subject: ', '')
			body = '\n'.join(body.split('\n')[1:])
			try:
				# Uncomment to actually send emails
				# send_email(user['email'], subject, body)
				user['isProcessEmailSent'] = True
				log_action(user, f'Email sent for process {user["process"]}% (single)')
				self.refresh_table()
				write_users(CSV_FILE, self.users)
				messagebox.showinfo('Info', f'Email sent to {user["email"]}.')
			except Exception as e:
				messagebox.showerror('Error', f'Failed to send email to {user["email"]}: {e}')
		else:
			messagebox.showwarning('Warning', f'No template for process {user["process"]}%')
	def see_history(self):
		selected = self.tree.selection()
		if not selected:
			messagebox.showinfo('Info', 'No user selected.')
			return
		idx = self.tree.index(selected[0])
		user = self.users[idx]
		history = []
		if os.path.exists(LOG_FILE):
			with open(LOG_FILE, 'r', encoding='utf-8') as f:
				for line in f:
					if user['email'] in line:
						history.append(line.strip())
		hist_win = tk.Toplevel(self)
		hist_win.title(f'History for {user["name"]} {user["surname"]}')
		hist_win.configure(bg='#f5f6fa')
		tk.Label(hist_win, text=f'Action History for {user["name"]} {user["surname"]}', font=('Segoe UI', 13, 'bold'), bg='#f5f6fa', fg='#353b48').pack(pady=(10, 5))
		txt = tk.Text(hist_win, width=80, height=20, font=('Segoe UI', 11), bg='white', fg='#353b48', relief=tk.GROOVE, bd=2)
		txt.pack(padx=10, pady=10)
		txt.insert('1.0', '\n'.join(history) if history else 'No history found.')
		txt.config(state='disabled')

	def save_csv(self):
		write_users(CSV_FILE, self.users)
		messagebox.showinfo('Info', 'CSV saved.')

if __name__ == '__main__':
	app = MailSenderApp()
	app.mainloop()
