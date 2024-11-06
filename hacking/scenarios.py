import client

chandelier_lights = [
    'ab3ac36c-6320-4b8d-ade5-1a18e9d4a1b4',
    '7db7d247-7ccb-496c-978d-641ec22e99e2',
    '891b0fb8-58d8-4d22-83f9-97933ba59c89',
    'd0e8d126-64ad-4efa-8a9c-53da0096bbeb',
    'b06bf1f5-dfb2-46a6-bc97-5f189c5e6633',
    'f3f23118-7a48-4d87-96ef-171f02c8229f',
]
torchere_lights = [
    '3d8e71d4-cea7-47ec-8cbf-19bd69a9fd7d',
]
sink_lights = [
    '78eef81b-fd07-47b7-9882-9d245c48efc0',
]
bath_lights = [
    '6e82160f-a0d8-43a9-9ab5-3e2b3470874d',
    'dedc0b80-b863-4d4d-81f9-c3cc17317e35',
]
toilet_lights = [
    '2a892eab-f2c2-4dc8-8c18-1319624ad1f7',
]

rgb_lights = chandelier_lights + torchere_lights + bath_lights + toilet_lights

var_light_state = '4e1d6fae-548c-427f-887f-3211456dc746'
var_light_state_ro = '225e22b8-65cd-487c-a5c9-a2d9c1a9ec5d'
var_movement = '8d17f1e6-1f82-48b1-9030-86ac74af1192'
var_talking = 'd7435697-37bb-4e6c-8542-988496cdeb9a'
var_is_night = '2e5ea4d0-6d84-41b3-8491-85a6e2d7a5a5'
var_is_morning = '1c21d753-7281-42ee-8793-89d43b59bb97'
var_is_morning_ro = '65b8aa45-c466-4785-8b09-c9e44d3bc138'

station_max = '2f515a47-4797-4255-ba69-f079c9d9c36e'

all_lights = chandelier_lights + torchere_lights + sink_lights + bath_lights + toilet_lights + [var_light_state]
night_lights_off = chandelier_lights + torchere_lights + sink_lights
night_lights_on = chandelier_lights + torchere_lights + bath_lights + toilet_lights

night_time = dict(
    start_time_offset=72000,
    end_time_offset=85500,
    duration=13500,
    days_of_week=[
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]
)

dev_button = "260d5253-7a1b-4843-8a4c-bacfbc558fd3"


def make_sound(dev_id, sound='switch-1'):
    return dict(
        id=dev_id,
        capabilities=[dict(
            type='devices.capabilities.quasar',
            state=dict(
                instance='sound_play',
                value=dict(
                    sound=sound
                )
            ),
        )]
    )


def do_set_on_off(dev_id, is_on, *, relative=False, color: str = None, brightness: int = None):
    if color is None:
        color = "daylight"
    if color == 'fiery_white' and dev_id not in chandelier_lights:
        color = 'daylight'
    if brightness is None:
        brightness = 100
    capabilities = [
        dict(
            type="devices.capabilities.on_off",
            state=dict(
                instance="on",
                relative=relative,
                value=is_on,
            )
        ),
    ]
    if is_on and dev_id in rgb_lights:
        capabilities.extend([
            dict(
                type="devices.capabilities.color_setting",
                state=dict(
                    instance="color",
                    value=color
                )
            ),
            dict(
                type="devices.capabilities.range",
                state=dict(
                    instance="brightness",
                    value=brightness
                )
            )
        ])
    return dict(
        id=dev_id,
        capabilities=capabilities,
    )


def on_button(btn_id, *values):
    return dict(
        type='scenario.trigger.property',
        value=dict(
            device=dict(id=btn_id),
            property_type='devices.properties.event',
            instance='button',
            condition=dict(values=values),
            skill_id='YAINDEX_IO',
        ),
    )


def on_command(text):
    return dict(
            type="scenario.trigger.voice",
            value=text,
    )


def on_on_off(lights_id, is_on):
    return dict(
        type='scenario.trigger.capability',
        value=dict(
            device_id=lights_id,
            capability_type='devices.capabilities.on_off',
            capability_instance='on',
            condition=dict(
                values=[is_on],
            )
        ),
    )


def test_on_off(lights_id, is_on):
    return dict(
        type='scenario.filter.capability',
        value=dict(
            device_id=lights_id,
            capability_type='devices.capabilities.on_off',
            capability_instance='on',
            condition=dict(
                values=[is_on],
            )
        ),
    )


def turn_off_lights_long_press():
    return dict(
        icon='off',
        name='Выключить свет кнопкой',
        triggers=[
            dict(trigger=on_button(dev_button, 'long_press'))
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(dev_id, False) for dev_id in all_lights]
                )
            ),
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


def turn_on_lights_double_click():
    return dict(
        icon='on',
        name='Включить свет кнопкой',
        triggers=[
            dict(trigger=on_button(dev_button, 'double_click'))
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(dev_id, True) for dev_id in all_lights]
                )
            ),
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


def toggle_lights_off():
    return dict(
        icon='toggle',
        name='Выключить общий свет',
        triggers=[
            dict(
                trigger=on_command('Выключи общий свет'),
            ),
            dict(
                trigger=on_button(dev_button, 'click'),
                filters=[test_on_off(var_light_state_ro, True)]
            ),
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(dev_id, False) for dev_id in all_lights]
                )
            )
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


def toggle_lights_on():
    return dict(
        icon='toggle',
        name='Включить общий свет',
        triggers=[
            dict(
                trigger=on_button(dev_button, 'click'),
                filters=[test_on_off(var_light_state_ro, False)]
            ),
            dict(
                trigger=on_command('Включи общий свет'),
            )
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(dev_id, True) for dev_id in all_lights]
                )
            )
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


def toggle_night_lights_off():
    return dict(
        icon='toggle',
        name='Выключить свет ночью',
        effective_time=night_time,
        triggers=[
            dict(
                trigger=on_on_off(var_is_morning_ro, False),  # только если утро закончилось
                filters=[test_on_off(var_talking, False),
                         test_on_off(var_movement, False)]
            ),
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=(
                            [do_set_on_off(dev_id, False) for dev_id in night_lights_off + [var_light_state]]
                            + [do_set_on_off(var_is_night, True)]  # Началась ночь
                    )
                )
            )
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


def toggle_night_lights_on():
    return dict(
        icon='toggle',
        name='Включить свет утром',
        triggers=[
            dict(
                trigger=on_on_off(var_movement, True),
                filters=[test_on_off(var_is_night, True)]  # только по утрам
            ),
            dict(
                trigger=on_on_off(var_talking, True),
                filters=[test_on_off(var_is_night, True)]  # только по утрам
            )
        ],
        steps=[
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(var_is_night, False)]  # закончилась ночь
                )
            ),
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(var_is_morning, True)]  # наступило утро
                )
            ),
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=(
                        [do_set_on_off(dev_id, True, color='fiery_white', brightness=10)
                         for dev_id in night_lights_on]
                    )
                )
            ),
            dict(
                type="scenarios.steps.delay",
                parameters=dict(delay_ms=15 * 60 * 1000)  # если свет был включен утром, то не выключаем его ещё 15 минут
            ),
            dict(
                type='scenarios.steps.actions',
                parameters=dict(
                    launch_devices=[do_set_on_off(var_is_morning, False)]  # утро закончилось, теперь может начаться ночь
                )
            ),
        ],
        settings=dict(
            continue_execution_after_error=True
        )
    )


print(repr(client.put_scenario('7a320b3c-108f-4321-b9f8-2279719e2b66', turn_off_lights_long_press())))
print(repr(client.put_scenario('1d93e611-489b-43c0-8a90-b0d17fe50169', turn_on_lights_double_click())))
print(repr(client.put_scenario('80d5a0bb-29a3-46ed-b329-6be3cf50c4ca', toggle_lights_off())))
print(repr(client.put_scenario('039c8629-2345-470e-8a0b-6db1e7775928', toggle_lights_on())))
print(repr(client.put_scenario('4824ee29-6c7e-459f-9708-6f92d60c6df9', toggle_night_lights_off())))
print(repr(client.put_scenario('ccd8fc04-7159-4f4e-902d-7e91ead460de', toggle_night_lights_on())))

