# conda
## Download 
https://www.anaconda.com/

## Install
bash Miniconda3-latest-Linux-x86_64.sh

**Install Miniconda (recommended — lightweight)**
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Follow the prompts — accept the license, confirm install location (default `~/miniconda3` is fine), and say **yes** when asked to initialize conda.

**Then reload your shell:**
```bash
source ~/.bashrc
```

**Verify:**
```bash
conda --version
```

---

If you'd prefer the full Anaconda distribution (includes many pre-installed packages but ~3GB):
```bash
wget https://repo.anaconda.com/archive/Anaconda3-latest-Linux-x86_64.sh
bash Anaconda3-latest-Linux-x86_64.sh
```

Miniconda is usually the better choice — you install only what you need.
