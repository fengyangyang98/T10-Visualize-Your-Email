# -*- coding: UTF-8 -*-

import imaplib
import email

class Email:
    def __init__(self, host, username, password, port=993):
        """init the Email class

        Args:
            host: the email server's pop host, like 'pop.qq.com'
            username: the username of the email
            password: the password
            port: the port of the pop host
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.mail = None

    def _parseHeader(self, message):
        # subject
        subject = message.get('subject')  
        dh = email.header.decode_header(subject)
        if(type(dh[0][0]) == bytes):
            subject = dh[0][0].decode(dh[0][1])

        # from
        sender = email.utils.parseaddr(message.get('from'))[1]
        # receiver
        receiver = email.utils.parseaddr(message.get('to'))[1]
        # copy
        copy = email.utils.parseaddr(message.get_all('cc'))[1]
        # time
        recvDate = email.utils.parseaddr(message.get_all('date'))[1]

        return subject, sender, receiver, copy, recvDate

    def login(self):
        """log in the email
        
        Returns:
            status: the logging status, 0 for success and -1 for failure
        """
        status = 0

        try:
            self.mail = imaplib.IMAP4(self.host)
        except(Exception):
            try:
                self.mail = imaplib.IMAP4_SSL(self.host)
            except(Exception):
                status = -1
                return status
            

        ret, msg = self.mail.login(self.username, self.password)
        if ret != 'OK':
            status = -1
        
        return status

    def logout(self):
        try:
            self.mail.close()
        except(Exception):
            return None
        
        try:
            self.mail.logout()
        except(Exception):
            return None

    def getEmailsIn(self, mailbox_name):
        """get the emails data in the mailbox

        Args:
            mailbox_name: the mailbox's name
        
        Returns:
            status: the status of getting the emails. 0 for success, 
                    -1 for failure
            ret: the list of each email's info
        """
        status = 0
        ret = []
        try:
            status, messages = self.mail.select(mailbox_name, True)  
        except(Exception):
            status = -1
            return status, ret
        
        email_count = len(self.mail.search(None, 'ALL')[1][0].split())
        
        for handler in range(email_count, 1, -1):
            res, data = self.mail.fetch(str(handler), 'BODY[HEADER]')
            msg = email.message_from_string(data[0][1].decode("utf-8")) 
            ret.append(self._parseHeader(msg))

        return status, ret
    

        
        
