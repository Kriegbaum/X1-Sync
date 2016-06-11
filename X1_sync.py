import plistlib
import os
import datetime
import shutil

def spacer():                                                                   #For readability in the console
    for i in range(5):
        print('.')
def spacer_small():
    print('')

def setup():                                                                    #Asks new user for information
    print('Enter the directory for your iTunes library')
    spacer_small()
    print('This is typically stored in your \'user/Music/iTunes\' folder')
    print('You can also make a copy wherever you want in iTunes')
    print('Just go File>Library>Export Library...')
    tunes_library_path = input()                                                #Where is my itunes library?
    spacer()
    print('Now you gotta give me the root directory for your media player')
    print('This is typically /Volumes/YOUR DEVICE NAME')
    fiio_dir = input()                                                          #Device directory
    if fiio_dir[len(fiio_dir) - 1] == '/':
        fiio_dir = fiio_dir[0: len(fiio_dir) - 1]                               #User may add an extra slash, get rid of it
    spacer()
    print('Ima save those settings')
    settings_body = 'iTunes Library Path:\n' + tunes_library_path + '\n' + 'Device Root Directory\n' + fiio_dir
    newsettings = open(fiio_dir + '/X1_sync_settings.txt', 'w')                 #Write a settings file into the root directory of device
    newsettings.write(settings_body)
    newsettings.close()
    return [tunes_library_path, fiio_dir]

def check_settings():                                                           #Checks to see if there are settings in /Volumes/
    for dir in os.listdir('/Volumes'):
        if not os.path.isfile('/Volumes/' + dir):
            if os.path.exists('/Volumes/' + dir + '/' + 'X1_sync_settings.txt'):
                return '/Volumes/' + dir + '/' + 'X1_sync_settings.txt'         #Returns path of settings file
    else:
        return False                                                            #Returns false if there are no settings

def read_settings():                                                            #Pulls settings out of text file
    settings_path = check_settings()
    if settings_path != False:
        settings = open(settings_path, 'r')
        settings.readline()
        tunes_library_path = settings.readline()                                #Pull iTunes library path
        settings.readline()
        settings.readline()
        fiio_dir = settings.readline()                                          #Pull device directory path
        settings.close()
        return [tunes_library_path, fiio_dir]
    else:
        setup()                                                                 #If no settings, run user through setup

print('Initializing...')
spacer()

settings_list = read_settings()                                                 #Obtain information about library and device
tunes_library_path = settings_list[0]
fiio_dir = settings_list[1]
tunes_library_path = tunes_library_path.replace('\n', '')
fiio_dir = fiio_dir.replace('\n', '')

fiio_lib = fiio_dir + '/Library'                                                #Device library folder
print('I\'m going to parse a whole bunch of XML data')
print('Hold please...')
spacer()
tunes_library = plistlib.readPlist(tunes_library_path)                          #Let's parse the iTunes library
print('I probably just loaded the iTunes library')
print('But I\'m really dumb, so uhhhhh... I dunno')
spacer()

def get_path(trackID):                                                          #Let's grab this song's filepath
    path = tunes_library['Tracks'][str(trackID)]['Location']                    #Nabs filepath from library xml, but the format its stored in is not useable, so:
    path = path.replace('file://', '')                                          #Strip out extraneous info
    path_list = path.split('%')
    newpath = bytes(path_list[0], 'utf-8')                                      #We need this to be a bytes literal, but can't do it befor the split command
    if len(path_list) > 1:                                                      #Skip process if no special characters
        for i in range(1,len(path_list)):                                       #Iterate through split list
            tmpbyte = path_list[i][0:2]                                         #Grab hex value after first split
            newbyte = bytes([int(str(tmpbyte), 16)])                            #Make that hex value into its ascii value and then convert the ascii value back into the same byte, but with proper formatting
            newpath += newbyte + bytes(path_list[i][2:len(path_list[i])], 'utf-8')  #Drop that byte and its associated chunk into the new filepath
    newpath = newpath.decode('utf-8')                                           #Decode remaining special characters
    return newpath

def get_fiio_path_noname(trackID):                                              #Lets grab our target path without the filename
    artist = tunes_library['Tracks'][str(trackID)]['Artist']                    #Grab artist name
    if artist[:4] == 'The ':                                                    #Remove 'the' from the beginning for storting
        artist = artist.replace('The ', '')
        artist = artist + ', The'
    album = tunes_library['Tracks'][str(trackID)]['Album']                      #Ditto for the album name
    if album[:4] == 'The ':
        album = album.replace('The ', '')
        album = album + ', The'
    if '/' in album:                                                            #Slashes are problematic because they mess with the filepath
        album = album.replace('/','')
    if '/' in artist:
        artist = artist.replace('/', '')
    return fiio_lib + '/' + artist + '/' + album

def get_fiio_path(trackID):                                                     #Let's get our target filepath
    source_path = get_path(trackID)                                             #We will need this for the file extension
    name = tunes_library['Tracks'][str(trackID)]['Name']
    if '/' in name:                                                             #Again, slashes fuck with filepath
        name = name.replace('/', '')
    if 'Track Number' in tunes_library['Tracks'][str(trackID)]:                 #Some tracks have no tracknum, check for that
        tracknum = str(tunes_library['Tracks'][str(trackID)]['Track Number'])
        if int(tracknum) > 0 and int(tracknum) < 10:                            #Always make tracknum 2 digits for readability
            tracknum = '0' + tracknum
    else:
        tracknum = ''
    ext = source_path[len(source_path) - 4:]                                    #Grab the file extension from source path
    return get_fiio_path_noname(trackID) + '/' + tracknum + ' ' + name + ext

def make_tree(trackID):                                                         #Establish library folder structure
    album_path = get_fiio_path_noname(trackID)
    if not os.path.exists(album_path):                                          #See if directory already exists
        os.makedirs(album_path)                                                 #If not, create it

def check_ifnewest(trackID):                                                    #Don't bother copying files that have not changed
    if os.path.exists(target_path):                                             #See if file exists already
        mt = os.path.getmtime(source_path)
        ct = os.path.getmtime(target_path)
        last_modified = datetime.datetime.fromtimestamp(mt)
        last_copied = datetime.datetime.fromtimestamp(ct)
        if last_modified > last_copied:
            return True
    else:
        return False


files_copied = 0                                                                #For updating user with progress
files_skipped = 0                                                               #This is here for debug, make sure we are not modifying existing files
total_files = len(tunes_library['Tracks'])

if not os.path.exists(fiio_lib):                                                #Ensure the fiio library directory exists
    os.makedirs(fiio_lib)

failed_copies = {}                                                              #Establish dictionary to track where sync failed

for trackID in tunes_library['Tracks']:                                         #Finally, we get to the copy process
    try:
        source_path = get_path(trackID)                                         #These two file paths are used a lot, define them early
        target_path = get_fiio_path(trackID)
        if '.Trash' in source_path:                                             #Trashed tracks will sometimes remain in library, they cannot be copied
            continue
        if not check_ifnewest(trackID):                                         #See if file exists and is most recent
            make_tree(trackID)                                                  #Establish filetree
            shutil.copy(source_path, target_path)                               #If not, copy that shit
        else:
            files_skipped += 1
        files_copied += 1                                                       #Even if we skip, that is progress
        if files_copied % 25 == 0:                                              #Keep our users up to date on progress
            print(files_copied,'of', total_files,'files synced')
    except Exception as e:                                                      #Add any errors to the error dictionary
            failed_copies[tunes_library['Tracks'][str(trackID)]['Name']] = e.args


print('Song copy process complete')
print('I skipped', files_skipped, 'files because they were up to date')
spacer_small()
print('I failed to copy', len(failed_copies), 'tracks')
for i in failed_copies:
    print('I failed to copy', i, 'because', failed_copies[i])
spacer()
print('Now I\'m going to copy your playlists')
spacer()

#Now it's time to fetch our Playlists

#This function should be given the dictionary containing playlist ID and name
def fetch_body(lst):                                                            #Here we fetch all appropriate filepaths for the m3u file
    body = ''
    for track in lst['Playlist Items']:
        trackID = track['Track ID']
        path = get_fiio_path(trackID).split('Library', 1)                       #Grab the path in the fiio library
        newpath = 'Library' + path[1].replace('/', '\\')                        #Strip out everything before root directory
        body += newpath + '\n'                                                  #Wrap into m3u body
    return body



for lst in tunes_library['Playlists']:                                          #Enter playlist dictionary and iterate
    if not 'Distinguished Kind' in lst:
        if not 'Master' in lst:
            name = lst['Name']                                                  #All these variables are for naming the new m3u file
            body = fetch_body(lst)
            ext = '.m3u'
            m3u = open(fiio_dir + '/' + name + ext, 'w')
            m3u.write(body)
            m3u.close()
            print('Copied',name,'to device')
