# -*- coding: utf-8 -*-
'''
Created on 5 janv. 2017

@author: Jacky
'''

import logging
import socket
import struct

from django.conf import settings

logger = logging.getLogger('RCON.{}'.format(__name__))
SETTINGS = getattr(settings,'RCON_CONNECTION')[0]

SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0

MAX_COMMAND_LENGTH=510 # found by trial & error

MIN_MESSAGE_LENGTH=4+4+1+1 # command (4), id (4), string1 (1), string2 (1)
MAX_MESSAGE_LENGTH=4+4+4096+1 # command (4), id (4), string (4096), string2 (1)

# there is no indication if a packet was split, and they are split by lines
# instead of bytes, so even the size of split packets is somewhat random.
# Allowing for a line length of up to 400 characters, risk waiting for an
# extra packet that may never come if the previous packet was this large.
#PROBABLY_SPLIT_IF_LARGER_THAN = MAX_MESSAGE_LENGTH - 400

class SourceRconError(Exception):
    pass
 
class Rcon(object):
    
    '''
    classdocs
    '''
 
    def __init__(self, address=SETTINGS.get('ip'), 
                        port=SETTINGS.get('port', 27015), 
                        password=SETTINGS.get('password', ''), 
                        timeout=SETTINGS.get('timeout', 3.0)):
        '''
        Constructor
        '''
        self.host = address
        self.port = port
        self.password = password
        self.timeout = timeout
        self.tcp = False
        self.reqid = 0
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.tcp:
            self.tcp.close()
            self.tcp = False
            self.reqid = 0
            logger.info('RCON is disconnected from {}:{}.'.format(self.host, self.port))
         
    def connect(self):
        """Disconnect to the server."""
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(self.timeout)
        self.tcp.connect((self.host, self.port))
        logger.info('RCON is connected to {}:{}.'.format(self.host, self.port))
        
    def send(self, reqid, cmd, messages):
        """Send command and messages to the server. Should only be used internally."""
        if len(messages) > MAX_COMMAND_LENGTH:
            raise SourceRconError('RCON messages too large to send')
            
        data = struct.pack('<l', reqid).decode() + struct.pack('<l', cmd).decode() + messages + '\x00\x00'
        self.tcp.send(struct.pack('<l', len(data)) + data.encode())
        if cmd == 3:
            logger.debug('Send RCON command= {}, messages= {}'.format(cmd, "***PASSWORD***"))
        else:
            logger.debug('Send RCON command= {}, messages= {}'.format(cmd, messages))

    def receive(self, reqid):
        """Receive a reply from the server. Should only be used internally."""
        packetsize = False
        requestid = False
        response = False
        messages = ''
        message2 = ''

        # response may be split into multiple packets, we don't know how many
        # so we loop until we decide to finish
        while 1:
            # read the size of this packet
            buf = b''

            while len(buf) < 4:
                try:
                    recv = self.tcp.recv(4 - len(buf))
                    if not len(recv):
                        raise SourceRconError('RCON connection unexpectedly closed by remote host')
                    buf += recv
                except SourceRconError:
                    raise
                except:
                    break

            if len(buf) != 4:
                # we waited for a packet but there isn't anything
                break

            packetsize = struct.unpack('<l', buf)[0]

#             if packetsize < MIN_MESSAGE_LENGTH or packetsize > MAX_MESSAGE_LENGTH:
#                 raise SourceRconError('RCON packet claims to have illegal size: %d bytes' % (packetsize,))

            # read the whole packet
            buf = b''

            while len(buf) < packetsize:
                try:
                    recv = self.tcp.recv(packetsize - len(buf))
                    if not len(recv):
                        raise SourceRconError('RCON connection unexpectedly closed by remote host')
                    buf += recv
                except SourceRconError:
                    raise
                except:
                    break

            if len(buf) != packetsize:
                raise SourceRconError('Received RCON packet with bad length (%d of %d bytes)' % (len(buf),packetsize,))

            # parse the packet
            requestid = struct.unpack('<l', buf[:4])[0]

            if requestid == -1:
                self.disconnect()
                raise SourceRconError('Bad RCON password')

            elif requestid != reqid:
                raise SourceRconError('RCON request id error: %d, expected %d' % (requestid, reqid,))

            response = struct.unpack('<l', buf[4:8])[0]

            if response == SERVERDATA_AUTH_RESPONSE:
                # This response says we're successfully authed.
                return True

            elif response != SERVERDATA_RESPONSE_VALUE:
                raise SourceRconError('Invalid RCON command response: %d' % (response,))

            # extract the two strings using index magic
            str1 = buf[8:].decode()
            pos1 = str1.index('\x00')
            str2 = str1[pos1+1:]
            pos2 = str2.index('\x00')
            crap = str2[pos2+1:]

            if crap:
                raise SourceRconError('RCON response contains %d superfluous bytes' % (len(crap),))

            # add the strings to the full messages result
            messages += str1[:pos1]
            message2 += str2[:pos2]
            
            # Remove useless chars
            messages = messages.strip()
            
            # unconditionally poll for more packets
#             poll = select.select([self.tcp], [], [], 0)
# 
#             if not len(poll[0]) and packetsize < PROBABLY_SPLIT_IF_LARGER_THAN:
#                 # no packets waiting, previous packet wasn't large: let's stop here.
#                 break

        if response is False:
            raise SourceRconError('Timed out while waiting for reply')

        elif message2:
            raise SourceRconError('Invalid response messages: %s' % (repr(message2),))
        
        logger.debug('Receive RCON response: {}\n'.format(messages))
        return messages

    def rcon(self, command):
        """Send RCON command to the server. Connect and auth if necessary,
           handle dropped connections, send command and return reply."""
        
        if self.reqid > 1000:
            self.reqid = 0
        else:
            self.reqid += 1
            
        reqid = self.reqid
            
        # special treatment for sending whole scripts
        if '\n' in command:
            commands = command.split('\n')
            def f(x): y = x.strip(); return len(y) and not y.startswith("//")
            commands = filter(f, commands)
            results = map(self.rcon, commands)
            
            return "".join(results)

        # send a single command. connect and auth if necessary.
        try:
            self.send(reqid, SERVERDATA_EXECCOMMAND, command)
            return self.receive(reqid)
        except:
            # timeout? invalid? we don't care. try one more time.
            self.disconnect()
            self.connect()
            self.send(reqid, SERVERDATA_AUTH, self.password)

            auth = self.receive(reqid)
            # the first packet may be a "you have been banned" or empty string.
            # in the latter case, fetch the second packet
            if auth == '':
                auth = self.receive(reqid)

            if auth is not True:
                self.disconnect()
                raise SourceRconError('RCON authentication failure: %s' % (repr(auth),))

            self.send(reqid, SERVERDATA_EXECCOMMAND, command)
            return self.receive(reqid)


# Test
if __name__ == '__main__':

    import ArkDiscordBot.wsgi
    
    conn = Rcon()
    
    try:
        print(conn.rcon("listplayers"))
    except Exception as e:
        logger.error('RCON test error: '.format(e))
        
    conn.disconnect()

