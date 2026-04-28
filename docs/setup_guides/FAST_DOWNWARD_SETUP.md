# Fast Downward Setup

Clone and build Fast Downward:

```bash
git clone https://github.com/aibasel/downward.git
cd downward
./build.py
./fast-downward.py --help
```

Then set:

```env
FAST_DOWNWARD_PATH=/absolute/path/to/downward/fast-downward.py
```

Open LaMMA-R falls back to a deterministic heuristic plan if Fast Downward is missing.

