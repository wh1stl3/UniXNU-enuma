"""Exercise residual/disconnect/reconnect traces without invoking any device API."""
from run_enuma_entry_probe import observe_fastboot_return


def main():
    cases = [([True, True, True], []),
             ([True, False, False, True], [3]),
             ([False, False, True], [2]),
             ([False, False, False], [])]
    for trace, expected in cases:
        disconnected = False
        events = []
        for index, present in enumerate(trace):
            disconnected, returned = observe_fastboot_return(present, disconnected)
            if returned:
                events.append(index)
        assert events == expected, (trace, events)
    print('PASS: residual enumeration rejected; reset-return needs disconnect then reconnect; no device I/O')


if __name__ == '__main__':
    main()
