document.addEventListener("DOMContentLoaded", () => {
  // Graph 1

  const data_chart = document.getElementById("generalActivityChart");
  const graphElement = document.getElementById("actvity_graph");

  console.log(data_chart.dataset.chart);
  console.log(graphElement.dataset.chart);

  const graphData1 = JSON.parse(graphElement.dataset.chart);

  const data1 = {
    labels: graphData1.labels,
    datasets: [
      {
        label: "Activity",
        data: graphData1.values,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "#00b4d8",
      },
    ],
  };

  const config1 = {
    type: "line",
    data: data1,
    options: {
      responsive: true,
    },
  };

  new Chart(data_chart, config1);

  // Graph 2
  const data_chart2 = document.getElementById("generalBlockedAllowedChart");
  const graphElement2 = document.getElementById("blocked_allowed_graph");

  const graphData2 = JSON.parse(graphElement2.dataset.chart);

  const data2 = {
    labels: ["Allowed", "Blocked"],
    datasets: [
      {
        label: "Allowed and Blocked",
        data: [graphData2.allowed, graphData2.blocked],
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "#00b4d8",
      },
    ],
  };

  const config2 = {
    type: "doughnut",
    data: data2,
    options: {
      responsive: true,
    },
  };

  new Chart(data_chart2, config2);
});
