#!/usr/bin/env python
import cgi, os, SocketServer, sys, time, urllib
from SimpleHTTPServer import SimpleHTTPRequestHandler
from StringIO import StringIO

version = "ver 1.91 by Claude Pageau"
# SimpleHTTPServer python program to allow selection of images from right panel and display in an iframe left panel
# Use for local network use only since this is not guaranteed to be a secure web server.
# based on original code by zeekay and modified by Claude Pageau Nov-2015 for use with pi-timolo.py on a Raspberry Pi
# from http://stackoverflow.com/questions/8044873/python-how-to-override-simplehttpserver-to-show-timestamp-in-directory-listing

# 1 - Use nano editor to change webserver.py web_server_root and other variables to suit
#   nano webserver.py
#     ctrl-x y to save changes
#
# 2 - On Terminal session execute command below.  This will display file access information
#   ./webserver.py
#     ctrl-c to stop web server.  Note if you close terminal session webserver.py will stop.
#
# 3 - To Run this script as a background daemon execute the command below.
#     Once running you can close the console and webserver will continue to run.
#   ./webserver.sh start
#     To check status of webserver type command below with no parameter   
#   ./webserver.sh
#
# 4 - On a LAN computer web browser url bar, input this RPI ip address and port number per example below.
#   http://192.168.1.110:8080

# Left iFrame Image Settings
image_width = "1024"           # width of images to display in px
image_height = "768"           # height of images to display in px
image_frame_width = "100%"     # Desired frame width to display images. can be eg percent "80%" or px "1280"
image_frame_height = "100%"    # Desired frame height to display images. Scroll bars if image larger (percent or px) 
image_max_listing = 0          # 0 = All or Specify Max right side file entries to show (must be > 1)

# Web Server settings
web_server_root = "motion"    # webserver root path to webserver image folder
web_server_port = 8080        # Web server access port eg http://192.168.1.100:8090
web_page_title = "Pi-Timolo Motion Images"     # web page title that browser show (not displayed on web page)
web_page_refresh_on = True    # False=Off (never)  Refresh True=On (per seconds below)       
web_page_refresh_sec ="180"   # Refresh page time default=180 seconds (three minutes)

web_iframe_width = "80%"         # Left Pane - Sets % of screen width allowed for image frame with rest for right list
web_list_height = image_height   # Right List - side menu height in px (link selection)

# Settings for right side files list
show_by_datetime = True          # True=datetime False=filename
sort_descending = True           # reverse sort order (filename or datetime per show_by_date setting

if show_by_datetime:
    dir_sort = 'DateTime'
else:
    dir_sort = 'FileName'

if sort_descending:
    dir_order = 'Descend'
else:
    dir_order = 'Ascend'

list_title = "%s %s" % ( dir_sort, dir_order )

class DirectoryHandler(SimpleHTTPRequestHandler):

    def list_directory(self, path):
        try:
            list = os.listdir(path)
            all_entries = len(list)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        if show_by_datetime:
            # Sort by most recent modified date/time first
            list.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime,reverse=sort_descending)
        else:
            # Sort by File Name
            list.sort(key=lambda a: a.lower(),reverse=sort_descending)
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        # Start HTML formatting code
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write('<head>')
        # Setup Meta Tags
        f.write('<meta "Content-Type" content="txt/html; charset=ISO-8859-1" />')
        f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
        if web_page_refresh_on:
            f.write('<meta http-equiv="refresh" content="%s" />' % ( web_page_refresh_sec ))
        f.write('</head>')
        
        tpath, cur_folder = os.path.split(self.path)
        f.write("<html><title>%s %s</title>" % ( web_page_title, self.path ))
        f.write("<body>")
        # Start Left iframe Image Panel
        f.write('<iframe width="%s" height="%s" align="left"' 
                        % (web_iframe_width, image_height))
        f.write('src="%s" name="imgbox" id="imgbox" alt="%s">' 
                        % (list[1], web_page_title)) 
                        # display second entry in right list since list[0] may still be in progress                        
        f.write('<p>iframes are not supported by your browser.</p></iframe>')
        # Start Right File selection List Panel
        list_style = '<div style="height: ' + web_list_height + 'px; overflow: auto; white-space: nowrap;">'
        f.write(list_style)
        # f.write('<center><b>%s</b></center>' % (self.path))
        f.write('<center><b>%s</b></center>' % (list_title))
        f.write('<ul name="menu" id="menu" style="list-style-type:none; padding-left: 4px">')        
        # Create the formatted list of right panel hyperlinks to files in the specified directory
        
        display_entries = 0
        for name in list:
            display_entries += 1
            if image_max_listing > 1:
                if display_entries >= image_max_listing:
                    break
            fullname = os.path.join(path, name)
            displayname = linkname = name
            date_modified = time.strftime('%H:%M:%S %d-%b-%Y', time.localtime(os.path.getmtime(fullname)))
            # Append / for directories or @ for symbolic links
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            if os.path.isdir(fullname):
                # Note this will open a new tab to display the selected folder.
                displayname = name + "/"
                linkname = os.path.join(displaypath, displayname)
                f.write('<li><a href="%s" target="_blank">%s</a></li>\n'
                          % ( urllib.quote(linkname), cgi.escape(displayname)))
            else:
                f.write('<li><a href="%s" target="imgbox">%s</a> - %s</li>\n'
                          % ( urllib.quote(linkname), cgi.escape(displayname), date_modified))
        f.write('</ul></div><p><b>')
        f.write('<div style="float: left; padding-left: 40px;">Web Root is [ %s ]</div>' % ( web_server_root )) 
        f.write('<div style="text-align: center;">%s</div>' % ( web_page_title ))

        if web_page_refresh_on:
             f.write('<div style="float: left; padding-left: 40px;">Auto Refresh [ %s sec ]</div>' % ( web_page_refresh_sec ))                         

        if image_max_listing > 1: 
            f.write('<div style="text-align: right; padding-right: 40px;">Listing Only %i of %i Files in [ %s ]</div>'
                                      % ( display_entries, all_entries, self.path ))
        else:
            f.write('<div style="text-align: right; padding-right: 50px;">Listing All %i Files in [ %s ]</div>'
                                      % ( all_entries, self.path ))
        # Display web refresh info only if setting is turned on
        f.write('</b></p>')
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

# Start Web Server Processing        
os.chdir(web_server_root)
SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", web_server_port), DirectoryHandler)
print("---------------------------- Settings --------------------------")
print("webserver.py %s" % (version))
print("Server - web_server_root=%s" % ( web_server_root ))
print("         web_server_port=%i  version=%s" % ( web_server_port, version ))
print("Images - image_frame_width=%s  image_frame_height=%s" % ( image_frame_width, image_frame_height ))
print("Sort   - show_by_datetime=%s  sort_decending=%s" % ( show_by_datetime, sort_descending ))
print("----------------------------------------------------------------")
print("From a computer on the same LAN. Use a Web Browser to access this server at")
print("http://IP_Address:%i"  % web_server_port)
print("Where IP_Address is IP address of this Raspberry Pi Eg. http://192.168.1.100:%i" % web_server_port)
print("")
print("IMPORTANT: If You Get - socket.error: [Errno 98] Address already in use")
print("           Wait a minute or so for webserver to timeout and Retry.")
print("              ctrl-c to exit this webserver script")
print("----------------------------------------------------------------")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("User Stopped webserver.py  Bye.")
    httpd.shutdown()
    httpd.socket.close()   
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))




