import matplotlib.pyplot as pyplot
import csv
from collections import OrderedDict 
import os,sys,re
import code
from ftplib import FTP

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir+'\pl1_rf_system')
    import pl1_rf_system_test_env

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d) if '.' in f]

def GetCsvFilesFtp ():
    rx_data_dir=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets'])
    ftp = FTP('corpftp.nvidia.com')
    ftp.login(user='PL1Team',passwd='CitJFeb3')
    ftp.cwd('RF_Driver/rx_characterisation')
    file_list=ftp.nlst()
    print file_list

    print('Downloading archived RX Data Sets')
    for file in file_list:
        destfile = os.path.join(rx_data_dir,file)
        localfile = open(destfile, 'wb')            # local file to store download
        ftp.retrbinary('RETR ' + file, localfile.write, 1024)
        localfile.close()
    ftp.quit()

def GetCsvNumFilesFtp ():
    ftp = FTP('corpftp.nvidia.com')
    ftp.login(user='PL1Team',passwd='CitJFeb3')
    ftp.cwd('RF_Driver/rx_characterisation')
    file_list=ftp.nlst()
    return len(file_list)

def ParseCsvData ():
    rx_data_dir=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets'])
    file_list = listdir_fullpath(rx_data_dir)

    #If there is no local data sets fetch from FTP
    if len(file_list) < 1:
        GetCsvFilesFtp()
        file_list = listdir_fullpath(rx_data_dir)

    result_list = []
    filename_list = []

    for file in file_list:
        (filepath,filename) = os.path.split(file)
        filename_list.append(filename)
        res_dic = OrderedDict()
        with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                res_dic[int(row[0])] = float(row[1])
                #print int(row[0]), float(row[1])
            result_list.append(res_dic)

    return filename_list,result_list

def GraphSelection (filename_list):

    num_selections = range(0,len(filename_list))
    graph_list = []

    for idx in num_selections:
        print "%d: %s" % (idx,filename_list[idx])

    graph_tuple = input("\nGraphs to Plot > ")

    for elem in graph_tuple:
        graph_list.append(elem)

    return graph_list

def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)

def PlotGraphs (graph_list,graph_data,filename_list):
    res_dir=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets', 'results'])

    fig = pyplot.figure(figsize=(14,12))
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    handle_dic = {}
    legend_list = []

    for graph in graph_list:
        print "GRAPH INDEX: %d" % graph
        print "GRAPH FILENAME: %s" % filename_list[graph]

        graph_filename = filename_list[graph].split('.')[0]+'.svg'

        if "3G" in graph_filename:
            rat = "3G"
        else:
            rat = "LTE"

        if "vesta" in graph_filename:
            platform = "Vesta"
        else:
            platform = "Olympus"

        obj = re.search(r'(CL\d+)', graph_filename, re.I)
        if obj:
            CL = obj.group(1)
        else:
            print "not able to get the CL"
            CL=""

        obj = re.search(r'(\d+MHz)', graph_filename, re.I)
        if obj:
            BW = obj.group(1)
            print "bandwidth: %s" % BW
        else:
            print "not able to get the CL"
            BW=""


        graph_abspath = os.path.join(res_dir,graph_filename)

        sweep_low_kHz = graph_data[graph].keys()[0]
        sweep_high_kHz = graph_data[graph].keys()[len(graph_data[graph].keys())-1]
        sweep_range_MHz = (sweep_high_kHz - sweep_low_kHz)/1e3
        pyplot.hold(True)
        handle_dic[graph]=pyplot.plot(graph_data[graph].keys(),graph_data[graph].values())
        pyplot.title('RX IQ Power vs Frequency - %d Mhz Sweep' % (int(sweep_range_MHz)))
        pyplot.ylabel('IQ Power (dBm)')
        pyplot.xlabel('Frequency (kHz)')
        pyplot.grid(True)
        pyplot.axis([sweep_low_kHz-50,sweep_high_kHz+50,15,50])
        legend_list.append(platform + ' ' + CL + ' ' + rat + ' ' +BW)

    pyplot.legend(legend_list)
    pyplot.savefig(graph_abspath)
    pyplot.show()
    #code.interact(local=locals())

if __name__ == '__main__':
    print "Starting Parse..."

    rx_sweep_data_results_folder=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets', 'results'])
    if not os.path.exists(rx_sweep_data_results_folder):
        os.makedirs(rx_sweep_data_results_folder)

    filename_list,result_list = ParseCsvData()

    graph_list = GraphSelection(filename_list)
    print "graph list:" , graph_list

    PlotGraphs(graph_list,result_list,filename_list)



