#coding:utf8
#分析邮件内容 和 发送邮件
#构建邮件内容
#使用服务器发送邮件
#read email from source 
#produce object structure of email
#render object tree back into text

#python 自己的邮件服务器smtpd 
#python 发送邮件客户端 smtp
#send mail to any localhost listen to 25

#RFC 821
#http://docs.python.org/2/library/smtplib.html?highlight=smtp#smtplib

#connection 
#sendmail
#quit

#可以用邮件编辑器 编辑一个邮件内容

import email
import smtplib
from email.mime.text import MIMEText

me = 'liyonghelpme@gmail.com'
you = '233242872@qq.com'

def simpleSend():
    fromAddr = 'liyonghelpme@gmail.com'
    toAddrs = ['233242872@qq.com']

    msg = ('From: %s\r\nTo: %s\r\n\r\n' % (fromAddr, ", ".join(toAddrs)))

    msg += 'hello world'
    print 'Message length is ', len(msg)

    smtpClient = smtplib.SMTP('localhost')
    smtpClient.set_debuglevel(1)

    #不用本地登录 listen to localhost
    #RFC822 
    #from_addr  to_addrs list 接受地址
    smtpClient.sendmail(fromAddr, toAddrs, msg)

    smtpClient.quit()


#MIME text
def rawSend():
    raw = 'hello world'
    msg = MIMEText(raw)
    msg['Subject'] = 'The contents of %s' % 'myMail'

    msg['From'] = me
    msg['To'] = you

    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    print msg.as_string()
    s.quit()

#contentType 类型的数据
def checkContent():
    raw = 'hello world'
    msg = MIMEText(raw)
    msg['Subject'] = 'The contents of %s' % 'myMail'
    me = 'liyonghelpme@gmail.com'
    you = '233242872@qq.com'
    msg['From'] = me
    msg['To'] = you
    print msg.as_string()

from email.parser import Parser 
def parserMail():
    headers = Parser().parsestr(
        'From: liyonghelpme@gmail.com\n'
        'To: 233242872@qq.com\n'
        'Subject: Test message\n'
        '\n'
        'Body here\n'
    )
    print headers['to']
    print headers['from']
    print headers['subject']
    print headers['body']


#添加附件
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
def sendPicture():
    COMMASPACE = ', '
    msg = MIMEMultipart()
    msg['Subject'] = 'Out family reunion'
    msg['from'] = me
    msg['to'] = you
    msg.preamble = 'Our family reunion'
    fp = open('range.jpg', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()


#分析文件的头部和 尾部

#send entire directory as email content
import os
import sys
import smtplib
import mimetypes

from optparse import OptionParser
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendEntireDirectory():
    COMMASPACE = ', '

    parser = OptionParser(usage="""\
    Send the contents of a directory as a MIME message.

    Usage: %prog [options]

    Unless the -o option is given, the email is sent by forwarding to your local
    SMTP server, which then does the normal delivery process.  Your local machine
    must be running an SMTP server.
    """)
    parser.add_option('-d', '--directory',
                      type='string', action='store',
                      help="""Mail the contents of the specified directory,
                      otherwise use the current directory.  Only the regular
                      files in the directory are sent, and we don't recurse to
                      subdirectories.""")
    parser.add_option('-o', '--output',
                      type='string', action='store', metavar='FILE',
                      help="""Print the composed message to FILE instead of
                      sending the message to the SMTP server.""")
    parser.add_option('-s', '--sender',
                      type='string', action='store', metavar='SENDER',
                      help='The value of the From: header (required)')
    parser.add_option('-r', '--recipient',
                      type='string', action='append', metavar='RECIPIENT',
                      default=[], dest='recipients',
                      help='A To: header value (at least one required)')
    opts, args = parser.parse_args()
    if not opts.sender or not opts.recipients:
        parser.print_help()
        sys.exit(1)
    directory = opts.directory
    if not directory:
        directory = './mail'
    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = 'Contents of directory %s' % os.path.abspath(directory)
    outer['To'] = COMMASPACE.join(opts.recipients)
    outer['From'] = opts.sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(path)
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(path, 'rb')
            msg = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(path, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(msg)
    # Now send or store the message
    composed = outer.as_string()
    if opts.output:
        fp = open(opts.output, 'w')
        fp.write(composed)
        fp.close()
    else:
        s = smtplib.SMTP('localhost')
        s.sendmail(opts.sender, opts.recipients, composed)
        s.quit()

#sendEntireDirectory()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def sendHTML():
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Try again'
    msg['From'] = me
    msg['To'] = you

    text = "Hi\n How are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
        <head></head>
        <body>
            <p>Hi!<br>
                How are you?<br>
                Here is the <a href="http://www.python.org">link</a>
            </p>
        </body>
    </html>
    """
    f = open('./mail/check.html', 'r')
    html = f.read()
    f.close()

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)


    s = smtplib.SMTP('localhost')
    s.sendmail(me, you, msg.as_string())
    s.quit()

#sendHTML()
def testEml():
    s = smtplib.SMTP('localhost')
    f = open('./mail/mail.eml')
    msg = f.read()
    f.close()
    s.sendmail(me, you, msg)
    s.quit()

#testEml()

def testChangeRecEML():
    f = open('hello.eml')
    msg = Parser().parse(f, True)
    f.close()
    print msg['Subject']
    print msg['From']
    print msg['To']
    print msg.__class__
    del msg['Subject']
    del msg['From']
    del msg['To']

    msg['Subject'] = "test modify from to"
    msg['From'] = 'liyonghelpme@hahaha.com'
    msg['To'] = '233242872@qq.com'

    print msg.is_multipart()
    #print msg.get_payload()
    print msg.get_charset()

    print len(msg)
    print msg.__len__()
    if 'message-id' in msg:
        print 'Message-ID:', msg['Message-ID']

    print
    print
    #print msg.as_string(False)

    """
    s = smtplib.SMTP('localhost')
    s.sendmail(me, you, msg.as_string())
    s.quit()
    """

    print msg.keys()
    print msg.values()
testChangeRecEML()

