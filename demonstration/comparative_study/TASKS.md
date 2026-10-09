# Repository Tasks

Open only the numbered project folder, not this parent folder.
Use the identical prompt in independent WITHOUT and WITH chats.
Study task answers and results are not placed inside upstream projects.

## 01_click

Upstream: https://github.com/pallets/click/tree/934813e4d421071a1b3db3973c02fe2721359a6e

```text
Explain IntRange range validation and clamping via _NumberRangeBase.convert and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/click/types.py` / `_NumberRangeBase.convert`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 02_itsdangerous

Upstream: https://github.com/pallets/itsdangerous/tree/096c8d42545d3b68ea21a4f890fb2b2d8979c0bd

```text
Explain TimestampSigner.unsign timestamp expiry validation and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/itsdangerous/timed.py` / `TimestampSigner.unsign`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 03_markupsafe

Upstream: https://github.com/pallets/markupsafe/tree/28ace20b140d15c083e1cbc163ee6b7778ba098c

```text
Explain escape HTML special character handling and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/markupsafe/__init__.py` / `escape`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 04_blinker

Upstream: https://github.com/pallets-eco/blinker/tree/669f3a027828d19786e708b511277fabcd6b9532

```text
Explain Signal.send receiver dispatch and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/blinker/base.py` / `Signal.send`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 05_requests

Upstream: https://github.com/psf/requests/tree/0e322af87745eff34caffe4df68456ebc20d9068

```text
Explain Response.json JSON decoding and error handling and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/requests/models.py` / `Response.json`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 06_flask

Upstream: https://github.com/pallets/flask/tree/ab8149664182b662453a563161aa89013c806dc9

```text
Explain RequestContext.pop teardown and context cleanup and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/flask/ctx.py` / `RequestContext.pop`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 07_tomli

Upstream: https://github.com/hukkin/tomli/tree/73c3d102eb81fe0d2b87f905df4f740f8878d8da

```text
Explain loads TOML parsing and invalid input handling and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/tomli/_parser.py` / `loads`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 08_tomli-w

Upstream: https://github.com/hukkin/tomli-w/tree/a8f80172ba16fe694e37f6e07e6352ecee384c58

```text
Explain dumps TOML serialization and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/tomli_w/_writer.py` / `dumps`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 09_tqdm

Upstream: https://github.com/tqdm/tqdm/tree/0ed5d7f18fa3153834cbac0aa57e8092b217cc16

```text
Explain tqdm.update progress counter refresh behavior and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `tqdm/std.py` / `tqdm.update`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 10_python-dotenv

Upstream: https://github.com/theskumar/python-dotenv/tree/d6c0b9638349a7dd605d60ee555ff60421c1a594

```text
Explain load_dotenv environment overwrite behavior and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/dotenv/main.py` / `load_dotenv`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 11_schedule

Upstream: https://github.com/dbader/schedule/tree/82a43db1b938d8fdf60103bd41f329e06c8d3651

```text
Explain Scheduler.run_pending due job scheduling and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `schedule/__init__.py` / `Scheduler.run_pending`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 12_boltons

Upstream: https://github.com/mahmoud/boltons/tree/5aed99eb066f563fbad2231498492df8403a643d

```text
Explain LRI cache eviction in __setitem__ and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `boltons/cacheutils.py` / `LRI.__setitem__`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 13_packaging

Upstream: https://github.com/pypa/packaging/tree/d8e3b31b734926ebbcaff654279f6855a73e052f

```text
Explain Version initialization and InvalidVersion validation and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/packaging/version.py` / `Version.__init__`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 14_platformdirs

Upstream: https://github.com/tox-dev/platformdirs/tree/bc0405cb9c9439e6923b2dc090f91ad5daaf7dec

```text
Explain Unix.user_cache_dir XDG cache path handling and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/platformdirs/unix.py` / `Unix.user_cache_dir`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 15_filelock

Upstream: https://github.com/tox-dev/filelock/tree/c2c43e456b4369ecac8c932115e41b3addc5c3d6

```text
Explain BaseFileLock.acquire timeout and blocking behavior and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/filelock/_api.py` / `BaseFileLock.acquire`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 16_cachetools

Upstream: https://github.com/tkem/cachetools/tree/b072920d6cfb803be7dbbc7eafd9adc61c5c3cbd

```text
Explain TTLCache item expiry in __getitem__ and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/cachetools/__init__.py` / `TTLCache.__getitem__`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 17_python-slugify

Upstream: https://github.com/un33k/python-slugify/tree/f85f9488520148d5f6899b5639199882b605e30a

```text
Explain slugify text normalization and truncation and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `slugify/slugify.py` / `slugify`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 18_more-itertools

Upstream: https://github.com/more-itertools/more-itertools/tree/1681cea3cd8fd1bfce41ac5db3987ae919d51b84

```text
Explain chunked_even balanced iterable grouping and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `more_itertools/more.py` / `chunked_even`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 19_python-semver

Upstream: https://github.com/python-semver/python-semver/tree/486e4897da9fa6f02e1392bbf24d2f69599f0970

```text
Explain Version.bump_patch semantic version incrementing and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `src/semver/version.py` / `Version.bump_patch`.

Define your supported-behavior checklist from source/tests before scoring either answer.

## 20_tenacity

Upstream: https://github.com/jd/tenacity/tree/a662bbb487cd6d34541824589f8e8c7a1f7791bb

```text
Explain stop_after_attempt retry attempt limits and its related tests. Do not modify any files.
Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.
```

Target for human verification: `tenacity/stop.py` / `stop_after_attempt.__call__`.

Define your supported-behavior checklist from source/tests before scoring either answer.
