# -*- coding: cp1252 -*-
import socket
import sys
import random
import MySQLdb
import os
import re
import string
import urllib2
import urllib
from time import ctime
from time import sleep
from time import time
from threading import Thread
import traceback

##[BEGIN - Global Settings]##
host = "irc.quakenet.org"
port = 6667
pub_chan = "#urtpickup"
admin_chan = "#urtpickup.admins"

OWNER="~gost0r@Gost0r.users.quakenet.orge"

print "initing values..."

filename_cfg    = "config.cfg"          #configfile
filename_ban    = "bans.cfg"            #banfile
filename_map    = "maps.cfg"            #mapfile
filename_player = "players.cfg"         #mapfile

version         = "v1.0"                #botversion
cmd_prefix      = "!"                   #cmd prefix
map_prefix      = "ut4_"                #map prefix

quit_cmd        = "!quit"               #quitcmd

pickup_remove   = "remove"              #pickup remove
pickup_maps     = "maps"                #pickup maplist
pickup_map      = "map"                 #pickup vote map
pickup_pw       = "lostpass"            #pickup lostpassword

pickup_add      = "add"                 #pickup add
pickup_gameover = "gameover"            #pickup gameover
pickup_status   = "status"              #pickup status
pickup_help     = "help"                #pickup help
pickup_ring     = "ring"                #pickup ring

pkup_lock       = "This game is currently locked"
pkup_map        = "Map was successfully voted."
pkup_signup     = "You can sign up again!"
pkup_pw         = "[ /connect .server. ; password .password. ]"
pkup_gameover   = "Thanks for submitting, .nick.! Need .gameoverleft. more player(s) to confirm that the match is over!"
pkup_status0    = "Nobody has signed up. Type !add to play."
pkup_status1    = "Sign up: [.playernumber./10] Type !status players to see who's signed up."
pkup_status2    = "Players [.playernumber./10]: .playerlist."
pkup_started    = "Game has already started. .remaintime. left."
pkup_go_admin   = "[ PickUp Game Info ][ Password: .password. ][ Map: .map. ][ Captains: .captain1. .captain2. ]"
pkup_go_cap     = "Pickup starts now and you are a Captain! The map is .map.. Connect to the server and have a 1on1 knife fight against .captain.. The winner can choose first! [ /connect .server. ; password .password. ]"
pkup_go_player  = "Pickup starts now! Connect to the server and stay as spectator until you are chosen by a captain! [ /connect .server. ; password .password. ]"
pkup_go_pub1    = "Pickup is about to start!"
pkup_go_pub2    = "Players: .playerlist."
pkup_go_pub3    = "Captains: .captain1. .captain2."
pkup_go_pub4    = "Map: .map."
pkup_go_pub5    = "Be patient when receiving the server address and password. It may take several seconds."
pkup_go_pub6    = "The messages have been sent. You didn't receive it? Type !lostpass"
pkup_sign       = "You can sign up again."
 
is_banned       = "You are banned from using this function."
already_gameover= "You can't submit gameover twice."
map_not_found   = "Map not found."

pickup_lock     = "lock"                #Locks a game                           DONE
pickup_unlock   = "unlock"              #Unlocks a game                         DONE
pickup_reset    = "reset"               #Resets a game                          DONE
pickup_getdata  = "getdata"             #Sends the ip + pw per pm to the admin  DONE
pickup_addmap   = "addmap"              #Adds a new map                         DONE
pickup_delmap   = "delmap"              #Removes a map                          DONE
pickup_server   = "setserver"           #Changes the server                     DONE
pickup_rcon     = "setrcon"             #Changes the rcon                       DONE
pickup_rconuse  = "rcon"                #Changes the rcon                       DONE
pickup_test     = "test"                #Sets the player number                 DONE for test proposes

ban_add         = "addban"              #cmd add ban                            DONE
ban_delete      = "delban"              #cmd remove ban                         DONE

banlist = []
maplist = []
votelist = []
gameoverlist = ['','','','','','','','','','']
playerlist = []
addlist = []
game = ''
locked = ''
playernum = ''
addnum = ''
gameover = ''
server = ''
rcon = ''
password = ''
endtime = ''
select = False
status_msg = False

msg_last = ''

a_server = ''
a_rcon = ''
a_smap = ''
a_password = ''
a_captain1 = ''
a_captain2 = ''

ping_last = 0
ping_active = 0

class pickup(Thread):
    def __init__(self, useprint):
        Thread.__init__(self)
        self.useprint = useprint
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.host = host
        self.port = port
        self.nick = "UrTPickup"
        self.realname = "UrTPickup " + version + " by Gost0r"
        self.identt = "URTPICKUP"
        self.readbuffer = ""

        self.gettime = ""
        self.getdate = ""
        self.getall = ""
        self.getmonth = ""
        self.getyear = ""

    def normalize_day(self, day):
        if len(day) == 1:
            return "0" + day
        else:
            return day

    def update_ping(self):
        global ping_last, ping_active
        ping_last = time()
        ping_active = 1

    def p_readin(self):
        global filename_cfg, filename_ban, filename_maps, game, locked, playernum, addnum, gameover, server, rcon, password, endtime, banlist, maplist, playerlist, votelist, addlist, addnum
        f = open(filename_cfg, 'r')
        game = f.readline().split('=')
        game = game[1].replace('\n','')
        locked = f.readline().split('=')
        locked = locked[1].replace('\n','')
        playernum = f.readline().split('=')
        addnum = playernum[1].replace('\n','')
        playernum = playernum[1].replace('\n','')
        gameover = f.readline().split('=')
        gameover = gameover[1].replace('\n','')
        server = f.readline().split('=')
        server = server[1].replace('\n','')
        rcon = f.readline().split('=')
        rcon = rcon[1].replace('\n','')
        password = f.readline().split('=')
        password = password[1].replace('\n','')
        endtime = f.readline().split('=')
        endtime = endtime[1].replace('\n','')
        f.close()
        print 'game: ' + game
        print 'locked: ' + locked
        print 'playernum: ' + playernum
        print 'gameover: ' + gameover
        print 'server: ' + server
        print 'rcon: ' + rcon
        print 'password: ' + password
        print 'endtime: ' + endtime
        
        f = open(filename_ban, 'r')
        banlist = f.readlines()
        for i in range(0,len(banlist)-1):
            banlist[i] = banlist[i].replace('\n','')
        f.close()
        print banlist
        
        f = open(filename_map, 'r')
        maplist = f.readlines()
        for i in range(0,len(maplist)-1):
            maplist[i] = maplist[i].replace('\n','')
        f.close()
        print maplist

        if game == "1":
            f = open(filename_player, 'r')
            playerlist = f.readlines()
            addlist = copy.deepcopy(playerlist)
            for i in range(0,len(playerlist)):
                playerlist[i] = playerlist[i].replace('\n','')
                addlist[i] = addlist[i].replace('\n','')
                votelist.append('')
            f.close()
            print playerlist
            print votelist
        else:
            playerlist = []
            addlist = []
            f = open(filename_player, 'w')                      #Clear file
            swrite = ""
            f.write(swrite)
            f.close()

            addnum = "0"
            playernum = "0"
            f = open(filename_cfg, 'r')
            cfg_file_cont = f.readlines()
            f.close()
            cfg_file_cont[2] = 'player='+ str(playernum) + '\n' #WRITE PLAYERNUM 0 in file
            swrite = ''
            f = open(filename_cfg, 'w')
            for i in range(0,len(cfg_file_cont)):
                swrite = swrite + cfg_file_cont[i]
            f.write(swrite)
            f.close()

    def p_add(self,nick,already_added):
        global playerlist, playernum, status_msg, votelist
        found = False
        for i in range(0, len(playerlist)): #ALREADY IN PLAYERLIST?
            if playerlist[i] == nick:
                found = True
        if found == False:
            playernum = str(int(playernum) + 1)
            cfg_file_cont = []
            f = open(filename_cfg, 'r')
            cfg_file_cont = f.readlines()
            f.close()
            cfg_file_cont[2] = 'player='+ str(playernum) + '\n' #WRITE PLAYERNUM IN FILE
            swrite = ''
            f = open(filename_cfg, 'w')
            for i in range(0,len(cfg_file_cont)):
                swrite = swrite + cfg_file_cont[i]
            f.write(swrite)
            f.close()
            playerlist.append(nick)                             #ADDING PLAYER TO LIST
            swrite = ''
            f = open(filename_player, 'w')                      #write playername in file
            for i in range(0,len(playerlist)):
                if i == 0:
                    swrite = playerlist[i]
                else:
                    swrite = swrite + '\n' + playerlist[i]
            f.write(swrite)
            f.close()
            votelist.append('')                                 #ADDING VOTE
            if playernum == '10':
                self.p_start()
            else:
                status_msg = True
    
    def p_quit(self,nick, has_quit):
        global playerlist, playernum, addnum, votelist, game, status_msg, addlist
        found = False
        for i in range(0, len(playerlist)):
            if playerlist[i] == nick:
                found = True
        if found == True:
            if game == "0":
                playernum = str(int(playernum)- 1)      #CHANGE PLAYERNUM
                addnum = str(int(addnum)- 1)            #CHANGE ADDNUM
                addlist.remove(nick)
                f = open(filename_cfg, 'r')
                cfg_file_cont = f.readlines()
                f.close()
                cfg_file_cont[2] = 'player='+ str(playernum) + '\n'
                swrite = ''
                f = open(filename_cfg, 'w')
                for i in range(0,len(cfg_file_cont)):
                    swrite = swrite + cfg_file_cont[i]
                f.write(swrite)
                f.close()
                print playerlist.index(nick)
                print votelist
                votelist.pop(playerlist.index(nick)) # vote rückgängig machen
                playerlist.remove(nick)
                swrite = ''
                f = open(filename_player, 'w')                      #write playername in file
                for i in range(0,len(playerlist)):
                    if i == 0:
                        swrite = playerlist[i]
                    else:
                        swrite = swrite + '\n' + playerlist[i]
                f.write(swrite)
                f.close()
                print playerlist
                if has_quit == False:
                    status_msg = True

    def p_maps(self, channel):
        global maplist, votelist
        if len(maplist) != 0:
            for i in range(0,len(maplist)):
                num_voted = votelist.count(maplist[i])
                if i == 0:
                    print_maps = map_prefix + maplist[i] + ': '+str(num_voted)
                else:
                    print_maps = print_maps + ' || ' + map_prefix + maplist[i] + ': '+str(num_voted)
            self.s.send('PRIVMSG ' + channel + ' :' + print_maps+ '\n')
            self.update_ping()

    def p_ring(self, channel):
        global playernum, game
        if game == "0":
            playerleft = 10 - int(playernum)
            playernum = str(playernum)
            if playernum == 1:
                players_s = ''
            else:
                players_s = 's'
            self.s.send('PRIVMSG ' + channel + ' :!ringer ' + str(playerleft) + ' Need ' + str(playerleft) + ' more player' + players_s + ' to start. Join ' + channel + ' and !add\n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :!ringer 1 A game has already started, but some players are missing. Join ' + channel + ' and help out\n')
        self.update_ping()
            
    def p_map(self, channel,nick,sent_map):
        global playerlist, votelist
        found = False
        for i in range(0, len(playerlist)):
            if playerlist[i] == nick:
                found = True
        if found == True:
            if votelist[playerlist.index(nick)] == '':
                sent_map = sent_map.replace(map_prefix,'')
                print maplist
                if sent_map in maplist:
                    votelist[playerlist.index(nick)] = sent_map
                    self.s.send('NOTICE ' + nick + ' :' + pkup_map + '\n')
                else:
                    self.s.send('NOTICE ' + nick + ' :' + map_not_found + '\n')
                self.update_ping()

    def p_setcfg(self, state,value):
        global locked, server, rcon
        cfg_file_cont = []
        f = open(filename_cfg, 'r')
        cfg_file_cont = f.readlines()
        f.close()
        if state == 'lock':
            cfg_file_cont[1] = 'locked=1\n'
            locked = '1'
        elif state == 'unlock':
            cfg_file_cont[1] = 'locked=0\n'
            locked = '0'
        elif state == 'server':
            cfg_file_cont[4] = 'server=' + value + '\n'
            server = value
        elif state == 'rcon':
            cfg_file_cont[5] = 'rcon=' + value + '\n'
            rcon = value
        elif state == 'test':
            cfg_file_cont[2] = 'player=' + value + '\n'
            playernum = value

        swrite = ''
        f = open(filename_cfg, 'w')
        for i in range(0,len(cfg_file_cont)):
            swrite = swrite + cfg_file_cont[i]
        f.write(swrite)
        f.close()

    def p_pw(self, nick):
        global playerlist, server, password
        found = False
        for i in range(0, len(playerlist)):
            if playerlist[i] == nick:
                found = True
        if found == True:
            msg = pkup_pw.replace(".server.", server)
            msg = msg.replace(".password.", str(password))
            self.s.send('PRIVMSG ' + nick + ' :' + msg + '\n')
            self.update_ping()
            
    def p_status(self, channel,typed):
        global playernum, playerlist, addnum, msg_last
        splayerlist = ''
        if int(playernum) > 0:
            if typed == True:
                msg = pkup_status2.replace(".playernumber.", str(playernum))
                for i in range(0,len(playerlist)):
                    if playerlist[i] != '':
                        if splayerlist == '':
                            splayerlist = playerlist[i]
                        else:
                            splayerlist = splayerlist + ' ' + playerlist[i]
                msg = msg.replace(".playerlist.", str(splayerlist))
                self.s.send('NOTICE ' + channel + ' :' + msg + '\n')
                self.update_ping()
            else:
                msg = pkup_status1.replace(".playernumber.", str(addnum))
        else:
            msg = pkup_status0
        if splayerlist == '':
            if not msg_last == msg:
                msg_last = msg
                self.s.send('PRIVMSG ' + pub_chan + ' :' + msg + '\n')
                self.update_ping()

    def p_gameover(self, channel,nick):
        global gameover, gameoverlist
        found = False
        for i in range(0, len(playerlist)):
            if playerlist[i] == nick:
                found = True
        if found == True:
            if gameoverlist[playerlist.index(nick)] == '':
                gameoverlist[playerlist.index(nick)] = '1'
                print playerlist.index(nick)
                print gameoverlist
                cfg_file_cont = []
                f = open(filename_cfg, 'r')
                cfg_file_cont = f.readlines()
                f.close()
                gameover = int(gameover) - 1
                cfg_file_cont[3] = 'gameover='+str(gameover) +'\n'
                swrite = ''
                f = open(filename_cfg, 'w')
                for i in range(0,len(cfg_file_cont)):
                    swrite = swrite + cfg_file_cont[i]
                f.write(swrite)
                f.close()
                if gameover == 0:
                    self.p_reset()
                else:
                    msg = pkup_gameover.replace('.gameoverleft.', str(gameover))
                    msg = msg.replace('.nick.', nick)
                    self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                    self.update_ping()
            else:
                self.s.send('PRIVMSG ' + channel + ' :' + already_gameover + '\n')
                self.update_ping()
            
    def p_help(self, channel):
        self.s.send('PRIVMSG ' + channel + ' :CMDs are !add !remove !status !map !maps !lostpass !gameover !ring \n')

    def devoiceall(self,plist):
        dvlist1 = ''
        dvlist2 = ''
        for i in range(0, len(plist)):
            if i < 5:
                dvlist1 = dvlist1 + ' ' + plist[i]
            else:
                dvlist2 = dvlist2 + ' ' + plist[i]
        self.s.send('MODE ' + pub_chan + ' -vvvvvv ' +dvlist1 + '\n')
        self.s.send('MODE ' + pub_chan + ' -vvvvvv ' +dvlist2 + '\n')
        self.s.send('MODE ' + pub_chan + ' -m\n')
        self.update_ping()
    
    def small(self, text):
        return text.lower()

    def p_endtime(self):
        global endtime
#        time = time.split(":")
#        hour = time[0]
#        minute = int(time[1]) + 30
#        sec = time[2]
#        date = date.split(".")
#        year = date[2]
#        month = date[1]
#        day = date [0]
#        if int(minute) >= 60:
#            minute = minute - 60
#            hour = int(hour) + 1
#            if int(hour) >= 24:
#                hour = 0
#                day = int(day) + 1
#            if int(day) > 31 and (int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or int(month) == 8 or int(month) == 10 or int(month) == 12):
#                day = 1
#                month = int(month) + 1
#            if int(day) > 30 and (int(month) != 1 and int(month) != 2 and int(month) != 3 and int(month) != 5 and int(month) != 7 and int(month) != 8 and int(month) != 10 and int(month) != 12):
#                day = 1
#                month = int(month) + 1
#            if int(day) > 28 and int(month) == 2:
#                day = 1
#                month = int(month) + 1
#            if int(month) >= 12:
#                month = 1
#                year = int(year) + 1
#            minute = self.normalize_day(str(minute)) #Function
#            hour = self.normalize_day(str(hour)) #Function
#            day = self.normalize_day(str(day)) #Function
#            month = self.normalize_day(str(month)) #Function
#            endtime = str(year) + str(month) + str(day) + str(hour) + str(minute) + str(sec)
#            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(endtime) + "' WHERE name='endtime'")
        endtime = time() + (30*60) # current time in s + 30mins
        cfg_file_cont = []
        f = open(filename_cfg, 'r')
        cfg_file_cont = f.readlines()
        f.close()
        cfg_file_cont[7] = 'endtime='+str(int(endtime))
        swrite = ''
        f = open(filename_cfg, 'w')
        for i in range(0,len(cfg_file_cont)):
            swrite = swrite + cfg_file_cont[i]
        f.write(swrite)
        f.close()

    def p_start(self):
        global game, server, rcon, password, maplist, votelist, playerlist, a_server, a_rcon, a_smap, a_password, a_captain1, a_captain2, select
        self.s.send('MODE ' + pub_chan + ' +m\n')
        #GAME#
        game = '1'
        select = True
        #TIME#
        self.p_endtime()
        #PASSWORD#
        password = random.randint(100000, 999999)
        #SAVE CFG#
        cfg_file_cont = []
        f = open(filename_cfg, 'r')
        cfg_file_cont = f.readlines()
        f.close()
        print cfg_file_cont[0]
        cfg_file_cont[0] = 'game=1\n'
        print cfg_file_cont[6]
        cfg_file_cont[6] = 'password=' + str(password) + '\n'
        swrite = ''
        f = open(filename_cfg, 'w')
        for i in range(0,len(cfg_file_cont)):
            swrite = swrite + cfg_file_cont[i]
        f.write(swrite)
        f.close()
        #VOTES#
        smaplist = []
        for i in range(0,len(maplist)):
            tempmaplist = maplist[i]
            tempvotelistcount = votelist.count(tempmaplist)
            smaplist.append(votelist.count(maplist[i]))
        print "smaplist passed"
        vmaplist = []
        for i in range(0,len(maplist)):
            vmaplist.append(maplist[i])
        print "vmaplist passed"
            
	durchlaeufe = len(smaplist)
	while durchlaeufe >= 1:
	    for k in range(len(smaplist) - 1):
                if smaplist[k] > smaplist[k+1]:
                    temp = smaplist[k]
                    vtemp = vmaplist[k]
                    smaplist[k] = smaplist[k+1]
                    vmaplist[k] = vmaplist[k+1]
                    smaplist[k+1] = temp
                    vmaplist[k+1] = vtemp
	    durchlaeufe = durchlaeufe - 1
    
        smap = vmaplist[len(vmaplist)-1]
            
        randommapwhentie = []
        randommapwhentie.append(smap)
        for i in range(len(smaplist)-2,0,-1):
            if smaplist[i] == smaplist[len(smaplist)-1]:
                randommapwhentie.append(vmaplist[i])
        randomnum = random.randint(0, len(randommapwhentie)-1)
        smap = 'ut4_' +randommapwhentie[randomnum]
            
        print "smap passed " + smap
        #CAPTAIN#
        captain1 = random.randint(0, 9)
        captain1 = playerlist[captain1]
        captain2 = random.randint(0, 9)
        captain2 = playerlist[captain2]
        while(captain1 == captain2):
            captain2 = random.randint(0, 9)
            captain2 = playerlist[captain2]
        print "captain passed " + captain1 + " " + captain2
        #SERVER SET#
        a_server = server
        a_rcon = rcon
        a_smap = smap
        a_password = password
        a_captain1 = captain1
        a_captain2 = captain2
        serverThread = q3rcon()
        serverThread.start()
        print "serverthread passed"
        #MAP votes
        print_maps = 'No votes for any map - RANDOM MAP!'
        derpcount = 0
        if len(maplist) != 0:
            for i in range(0,len(maplist)):
                num_voted = votelist.count(maplist[i])
                if num_voted > 0:
                    if derpcount == 0:
                        print_maps = map_prefix + maplist[i] + ': '+str(num_voted)
                        derpcount = 1
                    else:
                        print_maps = print_maps + ' || ' + map_prefix + maplist[i] + ': '+str(num_voted)
                        
        #MESSAGES
        msg = pkup_go_admin.replace(".captain1.", captain1)
        msg = msg.replace(".captain2.", captain2)
        msg = msg.replace(".password.", str(password))
        msg = msg.replace(".map.", smap)
        self.s.send('PRIVMSG ' + admin_chan + ' :' + msg + '\n')
        splayerlist = ''
        for i in range(0,len(playerlist)):
            if playerlist[i] != '':
                if splayerlist == '':
                    splayerlist = playerlist[i]
                else:
                    splayerlist = splayerlist + ' ' + playerlist[i]
        msg = pkup_go_pub2.replace(".playerlist.", str(splayerlist))
        self.s.send('PRIVMSG ' + pub_chan + ' :' + pkup_go_pub1 + '\n')
        sleep(2)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + print_maps + '\n')
        sleep(3)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + msg + '\n')
        sleep(2)
        msg = pkup_go_pub3.replace(".captain1.", captain1)
        msg = msg.replace(".captain2.", captain2)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + msg + '\n')
        sleep(2)
        msg = pkup_go_pub4.replace(".map.", smap)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + msg + '\n')
        sleep(2)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + pkup_go_pub5 + '\n')
        sleep(3)

        smsgcap = pkup_go_cap.replace(".map.", smap)
        smsgcap = smsgcap.replace(".server.", server)
        smsgcap = smsgcap.replace(".password.", str(password))
        msgply = pkup_go_player.replace(".map.", smap)
        msgply = msgply.replace(".server.", server)
        msgply = msgply.replace(".password.", str(password))
        
        for i in range(0,len(playerlist)):
            if playerlist[i] == captain1:
                msgcap = smsgcap.replace(".captain.", captain2)
                self.s.send('PRIVMSG ' + playerlist[i] + ' :' + msgcap + '\n')
            elif playerlist[i] == captain2:
                msgcap = smsgcap.replace(".captain.", captain1)
                self.s.send('PRIVMSG ' + playerlist[i] + ' :' + msgcap + '\n')
            else:
                self.s.send('PRIVMSG ' + playerlist[i] + ' :' + msgply + '\n')
            sleep(3)
        self.s.send('PRIVMSG ' + pub_chan + ' :' + pkup_go_pub6 + '\n')
        sleep(10)
        self.devoiceall(playerlist)
        self.update_ping()
    
    def p_end(self):
        global endtime
        if ((int(endtime) - int(time())) <= 0) and game == '1':
            self.p_reset()

    def p_reset(self):
        global playerlist, gameoverlist, votelist, playernum, addnum, gameover, game, addlist
        #PLAYERS#
        splayerlist = playerlist
        playerlist = []
        f = open(filename_player, 'w')
        f.close()
        self.devoiceall(splayerlist)
        addlist = []
        #STATUS#
        cfg_file_cont = []
        f = open(filename_cfg, 'r')
        cfg_file_cont = f.readlines()
        f.close()
        cfg_file_cont[0] = 'game=0\n'
        cfg_file_cont[2] = 'player=0\n'
        cfg_file_cont[3] = 'gameover=4\n'
        swrite = ''
        f = open(filename_cfg, 'w')
        for i in range(0,len(cfg_file_cont)):
            swrite = swrite + cfg_file_cont[i]
        f.write(swrite)
        f.close()
        playernum = '0'
        addnum = '0'
        gameover = '4'
        game = '0'
        #MAPS#
        votelist = []
        gameoverlist = ['','','','','','','','','','']
        #MSG#
        self.s.send('PRIVMSG ' + pub_chan + ' :' + pkup_sign + '\n')
        self.update_ping()


    def run(self):
        global locked, game, server, password, playerlist, playernum, addnum, a_server, a_rcon, rcon, ping_active, ping_last, select, status_msg, addlist
        self.s.connect((self.host, self.port))
        self.s.send("NICK %s\r\n" % self.nick)
        self.s.send("USER %s 0 0 %s\r\n" % (self.identt, self.realname))
        self.p_readin()
        op=[]

        ping_last = 0
        ping_active = 1
        while True:
            if self.useprint:
                try:
                    irctext = self.s.recv(4096).split('\n')
                    for textcounter in range(0, len(irctext)):
                        text = irctext[textcounter]
                        if len(text) > 0:
                            print text
                        data = text.split()
                        if len(data) <= 1:
                            data = ['', '']            
            
                        if data[1] == "513" and len(data) >= 9:
                            self.s.send('PONG ' + data[8] + '\n')
                            self.update_ping()
                        if "PING" in text and len(data) >= 2 and not "PRIVMSG" in text:
                            self.s.send('PONG ' + data[1] + '\n')
                            self.update_ping()
                        if "Nickname is already in use." in text and not "PRIVMSG" in text:
                            self.s.send('NICK UrTPickupBOT \r\n')
                            self.update_ping()
                        if "Message of the Day" in text and not "PRIVMSG" in text:
                            self.s.send ('PRIVMSG Q@CServe.quakenet.org :AUTH UrTPickup CPdLUjPAh3\n')
                            sleep(2)
                            self.s.send('MODE %s :+x \r\n' % (self.nick))
                            self.s.send("JOIN %s \r\n" % (pub_chan))
                            self.s.send("JOIN %s \r\n" % (admin_chan))
                            if game == "1":
                                sleep(3)
                                self.s.send('MODE ' + pub_chan + ' -m\n')
                            self.update_ping()
        
                        #PICKUP#
                        self.p_end() #Function

                        if data[1] == "QUIT" or data[1] == "PART":
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            self.p_quit(nick,True) #Function
                            if nick in op:
                                op.remove(nick)

                        if data[1] == "KICK":
                            nick = data[3]
                            self.p_quit(nick,True) #Function
                            if nick in op:
                                op.remove(nick)
                                op.append(newnick)
                            
                        if data[1] == "353" and len(data) >= 5:
                            if data[4] == pub_chan:
                                replacer = data[0] + " " + data[1] + " " + data[2] + " " + data[3] + " " + data[4] + " :"
                                getnames = text.replace(replacer, "")
                                getnames = getnames.split()
                                zahl = 0
                                names = ""
                                while(zahl < len(getnames)):
                                    if "@" in getnames[zahl]:
                                        getnames[zahl] = getnames[zahl].replace("@", "")
                                        op.append(getnames[zahl])
                                        print op
                                    elif "+" in getnames[zahl]:
                                        if game == '0':
                                            getnames[zahl] = getnames[zahl].replace("+", "")
                                            self.p_add(getnames[zahl],True) # ADDING THE PERSON
                                            found = False
                                            for i in range(0, len(addlist)):
                                                if addlist[i] == getnames[zahl]:
                                                    found = True
                                            if found == False:
                                                addlist.append(getnames[zahl])
                                                addnum = str(int(addnum)+1)
                                    zahl = zahl + 1

                        if data[1] == "NICK" and len(data) >= 3:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            newnick = data[2].replace(":","")
                            if nick in op:
                                op.remove(nick)
                                op.append(newnick)
                                print op
                            found = False
                            for i in range(0, len(playerlist)):
                                if playerlist[i] == nick:
                                    found = True
                            if found == True:
                                cfg_file_cont = []
                                f = open(filename_player, 'r')
                                cfg_file_cont = f.readlines()
                                f.close()
                                for i in range(0,len(playerlist)):
                                    if playerlist[i] == nick:
                                        playerlist[i] = newnick
                                        cfg_file_cont[i] = newnick
                                swrite = ''
                                f = open(filename_player, 'w')
                                for i in range(0,len(cfg_file_cont)):
                                    swrite = swrite + cfg_file_cont[i]
                                f.write(swrite)
                                f.close()
                                for i in range(0,len(addlist)):
                                    if addlist[i] == nick:
                                        addlist[i] = newnick

                        if data[1] == "MODE":
                            if "+o" in data[3]:
                                if data[2] == pub_chan: # data[2] = CHANNEL #data[4] = NICK
                                    op.append(data[4])
                                    print op
                            elif "-o" in data[3]:
                                if data[2] == pub_chan:
                                    if data[4] in op:
                                        op.remove(data[4])
                                        print op
                            elif "+v" in data[3]:
                                if data[2] == pub_chan:
                                    if game == '0':
                                        self.p_add(data[4],False)
                                        found = False
                                        for i in range(0, len(addlist)):
                                            if addlist[i] == data[4]:
                                                found = True
                                        if found == False:
                                            addlist.append(data[4])
                                            addnum = str(int(addnum)+1)
                            elif "-v" in data[3]:
                                if data[2] == pub_chan:
                                    if game == '0':
                                        self.p_quit(data[4],False)
                            elif data[3] == "-m":
                                select = False
                                
#                        if data[1] == "330" and len(data) >= 5:
#                            nick = data[3]
#                            if nick != "Q":
#                                authnick = data[4]
#                                self.cursor.execute("SELECT * FROM 1_peng_auth WHERE Nick='" + nick + "'")
#                                getauth = self.cursor.fetchone()
#                                if getauth == None:
#                                    self.cursor.execute("INSERT INTO 1_peng_auth (Nick, AuthNick, host) VALUES ('" + nick + "', '" + authnick + "', '" + LOGhost + "')")
#            
#                                if LOGchans != LOGchansold:##
#                                    LOGchansold = LOGchans##
#                                    num = 0##
#                                    LOGchans = LOGchans.split()##
#                                    while (num < len(LOGchans)):##
#                                        self.cursor.execute("SELECT name FROM 1_peng_chanstats WHERE name='" + nick + "' AND channel='" + LOGchans[num] + "'")##
#                                        LOGexist = self.cursor.fetchone()##
#                                        if LOGexist == None:##
#                                            self.cursor.execute("UPDATE 1_peng_chanstats SET qauth='" + str(authnick) + "' WHERE name='" + nick + "'")##
#                                            self.cursor.execute("UPDATE 1_peng_chanstats SET host='" + str(LOGhost) + "' WHERE name='" + nick + "'")##
#                                            self.cursor.execute("UPDATE 1_peng_chanstats SET lastseen='" + str(self.getdate) + " " + str(self.gettime) + "' WHERE name='" + nick + "'")##
#                                        num = num + 1##

                        if "PRIVMSG" in text and len(data) >= 4:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            nick = nick.replace("\'","`")
                            
                            if data[3] == ":"+quit_cmd:
                                shost = getnick[1]
                                print data[3] + " " + shost
                                if shost in OWNER:
                                    self.s.send('QUIT\n')
                                    ping_active = 0
                                    self.s.close()
                                    sys.exit()

                            if (":" + cmd_prefix) in data[3]:
                                channel = data[2]
                                if channel == admin_chan:
                                    if len(data) == 4:
                                        if data[3].lower() == ":!reboot":
                                            self.s.send('REBOOTING, brb\n')
                                            self.s.close()
                                            sys.exit()
                                            ping_last = 0
                                        if data[3].lower() == (":" + cmd_prefix + pickup_lock): #LOCK
                                            self.p_setcfg('lock',0)
                                            self.s.send('PRIVMSG ' + channel + ' :LOCKED\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_unlock): #UNLOCK
                                            self.p_setcfg('unlock',0)
                                            self.s.send('PRIVMSG ' + channel + ' :UNLOCKED\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_getdata): #GETDATA
                                            msg = pkup_pw.replace(".server.", server)
                                            msg = msg.replace(".password.", str(password))
                                            self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                                            self.update_ping()
                                    if len(data) == 5:
                                        if data[3].lower() == (":" + cmd_prefix + ban_delete): #DELBAN
                                            bannick = data[4]
                                            if bannick in banlist:
                                                cfg_file_cont = []
                                                f = open(filename_ban, 'r')
                                                cfg_file_cont = f.readlines()
                                                f.close()
                                                cfg_file_cont.remove(bannick)
                                                banlist.remove(bannick)
                                                swrite = ''
                                                f = open(filename_ban, 'w')
                                                for i in range(0,len(cfg_file_cont)):
                                                    swrite = swrite + cfg_file_cont[i]
                                                f.write(swrite)
                                                f.close()
                                                self.s.send('PRIVMSG ' + channel + ' :Ban of ' + bannick + ' was successfully deleted.\n')
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + bannick + ' isn\'t banned.\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + ban_add): #ADDBAN
                                            bannick = data[4]
                                            banlist.append(bannick)
                                            f = open(filename_ban, 'a+')
                                            if len(f.readlines()) < 1:
                                                f.write(bannick)
                                            else:
                                                f.write('\n'+bannick)
                                            f.close()
                                            self.s.send('PRIVMSG ' + channel + ' :Ban of ' + bannick + ' was successfully stored.\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_addmap): #ADDMAP
                                            newmap = data[4]
                                            maplist.append(newmap)
                                            f = open(filename_map, 'a+')
                                            if len(f.readlines()) < 1:
                                                f.write(newmap)
                                            else:
                                                f.write('\n'+newmap)
                                            f.close()
                                            self.s.send('PRIVMSG ' + channel + ' :Map ' + data[4] + ' added.\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_delmap): #DELMAP
                                            newmap = data[4]
                                            cfg_file_cont = []
                                            f = open(filename_map, 'r')
                                            cfg_file_cont = f.readlines()
                                            f.close()
                                            cfg_file_cont.remove(newmap)
                                            maplist.remove(newmap)
                                            swrite = ''
                                            f = open(filename_map, 'w')
                                            for i in range(0,len(cfg_file_cont)):
                                                swrite = swrite + cfg_file_cont[i]
                                            f.write(swrite)
                                            f.close()
                                            self.s.send('PRIVMSG ' + channel + ' :Map ' + data[4] + ' deleted.\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_test): #TEST
                                            playernum = data[4]
                                            playerlist = []
                                            i=0
                                            while len(playerlist) < int(data[4]):
                                                playerlist.append('Gost0r'+str(i))
                                                i=int(i)+1
                                            print playerlist
                                            self.s.send('PRIVMSG ' + channel + ' :Players set to ' + data[4] + '\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_rcon): #SETRCON
                                            self.p_setcfg('rcon',data[4])
                                            self.s.send('PRIVMSG ' + channel + ' :Rcon changed to ' + data[4] + '\n')
                                            self.update_ping()
                                        elif data[3].lower() == (":" + cmd_prefix + pickup_server): #SETSERVER
                                            self.p_setcfg('server',data[4])
                                            self.s.send('PRIVMSG ' + channel + ' :Server changed to ' + data[4] + '\n')
                                            self.update_ping()

                                if channel == pub_chan:
                                    if locked == '0':
                                        found = False
                                        for i in range(0, len(banlist)):
                                            if banlist[i] == nick:
                                                found = True
                                        if found == False:
                                            if game == '0': #and (data[4] != pickup_pw and data[4] != pickup_gameover):
                                            #ADD
                                                if data[3].lower() == (":" + cmd_prefix + pickup_add):
                                                    found = False
                                                    for i in range(0, len(addlist)):
                                                        if addlist[i] == nick:
                                                            found = True
                                                    if found == False:
                                                        if int(addnum) <= 9:
                                                            print playernum
                                                            addnum = str(int(addnum)+1)
                                                            addlist.append(nick)
                                                            print playernum
                                                            self.s.send('MODE ' + channel + ' +v ' +nick+ '\n')
                                                            self.update_ping()
                                            #REMOVE
                                                if data[3].lower() == (":" + cmd_prefix + pickup_remove):
                                                    found = False
                                                    for i in range(0, len(playerlist)):
                                                        if playerlist[i] == nick:
                                                            found = True
                                                    if found == True:
                                                        self.s.send('MODE ' + channel + '  -v ' +nick+ '\n')
                                                        self.update_ping()
                                            #MAPS
                                                if data[3].lower() == (":" + cmd_prefix + pickup_maps):
                                                    self.p_maps(channel)
                                            #MAP
                                                if data[3].lower() == (":" + cmd_prefix + pickup_map):
                                                    if len(data) >= 5:
                                                        self.p_map(channel,nick,data[4].lower())
                                                    else:
                                                        self.p_maps(channel)
                                            #STATUS
                                                if data[3].lower() == (":" + cmd_prefix + pickup_status):
                                                    self.p_status(nick, True)
                                                            
                                            elif game == '1' and (pickup_pw in data[3].lower() or pickup_gameover in data[3].lower()):
                                            #GAMEOVER
                                                if data[3].lower() == (":" + cmd_prefix + pickup_gameover):
                                                    self.p_gameover(channel,nick) #Function
                                            #PW
                                                if data[3].lower() == (":" + cmd_prefix + pickup_pw):
                                                    self.p_pw(nick) #Function
                                                            
                                            elif game == '1' and pickup_pw not in data[3].lower() and pickup_gameover not in data[3].lower() and pickup_reset not in data[3].lower() and pickup_rconuse not in data[3].lower() and pickup_ring not in data[3].lower() and select == False:
                                                stime = int(endtime) - int(time())
                                                stime1 = stime / 60
                                                stime1 = str(stime1).split('.')
                                                stime1 = stime1[0]
                                                stime2 = stime % 60
                                                stime2 = str(stime2).split('.')
                                                stime2 = stime2[0]
                                                if int(stime1) > 0:
                                                    stime = str(stime1) + 'min '
                                                else:
                                                    stime = ''
                                                stime = stime + str(stime2) + 'sec'
                                                msg = pkup_started.replace(".remaintime.", stime)
                                                self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                                                self.update_ping()
                                            
                                            if data[3].lower() == (":" + cmd_prefix + pickup_reset): #RESET
                                                found = False
                                                for i in range(0, len(op)):
                                                    if op[i] == nick:
                                                        found = True
                                                if found == True:
                                                    self.p_reset()
                                            
                                            if data[3].lower() == (":" + cmd_prefix + pickup_ring): #RINGER
                                                found = False
                                                for i in range(0, len(op)):
                                                    if op[i] == nick:
                                                        found = True
                                                for i in range(0, len(playerlist)):
                                                    if playerlist[i] == nick:
                                                        found = True
                                                if found == True:
                                                    self.p_ring(channel)
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                            self.update_ping()
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + pkup_lock  + '\n')
                                        self.update_ping()
                                            
                                    if data[3].lower() == (":" + cmd_prefix + pickup_rconuse): #RCONUSE
                                        found = False
                                        for i in range(0, len(op)):
                                            if op[i] == nick:
                                                found = True
                                        if found == True:
                                            replacer = data[0] + " " + data[1] + " " + data[2] + " " + data[3] + ' '
                                            msg = text.replace(replacer, "")
                                            if 'disconnect' in self.small(msg) or 'rconpassword' in self.small(msg):
                                                self.s.send('PRIVMSG ' + channel + ' :DON\'T USE THESE COMMANDS\n')
                                            else:
                                                a_server = server
                                                a_rcon = rcon
                                                serverThread_rconuse = q3rcon_rconuse(msg)
                                                serverThread_rconuse.start()
                                                self.s.send('PRIVMSG ' + channel + ' :Rcon cmd sent.\n')
                                            self.update_ping()
                        #HELP
                                    if data[3].lower() == (":" + cmd_prefix + pickup_help):
                                        self.p_help(channel)



                    if status_msg == True:
                        self.p_status(pub_chan,False)
                    status_msg = False
                    sleep(3) # recognize a txt all 3s

                except:
                    self.s.close()
                    print "DIE"
                    traceback.print_exc(file=sys.stdout)
                    sys.exit()


class ping_thread(Thread):
    
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global pickupthread
        while True:
            if ping_active == '0':
                sys.exit()
                break
            if (((int(ping_last) + 185) - time()) < 0):
                print 'ping: PING ALERT, GONNA RESTART'
                pickupThread = pickup(1)
                pickupThread.start()
                sleep(30)
            else:
                print 'ping: IT\'S OKAY, GONNA SLEEP'
                sleep(30)


class q3rcon_rconuse(Thread):
    '''Simple RCON class for Quake 3'''
    
    def __init__(self,msg):
        Thread.__init__(self)
        self.msg = msg

    def rconuse(self):
        msg_prefix = b'\xff'*4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(3)
        ipport = a_server.split(':')
        rconpw = a_rcon
        ip = ipport[0]
        port = int(ipport[1])
        self.socket.connect((ip, port))
        #self.fullmsg = msg_prefix + bytes((('rcon \"%s\" %s\n')%(rconpw, msg)), "UTF-8")
        self.fullmsg = msg_prefix + ('rcon \"%s\" %s\n')%(rconpw, self.msg)
        self.socket.send(self.fullmsg)
        self.socket.close()
        
    def run(self):
        print 'RCON COMMAND: ' + self.msg
        print "usercon starting..."
        self.rconuse()
        print "usercon done...."    
        


class q3rcon(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        serverThread_cap = q3rcon_setcaptain()
        serverThread_cap.start()
        sleep(5)
        serverThread_pw = q3rcon_setpassword()
        serverThread_pw.start()
        sleep(5)
        serverThread_map = q3rcon_setmap()
        serverThread_map.start()


class q3rcon_setcaptain(Thread):
    '''Simple RCON class for Quake 3'''
    
    def __init__(self):
        Thread.__init__(self)

    def setcaptain(self):
        msg_prefix = b'\xff'*4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(3)
        ipport = a_server.split(':')
        rconpw = a_rcon
        cap1 = a_captain1
        cap2 = a_captain2
        ip = ipport[0]
        port = int(ipport[1])
        self.socket.connect((ip, port))
        msg = 'sv_joinmessage\"^7Captains: ^1' + cap1 + ' ' + cap2
        #self.fullmsg = msg_prefix + bytes((('rcon \"%s\" %s\n')%(rconpw, msg)), "UTF-8")
        self.fullmsg = msg_prefix + ('rcon \"%s\" %s\n')%(rconpw, msg)
        self.socket.send(self.fullmsg)
        self.socket.close()
        
    def run(self):
        print "cap starting..."
        self.setcaptain()
        print "cap done...."        




class q3rcon_setpassword(Thread):
    '''Simple RCON class for Quake 3'''
    
    def __init__(self):
        Thread.__init__(self)

    def setpassword(self):
        msg_prefix = b'\xff'*4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(3)
        ipport = a_server.split(':')
        rconpw = a_rcon
        pw = a_password
        ip = ipport[0]
        port = int(ipport[1])
        self.socket.connect((ip, port))
        msg = "g_password " + str(pw)
        #self.fullmsg = msg_prefix + bytes((('rcon \"%s\" %s\n')%(rconpw, msg)), "UTF-8")
        self.fullmsg = msg_prefix + ('rcon \"%s\" %s\n')%(rconpw, msg)
        self.socket.send(self.fullmsg)
        self.socket.close()
        
    def run(self):
        print "pw starting..."
        self.setpassword()
        print "pw done...."




class q3rcon_setmap(Thread):
    '''Simple RCON class for Quake 3'''
    
    def __init__(self):
        Thread.__init__(self)

    def setmap(self):
        msg_prefix = b'\xff'*4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(3)
        ipport = a_server.split(':')
        rconpw = a_rcon
        smap = a_smap
        ip = ipport[0]
        port = int(ipport[1])
        self.socket.connect((ip, port))
        msg = "map " + smap
        print msg
        #self.fullmsg = msg_prefix + bytes((('rcon \"%s\" %s\n')%(rconpw, msg)), "UTF-8")
        self.fullmsg = msg_prefix + ('rcon \"%s\" %s\n')%(rconpw, msg)
        self.socket.send(self.fullmsg)
        self.socket.close()
        
    def run(self):
        print "map starting..."
        self.setmap()
        print "map done...."

#a_server = '46.4.27.24:27964'
#a_rcon = 'p1ckuplyf3'
#a_smap = 'ut4_abbey'
#a_password = 'pickupderp'
#a_captain1 = 'derp2'
#a_captain2 = 'derp3'
#serverThread = q3rcon()
#serverThread.start()
pickupThread = pickup(1)
pickupThread.start()
sleep(20)
pingthread = ping_thread()
pingthread.start()
