async function fetchPlotData() {
    try {
        const response = await fetch('/serve_plot_data');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const plotData = await response.json();
        console.log(plotData); // Use the data here
        return plotData;
    } catch (error) {
        console.error('Error fetching slider data:', error);
        return null;
    }
}

async function initPlot() {

    const plotData = await fetchPlotData();

    Plotly.newPlot('plot-container', plotData['traces'], plotData['layout']);

}