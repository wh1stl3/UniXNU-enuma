"""Offline decoding requires measured zero-code calibration, never a fixed baseline."""
import argparse
from run_value_probes import decode


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zero-seconds',type=float,required=True)
    p.add_argument('--seconds-per-code',type=float,default=3)
    p.add_argument('--tolerance',type=float,default=0.75)
    p.add_argument('seconds',type=float,nargs='+');a=p.parse_args()
    for seconds in a.seconds:
        print(decode(seconds,a.zero_seconds,a.seconds_per_code,a.tolerance))


if __name__=='__main__':main()
