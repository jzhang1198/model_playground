function createSlider(sliderData) {

    /**
     * Builds a slider from input data
     *
     * @param {JSON} sliderData - Slider data in JSON format.
     * @returns A container for slider and labels.
     */

    const { name, scale, min, max, initial_value, stepsize } = sliderData;

    // Generate labels
    const nameLabel = document.createElement('div');
    nameLabel.innerHTML = `<span id="${name}-label">${name}</span>`;
    const valueLabel = document.createElement('div');
    valueLabel.innerHTML = `<span id="${name}-value-label">${initial_value}</span>`;

    // Create the slider
    const slider = document.createElement('input');
    slider.id = `${name}-slider`;
    slider.classList.add('slider', scale);
    slider.type = 'range';

    const setSliderAttributes = () => {
        if (slider.classList.contains('log')) {
            slider.min = Math.log10(min).toString();
            slider.max = Math.log10(max).toString();
            slider.value = Math.log10(initial_value).toString();
        } else {
            slider.min = min.toString();
            slider.max = max.toString();
            slider.value = initial_value.toString();
        }
        slider.step = stepsize.toString();
    };

    setSliderAttributes();

    slider.addEventListener('input', async function() {

        // Transform value, if applicable
        let value;
        if (slider.classList.contains('log')) {
            value = Math.pow(10, slider.value);
            valueLabel.innerHTML = value;
        } else {
            // Update label
            value = slider.value;
            valueLabel.innerHTML = value;
        }

        const paramName = slider.id.split('-')[0];
        const paramValue = value;
        

        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ paramName: paramName, paramValue: paramValue })
        }

        const data = fetch('/send_data', requestOptions)
        .then(response => { return response.json() })
        .then(data => { return data.data });
    
        // Plotly.update('plot-container', { y: [data]});

    });

    return {slider: slider, nameLabel: nameLabel, valueLabel: valueLabel}
};

function createSettingsMenu(sliderData, slider, valueLabel) {
    const { name, scale, min, max, initial_value, value } = sliderData;

    // Dynamically generate HTML strings for menu components
    const scaleButton = `<button class="scale-button">${scale}</button>`;
    const fieldLabels = ['min', 'max', 'stepsize', 'initial_value']
        .map(field => {

            const reformattedField = field.replace('_', ' ');

            const fieldLabel = `
            <span class="field-label">${reformattedField}</span>
            `;

            return fieldLabel;
        }).join('');

    const fields = ['min', 'max', 'stepsize', 'initial_value']
        .map(field => {
            const fieldValue = sliderData[field];

            const inputField = `
            <input class="${field}-field" value="${fieldValue}" />
            `;
            return inputField;
        }).join('');

    const submitButton = `<button class="submit-button">Submit</button>`;

    // Generate the settings menu HTML element
    const settingsMenu = document.createElement('div');
    settingsMenu.classList.add('settings-menu', 'hidden');
    settingsMenu.innerHTML = `
        ${scaleButton}
        <div class="field-container">
            <div class="field-labels">${fieldLabels}</div>
            <div class="fields">${fields}</div>
        </div>
        ${submitButton}
    `;

    const scaleButtonElement = settingsMenu.querySelector(`.scale-button`);
    const minFieldElement = settingsMenu.querySelector(`.min-field`);
    const maxFieldElement = settingsMenu.querySelector('.max-field');
    const stepsizeFieldElement = settingsMenu.querySelector('.stepsize-field');
    const initialValueFieldElement = settingsMenu.querySelector('.initial_value-field');
    const submitButtonElement = settingsMenu.querySelector('.submit-button')

    scaleButtonElement.addEventListener('click', () => {
        if (scaleButtonElement.innerHTML === 'log') {
            scaleButtonElement.innerHTML = 'linear';
        } else {
            scaleButtonElement.innerHTML = 'log';
        }
    });
    

    submitButtonElement.addEventListener('click', () => {
        const min = parseFloat(minFieldElement.value);
        const max = parseFloat(maxFieldElement.value);
        const updatedValue = parseFloat(initialValueFieldElement.value);

        if (min > max || updatedValue < min || updatedValue > max) {
            // Display error
            console.log('Invalid values');
            return;
        }

        if (slider.classList.contains('linear')) {
            slider.classList.remove('linear');
            slider.classList.add(scaleButtonElement.innerHTML);
        } else {
            slider.classList.remove('log');
            slider.classList.add(scaleButtonElement.innerHTML);
        }

        slider.step = stepsizeFieldElement.value;
        slider.min = slider.classList.contains('log')
            ? Math.log10(min).toString()
            : min.toString();
        slider.max = slider.classList.contains('log')
            ? Math.log10(max).toString()
            : max.toString();
        slider.value = slider.classList.contains('log')
            ? Math.log10(updatedValue).toString()
            : updatedValue.toString();
        valueLabel.innerHTML = updatedValue;

        settingsMenu.style.display = 'none';

    });

    return settingsMenu;

}

async function init() {

    /* 
    NOTE: in the context of the entire program, the plots are initialized first.
    */

    const sliderDatas = await fetch('/send_slider_data')
        .then(response => { return response.json() });

    console.log(sliderDatas);

    // Collect all necessary containers
    const nameLabelsContainer = document.getElementById('name-labels');
    const slidersContainer = document.getElementById('sliders');
    const valueLabelsContainer = document.getElementById('value-labels');
    const settingsButtonsContainer = document.getElementById('settings-buttons');

    // Init sliders
    sliderDatas.forEach(sliderData => {

        // Create slider and corresponding dashboard panel
        const {slider, nameLabel, valueLabel} = createSlider(sliderData);

        // Create the settings menu
        const settingsMenu = createSettingsMenu(sliderData, slider, valueLabel);

        // Create a corresponding settings button
        const settingsButton = document.createElement('button');
        settingsButton.innerHTML = 'Settings';
        settingsButton.classList.add('settings-button');
        settingsButton.addEventListener('click', (event) => {

            if (!settingsMenu.contains(event.target)) {
                settingsMenu.style.display = "flex";
            }
        })

        document.addEventListener('click', (event) => {
            if (!settingsMenu.contains(event.target) && event.target !== settingsButton) {
                settingsMenu.style.display = 'none';
            }
        });

        // Add elements to their corresponding containers
        nameLabelsContainer.appendChild(nameLabel);
        valueLabelsContainer.appendChild(valueLabel);
        slidersContainer.appendChild(slider);
        settingsButton.appendChild(settingsMenu);
        settingsButtonsContainer.appendChild(settingsButton);

        // Ensure that settings menus are hidden as default
        settingsMenu.style.display = 'none';

    })

}

document.addEventListener("DOMContentLoaded", function() {
    init();
});