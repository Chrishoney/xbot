import argparse
import ConfigParser
from datetime import datetime

from irc.bot import SingleServerIRCBot as SimpleBot

class Xbot(SimpleBot):

    def __init__(self, channel, nick, server, port):
        super(Xbot, self).__init__([(server, port)], nick, nick)
        self.channel = channel
        self.server = server
        self.port = port
        self.nick = nick
        self.logformat = '%H:%M:%S %Y-%m-%d'
        self.timeformat = '%A, %B %d %I:%M %p'
        self.commands = dict((
            ('time', self.time), 
            ('echo', self.echo)
        ))
        


    ################## 
    # Event Handlers #
    ################## 
    
    def on_welcome(self, c, e):
        ''' Join the channel specified in the config file. '''
        self.log_event(e, 'connect')
        c.join(self.channel)

    def on_join(self, c, e):
        ''' Log the join event. '''
        self.log_event(e, 'join')

    def on_pubmsg(self, c, e):
        ''' Execute the command if it is valid and respond to the channel. '''
        if self.is_command(e.arguments()[0]):
            self.log_msg(e)
            self.do_command(c, e, e.arguments()[0], source=self.channel)

    def on_privmsg(self, c, e):
        ''' Execute the command if it is valid and respond to the user. '''
        if self.is_command(e.arguments()[0]):
            self.log_msg(e)
            self.do_command(c, e, e.arguments()[0], source=e.source().nick)

    def on_quit(self, c, e):
        ''' Log the quit event. Doesn't work. ''' 
        self.log_event(e, 'disconnect')


    ###################      
    # Logging Methods #
    ###################      

    def log_msg(self, e):
        ''' Log public and private commands. '''
        print "%s: %s %s: '%s'" % (
                datetime.now().strftime(self.logformat),
                e.eventtype().upper(), 
                e.source().nick, 
                e.arguments()[0]
        )

    def log_event(self, e, event_type):
        ''' Log bot events. '''
        event_types = {
                'join':       'Joined %s'            % self.channel,
                'connect':    'Connected to %s'      % self.server,
                'disconnect': 'Disconnected from %s' % self.server
        }

        if event_type in event_types:
            print "%s: %s at %s" % (
                    datetime.now().strftime(self.logformat),
                    event_types[event_type],
                    self.nick
            )

    def log_response(self, e, cmd, args):
        ''' Log bot responses to commands. '''
        print "%s: %s %s: '%s' <%s>" % (
                datetime.now().strftime(self.logformat),
                e.eventtype().upper(),
                self.nick,
                args,
                cmd.upper()
        )


    ################### 
    # Command Parsing #
    ################### 

    def is_command(self, cmd):
        ''' Check if a command is real. '''
        cmd = split_args(cmd)[0] if isinstance(cmd, tuple) else cmd
        return cmd.startswith('!') and check_command(cmd)

    def check_command(self, cmd):
        ''' Check if a command exists in the commands dict. '''
        return cmd.lstrip('!') in self.commands.keys()

    def split_args(self, cmd):
        ''' Splits a command from the arguments. Returns (cmd, args)'''
        tokens = cmd.split()
        return (tokens[0], ' '.join(tokens[1:]))


    #################### 
    # Command Dispatch #
    #################### 

    def do_command(self, c, e, cmd, source):
        ''' Execute a command after passing a check. '''
        nick = e.source().nick
        c = self.connection
        command, args = self.split_args(cmd)
        if self.is_command(command) and self.check_command(command):
            self.dispatch(command[1:], c, e, args, source)
        else:
            pass

    def dispatch(self, cmd, c, e, args, source):
        ''' Get the command from the commands dict and execute it. '''
        self.commands[cmd](c, e, args, source)


    ################# 
    # User Commands #
    ################# 
            
    def time(self, c, e, args, source):
        ''' !time. Prints the current time to the channel. '''
        time = datetime.today().strftime(self.timeformat)
        c.privmsg(source, time)
        self.log_response(e, 'time', time)

    def echo(self, c, e, args, source):
        ''' !echo <msg>. Echoes anything after !echo to the channel. '''
        c.privmsg(source, args)
        self.log_response(e, 'echo', args)


#################
# Configuration #
#################

def parse_config(rc='.botrc'):
    ''' Parse the default config file and return a dict of settings '''
    config = ConfigParser.ConfigParser()
    config.read('.botrc')
    options = ['server', 'port', 'channel', 'nick']
    header = 'connection'
    settings = dict(zip(
        options,
        [config.get(header, option).strip("'") for option in options]
    ))
    settings['port'] = int(settings['port'])
    return settings


################
# Main Program #
################

if __name__ == '__main__':
    settings = parse_config()
    server  = settings['server']
    port    = settings['port']
    nick    = settings['nick']
    channel = settings['channel']
    bot = Xbot(channel, nick, server, port)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect(msg='My process was interrupted with ctrl+c')