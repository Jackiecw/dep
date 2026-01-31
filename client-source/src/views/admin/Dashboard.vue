<template>
  <div class="dashboard-container">
    <h2>系统总览</h2>
    
    <div class="charts-row">
        <a-card title="任务完成情况" style="width: 45%">
            <v-chart class="chart" :option="pieOption" autoresize />
        </a-card>
        
        <a-card title="本周任务趋势" style="width: 45%">
            <v-chart class="chart" :option="barOption" autoresize />
        </a-card>
    </div>

    <a-alert 
        style="margin-top: 20px"
        type="info" 
        message="数据目前为模拟数据。Phase 2 将集成真实数据聚合。" 
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
      name: '任务状态',
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
      name: '完成任务数',
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
