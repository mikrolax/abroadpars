#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  ts.py
    A simple TS extractor
    
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
__author__='sebastien stang'
__author__='seb@mikrolax.me'
__license__='MIT'
__version__='beta'

import os
import logging
logging.basicConfig(level=logging.WARNING)

import bitstring

class TS(object):
  def __init__(self):
    self.bits=None
    self.extractedPid=[]
    self.poslistPerPid={}
    self.PATinfo={}
    self.PMTinfo={}
  #def parsePMT(self,pos=None):
  
  def parse_PAT(self,pos=None):
    table_id,section_syntax_indicator,zero,reserved,section_length=self.bits.readlist('uint:8,bin:1,bin:1,bin:2,uint12')
    #self.PATinfo[table_id]=
    transport_stream_id,reserved,version_number,current_next_indicator,section_number,last_section_number=self.bits.readlist('uint:16,bin:2,uint:5,bin:1,2*hex:8')
    '''
    for i = 0 to N
      program_number	56 + (i * 4)	16	uimsbf
      reserved	72 + (i * 4)	3	bslbf
      if program_number = 0
        network_PID	75 + (i * 4)	13	uimsbf
      else
        program_map_pid	75 + (i * 4)	13	uimsbf
      end if
    next
    CRC_32	88 + (i * 4)	32	rpchof
    '''

  
  def fromFile(self,filepath):
    self.bits=bitstring.ConstBitStream(filename=filepath)
    
  def find_sync(self):
    return self.bits.find('0x47',bytealigned=True)
      
  def parseAF(self):
    length=self.bits.read('uint:8')
    self.adaptationField=self.bits.read('hex:%s' %(length*8))
    return length 
    
  def extractPacket(self,pid): 
    if self.bits.pos+(188*8) > len(self.bits): #end of the bitstream
      return False     
    if self.bits.peek(8) != '0x47':
      logging.error('TS bad sync byte')
      return False
    self.sync_byte,tei,pusi,prio,PID,scr,af,cc=self.bits.readlist('hex:8,bool,bool,bool,uint:13,bin:2,bin:2,hex:4')
    #add PID if not in dict
    if PID not in self.poslistPerPid.keys():
      self.poslistPerPid[PID]=[]
    self.poslistPerPid[PID].append(self.bits.pos-(4*8))
    # get currrent pid
    if PID==pid:
      if af == '11':
        af_lenght=self.parseAF()
        self.extractedPid.append(self.bits.read('hex:%s' %((183-af_lenght)*8)))
      elif af == '01': # payload only
        self.extractedPid.append(self.bits.read('hex:%s' %(184*8)))
      else: #0x2 no payload
        self.bits.read('hex:%s' %(184*8))    
    else:
      skip=self.bits.read('hex:%s' %(184*8))
    return True
  
  def extract(self,pid=None,infilepath=None,outfilepath=None): #extractPES
    #if pid==None: get the first you see...
    self.extractedPid=[]
    if infilepath != None:
      self.fromFile(infilepath)
    logging.info('TS Extracting pid %s from %s' %(pid,str(os.path.basename(infilepath))))
    self.find_sync()
    logging.debug('found sync byte at pos %s' %self.bits.pos)
    nbTSpacket=0
    while self.extractPacket(pid) == True:
      #print '.',
      nbTSpacket+=1
      pass   
    logging.info('found %s TS packet' %str(nbTSpacket))  
    #import pprint
    #pprint.pprint(self.poslistPerPid.keys())
    if outfilepath != None:  
      self.writePES(outfilepath)
    else:
      #self.writePES('infilepath_pid%s.bin'%str(pid))
      return ''.join(self.extractedPid) #''.join(x.encode('hex') for x in all) 
  
  #def writeES(self,filepath): Need PES header parsing...
          
  def writePES(self,filepath):
    print 'Writing PES to %s' %(filepath)  
    #all=''.join(self.extractedPid)
    f=open(filepath,'wb')
    all=''.join(self.extractedPid)
    s=bitstring.ConstBitStream(hex=all)
    f.write(s.tobytes()) #s.tofile(f)
    f.close()

if __name__ == '__main__':    
  pass
      
