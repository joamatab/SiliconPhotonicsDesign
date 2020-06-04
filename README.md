# PyLum: Python Lumerical Templates 0.0.1

Create lumerical scripts from python.

Templates are based on [Textbook: Lukas Chrostowski, Michael Hochberg, "Silicon Photonics Design", Cambridge University Press 2015 ](https://github.com/lukasc-ubc/SiliconPhotonicsDesign)

It also can run the scripts using Lumerical's python API and store results locally

## Usage

See samples

## Installation

`make install`

To run using the lumapi you can set up the environment variable `PYTHONPATH` in your `~/.bashrc`


```

[ -d "/opt/lumerical/2020a" ] && export PATH=$PATH:/opt/lumerical/2020a/bin && export PYTHONPATH=/opt/lumerical/2020a/api/python
[ -d "/opt/lumerical/2019b" ] && export PATH=$PATH:/opt/lumerical/2019b/bin && export PYTHONPATH=/opt/lumerical/2019b/api/python

```
