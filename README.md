# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                               |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| custom\_components/roommind/\_\_init\_\_.py                        |      163 |       71 |     56% |45-47, 53-80, 103-104, 110-146, 155, 174-197, 237, 241-245, 255-256, 275-276 |
| custom\_components/roommind/binary\_sensor.py                      |       79 |        0 |    100% |           |
| custom\_components/roommind/climate.py                             |      472 |        1 |     99% |       711 |
| custom\_components/roommind/config\_flow.py                        |        9 |        9 |      0% |      3-23 |
| custom\_components/roommind/const.py                               |      266 |        0 |    100% |           |
| custom\_components/roommind/control/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| custom\_components/roommind/control/analytics\_simulator.py        |      243 |        2 |     99% |   86, 119 |
| custom\_components/roommind/control/direct\_valve.py               |      115 |        0 |    100% |           |
| custom\_components/roommind/control/mpc\_controller.py             |     1612 |       50 |     97% |288, 334-335, 410-411, 417-418, 430-440, 854-856, 940-947, 986-988, 1251, 2127, 2367, 2370, 2483-2485, 2510-2512, 2514-2524, 2553, 2756-2758, 2851-2853, 2878-2880, 3159, 3517, 3519, 3530, 3532, 3537, 3542, 3564, 3566 |
| custom\_components/roommind/control/mpc\_optimizer.py              |      435 |        0 |    100% |           |
| custom\_components/roommind/control/residual\_heat.py              |       48 |        0 |    100% |           |
| custom\_components/roommind/control/solar.py                       |       81 |        1 |     99% |        72 |
| custom\_components/roommind/control/thermal\_model.py              |      619 |        3 |     99% |478, 557, 1432 |
| custom\_components/roommind/coordinator.py                         |     2227 |       56 |     97% |305-306, 609-610, 619, 627-632, 641-643, 701, 801-802, 1260, 1419, 1524, 2080, 2259-2260, 2270-2271, 2273, 2985, 3053, 3082-3083, 3134, 3343, 3591-3594, 4212, 4238, 4246, 4252, 4437, 4442-4447, 4451, 4479, 4711, 4747-4748, 4842-4843, 4862, 4914-4915, 4934-4939, 4956-4957 |
| custom\_components/roommind/deprecation.py                         |       57 |        0 |    100% |           |
| custom\_components/roommind/diagnostics.py                         |      256 |        0 |    100% |           |
| custom\_components/roommind/errors.py                              |        6 |        0 |    100% |           |
| custom\_components/roommind/managers/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/managers/ac\_coil\_dry\_manager.py     |      253 |        0 |    100% |           |
| custom\_components/roommind/managers/ac\_dry\_manager.py           |      206 |        0 |    100% |           |
| custom\_components/roommind/managers/air\_quality\_manager.py      |      148 |        0 |    100% |           |
| custom\_components/roommind/managers/compressor\_group\_manager.py |      326 |        3 |     99% |171, 334, 424 |
| custom\_components/roommind/managers/cooling\_interlock.py         |       62 |        0 |    100% |           |
| custom\_components/roommind/managers/cover\_manager.py             |      227 |        0 |    100% |           |
| custom\_components/roommind/managers/cover\_orchestrator.py        |      302 |        1 |     99% |       218 |
| custom\_components/roommind/managers/dehumidifier\_manager.py      |      295 |        7 |     98% |86, 138, 143-145, 176-177 |
| custom\_components/roommind/managers/device\_setpoint\_tracker.py  |      102 |        0 |    100% |           |
| custom\_components/roommind/managers/ekf\_training\_manager.py     |       88 |        0 |    100% |           |
| custom\_components/roommind/managers/head\_offset\_tracker.py      |       67 |        2 |     97% |    97, 99 |
| custom\_components/roommind/managers/heat\_source\_observer.py     |      107 |        4 |     96% |21, 61, 75-76 |
| custom\_components/roommind/managers/heat\_source\_orchestrator.py |      126 |        2 |     98% |   69, 202 |
| custom\_components/roommind/managers/heating\_tariff.py            |       90 |        0 |    100% |           |
| custom\_components/roommind/managers/humidity\_manager.py          |       97 |        0 |    100% |           |
| custom\_components/roommind/managers/mold\_manager.py              |      106 |        1 |     99% |       105 |
| custom\_components/roommind/managers/price\_manager.py             |       87 |        0 |    100% |           |
| custom\_components/roommind/managers/recent\_temps.py              |       66 |        0 |    100% |           |
| custom\_components/roommind/managers/residual\_heat\_tracker.py    |      202 |        4 |     98% |150, 153, 222-223 |
| custom\_components/roommind/managers/room\_fan\_manager.py         |       56 |        0 |    100% |           |
| custom\_components/roommind/managers/shared\_ac\_manager.py        |      126 |        1 |     99% |        51 |
| custom\_components/roommind/managers/solar\_sensor\_manager.py     |      285 |        1 |     99% |       347 |
| custom\_components/roommind/managers/valve\_manager.py             |      115 |        0 |    100% |           |
| custom\_components/roommind/managers/weather\_manager.py           |       59 |        0 |    100% |           |
| custom\_components/roommind/managers/window\_manager.py            |       93 |        0 |    100% |           |
| custom\_components/roommind/repairs.py                             |       15 |        0 |    100% |           |
| custom\_components/roommind/sensor.py                              |       57 |        0 |    100% |           |
| custom\_components/roommind/services/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/services/analytics\_service.py         |      234 |        0 |    100% |           |
| custom\_components/roommind/services/analytics\_stats.py           |      205 |        4 |     98% |80, 109, 117, 159 |
| custom\_components/roommind/services/model\_backtest.py            |       77 |        0 |    100% |           |
| custom\_components/roommind/store.py                               |      240 |        0 |    100% |           |
| custom\_components/roommind/switch.py                              |      115 |        0 |    100% |           |
| custom\_components/roommind/utils/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| custom\_components/roommind/utils/area\_utils.py                   |       36 |        0 |    100% |           |
| custom\_components/roommind/utils/device\_utils.py                 |      201 |        0 |    100% |           |
| custom\_components/roommind/utils/history\_store.py                |      190 |        2 |     99% |   102-103 |
| custom\_components/roommind/utils/mold\_utils.py                   |       34 |        0 |    100% |           |
| custom\_components/roommind/utils/notification\_texts.py           |       14 |        0 |    100% |           |
| custom\_components/roommind/utils/notification\_utils.py           |       76 |        0 |    100% |           |
| custom\_components/roommind/utils/presence\_utils.py               |       59 |        0 |    100% |           |
| custom\_components/roommind/utils/price\_utils.py                  |      201 |        2 |     99% |   90, 176 |
| custom\_components/roommind/utils/reusable\_schedule.py            |      116 |        3 |     97% |145, 152, 168 |
| custom\_components/roommind/utils/schedule\_utils.py               |      308 |        3 |     99% |   479-481 |
| custom\_components/roommind/utils/sensor\_utils.py                 |       29 |        1 |     97% |        25 |
| custom\_components/roommind/utils/temp\_utils.py                   |       26 |        0 |    100% |           |
| custom\_components/roommind/websocket\_api.py                      |      543 |       16 |     97% |161, 796-803, 807-814, 821-828, 984, 1014, 1325-1328, 1703, 1723, 1757-1759 |
| **TOTAL**                                                          | **13155** |  **250** | **98%** |           |


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