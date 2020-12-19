# -*- coding: UTF-8 -*-

import imaplib
import email
import chardet

import utils
import chardet

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
            if dh[0][1] == None:
                subject = dh[0][0].decode()
            else:
                subject = dh[0][0].decode(dh[0][1])

        # from
        sender = email.utils.parseaddr(message.get('from'))[1]
        # receiver
        receiver = email.utils.parseaddr(message.get('to'))[1]
        # copy
        copy = email.utils.parseaddr(message.get_all('cc'))[1]
        # time
        recvDate = utils.getDatetime(email.utils.parseaddr(message.get_all('date'))[1])

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

    def getEmailsIn(self, mailbox_name, year = 0):
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
        if email_count == 0:
            return -1, ret

        # get the year
        if year == 0:
            start, end = utils.getTimeThisYear()
            year = start.year
        
        # recv the data
        for handler in range(email_count, 1, -1):
            res, data = self.mail.fetch(str(handler), 'BODY[HEADER]')
            if(res == 'NO'):
                return -1, ret

            typ = chardet.detect(data[0][1])
            msg = email.message_from_string(data[0][1].decode(typ['encoding'])) 
            tmp = self._parseHeader(msg)
            
            # the year's email
            if year == tmp[-1].year:
                ret.append(tmp)

        return status, ret

    def getMailboxs(self):
        ret = []
        status = 0
        tmp = []
        try:
            typ, tmp = self.mail.list()
        except(Exception):
            status = -1
            return status
        
        
        for i in tmp:
            ret.append(i.decode('utf-8').split(' "/" ')[1])
            
        return status, ret
    

        
        
