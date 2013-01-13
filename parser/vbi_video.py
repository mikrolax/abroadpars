#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  vbi_video.py:
    A simple parser to get VBI/VANC data inserted in video TS stream 
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
__author__='sebastien stang'
__author__='seb@mikrolax.me'
__license__='MIT'
__version__='beta'

import logging
logging.basicConfig(level=logging.INFO)

import bitstring
from ts import TS as TS

class vbiVid(object):
  def __init__(self):
    self.bits=None
    self.cc_data_infos=[]
    self.bar_data=[]
    self.afd_data=[]
    
  #parsing function  
  def get_cc_data(self,pos=None):
    if pos!=None:
      self.bits.pos=pos   
    if (self.bits.pos+(2*8))<len(self.bits): #use self.lenght
      process_em_data_flag,process_cc_data_flag,additional_data_flag,cc_count,em_data=self.bits.readlist('3*bool,uint:5,uint:8')
      if (self.bits.pos+(cc_count*24))<len(self.bits):
        cc_data_lst=[]
        for i in range(cc_count):
          marker_bits,cc_valid,cc_type,cc_data_1,cc_data_2=self.bits.readlist('bin:5,bool,bin:2,2*hex:8') 
          cc_data={}
          cc_data['marker_bits']=marker_bits
          cc_data['cc_valid']=cc_valid
          cc_data['cc_type']=cc_type
          cc_data['cc_data_1']=cc_data_1
          cc_data['cc_data_2']=cc_data_2
          cc_data_lst.append(cc_data)
        info={}
        info['process_em_data_flag']=process_em_data_flag
        info['process_cc_data_flag']=process_cc_data_flag
        info['additional_data_flag']=additional_data_flag
        info['cc_count']=cc_count
        info['em_data']=em_data
        info['cc_data']=cc_data_lst
        self.cc_data_infos.append(info)
                  
  def parse_MPEG_cc_data(self,pos=None):
    if pos!=None:
      self.bits.pos=pos
    print 'parse_MPEG_cc_data'
    self.get_cc_data()
    #verify 8 marker bit to '1'
    marker_bits=self.bits.read('hex:8')
    if marker_bits != '0xFF':
      print 'marker bits error...'

  def parse_parse_bar_data(self,pos=None):
    if pos!=None:
      self.bits.pos=pos
    print 'parse_bar_data'
    top_bar_flag,bottom_bar_flag, left_bar_flag, right_bar_flag,reserved=self.bits.readlist('4*bool,hex:4')
    #check reserved
    info={}
    info['top_bar_flag']=top_bar_flag
    info['bottom_bar_flag']=bottom_bar_flag
    info['left_bar_flag']=left_bar_flag
    info['right_bar_flag']=right_bar_flag
    info['reserved']=reserved
    if top_bar_flag == True:
      one_bits, line_number_end_of_top_bar=self.bits.readlist('hex:2,uint:14')
      info['one_bits']=one_bits
      info['line_number_end_of_top_bar']=line_number_end_of_top_bar
    if bottom_bar_flag == True:
      one_bits, line_number_start_of_bottom_bar=self.bits.readlist('hex:2,uint:14')
      info['one_bits']=one_bits
      info['line_number_start_of_bottom_bar']=line_number_start_of_bottom_bar
    if left_bar_flag == True:
      one_bits, pixel_number_end_of_left_bar=self.bits.readlist('hex:2,uint:14')
      info['one_bits']=one_bits
      info['pixel_number_end_of_left_bar']=pixel_number_end_of_left_bar      
    if right_bar_flag == True:
       one_bits, pixel_number_start_of_right_bar=self.bits.readlist('hex:2,uint:14')    
       info['one_bits']=one_bits
       info['pixel_number_start_of_right_bar']=pixel_number_start_of_right_bar
    self.bar_data.append(info)
             
  def parse_afd_data(self,pos=None):
    if pos!=None:
      self.bits.pos=pos
    info={}
    zero,active_format_flag,reserved=self.bits.readlist('2*bool,bin:6')
    info['zero']=zero
    info['active_format_flag']=active_format_flag
    info['reserved']=reserved    
    if zero!=0:
      print 'warning zero=1'
    if active_format_flag == True:
      reserved,active_format=self.bits.readlist('hex:4,uint:4')
      #should display info based on aspect_ratio....   
      info['reserved']=reserved
      info['active_format']=active_format
    self.afd_data.append(info)
  
  def parse_ATSC_user_data(self,pos=None):
    if pos!=None:
      self.bits.pos=pos
    user_data_type_code=self.bits.read('hex:8')
    if user_data_type_code == '03':
      self.parse_MPEG_cc_data()
    elif user_data_type_code == '06':
      self.parse_bar_data()
    else:
      print 'user_data_type_code %s (ATSC reserved)' %user_data_type_code
   
  def getUserData(self):
    #while ( self.bits.pos < ):
    if self.bits.find('0x000001b2'): # find all ??
      print 'found user data at pos %s' %self.bits.pos
      start_code=self.bits.read('hex:32')
      #self.bits.find('0x44544731')
      #if self.bits.find('0x47413934'):
      self.user_data_identifier=self.bits.read('hex:32')
      if self.user_data_identifier == '0x44544731':
        self.parse_afd_data()
      elif self.user_data_identifier == '0x47413934':
        self.parse_ATSC_user_data() 
      else:
        print start_code
        #tmp=self.bits.findall('0x000001b244544731',bytealigned=True)
        
        print 'user data identifier %s not managed' %self.user_data_identifier
    else:
      print 'Cannot find user data'

  def parse_sequence_header(self,poslst):
    for pos in poslst:
      self.bits.pos=pos
      sequence_header_code,horizontal_size_value,vertical_size_value,aspect_ratio_information=self.bits.readlist('hex:32,2*uint:12,uint:4')
      frame_rate_code,bit_rate_value,marker_bit=self.bits.readlist('uint:4,uint:18,bin:1')
      print aspect_ratio_information
      
  def analyseFromTS(self,filepath,pid):
    ts=TS()
    data = ts.extract(pid=pid,infilepath=filepath)
    print 'TS extraction done'
    self.bits=bitstring.ConstBitStream(hex=data)
    with open('userdata.bin','wb') as f:
      f.write(data)
    #self.analyse()
    
    print self.bits.pos
    print 'nb PES : %s' %len(list(self.bits.findall('0x000001e0')))
    print self.bits.pos
    self.bits.pos=0
    print self.bits.pos
    print 'pictures : %s' %list(self.bits.findall('0x00000100'))
    
    print self.bits.pos
    print 'sequence header : %s' %list(self.bits.findall('0x000001b3'))
    self.parse_sequence_header(list(self.bits.findall('0x000001b3')))
    
    print self.bits.pos 
    print 'GOP : %s' %list(self.bits.findall('0x000001b8'))
    print self.bits.pos
    print 'user data : %s' %list(self.bits.findall('0x000001b2'))
    print self.bits.pos
    print 'ATSC_user_data : %s' %list(self.bits.findall('0x000001b247413934'))
    print self.bits.pos
    print 'afd_data : %s' %list(self.bits.findall('0x000001b244544731'))    
    

    #print 'SEI itu_t_35 : %s' %list(self.bits.findall('0xb50031'))    
    print 'SEI ATSC_user_data : %s' %list(self.bits.findall('0xb5003147413934'))  
    for pos in list(self.bits.findall('0xb5003147413934',bytealigned=True)):
      self.parse_ATSC_user_data(pos+(7*8))  
    print 'SEI afd_data : %s' %list(self.bits.findall('0xb5003144544731'))    
    for pos in list(self.bits.findall('0xb5003144544731',bytealigned=True)):
      self.parse_afd_data(pos+(7*8))        
    print self.bits.find('0x000001b2')
    #self.getUserData()
    self.write()
  
  def write(self,mode='md'):    
    import pprint
    #if len(self.cc_data_infos)>0:
    #  for cc_data in self.cc_data_infos: 
    #    pprint.pprint(cc_data)
    if len(self.bar_data)>0:
      for bar_data in self.bar_data:  
        pprint.pprint(bar_data)
    if len(self.afd_data)>0:
      for afd_data in self.afd_data:  
        pprint.pprint(afd_data)        
  
  #check function
  def check(self,data_type,value,awaited): #add image number?
    print 'checking %s param %s. Awaited %s... ' %(data_type,value,awaited), 
    valueList=[]
    if data_type in ['afd','all']:
      for afd_data in self.afd_data: 
        if value in afd_data.keys():
          valueList.append(afd_data[value])    
    if data_type in ['cc','all']:
      for cc_data in self.cc_data_infos: 
        if value in cc_data.keys():
          valueList.append(cc_data[value]) 
    if data_type in ['bar','all']:
      for bar_data in self.bar_data: 
        if value in bar_data.keys():
          valueList.append(bar_data[value]) 
    if len(valueList)==0:
      print ' KO (no data)'
      return False         
    for value in valueList:
      if value!=awaited:
        print ' KO (found %s)' %value
        return False
    print ' OK'    
    return True
          
if __name__ == '__main__':
  vbiFromVid=vbiVid()
  vbiFromVid.analyseFromTS('user_data_pid3111.ts',pid=3111)  # add video pid    
  ret=vbiFromVid.check('afd','active_format',2)
  print 'afd active format=2 is %s' %ret
  vbiFromVid.check('cc','process_cc_data',True)

