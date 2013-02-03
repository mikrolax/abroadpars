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
__author_email__='seb@mikrolax.me'
__license__='MIT'

import argparse
import os

import logging
FORMAT = "%(levelname)s:%(module)s:%(message)s" #%(asctime)s
logging.basicConfig(format=FORMAT,level=logging.INFO)

from parser.vbi import vbiPES as vbiPES 
from parser.vbi_video import vbiVid as vbiVid

vbi=vbiPES()
video=vbiVid()

def checkFromFile(tst_file_path,report=None):
  #read file and execute tests
  lines=open(tst_file_path).readlines()
  for line in lines:
    line=line.rstrip('\n')
    line=line.rstrip()
    #if line.startswith('#'):
      #pass
    if line.startswith('vbi;'):
      if len(line.split(';'))==3:
        skip,action,value=line.split(';')
        vbi.check(action,value=value,report=report)
      elif len(line.split(';'))==5:
        skip,action,line,param,value=line.split(';')
        vbi.check(action,lineNb=line,param=param,value=value,report=report)
      else:
        pass
    elif line.startswith('video;'):
      pass
    else:
      pass
  return True


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
  
  if not os.path.exists(args.infile):
    #raise NameError('input file does not exist')
    raise ValueError('Error: Input file does not exist')
    #return 1
    
  if args.version:
    print 'running vbiparse v.%s' %__version__
    return 0  

  outstreampath=None
  if args.extract != 'None':
    if args.extract in ['pes','es']:
      if args.output_stream != 'None':
        outstreampath=args.output_stream
      else:
        outstreampath=os.path.splitext(args.infile)+'.pes'
    else:
      logging.warning(' Unknown EXTRACT type. No extraction will be performed.')

  if os.path.exists(args.test_file):
    test_file=args.test_file    
  else:
    test_file=None
        
  outreportpath=None        
  if args.report != 'None':
    if args.output_report != 'None':
      outreportpath=args.output_report
    else:
      if test_file !=None:
        outreportpath=os.path.splitext(test_file)[0]+'.md'
      else:
        outreportpath=os.path.splitext(args.infile)[0]+'.md'
    open(outreportpath,'w').close()
        
  print ' '
  print ' vbipars v.%s' %__version__
  print '   + prosessing file : %s' %os.path.basename(args.infile)
  print '     - format : %s' %args.format  
  print '     - video pid : %s' %args.video_pid
  print '     - vbi pid : %s' %args.vbi_pid
  print '     - extract : %s' %args.extract
  print '     - test_file : %s' %os.path.basename(test_file)
  print '     - report type: %s' %args.report
  print '     - report file: %s' %os.path.basename(outreportpath)
  print ' '
  
  # import TS, or PES or ES then extract/analyse
  if args.format=='pes' and  args.vbi_pid!=0:
    logging.warning(' Analysing PES file not implemented yet. Skipping.')
    #vbi.analyseFromES(args.infile)
  elif args.format=='es':
    logging.info(' Analysing ES file...')
    vbi.analyseFromPES(args.infile)
  elif args.format=='ts':
    logging.info(' Analysing TS file...')
    res=vbi.analyseFromTS(args.infile,pid=args.vbi_pid) 
    '''if res==0:
      logging.info(' TS file Analyse [OK]')   
    else:
      logging.info(' TS file Analyse [Error %s] ' %str(res))
    '''
  else: # assume TS and parse PAT/PMT...
    logging.info(' Auto-analysing TS file')
    #TS().extract()
    vbi.analyseFromTS(args.infile,pid=args.vbi_pid)
  if args.video_pid!=0:
    logging.info(' Analysing video PID %s' %str(args.video_pid))
    video.analyseFromTS(args.infile,pid=args.video_pid)  # add video pid    
  
  #if test, do them
  if os.path.exists(args.test_file):
    logging.info(' Passing tests from %s' %str(os.path.basename(args.test_file)))
    f=open(outreportpath,'w')
    f.write('###Check\n - - - - \n')
    f.close()  
    check_result=checkFromFile(args.test_file,report=outreportpath)
  else:
    logging.warning('Test file config dos not exist.Skipping.')  
  
  #output data if specify  
  if args.extract!='None':
    logging.info(' Extracting %s' %args.extract )
    if args.extract =='pes':
      vbi.writePES(outstreampath)
    else:
      logging.warning(' %s extraction type not supported' %args.extract)
      #vbi.writeES(outstreampath) 
    #video.write() #Info
  
  #write report if specified
  if args.report!=None:
    logging.info(' Write detailed report %s' %str(os.path.basename(outreportpath)))
    f=open(outreportpath,'a')
    f.write('###PES Analayse \n - - - - \n')
    f.close()  
    vbi.writeReport(outreportpath)  
    #video.write()  


if __name__ == '__main__':    
  cli()
  
