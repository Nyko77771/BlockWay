document.addEventListener('DOMContentLoaded', () => {
    const data_chart = document.getElementById('generalActivityChart');
    const graphElement = document.getElementById('graph-data');

    console.log(data_chart.dataset.chart);
    console.log(graphElement.dataset.chart);

    const graphData1 = JSON.parse(graphElement.dataset.chart)

    const data = {
    labels: graphData1.labels,
    datasets: [
        {
        label: "Activity",
        data: graphData1.values,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgb(75, 192, 192)",
        },
    ],
    };

    const config = {
        type: "line",
        data: data,
        options: {
            responsive: true,
        }
    };

    new Chart(
        data_chart,
        config
    );
})