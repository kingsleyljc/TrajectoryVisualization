<template>
  <el-container>
    <el-main>
      <div ref="map" id="map-container"></div>
    </el-main>
    <el-aside>
      <el-tabs stretch>
        <el-tab-pane label="操作栏">
          <i class="el-icon-edit-outline" id="diy"></i>
          <el-row type="flex" justify="center">
            <el-button type="warning" @click="backCenter">回到原中心位置</el-button>
          </el-row>
          <el-radio-group v-model="type" @change="typeChange">
            <el-row type="flex" justify="center">
              <el-radio :label="1">百度坐标系</el-radio>
              </el-row>
            <el-row type="flex" justify="center">
              <el-radio :label="2">wgs坐标系</el-radio>
              </el-row>
            <el-row type="flex" justify="center">
              <el-radio :label="3">gcj坐标系</el-radio>
              </el-row>
          </el-radio-group>
          <el-row type="flex">
            <el-input v-model="dir" placeholder="目录"></el-input>
            <el-button type="warning" @click="listDir">获取目录</el-button>
          </el-row>
          <el-checkbox-group
            v-model="checked"
            v-loading="loading"
            element-loading-text="加载中..."
            element-loading-spinner="el-icon-loading"
            element-loading-background="#42515e">
            <el-row v-for="file in files" :key="file" type="flex" justify="center">
              <el-checkbox :label="file" @change="checkedChange($event, file)">{{ file }}</el-checkbox>
            </el-row>
          </el-checkbox-group>
        </el-tab-pane>
        <el-tab-pane label="坐标系转换">
          <el-radio-group v-model="coord.type">
            <el-row><el-radio :label="1">百度坐标系</el-radio></el-row>
            <el-row><el-radio :label="2">wgs坐标系</el-radio></el-row>
            <el-row><el-radio :label="3">gcj坐标系</el-radio></el-row>
          </el-radio-group>
          <el-row>
            <el-input v-model="coord.lat" placeholder="lon" oninput="value=value.replace(/[^0-9.]/g,'')" />
            <el-input v-model="coord.lon" placeholder="lat" oninput="value=value.replace(/[^0-9.]/g,'')" />
            <el-button type="warning" @click="transform">转换</el-button>
          </el-row>
          <el-row v-if="coord.converted.visable">
            {{`百度坐标系: [${coord.converted[1][0]}, ${coord.converted[1][1]}]`}}
          </el-row>
          <el-row v-if="coord.converted.visable">
            {{`wgs坐标系: [${coord.converted[2][0]}, ${coord.converted[2][1]}]`}}
          </el-row>
          <el-row v-if="coord.converted.visable">
            {{`gcj坐标系: [${coord.converted[3][0]}, ${coord.converted[3][1]}]`}}
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-aside>
  </el-container>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap.js'
export default {
  name: 'Map',
  data () {
    return {
      chart: null,
      bmap: { center: [], zoom: 21, roam: true },
      series: [],
      dir: 'a',
      loading: false,
      checked: [],
      files: [],
      type: 1,
      coord: {
        type: 1,
        lat: null,
        lon: null,
        converted: { visable: false, 1: [], 2: [], 3: [] }
      }
    }
  },
  methods: {
    transform: async function () {
      try {
        await Promise.all([1, 2, 3].map(async type => {
          const res = await this.$axios({
            method: 'GET',
            url: 'http://localhost:8080',
            params: {
              transform: true,
              lat: this.coord.lat,
              lon: this.coord.lon,
              from_type: this.coord.type,
              to_type: type
            }
          })
          this.coord.converted[type] = res.data.content
        }))
        this.coord.converted.visable = true
      } catch {
        this.coord.converted.visable = false
      }
    },
    typeChange: async function () {
      for (const file of this.checked) {
        this.closeFile(file)
        await this.openFile(file)
      }
    },
    checkedChange: function (value, file) {
      if (value) {
        this.openFile(file)
      } else {
        this.closeFile(file)
      }
    },
    openFile: async function (file) {
      this.loading = true
      this.series.push({
        name: file,
        type: 'scatter',
        large: true,
        largeThreshold: 0,
        coordinateSystem: 'bmap',
        data: []
      })

      const index = this.series.findIndex((o) => o.name === file)
      const count = 500

      const res = await this.$axios({
        method: 'GET',
        url: `http://localhost:8080/${this.dir}/${file}`,
        params: { transform: false, type: 2, count, offset: 0 }
      })
      this.series[index].data = res.data.content
      this.bmap.center = res.data.content[0]

      this.chart.setOption({ bmap: this.bmap }, { replaceMerge: 'bmap' })
      this.chart.setOption({ series: this.series }, { replaceMerge: 'series' })

      const promises = []
      for (let offset = count; offset < res.data.amount; offset += count) {
        promises.push((async () => {
          const _res = await this.$axios({
            method: 'GET',
            url: `http://localhost:8080/${this.dir}/${file}`,
            params: { transform: false, type: this.type, count, offset }
          })
          Array.prototype.push.apply(this.series[index].data, _res.data.content)
          this.chart.setOption({ series: this.series }, { replaceMerge: 'series' })
        })())
      }
      await Promise.all(promises)
      this.loading = false
    },
    closeFile: function (file) {
      this.series.splice(this.series.findIndex((o) => o.name === file), 1)
      this.chart.setOption({ series: this.series }, { replaceMerge: 'series' })
    },
    backCenter: function () {
      this.centerCoords = [104.08769817540933, 30.70018619836269]
      this.chart.setOption({ bmap: this.bmap }, { replaceMerge: 'bmap' })
    },
    init: function () {
      this.bmap.center = [104.08769817540933, 30.70018619836269]
      this.chart = echarts.init(this.$refs.map, null, { useDirtyRect: true })
      this.chart.setOption({
        bmap: this.bmap,
        tooltip: {
          show: true,
          trigger: 'item',
          showContent: 'true',
          formatter: 'id:{b}\n经纬度：{c}'
        },
        series: []
      })
    },
    listDir: async function () {
      try {
        const res = await this.$axios({
          method: 'GET',
          url: `http://localhost:8080/${this.dir}`
        })
        this.files = res.data.dir
      } catch (err) {
        this.files = []
        console.log(err)
      }
    }
  },
  mounted () {
    this.init()
    this.listDir()
  },
  beforeDestroy () {}
}
</script>

<style>
#map-container {
  width: 100%;
  height: 100%;
  margin: 0;
  border-radius: 10px;
}
#diy {
  color: #9e7d60ff;
  font-size: 200%;
  margin-bottom: 10px;
}
.el-row {
  margin-bottom: 10px;
}
.loading {
  color: red;
}
.el-tag {
  margin-bottom: 6px;
  background-color: #2f4050 !important;
  color: #9e7d60ff !important;
  border-color: #9e7d60ff !important;
  font-size: 10px;
  height: 8% !important;
}
.el-pagination .btn-next,
.el-pagination .btn-prev,
.el-dialog,
.el-pager li,
.el-input-number__decrease,
.el-input-number__increase {
  background-color: #2f4050 !important;
  color: #9e7d60ff !important;
  border-color: #9e7d60ff !important;
}
.el-input__inner {
  background-color: #3f444c !important;
  color: #9e7d60ff !important;
  border-color: #9e7d60ff !important;
}
.el-input__inner:focus {
  border-color: white !important;
}
.el-button {
  margin-top: 0px !important;
  padding: 5px !important;
}
.el-button,
.el-button:focus {
  background-color: #2f4050 !important;
  color: #9e7d60ff !important;
  border-color: #9e7d60ff !important;
}
.el-button:hover,
.el-input-number__decrease:hover,
.el-input-number__increase:hover,
.el-tag:hover {
  background-color: #3f444c !important;
  color: #9e7d60ff;
  border-color: #9e7d60ff;
}
.el-tabs__active-bar {
  background-color: #9e7d60ff !important;
}
.el-loading-spinner .el-loading-text,
.el-icon-loading:before,
.el-tabs__item.is-active,
.el-tabs__item:hover {
  color: #9e7d60ff !important;
  letter-spacing: 3px;
  font-weight: bolder;
}
.el-tabs__item {
  color: #9e7d60ff !important;
  letter-spacing: 3px;
}
.situationBar {
  color: #9e7d60ff !important;
  line-height: 10px;
  letter-spacing: 2px;
}
.situationBar1 {
  display: inline-block;
  color: #9e7d60ff !important;
  line-height: 20px;
  letter-spacing: 3px;
}
</style>
