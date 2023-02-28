#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
import math
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPixmap, QPen
from PyQt5.QtCore import QRectF,QRect,QDir,QPoint,QSize,Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.pre_x=0
        self.pre_y=0
        self.outline = None

        self.pen_color=QColor(0, 0, 0)
        self.pen_size=3
    
    def error_finish_draw(self):
        if self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is not None:
                self.temp_item=None

    def start_draw_line(self, algorithm, item_id):
        self.error_finish_draw()
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_polygon(self,algorithm,item_id):
        self.error_finish_draw()
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_ellipse(self,item_id):
        self.error_finish_draw()
        self.status = 'ellipse'
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_curve(self,algorithm,item_id):
        self.error_finish_draw()
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_free(self,item_id):
        self.error_finish_draw()
        self.status = 'free'
        self.temp_id = item_id
        self.temp_item = None

    def start_translate(self):
        self.error_finish_draw()
        self.status = 'translate'
        self.temp_id = self.selected_id

    def start_rotate(self):
        self.error_finish_draw()
        self.status = 'rotate'
        self.temp_id = self.selected_id

    def start_scale(self):
        self.error_finish_draw()
        self.status = 'scale'
        self.temp_id = self.selected_id

    def start_clip(self, algorithm):
        self.error_finish_draw()
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_id = self.selected_id

    def set_pen_color(self,new_color):
        self.pen_color = new_color

    def set_pen_size(self,new_size):
        self.pen_size = new_size

    def start_draw(self):
        self.temp_id = self.main_window.get_id()

    def finish_draw(self):
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])
    
    def reset_canvas(self):
        self.clear_selection()
        self.item_dict = {}
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.pen_color=QColor(0, 0, 0)
        self.pen_size=3

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.start_draw()
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color,self.pen_size)
            self.scene().addItem(self.temp_item)
            self.finish_draw()
        elif self.status == 'ellipse':
            self.start_draw()
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], '',self.pen_color,self.pen_size)
            self.scene().addItem(self.temp_item)
            self.finish_draw()
        elif self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is None:
                self.start_draw()
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.pen_color,self.pen_size)
                self.scene().addItem(self.temp_item)
                self.finish_draw()
            else:
                if event.button() == Qt.RightButton:
                    self.temp_item = None
                else:
                    self.temp_item.p_list.append([x, y])
        elif self.status == 'free':
            self.start_draw()
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.pen_color,self.pen_size)
            self.scene().addItem(self.temp_item)
            self.finish_draw()
        elif self.status == 'translate' or self.status == 'scale':
            if self.selected_id in self.item_dict:
                self.temp_id = self.selected_id
                self.temp_item = self.item_dict[self.selected_id]
                self.pre_x, self.pre_y = x, y
            else:
                self.status=''
        elif self.status == 'rotate':
            if self.selected_id in self.item_dict and self.item_dict[self.selected_id].item_type != 'ellipse':
                self.temp_id = self.selected_id
                self.temp_item = self.item_dict[self.selected_id]
                self.pre_x, self.pre_y = x, y
            else:
                self.status=''
        elif self.status == 'clip':
            if self.selected_id in self.item_dict and self.item_dict[self.selected_id].item_type == 'line':
                self.temp_id = self.selected_id
                self.temp_item = self.item_dict[self.temp_id]
                self.pre_x, self.pre_y = x, y
                self.outline = MyItem(-1, 'outline', [[x, y], [x, y]], 'outline', QColor(192, 192, 192))
                self.scene().addItem(self.outline)
            else:
                self.status=''
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'free':
            self.temp_item.p_list.append([x, y])
        elif self.status == 'translate':
            self.temp_item.item_translate(x-self.pre_x,y-self.pre_y)
            self.pre_x,self.pre_y = x, y
        elif self.status == 'rotate':
            self.temp_item.item_rotate(x,y,self.pre_x,self.pre_y)
            self.pre_x,self.pre_y = x, y
        elif self.status == 'scale':
            self.temp_item.item_scale(x,y,self.pre_x,self.pre_y)
            self.pre_x,self.pre_y = x, y
        elif self.status == 'clip':
            self.outline.p_list[1] = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'clip':
            self.scene().removeItem(self.outline)
            self.temp_item.item_clip(self.pre_x,self.pre_y,x,y,self.temp_algorithm)
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '',pen_color=QColor(0, 0, 0),pen_size=3, parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.pen_color=pen_color
        self.pen_size=pen_size

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:       
        painter.setPen(QPen(self.pen_color,self.pen_size))
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                p=[round(p[0]),round(p[1])]
                painter.drawPoint(*p)
        elif self.item_type == 'polygon':
            if len(self.p_list)>1:
                item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
                for p in item_pixels:
                    p=[round(p[0]),round(p[1])]
                    painter.drawPoint(*p)
            else:
                for p in self.p_list:
                    p=[round(p[0]),round(p[1])]
                    painter.drawPoint(*p)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                p=[round(p[0]),round(p[1])]
                painter.drawPoint(*p)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                p=[round(p[0]),round(p[1])]
                painter.drawPoint(*p)
        elif self.item_type == 'free':
            n=len(self.p_list)
            i=0
            for i in range(n-1):
                item_pixels = alg.draw_line([self.p_list[i],self.p_list[i+1]], 'Bresenham')
                for p in item_pixels:
                    p=[round(p[0]),round(p[1])]
                    painter.drawPoint(*p)
        elif self.item_type == 'outline':
            painter.drawRect(self.boundingRect())
        if self.selected:
            painter.setPen(QPen(QColor(192, 192, 192),0))
            painter.drawRect(self.boundingRect())



    def item_translate(self, dx, dy):
        self.p_list = alg.translate(self.p_list, dx, dy)
    
    def item_rotate(self,x,y,pre_x,pre_y):
        min_x, min_y = self.p_list[0]
        max_x, max_y = self.p_list[0]
        for [x0,y0] in self.p_list:
            if x0 < min_x:
                min_x = x0
            if y0 < min_y:
                min_y = y0
            if x0 > max_x:
                max_x = x0
            if y0 > max_y:
                max_y = y0
        center_x=(max_x+min_x)/2
        center_y=(max_y+min_y)/2
        cur_r=math.atan2(y-center_y,x-center_x)/math.pi*180
        pre_r=math.atan2(pre_y-center_y,pre_x-center_x)/math.pi*180
        r=pre_r-cur_r
        self.p_list=alg.rotate(self.p_list,center_x,center_y,r)

    def item_scale(self,x,y,pre_x,pre_y):
        min_x, min_y = self.p_list[0]
        max_x, max_y = self.p_list[0]
        for [x0,y0] in self.p_list:
            if x0 < min_x:
                min_x = x0
            if y0 < min_y:
                min_y = y0
            if x0 > max_x:
                max_x = x0
            if y0 > max_y:
                max_y = y0
        center_x=(max_x+min_x)/2
        center_y=(max_y+min_y)/2
        pre=math.sqrt((pre_x-center_x)**2+(pre_y-center_y)**2)
        cur=math.sqrt((x-center_x)**2+(y-center_y)**2)
        self.p_list=alg.scale(self.p_list,center_x,center_y,float(cur/pre))

    def item_clip(self,x0,y0,x1,y1,algorithm):
        if x0 > x1:
            x0,x1=x1,x0
        if y0 > y1:
            y0,y1=y1,y0
        self.p_list = alg.clip(self.p_list, x0, y0, x1, y1, algorithm)


    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse' or self.item_type == 'outline':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(round(x - 1), round(y - 1), round(w + 2), round(h + 2))
        elif self.item_type == 'polygon' or self.item_type == 'curve' or self.item_type=='free':
            if len(self.p_list) == 0:
                return QRectF(0, 0, 0, 0)
            if len(self.p_list) == 1:
                x0, y0 = self.p_list[0]
                return QRectF(round(x0 - 1), round(y0 - 1), 2, 2)
            x, y = self.p_list[0]
            w, h = self.p_list[0]
            for [x0,y0] in self.p_list:
                if x0 < x:
                    x = x0
                if y0 < y:
                    y = y0
                if x0 > w:
                    w = x0
                if y0 > h:
                    h = y0
            w = w - x
            h = h - y
            return QRectF(round(x - 1), round(y - 1), round(w + 2), round(h + 2))


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.width = 600
        self.height = 600
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(1, 1, self.width+1, self.height+1)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.width+3, self.height+3)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_menu = file_menu.addMenu('设置画笔')
        pen_color_act = set_pen_menu.addAction('设置画笔颜色')
        pen_size_act = set_pen_menu.addAction('设置画笔粗细')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act=file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        free_act = draw_menu.addAction('自由绘制')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        pen_color_act.triggered.connect(self.set_pen_color)
        pen_size_act.triggered.connect(self.set_pen_size)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        free_act.triggered.connect(self.free_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_cur_id(self):
        _id = str(self.item_cnt)
        return _id

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def reset_canvas_action(self):
        '''
        mytext, Ok = QInputDialog.getText(self,"重置画布","宽 高",QLineEdit.Normal,"")
        input = list(map(int,mytext.strip().split()))
        if len(input)>0:
            self.width = input[0]
        if len(input)>1:
            self.height = input[1]
        '''
        temp,ok = QInputDialog.getInt(self, '画布大小', '画布长度', 600, 100, 2147483647)
        if ok==True:
            self.height=temp
        temp,ok = QInputDialog.getInt(self, '画布大小', '画布宽度', 600, 100, 2147483647)
        if ok==True:
            self.width=temp
        self.item_cnt = 0
        self.canvas_widget.reset_canvas()
        self.list_widget.currentTextChanged.disconnect(self.canvas_widget.selection_changed)
        self.list_widget.clear()
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        self.scene.clear()
        self.scene.setSceneRect(1, 1, self.width+1, self.height+1)
        self.canvas_widget.setFixedSize(self.width+3, self.height+3)

    def set_pen_color(self):
        new_color = QColorDialog.getColor()
        if new_color.isValid():
            self.canvas_widget.set_pen_color(new_color)

    def set_pen_size(self):
        input, ok = QInputDialog.getInt(self, '设置画笔粗细', '画笔大小', 3, 0, 100)
        if ok:
            self.canvas_widget.set_pen_size(input)

    def save_canvas_action(self):
        #my_path, Ok = QInputDialog.getText(self,"请输入保存路径","路径",QLineEdit.Normal,"")
        #if Ok:
        #    self.canvas_widget.save_canvas(my_path)

        filename, type = QFileDialog.getSaveFileName(self,"保存画布",QDir.currentPath(),"BMP Files (*.bmp);;JPG Files (*.jpg);;PNG Files (*.png)")
        if filename:
            if type=="BMP Files (*.bmp)":
                if len(filename)<4 or filename[-4:]!=".bmp":
                    filename=filename+".bmp"
            elif type=="JPG Files (*.jpg)":
                if len(filename)<4 or filename[-4:]!=".jpg":
                    filename=filename+".jpg"
            else:
                if len(filename)<4 or filename[-4:]!=".png":
                    filename=filename+".png"
            picture = QPixmap()
            picture = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            picture.save(filename)
        


    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_cur_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_cur_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_cur_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_cur_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_cur_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_cur_id())
        self.statusBar().showMessage('中点圆生成算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_cur_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_cur_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def free_action(self):
        self.canvas_widget.start_draw_free(self.get_cur_id())
        self.statusBar().showMessage('自由绘制')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移图元')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转图元')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放图元')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland算法对线段裁剪')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky算法对线段裁剪')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
