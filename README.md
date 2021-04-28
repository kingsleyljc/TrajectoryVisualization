
# TrajectoryVisualization轨迹点可视化与坐标系转换
Visualize trajectory points in .csv based on Baidu Map.
> - 填写本地相对目录点击获取按钮，即可显示该目录下的所有csv文件
> - 选择csv文件的原坐标系，即可自动转换为baidu坐标系并显示在百度地图中。
> - 坐标系转换支持gcj、wgs、bd坐标系之间的转换 （https://github.com/wandergis/coordTransform_py）
# Install
> 1. 先进入frontEnd文件夹，运行yarn install
> 2. 返回主目录，点击start.bat
> 3. 用浏览器打开localhost:8081
# Usage
- 将bus_track文件夹里的csv文件替换成你所需要的csv文件，或者将你的csv文件所在的文件夹复制到本目录下，即可通过输入目录名获得csv文件菜单。
# Demo
## Choose the original coordinate of the file and Select multi csv files.
![demo](https://github.com/kingsleyljc/TrajectoryVisualization/blob/main/Demo_gif/Select_csv.gif)
## Coordinate Convert 坐标系转换
### 支持gcj, wgs, bd坐标之间的转换.
![demo](https://github.com/kingsleyljc/TrajectoryVisualization/blob/main/Demo_gif/Coor_convert1.gif)
# Author
Shenzhen University.
2018151009@email.szu.edu.cn
