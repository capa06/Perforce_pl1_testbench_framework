'''
Created on 4 Aug 2013

@author: fsaracino, joashr
'''

def cfg_multilogging(log_level, log_file=""):
    """
    function enables multi way logging
    loglevel determines the messages sent to console output
    log_file, if specified, is the name of the log for debug prints

    useful information for logging
    logger.critical('This is a critical message.')
    logger.error('This is an error message.')
    logger.warning('This is a warning message.')
    logger.info('This is an informative message.')
    logger.debug('This is a low-level debug message.')

    """
    import sys
    import logging

    # Define the message format
    frmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Check if the input parameters log_level is valid
    numeric_level=getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid logging level: %s' % (log_level))


    logger = logging.getLogger()

    # severity of messages sent to the handlers
    logger.setLevel(logging.DEBUG)

    # Set up DEBUG logging to file
    if log_file:

        h_logfile=logging.FileHandler(log_file, 'w')
        h_logfile.setLevel(logging.DEBUG)
        #h_logfile.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        h_logfile.setFormatter(logging.Formatter(frmt_str))

        logger.addHandler(h_logfile)


    # Define console handler for  messages
    hc = logging.StreamHandler(sys.stdout)
    hc.setLevel(numeric_level)

    # Set a format for console messages
    hc_frmt=logging.Formatter(frmt_str)
    hc.setFormatter(hc_frmt)

    # Add handler to the root logger
    logging.getLogger('').addHandler(hc)

    return logging.getLogger('')


if __name__ == "__main__":
    import os
    import logging

    def main():
        logger=logging.getLogger('main')#

        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warning message')
        logger.error('error message')
        logger.critical('critical message')

    def test():
        logger=logging.getLogger('test')
        logger.debug("function ok?")
        logger.info("function ok")


    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    log_filename=os.path.splitext(cmdname)[0]+'.LOG'
    full_log_filename = os.sep.join(cmdpath.split(os.sep)[:]+[log_filename])

    logger=cfg_multilogging('DEBUG', full_log_filename)


    logger.info("START")

    main()
    test()
    logger.info("END")



