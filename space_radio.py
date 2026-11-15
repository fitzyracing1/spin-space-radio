"""spin-space-radio: Satellite pass time, Doppler shift, the hydrogen-line frequency, and frequency-to-band lookup"""
import sys

INTRO = (
    "spin-space-radio by Joshua Almeida.\n"
    "The calculator ships in a pull request. It will use published physical constants and clearly labeled band-name ranges, not a live TLE network.\n"
    "Sponsor: https://github.com/sponsors/fitzyracing1"
)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    print(INTRO)
    if argv and argv[0] in ("-h", "--help", "help"):
        print()
        print("Usage: python space_radio.py")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
