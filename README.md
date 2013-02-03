abroadpars
==========

>Another BROADcast stream PARser    
Toolbox for stream testing      

_in development and  not focused on video_     
- - -    


### vbipars
>A simple parser to get VBI/VANC data inserted in MPEG2/MPEG4 TS stream:    

__From VBI PID:__   

* analyse stream conforming to ETSI EN 301 775   

__From video PID:__   

* treat User Data (MPEG2) or SEI (MPEG4)    
* get AFD, Closed caption and bar data (time code TODO)    

Can generate markdown report and scriptable for automated test process.   

#### Usage
    $ python vbipars.py -h
    usage: vbipars.py [-h] [-v] [-f FORMAT] [-video VIDEO_PID] [-vbi VBI_PID] [-e EXTRACT] [-r REPORT] [-tst TEST_FILE]
                      [-os OUTPUT_STREAM] [-or OUTPUT_REPORT]
                      infile

    vbipars v.beta: analyse VBI/VANC data from TS/PES/ES

    positional arguments:
      infile                input file.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         display current version
      -f FORMAT, --format FORMAT
                            input file format (ts, pes or es) Default to ts.
      -video VIDEO_PID, --video_pid VIDEO_PID
                            Video PID to analyse.
      -vbi VBI_PID, --vbi_pid VBI_PID
                            VBI PID to analyse.
      -e EXTRACT, --extract EXTRACT
                            EXTRACT in ['pes,'es'']. For VBI PID, extract PES to file inputfilename_pid_nb.pes (or .es)
      -r REPORT, --report REPORT
                            REPORT in ['md','html','json']. Write results/report as markdown or html.
      -tst TEST_FILE, --test_file TEST_FILE
                            input test file. See doc for more.
      -os OUTPUT_STREAM, --output_stream OUTPUT_STREAM
                            output stream file name. Override default one.
      -or OUTPUT_REPORT, --output_report OUTPUT_REPORT
                            output report file name. Override default one.     

See latter for  more info an tests.   

- - -
### vbitest
>An easy way to automate tests with `vbipars`    

#### Usage
    $ python vbitest.py /path/to/testsuite_config_file

See latter for  more info an tests.   

- - -
#### Note for tests 
* __Testsuite__ config example  (used by `vbitest.py` script)     

         # test_name              // Needed, delimiter for tests 
         testsuite;test_name;     // Override previous name
         testsuite;input_file;    // Input file 
         testsuite;vbi_pid;       
         testsuite;video_pid;
         testsuite;tst_file;this  // check for vbi and video tests defined here!

* __Generic VBI tests__ config example (used by `vbipars.py` and `vbitest.py` script)      
_Here we will check that we have teletext on line 10_     

         vbi;data_unit;16             // check that PES data_unit equal 16
         vbi;line;10;data_unit_id;03  // check that data_unit_id of line 10 is equal to 3 (Teletext)
         vbi;PTS;7200                 // check that min delta PTS between 2 PES is 7200 tick unit

* __Generic Video tests__ config example (used by `vbipars.py` and vbitest.py script)      
_Here we check that we have valid closed caption and that AFD value is 2_

        video;cc;cc_valid;True                // Check that you have valid closed caption
        video;afd;active_format_descriptor;2  // Check active_format_descriptor equal 2
        video;afd;aspect_ratio;1              // Check aspect_ratio equal 1 i.e. 16:9
     
* a complete example     

        # test_1
        testsuite;input_file;testfile1.ts 
        testsuite;vbi_pid;258
        testsuite;tst_file;this

        # test_2
        testsuite;test_name;overriden_name_test
        testsuite;input_file;testfile2.ts 
        testsuite;video_pid;256
        testsuite;tst_file;mytest.test2.tstcfg

        vbi;data_unit;16
        vbi;line;10;data_unit_id;03
        vbi;line;10;data_unit_lenght;44
        vbi;line;9;data_unit_id;02
        vbi;line;9;data_unit_lenght;44
        vbi;PTS;40

- - -
## License
Under MIT-style licensing.
    
Copyright (C) 2013 Sebastien Stang    

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.    

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    

