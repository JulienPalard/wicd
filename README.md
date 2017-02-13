# About this fork

## Why this fork

 - To fix opened issues likes `UnicodeDecodeError: 'ascii' codec
can't decode byte 0xe0 in position 0: ordinal not in
range(128)`.
 - To try to port wicd to Python 3.

## What about python 2 compatibility ?

Just use the original wicd, I won't keep python 2 compatibility.

## About this fork

Wicd was previously hosted on [launchpad](https://launchpad.net/wicd),
so it was a bazar repository. I first migrated the repository from
bazar to git. wicd-daemon and wicd-curses are now working on Python 3,
any feedback welcome.

# Original README

THEORY OF OPERATION:

Wicd is designed to give the user as much control over behavior of network
connections as possible.  Every network, both wired and wireless, has its
own profile with its own configuration options and connection behavior.
Wicd will try to automatically connect only to networks the user specifies
it should try, with a preference first to a wired network, then to wireless.

For wired connections, users have many options for determining what network
settings to use.  Wicd allows creation of an unlimited number of wired
profiles, each of which has its own unique settings.  The user can choose to
automatically connect to a selected default profile, choose a profile from a
pop-up window every time wicd connects, or have wicd automatically choose the
last profile used to manually connect.

For wireless connections, users can select any number of wireless networks
to automatically connect; wicd will choose the one with the highest signal
strength to try to connect.

If the user chooses, wicd will try to automatically reconnect when it detects
that a connection is lost.  If the last known connection state is wired, wicd
will first try to reconnect to the wired network, and if it is not available,
wicd will try any available wireless networks which have automatic connection
enabled.  If the last known connection state is wireless, wicd will first try
to reconnect to the previously connected network (even if that network does
not have automatic connection enabled), and should that fail, it will try both
a wired connection and any available wireless networks which have automatic
connection enabled.

Wicd uses built-in linux wireless-tools, such as ifconfig and iwconfig, to
get and configure network info.  There is some flexibility in its use of DHCP,
providing support for dhclient, dhcpcd, and pump.  Wicd uses wpa_supplicant
to handle all wireless encryption settings, and uses a template-based system
to create the configuration files used by wpa_supplicant.  These templates
can be edited, and new templates can be created by the user and imported into
wicd, allowing connection to networks with uncommon encryption settings.


STRUCTURE:

Wicd has two major parts: the daemon, which runs with root privileges; and the
user interface, which runs with normal user privileges.  The two parts run as
separate processes and make use of D-Bus to communicate.

The daemon is responsible for making and configuring connections, reading and
writing configuration files and logs, and monitoring the connection status.
The daemon's job is split between two processes: daemon.py and monitor.py.
All the connection status monitoring, as well as the auto-reconnection logic,
takes place in monitor.py.  Everthing else is done by wicd-daemon.py.

The user interface (stored in wicd-client.py), which is made up of a tray
icon, a main GUI window, and its child dialogs, gets configuration and network
info from the daemon either by querying it using the methods in the daemon's
dbus interface or by receiving signals emitted from the daemon over D-Bus.
Any configuration changes made in the user interface are passed back to the
daemon, which actually applies the changes and writes them to configuration
files.

Since the user interface just queries for connection and configuration info
from the daemon, it is possible to run wicd without the GUI at all.  Also,
the daemon is started by wicd's init script during system startup (before any
user logs in), making it possible to use wicd with "headless" machines.
