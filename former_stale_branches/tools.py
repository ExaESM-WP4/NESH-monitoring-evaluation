
import glob
import tarfile
import pandas as pd
import numpy as np
import datetime

def read_host_logs(folder, files):
    
    def process_tar_archive(tar_file_name):
        """Read logs from tar archive and assign timestamp to each row by doing file name conversion."""
        with tarfile.open(tar_file_name,'r') as tar:
            tar_log_files = tar.getnames()
            queue_log_subset = pd.concat([ pd.read_csv(tar.extractfile(log),delim_whitespace=True).assign(
                Date=datetime.datetime.strptime(log.split('.')[0],'%Y-%m-%d-%H-%M-%S')
                ) for log in tar_log_files ])
        return queue_log_subset
    
    # Obtain archive file names.
    
    tar_files = glob.glob(folder+files)
    tar_files.sort() # Not mandatory.
    
    # Read logs and assign timestamp to each row by doing file name conversion.
    
    host_logs = pd.concat([ process_tar_archive(tar_file) for tar_file in tar_files ], sort=False)
    
    # Tidy up.
    
    mask = host_logs['ExecutionHost'].str.contains('--')
    host_logs = host_logs[~mask]
    
    target_types = {
        'Free_CPUs': int,
        'Used_CPUs': int,
        'Cpu': float,
        'Load': float,
        'Free_Mem1': float,
        'Used_Mem1': float,
        'Free_Swap1': float,
        'Used_Swap1': float,
        'ExecutionHost': str,
        'QueueName': str,
    } 
    
    host_logs = host_logs.astype(target_types)
    
    # Unit conversions.
    
    # Memory units given by `qstat` are not documented.
    # A scaling factor of 2**8 yields values roughly corresponding to /proc/meminfo.
    # For inspiration see e.g. https://en.wikipedia.org/wiki/Orders_of_magnitude_(data)

    convert_these_columns = ["Free_Mem1", "Used_Mem1", "Free_Swap1", "Used_Swap1"]
    host_logs[convert_these_columns] = host_logs[convert_these_columns].multiply(1/2**8)
    
    # Index data by timestamp. (For plotting.)
    
    host_logs = host_logs.set_index('Date')

    return host_logs

def read_request_logs(folder,files):
    """Merge, clean-up and unit conversion for log file entries located in the tar files."""
    
    def process_tar_archive(tar_file_name):
        """Read logs from tar archive and drop unnecessary information."""
        with tarfile.open(tar_file_name,'r') as tar:
            tar_log_files = tar.getnames()
            log_subset = pd.concat([ pd.read_csv(tar.extractfile(log)) for log in tar_log_files ])
            log_subset["Filename"] = tar_file_name
        return log_subset
    
    # Obtain archive file names.
    
    tar_files = glob.glob(folder+files)
    tar_files.sort() # Not mandatory.
    
    # Process logs.
    
    logs = pd.concat([ process_tar_archive(tar_file) for tar_file in tar_files ], ignore_index=True)
    
    # String conversion.
    
    logs["Time"] = pd.to_datetime(logs["Time"]).dt.tz_localize(tz='Europe/Berlin').dt.round('1s') # time stamps
    logs["Elapse"] = pd.to_numeric(logs["Elapse"], errors='coerce') # elapse in seconds
    logs["CPU"] = pd.to_numeric(logs["CPU"], errors='coerce') # accumulated CPU hours
    logs["Memory"] = logs["Memory"].apply(parse_size) # memory usage in GB
    logs["Jobs"] = pd.to_numeric(logs["Jobs"], errors='coerce')
    
    return logs

# https://stackoverflow.com/questions/42865724/python-parse-human-readable-filesizes-into-bytes

#units = {"B": 1, "K": 2**10, "M": 2**20, "G": 2**30, "T": 2**40}
units = {"B": 1, "K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12}
    
def parse_size(string):
    """Parse strings and return memory in GB."""

    if len(string[:-1]) > 0:
        number, unit = float(string[:-1]), string[-1]
        return number*units[unit]/units['G']
    else:
        return np.nan