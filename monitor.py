#!/usr/bin/env python

#
#   Copyright (C) 2007 Adam Blackburn
#   Copyright (C) 2007 Dan O'Reilly
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License Version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import dbus
import gobject
import os
import sys

import wpath
import misc

if sys.platform == 'linux2':
    # Set process name.  Only works on Linux >= 2.1.57.
    try:
        import dl
        libc = dl.open('/lib/libc.so.6')
        libc.call('prctl', 15, 'wicd-monitor\0', 0, 0, 0) # 15 is PR_SET_NAME
    except:
        pass
    
if __name__ == '__main__':
    wpath.chdir(__file__)

proxy_obj = dbus.SystemBus().get_object('org.wicd.daemon', '/org/wicd/daemon')
daemon = dbus.Interface(proxy_obj, 'org.wicd.daemon')
wired = dbus.Interface(proxy_obj, 'org.wicd.daemon.wired')
wireless = dbus.Interface(proxy_obj, 'org.wicd.daemon.wireless')

class ConnectionStatus():
    """ Class for monitoring the computer's connection status. """
    def __init__(self):
        """ Initialize variables needed for the connection status methods. """
        self.last_strength = -2
        self.displayed_strength = -1
        self.still_wired = False
        self.network = ''
        self.tried_reconnect = False
        self.connection_lost_counter = 0
        self.last_state = misc.NOT_CONNECTED
        self.reconnecting = False
        self.signal_changed = False

    def check_for_wired_connection(self, wired_ip):
        """ Checks for an active wired connection.

        Checks for and updates the tray icon for an active wired connection
        Returns True if wired connection is active, false if inactive.

        """
        
        if wired_ip and wired.CheckPluggedIn():
            # Only change the interface if it's not already set for wired
            if not self.still_wired:
                daemon.SetCurrentInterface(daemon.GetWiredInterface())
                self.still_wired = True
            return True
        # Wired connection isn't active
        self.still_wired = False
        return False

    def check_for_wireless_connection(self, wireless_ip):
        """ Checks for an active wireless connection.

        Checks for and updates the tray icon for an active
        wireless connection.  Returns True if wireless connection 
        is active, and False otherwise.

        """

        # Make sure we have an IP before we do anything else.
        if wireless_ip is None:
            return False
        
        # Reset this, just in case.
        self.tried_reconnect = False
        
        # Try getting signal strength, and default to 0 
        # if something goes wrong.
        try:
            if daemon.GetSignalDisplayType() == 0:
                wifi_signal = int(wireless.GetCurrentSignalStrength(self.iwconfig))
            else:
                wifi_signal = int(wireless.GetCurrentDBMStrength(self.iwconfig))
        except:
            wifi_signal = 0

        if wifi_signal == 0:
            # If we have no signal, increment connection loss counter.
            # If we haven't gotten any signal 4 runs in a row (12 seconds),
            # try to reconnect.
            self.connection_lost_counter += 1
            print self.connection_lost_counter
            if self.connection_lost_counter >= 4:
                self.connection_lost_counter = 0
                return False
        else:  # If we have a signal, reset the counter
            self.connection_lost_counter = 0

        # Only update if the signal strength has changed because doing I/O
        # calls is expensive, and the icon flickers.
        if (wifi_signal != self.last_strength or
            self.network != wireless.GetCurrentNetwork(self.iwconfig)):
            self.last_strength = wifi_signal
            self.signal_changed = True
            daemon.SetCurrentInterface(daemon.GetWirelessInterface())    
            
        return True

    def update_connection_status(self):
        """ Updates the tray icon and current connection status.
        
        Determines the current connection state and sends a dbus signal
        announcing when the status changes.  Also starts the automatic
        reconnection process if necessary.
        
        """
        wired_ip = None
        wifi_ip = None

        if daemon.GetSuspend():
            print "Suspended."
            state = misc.SUSPENDED
            self.update_state(state)
            return True

        # Determine what our current state is.
        # Check for wired.
        wired_ip = wired.GetWiredIP()
        wired_found = self.check_for_wired_connection(wired_ip)
        if wired_found:
            self.update_state(misc.WIRED, wired_ip=wired_ip)
            return True
        
        # Check for wireless
        wifi_ip = wireless.GetWirelessIP()
        self.iwconfig = wireless.GetIwconfig()
        self.signal_changed = False
        wireless_found = self.check_for_wireless_connection(wifi_ip)
        if wireless_found:
            self.update_state(misc.WIRELESS, wifi_ip=wifi_ip)
            return True
            
        # Are we currently connecting?
        if daemon.CheckIfConnecting():
            state = misc.CONNECTING
        else:  # No connection at all.
            state = misc.NOT_CONNECTED
            self.auto_reconnect()
        self.update_state(state)
        return True

    def update_state(self, state, wired_ip=None, wifi_ip=None):
        """ Set the current connection state. """
        # Set our connection state/info.
        if state == misc.NOT_CONNECTED:
            info = [""]
        elif state == misc.SUSPENDED:
            info = [""]
        elif state == misc.CONNECTING:
            if wired.CheckIfWiredConnecting():
                info = ["wired"]
            else:
                info = ["wireless", wireless.GetCurrentNetwork(self.iwconfig)]
        elif state == misc.WIRELESS:
            info = [wifi_ip, wireless.GetCurrentNetwork(self.iwconfig),
                    str(wireless.GetPrintableSignalStrength(self.iwconfig)),
                    str(wireless.GetCurrentNetworkID(self.iwconfig))]
        elif state == misc.WIRED:
            info = [wired_ip]
        else:
            print 'ERROR: Invalid state!'
            return True
        daemon.SetConnectionStatus(state, info)

        # Send a D-Bus signal announcing status has changed if necessary.
        if state != self.last_state or \
           (state == misc.WIRELESS and self.signal_changed):
            daemon.EmitStatusChanged(state, info)
        self.last_state = state
        return True

    def auto_reconnect(self):
        """ Automatically reconnects to a network if needed.

        If automatic reconnection is turned on, this method will
        attempt to first reconnect to the last used wireless network, and
        should that fail will simply run AutoConnect()

        """
        if self.reconnecting:
            return
        
        self.reconnecting = True
        daemon.SetCurrentInterface('')
        
        print 'autoreconnect'
        if daemon.GetAutoReconnect() and not daemon.CheckIfConnecting() and \
           not daemon.GetForcedDisconnect() and not daemon.GetAutoConnecting():
            print 'Starting automatic reconnect process'
            # First try connecting through ethernet
            if wired.CheckPluggedIn():
                print "Wired connection available, trying to connect..."
                daemon.AutoConnect(False)
                self.reconnecting = False
                return

            # Next try the last wireless network we were connected to
            cur_net_id = wireless.GetCurrentNetworkID(self.iwconfig)
            if cur_net_id > -1:  # Needs to be a valid network
                if not self.tried_reconnect:
                    print 'Trying to reconnect to last used wireless \
                           network'
                    wireless.ConnectWireless(cur_net_id)
                    self.tried_reconnect = True
                elif not wireless.CheckIfWirelessConnecting():
                    print "Couldn't reconnect to last used network, \
                           scanning for an autoconnect network..."
                    daemon.AutoConnect(True)
            else:
                daemon.AutoConnect(True)
        self.reconnecting = False
    
        
def main():
    monitor = ConnectionStatus()
    gobject.timeout_add(3000, monitor.update_connection_status)
    
    mainloop = gobject.MainLoop()
    mainloop.run()

if __name__ == '__main__':
    main()