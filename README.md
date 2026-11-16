# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                               |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| custom\_components/roommind/\_\_init\_\_.py                        |      164 |       87 |     47% |43-45, 51-86, 109-110, 116-154, 159-170, 186-209, 249, 253-257, 267-268, 287-288 |
| custom\_components/roommind/binary\_sensor.py                      |       66 |        0 |    100% |           |
| custom\_components/roommind/climate.py                             |      411 |        0 |    100% |           |
| custom\_components/roommind/config\_flow.py                        |       11 |       11 |      0% |      3-23 |
| custom\_components/roommind/const.py                               |      193 |        0 |    100% |           |
| custom\_components/roommind/control/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| custom\_components/roommind/control/analytics\_simulator.py        |      241 |        2 |     99% |   83, 115 |
| custom\_components/roommind/control/direct\_valve.py               |      115 |        0 |    100% |           |
| custom\_components/roommind/control/mpc\_controller.py             |     1488 |       33 |     98% |262, 308-309, 382-383, 389-390, 402-412, 731-733, 817-824, 1094, 1964, 2198, 2201, 2324-2333, 2348, 2791, 2923, 3280, 3282, 3293, 3295, 3300, 3305, 3327, 3329 |
| custom\_components/roommind/control/mpc\_optimizer.py              |      435 |        0 |    100% |           |
| custom\_components/roommind/control/residual\_heat.py              |       48 |        0 |    100% |           |
| custom\_components/roommind/control/solar.py                       |       81 |        1 |     99% |        72 |
| custom\_components/roommind/control/thermal\_model.py              |      619 |        3 |     99% |478, 557, 1432 |
| custom\_components/roommind/coordinator.py                         |     1757 |       51 |     97% |466-467, 475, 483-487, 496-497, 552, 648-649, 1040, 1196, 1293, 1803, 1949-1950, 1960-1961, 1963, 2621, 2682, 2711-2712, 2763, 2972, 3196-3199, 3621, 3630, 3652, 3659, 3662, 3665, 3711, 3716-3721, 3725, 3957, 3977-3985, 4005-4006, 4021-4026, 4043-4044 |
| custom\_components/roommind/deprecation.py                         |       56 |        0 |    100% |           |
| custom\_components/roommind/diagnostics.py                         |      241 |        0 |    100% |           |
| custom\_components/roommind/managers/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/managers/ac\_coil\_dry\_manager.py     |      248 |        0 |    100% |           |
| custom\_components/roommind/managers/air\_quality\_manager.py      |      128 |        0 |    100% |           |
| custom\_components/roommind/managers/compressor\_group\_manager.py |      186 |        2 |     99% |  125, 223 |
| custom\_components/roommind/managers/cooling\_interlock.py         |       62 |        0 |    100% |           |
| custom\_components/roommind/managers/cover\_manager.py             |      227 |        0 |    100% |           |
| custom\_components/roommind/managers/cover\_orchestrator.py        |      297 |        1 |     99% |       213 |
| custom\_components/roommind/managers/dehumidifier\_manager.py      |      286 |        7 |     98% |81, 133, 138-140, 171-172 |
| custom\_components/roommind/managers/device\_setpoint\_tracker.py  |      102 |        0 |    100% |           |
| custom\_components/roommind/managers/ekf\_training\_manager.py     |       88 |        0 |    100% |           |
| custom\_components/roommind/managers/head\_offset\_tracker.py      |       67 |        2 |     97% |    97, 99 |
| custom\_components/roommind/managers/heat\_source\_observer.py     |      107 |        4 |     96% |21, 61, 75-76 |
| custom\_components/roommind/managers/heat\_source\_orchestrator.py |      126 |        2 |     98% |   69, 202 |
| custom\_components/roommind/managers/heating\_tariff.py            |       90 |        0 |    100% |           |
| custom\_components/roommind/managers/mold\_manager.py              |       89 |        0 |    100% |           |
| custom\_components/roommind/managers/price\_manager.py             |       87 |        0 |    100% |           |
| custom\_components/roommind/managers/recent\_temps.py              |       66 |        0 |    100% |           |
| custom\_components/roommind/managers/residual\_heat\_tracker.py    |      202 |        4 |     98% |150, 153, 222-223 |
| custom\_components/roommind/managers/shared\_ac\_manager.py        |      126 |        1 |     99% |        51 |
| custom\_components/roommind/managers/valve\_manager.py             |      115 |        0 |    100% |           |
| custom\_components/roommind/managers/weather\_manager.py           |       59 |        0 |    100% |           |
| custom\_components/roommind/managers/window\_manager.py            |       93 |        0 |    100% |           |
| custom\_components/roommind/repairs.py                             |       15 |        0 |    100% |           |
| custom\_components/roommind/sensor.py                              |       56 |        0 |    100% |           |
| custom\_components/roommind/services/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/services/analytics\_service.py         |      228 |        0 |    100% |           |
| custom\_components/roommind/services/analytics\_stats.py           |      205 |        4 |     98% |80, 109, 117, 159 |
| custom\_components/roommind/services/model\_backtest.py            |       77 |        0 |    100% |           |
| custom\_components/roommind/store.py                               |      230 |        0 |    100% |           |
| custom\_components/roommind/switch.py                              |      114 |        0 |    100% |           |
| custom\_components/roommind/utils/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| custom\_components/roommind/utils/area\_utils.py                   |       18 |        0 |    100% |           |
| custom\_components/roommind/utils/device\_utils.py                 |      201 |        0 |    100% |           |
| custom\_components/roommind/utils/history\_store.py                |      190 |        2 |     99% |   102-103 |
| custom\_components/roommind/utils/mold\_utils.py                   |       34 |        0 |    100% |           |
| custom\_components/roommind/utils/notification\_utils.py           |       76 |        0 |    100% |           |
| custom\_components/roommind/utils/presence\_utils.py               |       49 |        0 |    100% |           |
| custom\_components/roommind/utils/price\_utils.py                  |      201 |        2 |     99% |   90, 176 |
| custom\_components/roommind/utils/reusable\_schedule.py            |      111 |        3 |     97% |135, 142, 158 |
| custom\_components/roommind/utils/schedule\_utils.py               |      279 |        3 |     99% |   425-427 |
| custom\_components/roommind/utils/sensor\_utils.py                 |       29 |        1 |     97% |        25 |
| custom\_components/roommind/utils/temp\_utils.py                   |       26 |        0 |    100% |           |
| custom\_components/roommind/websocket\_api.py                      |      498 |       15 |     97% |632-633, 637-638, 645-646, 794, 824, 1110-1115, 1454, 1473, 1500-1502 |
| **TOTAL**                                                          | **11414** |  **241** | **98%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/zomk3/roommindm/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/zomk3/roommindm/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fzomk3%2Froommindm%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.