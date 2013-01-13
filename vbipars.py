#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  vbipars.py:
    A simple parser to get VBI/VANC data inserted in MPEG2/MPEG4 TS stream 
    
    From VBI PID:
      - analyse stream conforming to ETSI EN 301 775
      
    From video PID:
     - treat User Data (MPEG2) or SEI (MPEG4) 
     - get AFD, Closed caption and bar data (time code TODO)
     
Copyright (C) 2013 Sebastien Stang

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
__version__='beta'
__author__='sebastien stang'
__author__='seb@mikrolax.me'
__license__='MIT'

import argparse
import os

import logging
logging.basicConfig(level=logging.INFO)

from parser.vbi import vbiPES as vbiPES 
from parser.vbi_video import vbiVid as vbiVid

def cli():
  parser = argparse.ArgumentParser(description='vbipars v.%s:  analyse VBI/VANC data from TS/PES/ES' %__version__,epilog='Sebastien Stang') #add version? 
  parser.add_argument("-v", "--version",action='store_true',default=False,help="display current version")
  parser.add_argument("-f", "--format",type=str,default='ts',help="input file format (ts, pes or es) Default to ts.")
  parser.add_argument("-video", "--video_pid",type=int,default=0,help="Video PID to analyse.")
  parser.add_argument("-vbi", "--vbi_pid",type=int,default=0,help="VBI PID to analyse.")
  parser.add_argument("-e", "--extract",type=str,default='None',help="EXTRACT in ['pes,'es'']. For VBI PID, extract PES to file inputfilename_pid_nb.pes (or .es)")
  parser.add_argument("-r", "--report",type=str,default='md',help="REPORT in ['md','html','json']. Write results/report as markdown or html.")
  parser.add_argument("-tst", "--test_file",type=str,default='',help="input test file. See doc for more.")
  parser.add_argument("-os", "--output_stream",type=str,default='None',help="output stream file name. Override default one.")
  parser.add_argument("-or", "--output_report",type=str,default='None',help="output report file name. Override default one.")
  parser.add_argument("infile",type=str,default='',help="input file.")
  args = parser.parse_args()
  
  #print args.infile
  if not os.path.exists(args.infile):
    print 'input file does not exist'
    return 1
    
  if args.version:
    print 'running vbiparse v.%s' %__version__
    return 0  

  outstreampath=None
  if args.extract != 'None':
    if args.extract in ['pes','es']:
      if args.output_stream != 'None':
        outstreampath=args.output_stream
      else:
        outstreampath=args.infile+'.pes'
    else:
      logging.warning('Unknown EXTRACT type. No extraction will be performed.')
  
  outreportpath=args.report        
  if args.report != 'None':
    if args.output_report != 'None':
      outreportpath=args.output_report
    else:
      outreportpath=args.infile+'.md'
      
  print '********************************************'
  print '* '
  print '* vbipars v.%s' %__version__
  print '* '
  print '* + prosessing file : %s' %args.infile
  print '*   - format : %s' %args.format  
  print '*   - video pid : %s' %args.video_pid
  print '*   - vbi pid : %s' %args.vbi_pid
  print '*   - extract : %s' %args.extract
  print '*   - report : %s' %args.report
  print '*   - test_file : %s' %args.test_file
  print '* '
  print '********************************************'

  
  vbi=vbiPES()
  video=vbiVid()
  # import TS, or PES or ES then extract/analyse
  if args.format=='pes' and  args.vbi_pid!=0:
    print 'analysing PES file not implemented yet'
    #vbi.analyseFromES(args.infile)
  elif args.format=='es':
    print 'analysing ES file :'
    vbi.analyseFromPES(args.infile)
  elif args.format=='ts':
    print 'analysing TS file :'  
    vbi.analyseFromTS(args.infile,pid=args.vbi_pid) 
  else: # assume TS and parse PAT/PMT...
    print 'auto-analysing TS file...'  
    #TS().extract()
    vbi.analyseFromTS(args.infile,pid=args.vbi_pid)
  
  if args.video_pid!=0:
    logging.info('analysing video PID ' %str(args.video_pid))
    video.analyseFromTS(args.infile,pid=args.video_pid)  # add video pid    
    
  #if test, do them
  if args.test_file:
    logging.info('passing tests from %s' %args.test_file) 
    ret=video.check('afd','active_format',2)  
    ret=vbi.check('afd','active_format',2)  
    
  #output data if specify  
  if args.extract:
    logging.info('extracting %s' %args.extract )
    if args.extract =='pes':
      vbi.writePES(outstreampath)
    else:
      logging.info('unknwown')
      #vbi.writeES(outstreampath) 
    video.write() #Info

  #write report if specified
  if args.report:
    logging.info('write report %s' %args.report)
    vbi.writeReport(outreportpath)  
    video.write()  


if __name__ == '__main__':    
  cli()
  '''
  tst file as follow:
  
  afd:active_format:2
  cc:process_cc_data:True
  vbi:data_unit:16
  vbi:data_unit_id:03
  vbi:line:07
  all:data_unit_id:16
  '''
  
