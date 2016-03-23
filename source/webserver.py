#!/usr/bin/env python
import cgi, os, SocketServer, sys, time, urllib
from SimpleHTTPServer import SimpleHTTPRequestHandler
from StringIO import StringIO

version = "ver 1.0"
# SimpleHTTPServer python program to allow selection of images from right panel and display in an iframe left panel
# Use for local network use only since this is not guaranteed to be a secure web server.
# based on original code by zeekay and modified by Claude Pageau Nov-2015 for use with pi-timolo.py on a Raspberry Pi
# from http://stackoverflow.com/questions/8044873/python-how-to-override-simplehttpserver-to-show-timestamp-in-directory-listing

# 1 - Use nano editor to change webserver.py web_server_root and other variables to suit
# 2 - On Terminal session execute
# python ./webserver.py
# 3 - On a web browser url bar input the server ip address and port number
# eg 192.168.1.110:8000
# 4 - If you wish to launch in the background then add /etc/init.d script (copied from skeleton and edit accordingly) then initialize script
# eg
# chmod +x webserver.py
# cd /etc/init.d
# sudo cp skeleton webserver
# sudo nano webserver      (change variables in script to point to location of webserver.py) 
# sudo chmod +x webserver
# sudo update-rc.d webserver defaults
# sudo webserver       (test to make sure it works and trouble shoot as necessary)
# Reboot to test that webserver auto starts on boot.

# Web Server settings
web_server_root = "/home/pi/pi-timolo/motion"  # path to webserver image folder
web_server_port = 8080                         # Web server access port eg http://192.168.1.100:8090
web_page_title = "pi-timolo motion images"     # web page title that browser show (not displayed on web page)

# Size of Images to display 
image_width = "1280"
image_height = "720"

# Left side image iframe settings to same as image dimensions 
image_frame_width = image_width   
image_frame_height = image_height

# Settings for right side files list
show_by_datetime = True           # True=datetime False=filename
sort_descending = True            # reverse sort order (filename or datetime per show_by_date setting
list_height = image_frame_height  # height of directory listing on right side 

class DirectoryHandler(SimpleHTTPRequestHandler):

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        if show_by_datetime:
            list_title = "by DateTime decending=%s" % sort_descending
            list.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime,reverse=sort_descending)   # Sort by most recent modified date/time first
        else:
            list_title = "by FileName decending=%s" % sort_descending       
            list.sort(key=lambda a: a.lower(),reverse=sort_descending)
            
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        # Start HTML formatting code
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>%s %s</title>\n" % (web_page_title, displaypath))
        f.write("<body>\n")
        # Start Left iframe Image Panel
        f.write('<iframe width="%s" height="%s" align="left"' % (image_frame_width, image_frame_height))
        f.write('src="%s" name="imgbox" id="imgbox" alt="%s">' % (list[0], web_page_title))  # display first image in list
        f.write('<p>iframes are not supported by your browser.</p></iframe>')
        # Start Right File selection List Panel
        list_style = '<div style="height: ' + list_height + 'px; overflow: auto;">'
        f.write(list_style)
        f.write('<center><b>%s</b></center><hr><ul>' % list_title)
        # Create the formatted list of right panel hyperlinks to files in the specified directory
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            date_modified = time.ctime(os.path.getmtime(fullname))
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = os.path.join(displaypath, displayname)
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s" target="imgbox">%s</a> - %s</li>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname), date_modified))
        f.write('</ul><hr></div><p><center><b>%s</b></center></p></body>\n</html>\n' % web_server_root)
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
httpd = SocketServer.TCPServer(("", web_server_port), DirectoryHandler)
print ("---------------------------- Settings --------------------------")
print ("Server - web_server_root=%s" % ( web_server_root ))
print ("         web_server_port=%i  version=%s" % ( web_server_port, version ))
print ("Images - image_width=%s  image_height=%s" % ( image_width, image_height ))
print ("Sort   - show_by_datetime=%s  sort_decending=%s" % ( show_by_datetime, sort_descending ))
print ("----------------------------------------------------------------")
print ("              Use a Web Browser to access this server at")
print ("http://IP_Address:%i"  % web_server_port)
print ("Where IP_Address is IP address of this Raspberry Pi Eg. http://192.168.1.100:%i" % web_server_port)
print ("----------------------------------------------------------------")
httpd.serve_forever()


