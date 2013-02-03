#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  vbi.py
    A simple Broadcasted VBI Data parser (mostly conforming to ETSI EN 301 775)
    
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
FORMAT = "%(levelname)s:%(module)s:%(message)s" #%(asctime)s
logging.basicConfig(format=FORMAT,level=logging.INFO)

import bitstring
from ts import TS as TS #or Extractor()
data_unit_info={'02':'Teletexte Magazine',
                '03':'Teletexte Subtitle',
                'C3':'VPS',
                'C4':'WSS',
                'C6':'Monochrome Transparent',
                'E0':'Video Index',
                'D0':'AMOL1',
                'D1':'AMOL2',
                'D5':'NABTS',
                'D6':'TvGuide2x',
                'D9':'VITC'
                }
                            
class vbiPES(object):
  def __init__(self):
    self.bits=None
    self.ts=TS()
    self.line_infos=[]
    self.pesInfos=[] #list of currentPES dict
    self.currentPES={}
    self.pesStat=[] 
    # [ {pts:PTS,data:[(line_idx,data_type),(line_idx,data_type)]},
    #   {pts:PTS,data:[(line_idx,data_type),(line_idx,data_type)]},
    #   {pts:PTS,data:[(line_idx,data_type),(line_idx,data_type)]} ]

  def find_sync(self):
    return self.bits.find('0x000001bd')
  
  def parse_header(self):
    self.packet_start_code,self.stream_id,self.pes_packet_lentgh = self.bits.readlist('hex:24,hex:8,uint:16') #use le when generating from lib...
    #print 'packet_start_code 0x%s' %self.packet_start_code
    #print 'stream_id 0x%s' %self.stream_id
    #print 'pes_packet_lentgh %s' %self.pes_packet_lentgh
    #self.pesInfos.append(pesInfos)
    logging.debug('packet_start_code : 0x%s' %str(self.packet_start_code))
    if (self.packet_start_code == '000001') : #000001
      if(self.stream_id == 'bd' ):
        optional_pes_header_part,self.pes_header_data_length=self.bits.readlist('hex:16,uint:8')
        self.currentPES={}
        pesInfos={}
        pesInfos['optional_pes_header_part']=optional_pes_header_part
        pesInfos['pes_header_data_length']=self.pes_header_data_length
        #print  'optional_pes_header_part 0x%s' %optional_pes_header_part
        #print  'pes_header_data_length %s' %self.pes_header_data_length
        if self.pes_header_data_length>0:
          if optional_pes_header_part=='8480': # PTS field present
            if self.pes_header_data_length == 5:
              pts_field=self.bits.read('hex:40') #5*8
              pesInfos['PTS']=pts_field
            elif self.pes_header_data_length == 36:
              pts_field=self.bits.read('hex:40')
              stuffing=self.bits.read('hex:248') 
              pesInfos['PTS']=pts_field
            else:
              print 'error : pes_header_data_length %d' %self.pes_header_data_length
              pesInfos['error']='pes header data'
          elif optional_pes_header_part == '8401':
            if self.pes_header_data_length == 36:
              pesInfos['PTS']=self.bits.read('hex:288')
            else:
              print 'error : pes_header_data_length'
              pesInfos['error']='pes_header_data_length'
          else:
            print 'error optional_pes_header_part 0x%s, skipping %s bytes...' %(str(optional_pes_header_part),str(self.pes_header_data_length))
            skip=self.pes_header_data_length*8
            self.bits.read('hex:%s' %str(skip))
            pesInfos['error']='error optional_pes_header_part 0x%s, skipping %s bytes...' %(str(optional_pes_header_part),str(self.pes_header_data_length))   
          self.currentPES['header']=pesInfos        
          return True  
      else:
        logging.error('VBI PES header : stream_id=0x%s' %self.stream_id)      
        return False
    else:
      logging.error('VBI PES header : packet_start_code=0x%s at bytes %d/%d' %(self.packet_start_code,self.bits.bytepos,(len(self.bits)/8)))
      return False
       
  def parsePayload(self):
    self.data_identifier=self.bits.read('uint:8')
    logging.debug('data_identifier %s' %self.data_identifier)
    if self.data_identifier==16:
      #while self.parse_teletext_data()==True:
      #  pass
      self.parse_teletext_data() #return successful or not?  
    else:
      logging.warning('other data_identifier : %s , skipping bytes...' %str(self.data_identifier))
      skip=self.bits.read('hex:%s' %str((self.pes_packet_lentgh-2-self.pes_header_data_length-2)*8))
    return self.pes_packet_lentgh-2-self.pes_header_data_length-2
  
  def parse_teletext_data(self):
    lenght=self.pes_packet_lentgh-2-self.pes_header_data_length-1-1
    logging.debug('%s nb bytes to parse' %str(lenght))
    self.line_infos=[]
    while lenght>0:   
      if (self.bits.pos+(3*8)) < len(self.bits): 
        data_unit_id,data_unit_lenght,reserved,field_parity,line = self.bits.readlist('hex:8,uint:8,bin:2,bin:1,uint:5')
        if data_unit_lenght == 0:
          print 'Error sync !?? Aborting... lenght=%s data_unit_id=%s' %(lenght,data_unit_id)
          return False      
        logging.debug('data_unit_id %s ' %data_unit_id)
        logging.debug('data_unit_lenght %s ' %data_unit_lenght)
        logging.debug('line %s ' %line)
        if (self.bits.pos+((data_unit_lenght-1)*8)) < len(self.bits):
          data=self.bits.read('hex:%s' %str((data_unit_lenght-1)*8))
          self.line_infos.append( (data_unit_id,data_unit_lenght,field_parity,line,data) )
          lenght-=(data_unit_lenght+2)   
          #self.print_line_infos() #store infos
        else:
          return False
      else:
        return False        
    self.print_line_infos()
    return True
      
  def print_line_infos(self):
    logging.debug('### new PES') #add pes packet nb
    infos=[]
    self.currentPES['payload']=[]
    for data_unit_id,data_unit_lenght,field_parity,line,data in self.line_infos:
      if data_unit_id in data_unit_info.keys():
        logging.debug('* found %s on line %s '%(data_unit_info[data_unit_id],line))
        line_infos={}
        line_infos['data_unit_id']=data_unit_id
        line_infos['data_unit_lenght']=data_unit_lenght
        #if field_parity == 0 and (data_unit_id=='02' or data_unit_id=='03'):
        #  line+=314
        line_infos['line']=line #check fo doublon? 
        line_infos['data']=data
        infos.append(line_infos)
    self.currentPES['payload']=infos #payload image number?
        #print data
          
  def fromFile(self,filepath):
    self.bits=bitstring.ConstBitStream(filename=filepath)
  
  #def analysefromES(self,filepath=None):
    #self.parsePayload()
          
  def analyse(self,filepath=None): #fromPES
    logging.info('PES analyse')
    if filepath !=None:
      self.fromFile(filepath)  
    self.find_sync()
    #while self.bits.pos+48 < len(self.bits) :  #6*8+4*8
    while self.parse_header() == True:  
      size=self.parsePayload() #better to return info dict
      self.pesInfos.append(self.currentPES)
      #print 'resyncing'  
      #self.bits.pos+=8
      #print  self.bits.pos 
      #print  len(self.bits)
      
  def analyseFromTS(self,filepath,pid):
    data = self.ts.extract(pid=pid,infilepath=filepath)
    logging.info('TS extraction done')
    self.bits=bitstring.ConstBitStream(hex=data)
    #with open('vbipes.bin','wb') as f:
    #  f.write(data)
    self.analyse()
    self.computeStat()

  def computeStat(self):
    pesStat=[]
    for pes in self.pesInfos:
      stat={}
      if 'header' in pes.keys():
        if 'PTS' in pes['header'].keys():
          stat['pts']=pes['header']['PTS']
        else:
          stat['pts']=None
      else:  
        stat['pts']=None
      data=[]
      if 'payload' in pes.keys(): 
        for line_info in pes['payload']:
          data.append( (line_info['line'],line_info['data_unit_id']) )
      stat['data']=data
      pesStat.append(stat)  
    self.pesStat=pesStat

  # Write functions
  def writeES(self,filepath):
    logging.warning('ES stream writing not implemented yet...')
    pass
    
  def writePES(self,filepath):
      self.ts.writePES(filepath)
      #or write self.bits!
      
  def writeReport(self,filepath,mode='md'):
    logging.info('writeReport (%s): write %s pes infos' %(mode,str(len(self.pesInfos))))    
    logging.debug('write into %s' %str(os.path.basename(filepath)))
    if mode == 'md':
      with open(filepath,'a') as mdfile:
        pesidx=0
        for pes in self.pesInfos:
          pesidx+=1
          mdfile.write('* PES %s infos     \n' %str(pesidx))
          mdfile.write('     \n')
          if 'header' in pes.keys():
            for key in pes['header'].keys():
              mdfile.write('        %s : %s     \n'%(key,pes['header'][key]))
          if 'payload' in pes.keys(): 
            for line_info in pes['payload']:
              mdfile.write('        found %s on line %s : %s bytes     \n'%(data_unit_info[line_info['data_unit_id']],line_info['line'],line_info['data_unit_lenght']))
          mdfile.write('     \n') 
      mdfile.close()  
  
  # Check functions
  def checkDeltaPTS(self,valueInTick):
    delta=[]
    prev_pts=self.pesStat[0]['pts']
    result=False
    status='no PTS found'    
    for pes in self.pesStat[1:]:
      try:
        delta.append(long(pes['pts'],base=16)-long(prev_pts,base=16))
      except :
        pass
      prev_pts=pes['pts']
    if len(delta):
      logging.debug('Delta PTS min : %s' %str(min(delta)))
      logging.debug('Delta PTS max : %s' %str(max(delta)))
      if min(delta[1:])==long(valueInTick):
        result=True
      status='Min:%s / Max:%s' %( str(min(delta[1:])),str(max(delta[1:])) ) 
    return (result,status)
      
  def checkDataUnit(self,value):
    result=False
    status='not found'    
    return (result,status)
  
  def checkDataLine(self,lineNb,param,value):
    result=False
    status='not found'
    value_list=[]
    pes_idx=0
    for pes in self.pesInfos:
      pes_idx+=1
      if 'payload' in pes.keys():
        for line_info in pes['payload']:
          if line_info['line']==int(lineNb):
            if int(line_info[param])==int(value):
              #print 'found param %s:%s' %(param,line_info[param])
              value_list.append(True)
    if len(value_list)>0:
      result=True
      status='%d/%d' %(len(value_list),pes_idx)      
    return (result,status)
  
        
  def check(self,action,lineNb=None,param=None,value=None,report=None):
    #available_action=['line','data_unit','PTS']
    if action=='line':
      msg='line %d check if %s=%s...' %(int(lineNb),str(param),str(value))
      res=self.checkDataLine(lineNb,param,value)
    elif action=='data_unit':
      msg='check if data_unit=%s...' %(str(value))
      res=self.checkDataUnit(value)      
    elif action=='PTS':
      msg='check if Delta PTS=%s...' %(str(value))
      res=self.checkDeltaPTS(value)
    else:
      msg='Unknown check expression %s.Skipping.' %action
      return False
    logging.info('     %s : %s' %(str(msg),str(res)) )
    
    if report!=None:
      md='     %s : %s\n' %(str(msg),str(res)) 
      mdfile=open(report,'a')    # codecs.open(report,'a','utf8')
      mdfile.write(md)
      #mdfile.write('     \n')   
      mdfile.close()
    return res
  
if __name__ == '__main__':
  pass
  
