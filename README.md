abroadpars
==========

Another BROADcast stream PARser     

_in development_     

## Current status 
### vbipars
A simple parser to get VBI/VANC data inserted in MPEG2/MPEG4 TS stream    

From VBI PID:   
* analyse stream conforming to ETSI EN 301 775   
      
From video PID:   
* treat User Data (MPEG2) or SEI (MPEG4)    
* get AFD, Closed caption and bar data (time code TODO)    

#### Usage
    $ python vbipars.py -h
    usage: vbipars.py [-h] [-v] [-f FORMAT] [-video VIDEO_PID] [-vbi VBI_PID]
                      [-e EXTRACT] [-r REPORT] [-tst TEST_FILE]
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

 

