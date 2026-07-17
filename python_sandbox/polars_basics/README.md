# Polars Basics — Ingest & Transform

A minimal Polars sandbox that reads a CSV, drops a column, and writes the result
back out. It demonstrates the idiomatic **lazy** workflow (`scan_csv` → transform
→ `sink_csv`).

## Files

| File | Purpose |
|---|---|
| `basic_ingest_transform.py` | The script: ingest → transform → output |
| `input.csv` | Sample data (a small zoo animal inventory) |
| `output.csv` | Generated result (`input.csv` with the `diet` column removed) |

## Run

```bash
cd python_sandbox/polars_basics
pip install polars
python basic_ingest_transform.py
```

You should see log output confirming the `diet` column was dropped and the file
was written to `output.csv`.

## Lazy scan in Polars

### What it is

Polars has two execution modes:

- **Eager** — `pl.read_csv(...)` reads the *entire* file into a `DataFrame` in
  memory immediately, and each subsequent operation runs one step at a time.
- **Lazy** — `pl.scan_csv(...)` returns a `LazyFrame`. Nothing is read or computed
  yet. You chain operations to build a **query plan**, and the work only happens
  when you call `.collect()` (into memory) or `.sink_csv()` (streamed to disk).

### Why it's used

When you go lazy, Polars sees the *whole* pipeline before running anything, so its
query optimizer can be smart about the work:

- **Projection pushdown** — if you only keep certain columns, Polars avoids
  reading the others from disk at all.
- **Predicate pushdown** — filters are applied as early as possible (ideally while
  reading), so less data flows through the pipeline.
- **Streaming** — `sink_csv` can process data in batches rather than holding the
  full dataset in RAM, which matters for files larger than memory.

In short: **eager is simplest for quick exploration; lazy scales and optimizes.**
Reaching for lazy by default is good practice even on small files like this one.

### Example

Eager (reads everything, then drops):

```python
import polars as pl

df = pl.read_csv("input.csv")        # full file loaded into memory now
df_cleaned = df.drop("diet")         # operates on the in-memory frame
df_cleaned.write_csv("output.csv")
```

Lazy (builds a plan, optimizes, then executes):

```python
import polars as pl

lf = pl.scan_csv("input.csv")        # nothing read yet — just a LazyFrame
lf_cleaned = lf.drop("diet")         # still nothing executed — plan only
lf_cleaned.sink_csv("output.csv")    # NOW it runs, optimized + streamed
```

You can inspect what Polars will actually do before running it:

```python
print(lf_cleaned.explain())          # shows the optimized query plan
```

Both versions produce the same `output.csv`. The lazy version simply gives the
engine room to be efficient — only reading and moving the data it truly needs.
