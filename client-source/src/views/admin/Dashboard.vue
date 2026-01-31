<template>
  <div class="dashboard-container">
    <h2>System Overview</h2>
    
    <div class="charts-row">
        <a-card title="Task Completion Status" style="width: 45%">
            <v-chart class="chart" :option="pieOption" autoresize />
        </a-card>
        
        <a-card title="Weekly Task Trend" style="width: 45%">
            <v-chart class="chart" :option="barOption" autoresize />
        </a-card>
    </div>

    <a-alert 
        style="margin-top: 20px"
        type="info" 
        message="Data is currently mocked. Connect to /reports API for real aggregation." 
        show-icon 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, BarChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import api from '../../api/request';

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
]);

provide(THEME_KEY, 'light');

const pieOption = ref<any>({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '5%',
    left: 'center'
  },
  series: [
    {
      name: 'Task Status',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: []
    }
  ]
});

const barOption = ref<any>({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: [],
      axisTick: {
        alignWithLabel: true
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: 'Tasks Completed',
      type: 'bar',
      barWidth: '60%',
      data: []
    }
  ]
});

onMounted(() => {
    fetchStats();
});

async function fetchStats() {
    try {
        const res = await api.get('/stats/dashboard');
        const data = res.data;
        
        // Update Pie
        pieOption.value.series[0].data = data.pie;
        
        // Update Bar
        barOption.value.xAxis[0].data = data.bar.days;
        barOption.value.series[0].data = data.bar.counts;
        
    } catch (e) {
        console.error("Failed to load dashboard stats", e);
    }
}
</script>

<style scoped>
.dashboard-container {
    padding: 0;
}
.charts-row {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-top: 20px;
}
.chart {
  height: 300px;
  width: 100%;
}
</style>
