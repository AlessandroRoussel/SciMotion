import numpy as np

"""
The Time class provides utilitary functions
to manage time, durations, and frames...
"""

class Time:
	# converts a duration in frames to a string
	def formatTime(duration, fps):
		
		# calculates the amount of frames, seconds, minutes, hours
		frames = int(duration % fps)
		seconds = int(np.floor(duration/fps)) % 60
		minutes = int(np.floor(duration/fps/60)) % 60
		hours = int(np.floor(duration/fps/3600))
		
		# converts them to strings with 2 digits except for the hours
		str_frames = ("0" if frames < 10 else "") + str(frames)
		str_seconds = ("0" if seconds < 10 else "") + str(seconds)
		str_minutes = ("0" if minutes < 10 else "") + str(minutes)
		str_hours = str(hours)
		
		# returns with "h:mm:ss.ff" format
		return str_hours+":"+str_minutes+":"+str_seconds+"."+str_frames