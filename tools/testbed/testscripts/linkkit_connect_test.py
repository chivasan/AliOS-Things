import os, sys, time
from autotest import Testcase

required_devices = [ [1, 'general'] ]

def main():
    tc = Testcase('linkkit-connect')
    ap_ssid = tc.ap_ssid
    ap_pass = tc.ap_pass
    at = tc.at

    number, purpose = required_devices[0]
    [ret, result] = tc.start(number, purpose)
    if ret != 0:
        tc.stop()
        print '\nlinkkit connect test failed'
        return [ret, result]

    time.sleep(16)  #wait device boot up

    at.device_run_cmd('A', 'netmgr connect {0} {1}'.format(ap_ssid, ap_pass)) #connect device A to wifi
    responses = at.device_read_log('A', 1, 120, ['mqtt connect success!'])
    if len(responses) != 1:
        at.device_run_cmd('A', 'netmgr clear')
        time.sleep(0.5)
        at.device_control('A', 'reset')
        tc.stop()
        print '\nerror: device failed to make mqtt connection, logs:'
        tc.dump_log()
        print '\nlinkkit connect test failed'
        return [1, 'failed']

    number_of_responses = 30
    timeout = 90
    filter = ['DM Send Message, URI:', 'Publish Result: 0']
    if len(responses) == 1:
        print responses[0]
        responses = at.device_read_log('A', number_of_responses, timeout, filter)

    #disconnect device from alibaba cloud
    at.device_run_cmd('A', 'netmgr clear')  #run 'netmgr clear' command at device A
    time.sleep(0.5)
    at.device_control('A', 'reset')         #control device A, let it reboot
    tc.stop()

    ret = 0; result = 'succeed'
    if len(responses) < number_of_responses:
        print 'error: can not get {} lines of log containing {}'.format(number_of_responses, filter)
        print 'actual number of lines: {}'.format(len(responses))
        print "responses:"
        for i in range(len(responses)):
            print "  {}. {}".format(i+1, responses[i])
        ret = 1; result = 'failed'

    print '\nlogs:'
    tc.dump_log()

    print '\nmqtt connect test {}'.format(result)
    return [ret, result]

if __name__ == '__main__':
    [code, msg] = main()
    sys.exit(code)