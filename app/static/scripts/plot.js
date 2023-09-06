async function initPlot() {

    const plotData = await fetch('/send_initial_data')
        .then(response => { return response.json() });

    plotData['type'] = 'scatter';
    plotData['mode'] = 'line';

    const layout = {
        title: 'Test',
        xaxis: {
            title: 'X-axis',
            aspectratio: 1, // Set the aspect ratio for the x-axis
        },
        yaxis: {
            title: 'Y-axis',
            aspectratio: 1, // Set the aspect ratio for the y-axis
        },
    };
    

    Plotly.newPlot('plot-container', [plotData], layout);

    }

document.addEventListener("DOMContentLoaded", function() {
    initPlot();
});