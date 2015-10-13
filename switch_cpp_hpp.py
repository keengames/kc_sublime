import sublime, sublime_plugin, re, os

last_cpp_hpp_switch_map = {}

class SwitchToCppHppCommand( sublime_plugin.TextCommand ):

	def openCodeFile( self, picked ):
		global last_cpp_hpp_switch_map
		if picked >= 0:
			self.view.window().open_file( self.code_files[ picked ] )
			last_cpp_hpp_switch_map[ self.switch_file_path ] = self.code_files[ picked ]

	def openCodeFiles( self ):
		global last_cpp_hpp_switch_map

		self.code_files = sorted( self.code_files )

		if self.switch_file_path in last_cpp_hpp_switch_map:
			last_choice = last_cpp_hpp_switch_map[ self.switch_file_path ]
			if last_choice in self.code_files:
				last_choice_index = self.code_files.index( last_choice )
				if last_choice_index > 0:
					self.code_files.insert( 0, self.code_files.pop( last_choice_index ) )

		if len( self.code_files ) > 1:
			self.view.window().show_quick_panel( self.code_files, self.openCodeFile, sublime.MONOSPACE_FONT )
		elif len( self.code_files ) > 0:
			self.view.window().open_file( self.code_files[ 0 ] )

	def stripCodePostfix( self, filename, hasprefix ):
		if hasprefix:
			return filename
		for prefix in self.code_postfixes:
			if filename.endswith( '_' + prefix ):
				return filename[:-len( '_' + prefix )]
		return filename

	def hasCodePrefix( self, filename ):
		for prefix in self.code_postfixes:
			if filename.endswith( '_' + prefix ):
				return True
		return False

	def openCppFile( self, file_drive, file_folders, file_base_name ):

		#print( file_drive, file_folders, file_base_name )

		file_path_near = file_drive + '/'.join( file_folders ) + '/' + file_base_name

		if os.path.isfile( file_path_near + '.cpp' ):
			self.code_files.append( file_path_near + '.cpp' )

		if os.path.isfile( file_path_near + '.inl' ):
			self.code_files.append( file_path_near + '.inl' )

		if os.path.isfile( file_path_near + '.mm' ):
			self.code_files.append( file_path_near + '.mm' )

		if os.path.isfile( file_path_near + '.m' ):
			self.code_files.append( file_path_near + '.m' )

		if 'include' in file_folders:
			include_index = file_folders.index( 'include' ) 
			sources_path = file_drive + '/'.join( file_folders[:include_index] ) + '/sources'
		
			has_code_prefix = self.hasCodePrefix( file_base_name )

			for root, dirs, files in os.walk( sources_path ):
				file_path = root.replace( '\\', '/' ) + '/'
				for file_name in files:
					base_name, extension = os.path.splitext( file_name )
					if extension != '.cpp' and extension != '.inl':
						continue

					# only strip postfix if source file has no postfix
					base_name_stripped = self.stripCodePostfix( base_name, has_code_prefix ) 
				
					if base_name_stripped == file_base_name:
						self.code_files.append( file_path + file_name )

		self.openCodeFiles()

	def openHppFile( self, file_drive, file_folders, file_base_name ):

		#print( file_drive, file_folders, file_base_name )

		file_path_near = file_drive + '/'.join( file_folders ) + '/' + file_base_name

		if os.path.isfile( file_path_near + '.hpp' ):
			self.code_files.append( file_path_near + '.hpp' )

		if os.path.isfile( file_path_near + '.h' ):
			self.code_files.append( file_path_near + '.h' )

		if 'sources' in file_folders:
			include_index = file_folders.index( 'sources' ) 
			sources_path = file_drive + '/'.join( file_folders[:include_index] ) + '/include'

			# always strip postfix		
			file_base_name_stripped = self.stripCodePostfix( file_base_name, False ) 

			for root, dirs, files in os.walk( sources_path ):
				file_path = root.replace( '\\', '/' ) + '/'
				for file_name in files:
					base_name, extension = os.path.splitext( file_name )
					if extension != '.hpp':
						continue

					base_name_stripped = self.stripCodePostfix( base_name, False ) 

					if base_name_stripped == file_base_name_stripped:
						self.code_files.append( file_path + file_name )

		self.openCodeFiles()

	def run( self, edit ):

		# einkaufswagencode
		file_complete_path = self.view.file_name().replace( '\\', '/' ) 
		file_drive, file_path_and_file = os.path.splitdrive( file_complete_path )
		file_drive += '/'
		file_path, file_name = os.path.split( file_path_and_file )
		file_base_name = os.path.splitext( file_name )[0]
		file_ext = os.path.splitext( file_name )[1]
		file_folder_path = file_path
		file_folders = []
		while 1:
		    file_folder_path, file_folder = os.path.split( file_folder_path )
		    if file_folder != '':
		        file_folders.append( file_folder )
		    else:
		        if file_folder_path != '' and file_folder_path != '/':
		            file_folders.append( file_folder_path )
		        break
		file_folders.reverse()

		self.code_postfixes = ['win32','posix','linux','osx','android','ios','gl','gles','d3d11','ps3','ps4','xb360','wp8']
		self.code_files = []
		self.switch_file_path = file_complete_path

		# print( file_complete_path, file_drive, file_path, file_base_name, file_ext, file_folders )

		if file_ext == '.hpp' or file_ext == '.h':
			self.openCppFile( file_drive, file_folders, file_base_name )
		elif file_ext == '.cpp' or file_ext == '.inl' or file_ext == '.mm' or file_ext == '.m':
			self.openHppFile( file_drive, file_folders, file_base_name )
