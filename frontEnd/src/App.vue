<template>
  <div id="app">
    <el-container style="height: 100%">
      <el-header>
        <i class="el-icon-location-outline"></i>
        CSV 轨迹点可视化
      </el-header>
      <Map></Map>
    </el-container>
    <!-- <copy></copy> -->
  </div>
</template>

<script>
import Map from './components/map'
// import copy from './components/trytable'
export default {
  name: 'App',
  components: {
    Map
  }
}
</script>

<style>
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  background-color: #3f444c;
}
.anchorBL {
  display: none;
}
.el-radio__input.is-checked+.el-radio__label{
  color: #9e7d60ff !important;
}
.el-radio__input.is-checked .el-radio__inner{
  border-color: #9e7d60ff !important;
  background: #9e7d60ff !important;
}
.el-checkbox__input.is-checked+.el-checkbox__label{
  color: #9e7d60ff !important;
}
.el-checkbox__input.is-checked .el-checkbox__inner, .el-checkbox__input.is-indeterminate .el-checkbox__inner{
  background-color:#9e7d60ff !important;
  border-color: #9e7d60ff !important;

}
.el-header {
  text-align: left;
  font-weight: bolder;
  font-size: 150%;
  letter-spacing: 2px;
  font-family: Impact, Haettenschweiler, ‘Arial Narrow Bold’, sans-serif;
}
.el-header,
.el-footer {
  background-color: #2f4050;
  color: #9e7d60ff;
  line-height: 10vh;
  border-radius: 10px;
  height: 10% !important;
}
.el-aside {
  background-color: rgb(65, 81, 95);
  border-radius: 10px;
  padding: 10px;
  width: 23% !important;
}
#app {
  width: 100%;
  height: 100%;
  margin: 0;
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
