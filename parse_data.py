import lecroyparser as parse
import numpy as np
import matplotlib.pyplot as plt
from os import walk
from os.path import exists
from os import mkdir
from scipy import stats

#PATH = "TPC_lab/"
PATH = "alpha_v2/"
test_event = "C1--PMT-test_calibration_long--00000.trc"
output_dir = "output/"

def plot_signal_event(event_name):
    '''
    plot events that appear to have signal in them (y value much larger than the baseline)
    '''
    data = parse.ScopeData(PATH+str(event_name))
    x_vals = np.linspace(0,len(data.x), dtype = int, num = len(data.x), endpoint = True)
    #plt.plot(data.x, data.y)
    plt.plot(x_vals, data.y)
    plt.show()


def port_event(event_name):
    '''
    collect data for a singular lecroy trc file
    '''
    data = parse.ScopeData(PATH+str(event_name))
    #path = PATH+str(event_name)
    #contents = open(path, 'rb').read()
    #data = parse.ScopeData(data=contents)
    ####print("Initial data value: {}".format(data.y[25]))
    return data.y


def plot_single(test_event):
    '''
    plot single event
    '''
    data = port_event(test_event)
    print(data)
    plt.plot(data.x, data.y)
    plt.show()

    return 0

def integrate(y_data):
    '''
    collect the integral across an event by summing y components
    '''
    ####print("Baseline subtracted value: {}".format(y_data[25]))
    int_tot = np.sum(y_data)
    return(int_tot)

def ADC_plot(ADCs, bins = 100,run_no = -1):
    '''
    plot charge histogram of event with ADCs along x and events along y
    '''

    # check
    if run_no == -1:
        "Input a run_number before plotting!"
        return

    x_label = "ADC counts"
    y_label = "Counts"
    plt.hist(ADCs, bins)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title("Charge histogram")
    plt.savefig(output_dir + "RUN_" + str(run_no) + "/ADC_plot.png")
    plt.show()

def collate_ADC_data(path_dir):
    '''
    collect all the ADC value across individual events recursively
    '''
    # collect filenames
    filenames = next(walk(path_dir), (None, None, []))[2]
    print(filenames[1])
    print("Number of files: {}".format(len(filenames)))

    file_length = len(filenames)
    plot_numbers = np.linspace(0,2000002, dtype = int, num = 2000002, endpoint = True)
    display_vals = np.linspace(0,file_length, dtype = int, num = 25 )

    ADC_list = []
    for i in range(file_length):
        # integrate y axis of each event and append to ADC_list

        # breaking it down into constituent components for testing
        #plot_signal_event("C1--PMT-test_calibration_long--01934.trc")
        #print(filenames[i])
        try:
            a = port_event(filenames[i])
            #print(a)

            b = subtract_baseline(a, type = 'median')
            #print(b)

            c = integrate(b)
            #if (c < -500):
            #    print(c)
            #    plt.plot(plot_numbers,a)
            #    plt.show()

            ADC_list += (-c),

            # print when used
            if i in display_vals:
                # print progress
                print("{:.1f}% complete".format((i/len(filenames))*100))


        except:
            pass
    return ADC_list

def subtract_baseline(y_data, type = 'median'):
    '''
    remove the pedestal in singular events (quickly!)
    '''


    # convert y_data to numpy array for your own sanity
    y_data = np.array(y_data)

    # MEAN METHOD
    # add all ADC values and divide by length (rough), also remove negatives
    if (type=='mean'):
        total = (np.sum(y_data)/len(y_data))
    # MODE METHOD
    elif (type=='mode'):
        value, counts = np.unique(y_data, return_counts=True)
        m = counts.argmax()
        # counteracting mode being stupid
        #if counts[m] == 1:
        #    print("Only one count of this value, please use a different method! (Mode sucks Brais >:( ))")
        #else:
        #    total = value[m]
        total = value[m]
        ## SCIPY IS SLOW!
        ##return (stats.mode(y_data))
    # MEDIAN METHOD
    elif (type=='median'):
        total = np.median(y_data)
    else:
        print("Please input a baseline method, exiting...")
        return 0

    # return values subtracted
    return y_data - total

def main():

    #plot_signal_event(test_event)

    run_no = input("Run Number: ")

    # make directory if it doesnt exist in output directory
    if exists(output_dir+"RUN_" + str(run_no)):
        print("Directory exists! Overwriting previous data...")
    else:
        mkdir(output_dir+"RUN_" + str(run_no))


    # collect then save data
    data = collate_ADC_data(PATH)
    np.save(output_dir + "RUN_" + str(run_no) + "/ADC_data",np.array(data))


    ## load data
    #data = np.load(output_dir+"RUN_" + str(run_no) + '/ADC_data.npy')

    # hist show data
    ADC_plot(data, bins = 60, run_no = run_no)


    print("Job done!")


main()
