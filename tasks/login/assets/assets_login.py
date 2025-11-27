from module.base.button import Button, ButtonWrapper

# This file was auto-generated, do not modify it manually. To generate:
# ``` python -m dev_tools.button_extract ```

ACCOUNT_CONFIRM = ButtonWrapper(
    name='ACCOUNT_CONFIRM',
    share=[
        Button(
            file='./assets/share/login/ACCOUNT_CONFIRM.png',
            area=(583, 424, 696, 450),
            search=(563, 404, 716, 470),
            color=(172, 145, 92),
            button=(583, 424, 696, 450),
        ),
        Button(
            file='./assets/share/login/ACCOUNT_CONFIRM.2.png',
            area=(602, 416, 644, 442),
            search=(582, 396, 664, 462),
            color=(180, 150, 93),
            button=(602, 416, 644, 442),
        ),
    ],
)
LOGIN_CONFIRM = ButtonWrapper(
    name='LOGIN_CONFIRM',
    share=[
        Button(
            file='./assets/share/login/LOGIN_CONFIRM.png',
            area=(1188, 44, 1220, 74),
            search=(1168, 24, 1240, 94),
            color=(140, 124, 144),
            button=(683, 327, 1143, 620),
        ),
        Button(
            file='./assets/share/login/LOGIN_CONFIRM.2.png',
            area=(1109, 48, 1139, 73),
            search=(1089, 28, 1159, 93),
            color=(149, 145, 164),
            button=(683, 327, 1143, 620),
        ),
    ],
)
LOGIN_LOADING = ButtonWrapper(
    name='LOGIN_LOADING',
    share=Button(
        file='./assets/share/login/LOGIN_LOADING.png',
        area=(1103, 599, 1119, 616),
        search=(1083, 579, 1139, 636),
        color=(98, 98, 106),
        button=(1103, 599, 1119, 616),
    ),
)

# FX
LOGIN_CONFIRM = ButtonWrapper(
    name='LOGIN_CONFIRM',
    share=Button.default_init(
        file='./assets/share/login/LOGIN_CONFIRM.png',
        area=(1191,642,1251.5,716),color=(215,177,120),
        button=(338,268,951,543)
    )
)

LOGIN_SUCCESS_DATA=ButtonWrapper(
    name='LOGIN_SUCCESS_DATA',
    share=Button.default_init(
        file='./assets/share/login/LOGIN_SUCCESS_DATA.png',
        area=(583,343.5,753,379.5),color=(118,116,111)
    )
)

LOGIN_REWARD=ButtonWrapper(
    name='LOGIN_REWARD',
    share=Button.default_init(
        area=(416,92,598,121),color=(164,135,167),
        file='./assets/share/login/LOGIN_REWARD.png',
        button=(1216,80,1261,125)
    )
)
LOGIN_NOTIFICATION=ButtonWrapper(
    name='LOGIN_NOTIFICATION',
    share=Button.default_init(
        area=(185,102,244,147),color=(184,184,184),
        file='./assets/share/login/LOGIN_NOTIFICATION.png',
        button=(1118,48,1155,84)
    )
)

LOGIN_LOADING = ButtonWrapper(
    name='LOGIN_LOADING',
    share=Button.default_init(
        area=(551,691,730,710),color=(117,121,133),
        file='./assets/share/login/LOGIN_LOADING.png'
    ),
)
NETWORK_ERROR = ButtonWrapper(
    name='NETWORK_ERROR',
    share=Button.default_init(
        area=(569,313,714,368),color=(179,179,186),
        file='./assets/share/login/NETWORK_ERROR.png',
        button=(690,425,874,468)
    )
)

SERVER_MAINTAIN = ButtonWrapper(
    name='SERVER_MAINTAIN',
    share=Button.default_init(
        area=(579,325,701,354),color=(148,148,148),
        file='./assets/share/login/SERVER_MAINTAIN.png'
    )
)
APP_UPDATE = ButtonWrapper(
    name='APP_UPDATE',
    share=Button.default_init(
        area=(501,342,777,369),color=(168,168,174),
        file='./assets/share/login/APP_UPDATE.png',
        button=(689,423,872,468)
    )
)