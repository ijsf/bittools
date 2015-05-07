#!/usr/bin/python
##############################################################################
#
# bitman.py - bitwise file viewer
#
# Copyright (c) 2015, Cecill Etheredge, ijsf - http://ijsf.nl/
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################

import sys
import argparse
import struct
import colorama
from termcolor import colored

def main(argv):
	#
	# Prints bits, LSB first
	#
	# Originally published by user97370 at: http://stackoverflow.com/questions/2576712/using-python-how-can-i-read-the-bits-in-a-byte
	#
	def bits(f):
	    bytes = (ord(b) for b in f.read())
	    for b in bytes:
	        for i in xrange(8):
	            yield (b >> i) & 1
	
	def autoint(x):
		return int(x or 0, 0)
	
	# Initialize
	colorama.init()
	
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help = "Input file");
	parser.add_argument("-o", "--output", help = "Output file");
	parser.add_argument("-p", "--pattern", help = "Binary pattern to highlight");
	parser.add_argument("-g", "--grid", help = "Enables grid coloring of every 8th bit", action="store_true");
	parser.add_argument("-s", "--skip", help = "Amount of bits to skip (decimal or hexadecimal)", type=autoint, default=0);
	parser.add_argument("-l", "--length", help = "Amount of bits to print (decimal or hexadecimal)", type=autoint, default=0);
	parser.add_argument("-c", "--columns", help = "Column width or amount of bits to print on one line", type=int, default=80);
	args = parser.parse_args()
	
	try:
		# File handling
		fileInput = open(args.input, "rb")
		if not fileInput:
			raise IOError("Input file '%s' could not be opened" % args.input)
		
		fileOutput = None
		if args.output:
			fileOutput = open(args.output, "wb")
			if not fileOutput:
				raise IOError("Output file '%s' could not be opened" % args.output)
		
		# Variables
		hl = ''
		hlLength = args.pattern and (len(args.pattern) + 1)
		p = 0
		c = 0
		buf = 0
		bufCnt = 0
		
		# Consume file, bit by bit
		for b in bits(fileInput):
			if p >= args.skip and (p < (args.length + args.skip) or args.length == 0):
				# Keep pattern matching string
				if hlLength:
					hl += str(b)
					if len(hl) == hlLength:
						hl = hl[1:hlLength]
				
				# Check if column width was exceeded
				if c >= args.columns:
					# New line
					sys.stdout.write('\n')
					c = 0
				
				# Print location data for every first bit on newline
				if c == 0:
					sys.stdout.write(colored(str('0x%08X + 0x%04X ' % (p - args.skip, args.skip)), 'white'))

				# Color handling
				if args.pattern and hl == args.pattern:
					# Pattern found, mark last bit with green
					sys.stdout.write(colored(str(b), 'green'))
				else:
					if args.grid and (c % 8) == 0:
						# Grid bit, mark with white
						sys.stdout.write(colored(str(b), 'white'))
					else:
						# Regular bit, mark with magenta
						sys.stdout.write(colored(str(b), 'magenta'))
				
				# Write to output file, if necessary
				if fileOutput:
					if bufCnt == 8:
						fileOutput.write(struct.pack('B',buf))
						buf = 0
						bufCnt = 0
					
					buf = buf | (b << bufCnt)
					bufCnt += 1
				
				c += 1
			p += 1
		sys.stdout.write('\n')
	finally:
		if fileInput:
			fileInput.close()
		if fileOutput:
			fileOutput.close()

if __name__ == "__main__":
	main(sys.argv)
