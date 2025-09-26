# alita

To install pyaudio on macOS, you may need to install portaudio first. You can do this using Homebrew:
```bash
brew install portaudio
pip install pyaudio --global-option='build_ext' --global-option="-I/opt/homebrew/include" --global-option="-L/opt/homebrew/lib"
```