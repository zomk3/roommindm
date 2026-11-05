# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/zomk3/roommindm/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                               |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| custom\_components/roommind/\_\_init\_\_.py                        |      138 |       79 |     43% |39-41, 47-71, 94-95, 101-139, 144-155, 171-194, 205, 209-213, 223-224, 242-243 |
| custom\_components/roommind/binary\_sensor.py                      |       38 |        0 |    100% |           |
| custom\_components/roommind/climate.py                             |      420 |        0 |    100% |           |
| custom\_components/roommind/config\_flow.py                        |       11 |       11 |      0% |      3-23 |
| custom\_components/roommind/const.py                               |      158 |        0 |    100% |           |
| custom\_components/roommind/control/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| custom\_components/roommind/control/analytics\_simulator.py        |      232 |        2 |     99% |   81, 113 |
| custom\_components/roommind/control/direct\_valve.py               |      115 |        0 |    100% |           |
| custom\_components/roommind/control/mpc\_controller.py             |     1372 |       33 |     98% |234, 280-281, 353-354, 360-361, 373-383, 701-703, 721-722, 786-793, 1029, 1991, 1994, 2115-2124, 2139, 2558, 3032, 3034, 3045, 3047, 3052, 3057, 3079, 3081 |
| custom\_components/roommind/control/mpc\_optimizer.py              |      306 |        0 |    100% |           |
| custom\_components/roommind/control/residual\_heat.py              |       34 |        0 |    100% |           |
| custom\_components/roommind/control/solar.py                       |       81 |        1 |     99% |        72 |
| custom\_components/roommind/control/thermal\_model.py              |      480 |       17 |     96% |434, 943-951, 1069, 1198, 1205-1209 |
| custom\_components/roommind/coordinator.py                         |     1213 |       53 |     96% |337-338, 451-452, 1171-1172, 1182, 1184, 1724, 1775, 1803-1804, 1855, 2215-2218, 2465-2467, 2471-2477, 2481, 2490, 2512, 2517, 2519, 2522, 2525, 2569, 2574-2579, 2583, 2623, 2625, 2628, 2631, 2657-2658, 2774, 2794-2802, 2820-2821, 2836-2841, 2858-2859 |
| custom\_components/roommind/deprecation.py                         |       56 |        0 |    100% |           |
| custom\_components/roommind/diagnostics.py                         |      231 |        0 |    100% |           |
| custom\_components/roommind/managers/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/managers/ac\_coil\_dry\_manager.py     |      248 |        0 |    100% |           |
| custom\_components/roommind/managers/compressor\_group\_manager.py |      186 |        2 |     99% |  125, 223 |
| custom\_components/roommind/managers/cover\_manager.py             |      204 |        0 |    100% |           |
| custom\_components/roommind/managers/cover\_orchestrator.py        |      243 |        2 |     99% |   85, 197 |
| custom\_components/roommind/managers/dehumidifier\_manager.py      |      267 |        7 |     97% |81, 128, 133-135, 156-157 |
| custom\_components/roommind/managers/ekf\_training\_manager.py     |       71 |        1 |     99% |        38 |
| custom\_components/roommind/managers/head\_offset\_tracker.py      |       67 |        2 |     97% |    97, 99 |
| custom\_components/roommind/managers/heat\_source\_orchestrator.py |      123 |        2 |     98% |   71, 211 |
| custom\_components/roommind/managers/mold\_manager.py              |       74 |        0 |    100% |           |
| custom\_components/roommind/managers/residual\_heat\_tracker.py    |       69 |        0 |    100% |           |
| custom\_components/roommind/managers/valve\_manager.py             |      112 |        0 |    100% |           |
| custom\_components/roommind/managers/weather\_manager.py           |       59 |        0 |    100% |           |
| custom\_components/roommind/managers/window\_manager.py            |       93 |        0 |    100% |           |
| custom\_components/roommind/repairs.py                             |       15 |        0 |    100% |           |
| custom\_components/roommind/sensor.py                              |       55 |        0 |    100% |           |
| custom\_components/roommind/services/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| custom\_components/roommind/services/analytics\_service.py         |      171 |        0 |    100% |           |
| custom\_components/roommind/store.py                               |      184 |        0 |    100% |           |
| custom\_components/roommind/switch.py                              |       94 |        0 |    100% |           |
| custom\_components/roommind/utils/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| custom\_components/roommind/utils/area\_utils.py                   |       18 |        0 |    100% |           |
| custom\_components/roommind/utils/device\_utils.py                 |      201 |        0 |    100% |           |
| custom\_components/roommind/utils/history\_store.py                |      146 |        2 |     99% |     62-63 |
| custom\_components/roommind/utils/mold\_utils.py                   |       36 |        0 |    100% |           |
| custom\_components/roommind/utils/notification\_utils.py           |       50 |        0 |    100% |           |
| custom\_components/roommind/utils/presence\_utils.py               |       49 |        0 |    100% |           |
| custom\_components/roommind/utils/schedule\_utils.py               |      209 |        0 |    100% |           |
| custom\_components/roommind/utils/sensor\_utils.py                 |       29 |        1 |     97% |        25 |
| custom\_components/roommind/utils/temp\_utils.py                   |       26 |        0 |    100% |           |
| custom\_components/roommind/websocket\_api.py                      |      350 |        9 |     97% |517-518, 522-523, 530-531, 651, 891-896 |
| **TOTAL**                                                          | **8334** |  **224** | **97%** |           |


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