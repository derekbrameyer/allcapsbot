# This Python file uses the following encoding: utf-8
import sys, socket, ssl, string, os, re, pycurl, simplejson, cStringIO, sched, random, urllib, getopt, time, math, ast, itertools, getpass
from django.utils.encoding import smart_str
import threading

class AllCapsBot:
    def __init__(self, host, port, pw, irc_pass):
        self.HOST = host
        self.PORT = int(port)
        self.PASS = pw
        self.NICK = 'AllCapsBot' #CONFIG
        self.IDENT = 'AllCapsBot' #CONFIG
        self.IDENT_PASS = irc_pass
        self.REALNAME = 'AllCapsBot' #CONFIG
        self.CHANNELS = ['#trashtalk'] #CONFIG
        self.IDENT_CHAR = '`' #CONFIG
        self.illegal_nicks = ['ChanServ', 'WTAbot', self.NICK] #CONFIG
        self.sender = None
        self.ircsock = None
        self.kick_message = 'PLEASE USE ALL CAPS. THANK YOU VERY MUCH.' #CONFIG
    
    # Send an IRC message
    def sendIrcMessage(self, nick, channel, message, has_pm_flag, default_to_user):
        message = smart_str(message)
        if has_pm_flag:
            self.sender.send('PRIVMSG %s :%s\r\n' % (nick, message))
        elif channel == self.NICK:
            # Command was sent directly to bot with no PM flag
            if int(default_to_user) == 1:
                # Send back to user in this case
                self.sender.send('PRIVMSG %s :%s\r\n' % (nick, message))
            elif int(default_to_user) == 0:
                # Send to base channel in this case (rare)
                self.sender.send('PRIVMSG %s :%s\r\n' % (self.CHANNELS[0], nick + ' said: ' + message))
        else:
            self.sender.send('PRIVMSG %s :%s\r\n' % (channel, message))
    
    # Send KICK message to ChanServ
    def kickUser(self, channel, user, message):
        self.sender.send('PRIVMSG %s :%s\r\n' % ('ChanServ', 'KICK ' + channel + ' ' + user + ' ' + message))

    # Connect to the server
    def IRCconnect(self):
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.HOST, self.PORT))
        self.sender = ssl.wrap_socket(self.sender)
        self.sender.send('PASS %s\r\n' % (self.PASS))
        self.sender.send('USER %s %s bla :%s\r\n' % (self.IDENT, self.HOST, self.REALNAME))
        self.sender.send('NICK %s\r\n' % self.NICK)
        self.sender.send('PRIVMSG NickServ :IDENTIFY %s\r\n' % self.IDENT_PASS) #OPTCHANGEME
    
    # Regain control of nick
    def regainNick(self):
        self.sender.send('PRIVMSG NickServ :GHOST %s\r\n' % (self.NICK + ' ' + self.IDENT_PASS)) #OPTCHANGEME
        self.sender.send('NICK %s\r\n' % self.NICK)
        self.sender.send('PRIVMSG NickServ :IDENTIFY %s\r\n' % self.IDENT_PASS) #OPTCHANGEME
    
    # Decide what to do with message
    def parseLine(self, line):
        prefix, command, params = self.parseIrcMsg(line)
        command = command.upper()
        if command == 'PRIVMSG':
            print self.parseIrcUser(prefix) + ' sent PRIVMSG to chan/user ' + params[0] + ' with text ' + params[1]
            isBotCommand = False
            if params[1].startswith(self.IDENT_CHAR):
                isBotCommand = True
            if not isBotCommand and not params[1].isupper() and any(c.isalpha() for c in params[1]):
                # Kick or message the user
                if params[0] == self.NICK:
                    self.sendIrcMessage(self.parseIrcUser(prefix), params[0], self.kick_message, True, True)
                elif self.parseIrcUser(prefix) not in self.illegal_nicks:
                    self.kickUser(params[0], self.parseIrcUser(prefix), self.kick_message)
        elif command == '001':
            print 'Joined network, now joining channels!'
            for channel in self.CHANNELS:
                self.sender.send('JOIN %s\r\n' % channel)
        elif command == '433':
            print 'Nickname is already in use.'
            self.sender.send('NICK %s\r\n' % (self.NICK + '_'))
            self.regainNick()
    
    # Breaks a message from an IRC server into its prefix, command, and arguments.
    def parseIrcMsg(self, s):
        prefix = ''
        trailing = []
        if not s:
           print 'Empty line.'
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args
    
    # Breaks an IRC-styled username into just the username (no hostmask)
    def parseIrcUser(self, s):
        user =  s.split('!')[0]
        user = user.replace('~', '') # owners
        user = user.replace('&', '') # admins
        user = user.replace('@', '') # ops
        user = user.replace('%', '') # half-ops
        user = user.replace('+', '') # voiced
        user = user.replace(':', '') # just because
        return user
    
    def run(self):
        self.IRCconnect()
        readbuffer = ''
        while 1:
            readbuffer = readbuffer + self.sender.recv(4096)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop( )
            for line in temp:
                print line
                line = string.rstrip(line)                
                self.parseLine(line)
                line = string.split(line)
                if (line[0] == "PING"):
                    self.sender.send("PONG %s\r\n" % line[1])

def main():
    host = raw_input('IRC server: ')
    port = raw_input('IRC server port: ')
    pw = getpass.getpass('IRC server password: ')
    irc_pass = getpass.getpass(prompt = 'IRC ident password: ')
    allcapsbot = AllCapsBot(host, port, pw, irc_pass)
    allcapsbot.run()

if __name__ == "__main__":
    main()