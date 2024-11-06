// ==UserScript==
// @name         Yandex IOT syncer
// @namespace    http://tampermonkey.net/
// @version      2024-11-06
// @description  try to take over the world!
// @author       You
// @match        https://yandex.ru/iot/*
// @icon         https://yandex.ru/iot
// @grant        none
// @require      https://unpkg.com/js-yaml@4.1.0/dist/js-yaml.min.js
// ==/UserScript==

(function () {
    'use strict';

    function convertTrigger(trigger, devices) {
        return {
            trigger: convertCondition(trigger, devices),
            filters: trigger.when.map(condition => convertFilter(condition, devices))
        };
    }

    function convertCondition(condition, devices) {
        return {
            type: 'scenario.filter.capability',
            value: {
                device_id: devices[condition.device] || condition.device,
                capability_type: 'devices.capabilities.on_off',
                capability_instance: 'on',
                condition: {
                    values: [condition.is == 'on']
                },
            }
        };
    }

    function convertStep(step, devices) {
        return {
            type: 'scenarios.steps.actions.v2',
            parameters: {
                items: step.device.map(deviceId => ({
                    id: devices[deviceId] || deviceId,
                    type: 'step.action.item.device',
                    value: {
                        id: devices[deviceId] || deviceId,
                        capabilities: [{
                            type: 'devices.capabilities.on_off',
                            state: {
                                instance: 'on',
                                value: step.turn == 'on',
                                relative: false
                            },
                        }],
                    }
                }))
            }
        };
    }

    function convertScenario(input, devices) {
        const scenario = {
            id: input.id,
            name: input.name,
            triggers: input.triggers.map(trigger => convertTrigger(trigger, devices)),
            steps: input.steps.map(step => convertStep(step, devices)),
            icon: input.icon,
            settings: input.settings,
            effective_time: {
                start_time_offset: convertTimeToSeconds(input.time.start) - 3 * 3600,
                end_time_offset: convertTimeToSeconds(input.time.end) - 3 * 3600,
                days_of_week: input.time.days_of_week,
                duration: computeDuration(input.time.start, input.time.end)
            },
        };

        return scenario;
    }

    function convertTimeToSeconds(time) {
        const [hours, minutes] = time.split(':').map(Number);
        return hours * 3600 + minutes * 60;
    }

    function computeDuration(start, end) {
        if (start > end) {
            end += 24 * 3600;
        }
        return convertTimeToSeconds(end) - convertTimeToSeconds(start);
    }

    function waitForElm(selector) {
        return new Promise(resolve => {
            if (document.querySelector(selector)) {
                return resolve(document.querySelector(selector));
            }

            const observer = new MutationObserver(mutations => {
                if (document.querySelector(selector)) {
                    observer.disconnect();
                    resolve(document.querySelector(selector));
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }

    async function putScenario(scenario) {
        await fetch(`https://iot.quasar.yandex.ru/m/v4/user/scenarios/${scenario.id}`, {
            "credentials": "include",
            "headers": {
                "x-csrf-token": window.storage.csrfToken2
            },
            "body": JSON.stringify(scenario),
            "method": "PUT",
            "mode": "cors"
        });
    }

    async function onclick() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.yaml';
        fileInput.style.display = 'none';

        // Add an event listener to handle file selection
        fileInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    try {
                        const json = jsyaml.load(e.target.result);
                        console.log(json);
                        for (let s of json.scenarios) {
                            putScenario(convertScenario(s, json.devices));
                        }
                    } catch (error) {
                        console.error('Error parsing JSON:', error);
                    }
                };
                reader.readAsText(file);
            }
        });

        fileInput.click();
    }

    waitForElm('.iot-news-feed__content').then((root) => {
        var element = document.createElement("button");
        element.appendChild(document.createTextNode("Загрузить сценарии"));
        root.appendChild(element);
        element.onclick = () => onclick();
    });
})();