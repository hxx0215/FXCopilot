
from module.base.button import Button, ButtonWrapper,ItemWrapper


SCHEDULER_POP_DISMISS=ButtonWrapper(
    name='SCHEDULER_POP_DISMISS',
    share=Button.default_init(
        area=(656,244,737,270),color=(37,70,85),
        file='./assets/share/rescheduler/SCHEDULE_POP_DISMISS_ENSURE.png'
    )
)
SCHEDULE_EDIT_BUTTON=ButtonWrapper(
    name='SCHEDULE_EDIT_BUTTON',
    share=Button.default_init(
        file='./assets/share/rescheduler/SCHEDULE_EDIT_BUTTON.png',
        area=(795,607,995,644),
        color=(0,104,163)
    )
)
SCHEDULE_START_BUTTON=ButtonWrapper(
    name='SCHEDULE_EDIT_BUTTON',
    share=Button.default_init(
        file='./assets/share/rescheduler/SCHEDULE_START_BUTTON.png',
        area=(800,607,993,644),
        color=(4, 124, 97)
    )
)
SCHEDULE_UPGRADE=ButtonWrapper(
    name='SCHEDULE_UPGRADE',
    share=Button.default_init(
        file='./assets/share/rescheduler/SCHEDULE_UPGRADE.png',
        area=(948,626,995,650),color=(83,144,137),
        button=(919,621,1027,658)
    )
)