"""
SMS() Class:
    Uses Gmail SMTP and IMAP servers to send and recieve text messages via email.
    Provides a medium for users to interact and control running programs.

    Uses a Email_SMS config file to gather the required information to login and
    send messages.

    NOTE: "Less Secure App Access" needs to be enabled from your Google account in order to use this application.

"""

import globals
from imports import *
from helper import *

class Email_SMS():
    """
        __init()__:
            Email_SMS class constructor. Gets necessary SMTP/IMAP server login credentials
            and sets up the class parameters.
    """
    def __init__(self, debug=False, **kwargs):
        self.debug = debug
        self.IMAP_server = None
        self.SMTP_server = None
        self.name = str(self.__class__.__name__)
        self.idle_count = 0
        self.LOGIN_FLAG = False

        self.message_queue = Queue()
        self.move = kwargs.get('move')
        self.unread = kwargs.get('unread')
        self.delete = kwargs.get('delete')
        self.enable_logger = kwargs.get('logger')
        
        if self.enable_logger:
            self.logger = self.email_sms_logger_setup()

        # Get Email_SMS credentials from config file 
        # --- (Add security measure to enter passcode to unlock config file for reading)
        self.config_initialize()



    """
        login():
            Logs into the IMAP and SMTP servers to receive and send email
            messages as text messages.
    """
    def login(self):
        # Login to Gmail IMAP Server (Listen)
        if self.enable_logger:
            self.logger.info('Logging into IMAP Server . . . ')
        else:
            print(">>> Logging into IMAP Server. . .")

        self.IMAP_server = imaplib.IMAP4_SSL(host='imap.gmail.com')
        self.IMAP_server.login(self.email, self.password)
        self.IMAP_server.select(self.folder, readonly=False)
        
        # Login to Gmail SMTP Server (Respond)
        if self.enable_logger:
            self.logger.info('Logging into SMTP Server . . . ')
        else:
            print(">>> Logging into SMTP Server. . .")

        context = ssl.create_default_context()
        self.SMTP_server = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465, context=context)
        self.SMTP_server.login(self.email, self.password)

        # Set login flag to true
        self.LOGIN_FLAG = True

        # Send sms startup message to receiver
        #self.sms_send_startup_message()

    """
        logout():
            Logs out of the IMAP and SMTP servers
    """
    def logout(self):
        # Send shutdown message
        #self.sms_send_shutdown_message()

        # Remove all Email_SMS messages from Gmail
        if self.enable_logger:
            self.logger.info('Cleaning up . . . ')
        else:
            print(">>> Cleaning Up. . .")

        self.email_sms_cleanup()

        # Logout of Gmail IMAP Server (Listen)
        if self.enable_logger:
            self.logger.info('Logging out of IMAP Server . . . ')
        else:
            print(">>> Logging out of IMAP Server. . .")

        self.IMAP_server.expunge()  # Not needed if auto-expunge is enabled
        self.IMAP_server.close()
        self.IMAP_server.logout()
        self.IMAP_server = None

        # Logout of Gmail SMTP Server (Respond)
        if self.enable_logger:
            self.logger.info('Logging out of SMTP Server . . . ')
        else:
            print(">>> Logging out of SMTP Server. . .")

        self.SMTP_server.quit()
        self.SMTP_server = None

        # Set login flag to false
        self.LOGIN_FLAG = False


#   /// SEND MESSAGE METHODS ///
    """
        sms_send_top_tickers():
            Sends sms message to reciever w/ top tickers mentioned on WSB.
    """
    def sms_send_top_tickers(self, top_tickers_df):
        self.login()     # Login to SMTP and IMAP servers

        # Send SMS alert message to reciever for incoming tickers
        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.WSB_MSG_SUBJECT, 
                                     text=globals.SMS_WSB_TICKERS)
        time.sleep(1)   # Delay (1 second)

        # Send the first top 10 tickers
        for ticker in top_tickers_df.index[:10]:    
            message = f"Bull/Bear Ratio: {round(top_tickers_df.loc[ticker, 'Bull/Bear Ratio'],2)}"
            
            # Send SMS message w/ ticker information
            self.send_singlepart_message(recipient=self.receiver,
                                         subject=f"{ticker}", 
                                         text=message)

            time.sleep(1)   # Delay (1 second)

        self.logout()   # Logout of SMTP and IMAP servers after message is sent
        return

    """
        sms_send_startup_message():
            Sends a startup message with a list of commands to the user/receiver.
    """
    def sms_send_startup_message(self):
        if self.enable_logger:
            self.logger.info(f'Sending Startup Message to {self.format_phone_number()} . . . ')
        else:
            print(f">>> Sending Startup Message to {self.format_phone_number()}. . .")

        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.STARTUP_MSG_SUBJECT,
                                     text=globals.SMS_STARTUP)

    """
        sms_send_message():
            Sends a text message to the user/receiver.
    """
    def sms_send_message(self, message):
        if self.enable_logger:
            self.logger.info(f'Sending message to {self.phone_number} . . . ')
        else:
            print(f">>> Sending Message to {self.phone_number}. . .")

        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.MSG_SUBJECT,
                                     text=message)

    """
        sms_send_command_menu_message():
            Re-sends a list of valid Email_SMS commands to the user/receiver.
    """
    def sms_send_command_menu_message(self):
        if self.enable_logger:
            self.logger.info(f'Sending Command Options Message to {self.format_phone_number(self.phone_number)} . . . ')
        else:
            print(f">>> Sending Command Options Message to {self.format_phone_number(self.phone_number)}. . .")

        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.MSG_SUBJECT,
                                     text=globals.EMAIL_SMS_CMDS)

    """
        sms_send_error_message():
            Sends an error message to the user/reciever if they enter an invalid 
            Email_SMS command.
    """
    def sms_send_error_message(self, err_type):
        if self.enable_logger:
            self.logger.info(f'Sending [{err_type}] Error Message to {self.format_phone_number(self.phone_number)} . . . ')
        else:
            print(f">>> Sending [{err_type}] Error Message to {self.format_phone_number(self.phone_number)}. . .")

        if err_type == 'error-invalid-cmd':
            error_text = globals.SMS_ERROR_INVALID_CMD
        else:
            error_text = globals.SMS_ERROR_GENERAL

        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.ERROR_MSG_SUBJECT,
                                     text=error_text)

    """
        sms_send_confirmation_message():
            Sends a confirmation text message to the user/reciever to let the user
            know that the message has been recieved.
    """
    def sms_send_confirmation_message(self):
        if self.enable_logger:
            self.logger.info(f'Sending Confirmation Message to {self.format_phone_number()} . . . ')
        else:
            print(f">>> Sending Confirmation Message to {self.format_phone_number()}. . .")

        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.MSG_SUBJECT,
                                     text=globals.SMS_CONFIRM)

    """
        sms_send_shutdown_message():
            Sends a confirmation shutdown message to the user/reciever.
    """
    def sms_send_shutdown_message(self):
        if self.enable_logger:
            self.logger.info(f'Sending Shutdown Confirmation Message to {self.format_phone_number()} . . . ')
        else:
            print(f">>> Sending Shutdown Confirmation Message to {self.format_phone_number()}. . .")
        
        self.send_singlepart_message(recipient=self.receiver,
                                     subject=globals.SHUTDOWN_MSG_SUBJECT,
                                     text=globals.SMS_SHUTDOWN)


#   /// PROCESSING METHODS ///
    """
        wait_for_incoming_messages():
            Listens for incoming text messages from the user/reciever and processes
            the messages that are recieved.
    """
    def wait_for_incoming_messages(self):
        message_dict = dict()           # Create empty message dictionary
        self.IMAP_server.select(self.folder) # Select/Re-select primary folder (INBOX)

        # Search for UNSEEN messagaes from primary user
        _r, data = self.IMAP_server.uid('SEARCH', None,
                                        "UNSEEN",
                                        "FROM {0}".format(self.receiver.strip()))
            
        if _r == 'OK':
            # If no messages have been found
            if not data[0].decode('utf-8'):
                if not self.idle_count % 60:

                    if self.enable_logger:
                        self.logger.info('IMAP Server currently IDLE . . . ')
                    else:
                        print(">>> IMAP Server currently IDLE. . .")

                    self.idle_count = 0
                self.idle_count += 1
                return
            
            # If a message has been received, get the UID and fetch for the message contents
            message_uid = data[0].split()[-1]   # Get the most recent message received from the user/reciever
            _r, data = self.IMAP_server.uid('fetch', message_uid, "(RFC822)")

            if _r == 'OK':
                raw_message = data[0][1]
                text_message = email.message_from_bytes(raw_message)

                text_from = self.__get_from(text_message)   # Get who the message is from
                message_uid = message_uid.decode('utf-8')   # Decode message UID

                key = f"{message_uid}_{text_from}"
                val_dict = dict()                           # Create a values dictionary

                if self.enable_logger:
                    self.logger.info(f'PROCESSING: UID = {message_uid} \t FROM: {text_from}')
                else:
                    print(f">>> PROCESSING: UID = {message_uid} \t FROM: {text_from}")

                val_dict['Subject'] = self.__get_subject(text_message)  # Get message subject line

                # Determine if incoming message is multi or single part and process each accordingly
                if text_message.is_multipart():
                    val_dict = self.__parse_multipart_message(text_message, val_dict)
                else:
                    val_dict = self.__parse_singlepart_message(text_message, val_dict)

                message_dict[key] = val_dict            # Add values dictionary to message dictionary

                # Determine if the message should be moved, marked unread, or deleted
                # Email_SMS will delete the incoming messages after they are processed
                self.__execute_options(message_uid, self.move, self.unread, self.delete)

                # Retrieve the 'Plain-Text' content of the message for further processing
                self.process_incoming_messages(message_dict)
                return

    """
        check_incoming_message_queue():
            Checks for incoming Email_SMS commands sent by the user/reciever.
    """
    def check_incoming_message_queue(self):
        if not self.message_queue.empty():
            if self.enable_logger:
                self.logger.info(f'Received Incoming SMS Message at {self.convert_to_12_hr(dt.datetime.now())} . . . ')
            else:
                print(f">>> Received Incoming SMS Message at {self.convert_to_12_hr(dt.datetime.now())}. . .")
            
            self.sms_send_confirmation_message()
            incoming_msg = self.message_queue.get()
            return incoming_msg[1]  # Get the plain_text message

    """
        process_incoming_messages():
            Processes the text message/command sent from the user/reciever.
    """
    def process_incoming_messages(self, message_dict):
        for key in message_dict.keys():
            # If email received is from primary user, add message to queue (**probably dont need the if-statement)
            if key.find(self.receiver):
                retreived_message = message_dict[key]['Plain_Text'].replace('\r\n','')
                self.message_queue.put([self.name, retreived_message])



#   /// MESSAGE TYPE METHODS ///  
    """
        send_singlepart_message():
            Sends a singlepart message w/ no attachments to the user/reciever.
    """
    def send_singlepart_message(self, recipient, subject, text):
        message = "Subject: {}\n\n{}".format(subject,text)
        self.SMTP_server.sendmail(self.email, recipient, message)

        if self.enable_logger:
            self.logger.info('Message sent successfully . . . ')
        else:
            print(">>> Message Sent Successfully. . .")

        return

    """
        send_multipart_message():
            Sends a multipart message w/ attachments to the user/reciever.
    """
    def send_multipart_message(self, recipient, subject, text, **kwargs):
        # Process kwargs
        html = kwargs.get('html')
        images = kwargs.get('images')
        attachments = kwargs.get('attachments')

        # Overall message object
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From'] = self.email
        message['To'] = recipient

        # Create the body
        message_body = MIMEMultipart('alternative')
        message_body.attach(MIMEText(text, 'plain'))

        # If there is an html part, attach it
        if html is not None:
            # Create a new multipart section
            message_html = MIMEMultipart('related')
            # Attach the html text
            message_html.attach(MIMEText(html, 'html'))

            # If there are images, include them
            for i in range(len(images or [])):
                # Open the image, read it, and name it so that it can be
                # referenced by name in the html as:
                # <img src='cid:image[i]'>
                # where [i] is the index of the image in images
                fp = open(images[i], 'rb')
                image_type = images[i].split('.')[-1]
                image = MIMEImage(fp.read(), _subtype=image_type)
                image.add_header('Content-ID', "<image{}>".format(i))
                fp.close()
                # Attach the image to the html part
                message_html.attach(image)
            
            # Attach the html section to the alternative section
            message_body.attach(message_html)

        # Attach the alternative section to the message
        message.attach(message_body)

        # Attach each attachment
        for file in attachments or []:
            # Open the file
            f = open(file,'rb')
            # Read in the file, and give set the header
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition',
                            'attachment; filename={}'.format(os.path.basename(file)))
            # Attach the attachment to the message
            f.close()
            message.attach(part)

        # Send the email
        self.SMTP_server.sendmail(self.email, recipient, message.as_string())
        
        if self.enable_logger:
            self.logger.info('Message sent successfully . . . ')
        else:
            print(">>> Message Sent Successfully. . .")
        
        return


#   /// GET, PARSE, EXECUTE METHODS ///
    """
        __get_to():
            Gets the reciever of the text message.
    """
    def __get_to(self, text_message):
        return text_message.get('To')

    """
        __get_bcc():
            Gets the email Blind Carbon Copy (Bcc).
    """
    def __get_bcc(self, text_message):
        return text_message.get('Bcc')

    """
        __get_from():
            Gets the sender of the text message.
    """
    def __get_from(self, text_message):
        return email.utils.parseaddr(text_message.get('From'))[1]

    """
        __get_subject():
            Gets the subject of the text message.
    """
    def __get_subject(self, text_message):
        subject = text_message.get('Subject')
        if subject is None:
            return "No Subject"
        return subject

    """
        ___parse_multipart_message():
            Parses the contents of a multi-part message (i.e message w/ and attachment).
    """
    def __parse_multipart_message(self, email_message, val_dict):
        # For each part
        for part in email_message.walk():
            # If the part is an attachment
            file_name = part.get_filename()
            if bool(file_name):
                # Generate file path
                file_path = os.path.join(self.attachment_dir, file_name)
                file = open(file_path, 'wb')
                file.write(part.get_payload(decode=True))
                file.close()
                # Get the list of attachments, or initialize it if there isn't one
                attachment_list = val_dict.get("attachments") or []
                attachment_list.append("{}".format(file_path))
                val_dict["attachments"] = attachment_list

            # If the part is html text
            elif part.get_content_type() == 'text/html':
                # Convert the body from html to plain text
                val_dict["Plain_HTML"] = html2text.html2text(
                        part.get_payload())
                val_dict["HTML"] = part.get_payload()

            # If the part is plain text
            elif part.get_content_type() == 'text/plain':
                # Get the body
                val_dict["Plain_Text"] = part.get_payload()

        return val_dict

    """
        __parse_singlepart_message():
            Parses the contents of a single-part message.
    """
    def __parse_singlepart_message(self, email_message, val_dict):
        # Get the message body, which is plain text
        val_dict["Plain_Text"] = email_message.get_payload()
        return val_dict

    """
        __execute_options():
            Will move, delete, or mark unread the message recieved from the user/recipient.
    """
    def __execute_options(self, uid, move, unread, delete):
        # If the message should be marked as unread
        if bool(unread):
            self.IMAP_server.uid("STORE", uid, '-FLAGS', '\\Seen')

        # If a move folder is specified
        if move is not None:
            try:
                # Move the message to another folder
                self.IMAP_server.uid("COPY", uid, '_Email_SMS_')
            except:
                # Create the folder and move the message to the folder
                self.IMAP_server.create('_Email_SMS_')
                self.IMAP_server.uid("COPY", uid, '_Email_SMS_')
                self.IMAP_server.uid("STORE", uid, '+FLAGS', '\\Deleted')                

        # If the message should be deleted
        elif bool(delete):
            # Move the email to the trash
            self.IMAP_server.uid("STORE", uid, '+FLAGS', '\\Deleted')
        return


#   /// GMAIL CLEANUP METHODS
    """
        email_sms_cleanup():
            Removes any Email_SMS messages from Gmail mailboxes.
    """
    def email_sms_cleanup(self):
        # Remove Email_SMS messages from "Inbox" mailbox
        self.delete_mailbox_messages(self.folder)

        # Remove Email_SMS messages from "Gmail/Sent Mail" mailbox
        self.delete_mailbox_messages('"[Gmail]/Sent Mail"')

        # Remove Email_SMS messages from "Gmail/Important" mailbox
        self.delete_mailbox_messages('"[Gmail]/Important"')

        # Remove Email_SMS messages from "Gmail/All Mail" mailbox
        # NOTE: Gmail/All Mail archives messages and will not delete them unless they are moved
        #       to [Gmail]/Trash (Example at: http://radtek.ca/blog/delete-old-email-messages-programatically-using-python-imaplib/).
        self.delete_archieved_messages('"[Gmail]/All Mail"')      

    """
        delete_mailbox_messages():
            Deletes Email_SMS messages from specified Gmail mailbox.
    """
    def delete_mailbox_messages(self, mailbox):
        # Select Gmail mailbox
        self.IMAP_server.select(mailbox)

        # Set search type (TO / FROM)
        if ('Important' in mailbox) or ('Inbox' in mailbox):
            search_type = 'FROM'                                # "Important" or "Inbox" mailbox
        else:
            search_type = 'TO'                                  # "Sent" mailbox

        # Search for all instances of sent messages to receiver
        _r, data = self.IMAP_server.uid('SEARCH', None, 
                                        'ALL', 
                                        "{0} {1}".format(search_type, self.receiver.strip()))
        
        if _r == 'OK':
            if data:
                data = data[0].split()
                # Delete all messages that match the search criteria
                for message_uid in data:
                    self.__execute_options(message_uid, self.move, self.unread, self.delete)

    """
        delete_archieved_messages():
            Moves archieved messages from "[Gmail]/All Mail" to "[Gmail]/Trash" and marks
            them for deletion.
    """
    def delete_archieved_messages(self, mailbox):
        # Select "[Gmail]/All Mail" mailbox (Archive)
        self.IMAP_server.select(mailbox)

        # >>> BCC MESSAGES CLEANUP <<<
        # Search for all "Bcc" instances in mailbox
        search_type = 'Bcc'     
        _r, data = self.IMAP_server.uid('SEARCH', None, 
                                        'ALL', 
                                        "{0} {1}".format(search_type, self.receiver.strip()))

        if _r == 'OK':
            if data:
                data = data[0].split()
                # Move all messages that match the search criteria
                for message_uid in data:
                    # Move messages to trash
                    self.IMAP_server.uid("STORE", message_uid, '+X-GM-LABELS', '\\Trash')


        # >>> FROM MESSAGES CLEANUP <<<
        # Search for all "From" instances in mailbox
        search_type = 'FROM'     
        _r, data = self.IMAP_server.uid('SEARCH', None, 
                                        'ALL', 
                                        "{0} {1}".format(search_type, self.receiver.strip()))
        
        if _r == 'OK':
            if data:
                data = data[0].split()
                # Move all messages that match the search criteria
                for message_uid in data:
                    # Move messages to trash
                    self.IMAP_server.uid("STORE", message_uid, '+X-GM-LABELS', '\\Trash')

        # Select "[Gmail]/Trash" mailbox
        self.IMAP_server.select('"[Gmail]/Trash"')
        self.IMAP_server.uid("STORE", "1:*", '+FLAGS', '\\Deleted')   # Flag all trash to be deleted
 

#   /// GENERAL METHODS ///
    """
        sms_is_login():
            Checks to verify login status.
    """
    def sms_is_login(self):
        return self.LOGIN_FLAG

    """
        convert_to_12_hr():
            Converts 24 hr time to 12 hour time.
    """
    def convert_to_12_hr(self, timeValue):
        if type(timeValue) == dt.datetime:
            return timeValue.time().strftime('%I:%M %p')					# Convert and return 12 hr. str type

        elif type(timeValue) == str:
            hr_12 = dt.datetime.strptime(timeValue[0:5], '%H:%M').time()	# Convert str type to datetime.time type (Only collect Hour/Min from str)
            return hr_12.strftime('%I:%M %p')	
  
    """
        convert_to_24_hr():
            Converts 12 hr time to 24 hour time.
    """
    def convert_to_24_hr(self, timeValue):
        return dt.datetime.strptime(timeValue, '%I:%M %p').time()			# Convert and return 24 hr. datetime.time type

    """
        format_phone_number():
            Formats phone number from config file to include '-' characters (###-####).
    """
    def format_phone_number(self):
        return format(int(self.phone_number[:-1]), ",").replace(",","-") + self.phone_number[-1]                                                                                        

    """
        config_initialize():
            Reads settings from Email_SMS config file.
    """
    def config_initialize(self):
        if self.enable_logger:
            self.logger.info('Using SMS_Config file to initialize . . . ')
        else:
            print(">>> Using SMS_Config file to initialize. . .")

        # Create parser to read from config file
        self.configParser = configparser.RawConfigParser()

        # Set config file path for reading
        self.configParser.read(f'{os.path.dirname(os.path.abspath(__file__))}\SMS_Config.config')

        # Read all data from config file
        # Prompt for Email if not given in Config file
        self.email = self.verify_config_value(dict(self.configParser.items('Email_SMS'))['email'])
        if self.email == None:
            self.email = input('Enter Email Address: ')
        
        # Prompt for Email password if not given in Config file
        self.password = self.verify_config_value(dict(self.configParser.items('Email_SMS'))['email_password'])
        if self.password == None:
            self.password = getpass.getpass('Enter Email Password: ')

        self.folder = self.verify_config_value(dict(self.configParser.items('Email_SMS'))['email_folder'])
        self.phone_number = self.verify_config_value(dict(self.configParser.items('Email_SMS'))['phone_number'])
        self.receiver = self.phone_number + globals.CARRIERS[self.verify_config_value(dict(self.configParser.items('Email_SMS'))['phone_carrier'])]
        self.attachment_dir = self.verify_config_value(dict(self.configParser.items('Email_SMS'))['attachment_dir'])

    """
        verify_config_value():
            Sets empty config file values to 'None'.
    """
    def verify_config_value(self, config_value):
        # If empty value, set to None
        if not config_value:
            return None
        return config_value

    """
        email_sms_logger_setup():
            Sets up and initializes a logger for Email_SMS.
    """
    def email_sms_logger_setup(self):
        logger = logging.getLogger(self.name)                               # Create logger

        if not self.debug:
            logger.setLevel(logging.INFO)                                   # Set logger level to INFO
            console_handler = logging.StreamHandler()                       # Create console handler
            console_handler.setLevel(logging.ERROR)                         # Set console level to ERROR
        else:
            logger.setLevel(logging.DEBUG)                                  # Set logger level to DEBUG
            console_handler = logging.StreamHandler(sys.stdout)             # Create console handler
            console_handler.setLevel(logging.DEBUG)                         # Set console level to DEBUG

        run_date = dt.datetime.today().date()

        # Remove old log file if it exists
        if os.path.exists(f'Error_Logs/EMAIL_SMS_RUN_LOG_{run_date}.log'):
            os.remove(f'Error_Logs/EMAIL_SMS_RUN_LOG_{run_date}.log')

        file_handler = logging.FileHandler(f'Error_Logs/EMAIL_SMS_RUN_LOG_{run_date}.log') # Create file handler
        file_handler.setLevel(logging.DEBUG)                                    # Set file handler level to DEBUG

        # Create and set logging format
        formatter = logging.Formatter("[%(asctime)s | %(levelname)s | %(name)s]   %(message)s") 

        # Add format to both console and file handlers
        console_handler.setFormatter(formatter)     
        file_handler.setFormatter(formatter)
        
        # Add console and file handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
