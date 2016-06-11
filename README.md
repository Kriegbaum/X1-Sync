X1_Sync v0.1

	A utility that syncs a non-apple device with an iTunes library in Mac OS X.

	This was designed with the Fiio X1 in mind, but should work on other high capacity media players.

	This is the first piece of software I’ve ever written, so go easy on me here


OPERATING INSTRUCTIONS:

	-Download script and drop it somewhere

	-IMPORTANT: This is not yet cross platform, it only works with Mac OSX

	-For the full library sync process, run X1_sync.py

	-If you’re only interested in syncing playlists, use X1_playlist_module.py

	-The sync process is going to create a specific file structure, and there is no cleanup operation at present, so it is best to wipe your device before running

	-The process will create a settings file on the root of your directory, currently it only stores your library file path and the device’s root directory, future settings pending

	-IMPORTANT: The Fiio X1 will want to sleep itself during a long sync process. Set the “Idle power off” to ‘off’ on the device before initiating sync. This is especially important on the first sync, mine took 3 hours for an 8500 item library

	-For the Fiio X1, this should make browsing for music using the file browser easy. The library will appear at the top of the root list, the playlists will appear below it



CONTRIBUTING:

	-Feel free to make changes, make yourself a branch first though
	
	-Please send error reports and issues, this was a learning exercise for me, and reports will only help me



TODO:

	-Speed up sync process (I need to learn how to multithread)
	
	-Find some way to prevent device from sleeping using the software
	
	-Create a cleanup function that removes files not in the library
	
		-Make a setting that allows user to disable this
		
	-Purchase more bagels (refrigerator is empty)
	
	-Make this thing so cross-platform, it’ll make your nose bleed
	



VERSION HISTORY:
	
	v0.1:
	-First!
	-I made a thing, here it is!



CREDITS:

	Code written by Kriegbaum
	Spiritual guidance and troubleshooting by aagallag



LICENSE:
	Ima give this thing a GNU GPLv3 license, terms are attached
