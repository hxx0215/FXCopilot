from module.base.button import Button, ButtonWrapper,ItemWrapper


MAINLINE_NORMAL_ACTIVE=ButtonWrapper(
    name='MAINLINE_NORMAL_ACTIVE',
    share=Button.default_init(
        area=(929,592,1066,623),color=(109,206,215),
        file='./assets/share/attack/mainline/MAINLINE_NORMAL_ACTIVE.png'
    )
)
MAINLINE_NORMAL_INACTIVE=ButtonWrapper(
    name='MAINLINE_NORMAL_INACTIVE',
    share=Button.default_init(
        area=(929,592,1055,623),color=(198,187,186),
        file='./assets/share/attack/mainline/MAINLINE_NORMAL_INACTIVE.png'
    )
)
