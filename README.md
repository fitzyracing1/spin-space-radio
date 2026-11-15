# spin-space-radio

[![Sponsor](https://img.shields.io/badge/Sponsor-fitzyracing1-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/fitzyracing1)
[![test](https://github.com/fitzyracing1/spin-space-radio/actions/workflows/test.yml/badge.svg)](https://github.com/fitzyracing1/spin-space-radio/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Satellite pass time, Doppler shift, the hydrogen-line frequency, and frequency-to-band lookup. Same input, same answer, no API, no cost, works offline.

It uses published physical constants and clearly labeled band-name ranges. It does not download TLEs or talk to a network.

```sh
python space_radio.py hydrogen
python space_radio.py hydrogen --radial-ms 21000
python space_radio.py doppler 145MHz --radial-ms 7215
python space_radio.py pass 400 --freq 145MHz
python space_radio.py period 400
python space_radio.py band 1420.405751MHz
```

Constants: speed of light 299792458 m/s (exact SI), hydrogen-line rest frequency 1420.405751 MHz, mean Earth radius 6371 km (a sphere, not a geoid), and Earth GM 3.986004418e14 m^3/s^2. Positive radial velocity means the source is receding, so the observed frequency falls. Pass time is the geometric visibility of an overhead circular-orbit pass, not a prediction for a named satellite.

Band names are commonly used ITU radio bands and IEEE Std 521 radar-letter bands, for lookup only. They are not a license, an allocation, or an official assignment.

## Run it

It's plain Python 3 with no packages to install, so it runs anywhere Python does.

```sh
gh repo clone fitzyracing1/spin-space-radio
cd spin-space-radio
python space_radio.py
python -m pytest -q
```

### Windows (PowerShell)
```powershell
winget install Python.Python.3.12 GitHub.cli
gh auth login
gh repo clone fitzyracing1/spin-space-radio; cd spin-space-radio; py space_radio.py
```

### Mac
```sh
brew install python gh && gh auth login
gh repo clone fitzyracing1/spin-space-radio && cd spin-space-radio && python3 space_radio.py
```

### Linux
```sh
sudo apt install -y python3 gh && gh auth login
gh repo clone fitzyracing1/spin-space-radio && cd spin-space-radio && python3 space_radio.py
```

### Termux (Android)
```sh
pkg install -y python git gh && gh auth login
gh repo clone fitzyracing1/spin-space-radio ~/spin-space-radio && cd ~/spin-space-radio && python space_radio.py
```

## Support this project

spin-space-radio is free and MIT licensed. If it saves you time, please [sponsor me on GitHub](https://github.com/sponsors/fitzyracing1). It keeps the tools coming.

| Plan | Price | What you get |
| --- | --- | --- |
| Free | $0 | Everything in this repo, forever |
| Pro | $49/month | Priority issues and help adding your own tools |
| Team | $199/month | Custom tools built for your team, plus Pro |

Plans are paid through [GitHub Sponsors](https://github.com/sponsors/fitzyracing1). You can also star the repo, share it, or open an issue with a tool idea.

## Author

Built by Joshua Almeida ([@fitzyracing1](https://x.com/fitzyracing1), [fitzyracing1.com](https://fitzyracing1.com), [GitHub](https://github.com/fitzyracing1)).

## License

[MIT](LICENSE) © 2026 Joshua Almeida
