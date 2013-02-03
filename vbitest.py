#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""     
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

import os
import unittest
import subprocess
import datetime
import logging

FORMAT = "%(levelname)s:%(module)s:%(message)s" #%(asctime)s
logging.basicConfig(format=FORMAT,level=logging.INFO)
  
tst_list=[{'name':'default',
           'input_file':None,
           'vbi_pid':0,
           'video_pid':0,
           'tst_file':None,
           }]

prefix='testsuiteprefix'

def _module_path():
  return os.path.dirname(os.path.abspath(__file__))

def getPlatformInfos():
  import platform
  _date=datetime.datetime.today()
  _platform          =platform.platform()
  _machine           =platform.machine()
  _processor         =platform.processor()
  _py_compiler       =platform.python_compiler()
  _py_version        =platform.python_version()
  _py_implementation =platform.python_implementation()
  return dict(date=_date,platform=_platform,machine=_machine,processor=_processor,py_implementation=_py_implementation,py_compiler=_py_compiler,py_version=_py_version)
  
def getTestListFromFile(filePath):
  tstLst=[]
  global prefix
  prefix=os.path.abspath(os.path.splitext(filePath)[0])  
  lines=open(filePath).readlines()
  for line in lines:
    line=line.rstrip('\n')
    if line.startswith('#'):  # add tests
      logging.info('New test %s' %(line.lstrip('#')))
      try:
        tstLst.append(tst)
        test_name=line.lstrip('#')
      except:
        test_name=line.lstrip('#')
        last_tst_file='None'
        last_input_file='None'
        last_vbi_pid=0
        last_video_pid=0
        pass
      tst={} 
      tst['name']=test_name
      tst['tst_file']=last_tst_file
      tst['input_file']=last_input_file
      tst['vbi_pid']=last_vbi_pid
      tst['video_pid']=last_video_pid
    if line.startswith('testsuite;'):
      skip,param,value=line.rsplit(';')
      if param=='tst_file': 
        if value=='this':
          tst['tst_file']=os.path.basename(filePath)
        else:
          tst['tst_file']=value
        last_tst_file=tst['tst_file']          
      elif param=='input_file':  
        last_tinput_file=value          
        tst[param]=value
      elif param=='vbi_pid':
        last_vbi_pid=value
        tst[param]=value
      elif param=='video_pid':
        last_video_pid=value
        tst[param]=value
      elif param=='test_name': 
        if (len(value)>0) and (value not in [' ',' \n']):
          tst['name']=value
          test_name=value  
      else:
        logging.warning('Unknown param %s' %param)   
  tstLst.append(tst)
  global tst_list
  tst_list=tstLst

  return tstLst


class Result():
  def __init__(self):
    self.result=[]
    self.infos=getPlatformInfos()
  
  def add(self,result):
    self.result.append(result)
      
  def write(self):
    import codecs
    with codecs.open(prefix+'.overview.md','w','utf8') as mdfile: #prefix
      mdfile.write('### Infos:      \n')
      for info in self.infos.keys(): 
        mdfile.write('     %s : %s      \n' %(info,self.infos[info]))
      mdfile.write('### Results:      \n')
      for result in self.result: 
        mdfile.write('     Test : %s : %s      \n' %(str(result[0]),str(result[1])))
    
  def _print(self):  
    print '--------------------------------------------------------------'  
    for info in self.infos.keys():
      logging.info('Global infos: %s : %s' %(info,self.infos[info]))
    print '--------------------------------------------------------------'  
    for result in self.result:
      logging.info('Test result: %s : %s : %s' %(str(result[0]),str(result[1]),str(result[2])))
      

          
class VbiParsTst(unittest.TestCase):  
  def setUp(self):
    self.result=Result()
    self.tst_list=tst_list
      
  def runTest(self):    
    for test in self.tst_list: 
      self.testName=test['name']
      self.inFile=os.path.join(os.path.dirname(prefix),test['input_file'])
      self.vbi=test['vbi_pid']
      self.video=test['video_pid']
      self.tst=os.path.join(os.path.dirname(prefix),test['tst_file'])
      md_out=prefix+'.'+self.testName.strip()+'.md'         #prefix
      cmd='python vbipars.py -vbi %s -video %s -tst %s -or %s %s ' %(self.vbi,self.video,self.tst,md_out,self.inFile)
      print cmd
      print ' '
      #print 'Testing %s ...' %(os.path.basename(self.tst))
      logging.info('Testing %s ...' %(self.testName))
      print '--------------------------------------------------------------'
      start_time=datetime.datetime.now()
      ret=subprocess.call(cmd,shell=True)
      end_time=datetime.datetime.now()
      res=(self.testName,ret,end_time-start_time) #add name & comment?
      self.result.add(res)
      #self.assertEqual(ret,0)

  def tearDown (self): 
    print ' '
    self.result._print()
    self.result.write()


def get_test_suite():
    suite = unittest.TestSuite()
    suite.addTest(VbiParsTst())  
    return suite
  
  
if __name__ == '__main__':  
  import sys
  print sys.argv
  if os.path.exists(sys.argv[-1]):
    logging.info('load test from %s' %str(sys.argv[-1]))
    getTestListFromFile(sys.argv[-1])
  runner = unittest.TextTestRunner()
  test_suite = get_test_suite()
  res=runner.run(test_suite)     
   
