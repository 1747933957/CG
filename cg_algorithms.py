#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = round(p_list[0][0]),round(p_list[0][1])
    x1, y1 = round(p_list[1][0]),round(p_list[1][1])
    result = []
    if x0<0 or y0<0 or x1<0 or y1<0:
        return result
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0 # 确保x0在x1的左部
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        elif y0 == y1:
            for x in range(x0, x1 + 1):
                result.append((x, y0))
        else:
            k = (y1 - y0) / (x1 - x0)
            if k <= 1 and k >= -1:
                temp = y0
                for x in range(x0, x1 + 1):
                    result.append((x, round(temp)))
                    temp += k
            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0 # 确保y0在y1的下部
                k = (x1 - x0) / (y1 - y0)
                temp = x0
                for y in range(y0, y1 + 1):
                    result.append((round(temp), y))
                    temp += k
    elif algorithm == 'Bresenham':
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
            return result
        if y0 == y1:
            if x0 > x1:
                x0, x1 = x1, x0
            for x in range(x0, x1 + 1):
                result.append((x, y0))
            return result
        delta_x = x0 - x1
        if delta_x < 0:
            delta_x = -delta_x
        delta_y = y0 - y1
        if delta_y < 0:
            delta_y = -delta_y
        m = delta_y / delta_x
        if m < 1:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            step = int((y1-y0)/delta_y)
            step_1 = 2 * delta_y
            step_2 = 2 * delta_y - 2 * delta_x
            p = 2 * delta_y - delta_x
            result.append((x0, y0))
            cur_x = x0
            cur_y = y0
            for k in range(0,delta_x):
                if p < 0:
                    cur_x = cur_x + 1
                    result.append((cur_x,cur_y))
                    p = p + step_1
                else:
                    cur_x = cur_x + 1
                    cur_y = cur_y + step
                    result.append((cur_x,cur_y))
                    p = p + step_2
        else:
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            step = int((x1-x0)/delta_x)
            step_1 = 2 * delta_x
            step_2 = 2 * delta_x - 2 * delta_y
            p = 2 * delta_x - delta_y
            result.append((x0, y0))
            cur_x = x0
            cur_y = y0
            for k in range(0,delta_y):
                if p < 0:
                    cur_y = cur_y + 1
                    result.append((cur_x,cur_y))
                    p = p + step_1
                else:
                    cur_x = cur_x + step
                    cur_y = cur_y + 1
                    result.append((cur_x,cur_y))
                    p = p + step_2
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = round(p_list[0][0]),round(p_list[0][1])
    x1, y1 = round(p_list[1][0]),round(p_list[1][1])
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 < y1:
        y0, y1 = y1, y0
    result = []
    delta_x = (x0+x1)/2
    delta_y = (y0+y1)/2
    rx = (x1-x0)/2
    ry = (y0-y1)/2
    if rx == 0 or ry == 0:
        return draw_line(p_list, 'Bresenham')
    p1 = ry*ry-rx*rx*ry+rx*rx/4
    cur_x = 0
    cur_y = ry
    result.append((cur_x,cur_y))
    while ry*ry*cur_x < rx*rx*cur_y:
        if p1 < 0:
            cur_x = cur_x + 1
            result.append((cur_x,cur_y))
            p1 = p1+2*ry*ry*cur_x+ry*ry
        else:
            cur_x = cur_x + 1
            cur_y = cur_y - 1
            result.append((cur_x,cur_y))
            p1 = p1+2*ry*ry*cur_x-2*rx*rx*cur_y+ry*ry
    p2 = ry*ry*(cur_x+1/2)*(cur_x+1/2)+rx*rx*(cur_y-1)*(cur_y-1)-rx*rx*ry*ry
    while cur_y >= 0:
        if p2 > 0:
            cur_y = cur_y -1
            result.append((cur_x,cur_y))
            p2 = p2-2*rx*rx*cur_y+rx*rx
        else:
            cur_y = cur_y -1
            cur_x = cur_x +1
            result.append((cur_x,cur_y))
            p2 = p2+2*ry*ry*cur_x-2*rx*rx*cur_y+rx*rx

    # 对result进行对称、平移
    for (x,y) in list(result):
        result.append((-x,y))
    for (x,y) in list(result):
        result.append((x,-y))
    for i in range(0,len(result)):
        result[i]=(round(result[i][0]+delta_x),round(result[i][1]+delta_y))
    return result

def B_spline(u,k,i):
    if k == 1:
        if u>=i and u<i+1:
            return 1
        else:
            return 0
    else:
        B1=B_spline(u,k-1,i)
        B2=B_spline(u,k-1,i+1)
        x=B1*(u-i)/(k-1)+B2*(i+k-u)/(k-1)
        return x

def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result=[]
    n = len(p_list)
    pp_list=p_list.copy()
    if n <= 1:
        return p_list
    if algorithm == 'Bezier':
        du=0.001/n
        result.append(pp_list[0])
        u=du
        while u<1:
            temp=pp_list.copy()
            for i in range(1,n):    #n-1次
                for j in range(0,n-i):
                    x=(1-u)*temp[j][0]+u*temp[j+1][0]
                    y=(1-u)*temp[j][1]+u*temp[j+1][1]
                    temp[j]=[x,y]
            result.append([round(temp[0][0]),round(temp[0][1])])
            u=u+du
        return result
    elif algorithm == 'B-spline':
        n=len(pp_list)
        dk=0.001/n
        k = 4
        for i in range(k-1,n):
            u = i+dk
            while u <= i+1:
                x = 0
                y = 0
                for j in range(i-k+1,i+1):
                    temp=B_spline(u,k,j)
                    x=x+pp_list[j][0]*temp
                    y=y+pp_list[j][1]*temp
                result.append([round(x),round(y)])
                u = u + dk
        return result
        




def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    for i in range(0,len(p_list)):
        p_list[i]=[p_list[i][0]+dx,p_list[i][1]+dy]
    return p_list


def rotate(p_list, xr, yr, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    angle = r * math.pi / 180
    for i in range(0,len(p_list)):
        x, y = p_list[i]
        x1 = xr + (x-xr) * math.cos(angle) + (y-yr) * math.sin(angle)
        y1 = yr - (x-xr) * math.sin(angle) + (y-yr) * math.cos(angle)
        p_list[i] = [x1, y1]
    return p_list


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    for i in range(0,len(p_list)):
        x1=x+(p_list[i][0]-x)*s
        y1=y+(p_list[i][1]-y)*s
        p_list[i]=[x1,y1]
    return p_list

def get_code(x,y,x_min,y_min,x_max,y_max):
    res=0
    if x < x_min:
        res=res|0b0001
    if x > x_max:
        res=res|0b0010
    if y < y_min:
        res=res|0b0100
    if y > y_max:
        res=res|0b1000
    return res

def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm == 'Cohen-Sutherland':
        code0=get_code(x0,y0,x_min,y_min,x_max,y_max)
        code1=get_code(x1,y1,x_min,y_min,x_max,y_max)
        k1,k2=0,0
        if x1 != x0:
            k1=(y1-y0)/(x1-x0)
        if y1 != y0:
            k2=(x1-x0)/(y1-y0)
        while True:
            if code0==0 and code1==0:
                return [[round(x0),round(y0)],[round(x1),round(y1)]]
            elif code0&code1!=0:
                return [[-1,-1],[-1,-1]]
            elif code0&0b0001==0b0001:  #剪[x0,y0]在框左边的部分
                y0=k1*(x_min-x0)+y0
                x0=x_min
                code0=code0&0b1110
            elif code1&0b0001==0b0001:  #剪[x1,y1]在框左边的部分
                y1=k1*(x_min-x1)+y1
                x1=x_min
                code1=code1&0b1110
            elif code0&0b0010==0b0010:  #剪[x0,y0]在框右边的部分
                y0=k1*(x_max-x0)+y0
                x0=x_max
                code0=code0&0b1101
            elif code1&0b0010==0b0010:  #剪[x1,y1]在框右边的部分
                y1=k1*(x_max-x1)+y1
                x1=x_max
                code1=code1&0b1101
            elif code0&0b0100==0b0100:  #剪[x0,y0]在框下边的部分
                x0=k2*(y_min-y0)+x0
                y0=y_min
                code0=code0&0b1011
            elif code1&0b0100==0b0100:  #剪[x1,y1]在框下边的部分
                x1=k2*(y_min-y1)+x1
                y1=y_min
                code1=code1&0b1011
            elif code0&0b1000==0b1000:  #剪[x0,y0]在框上边的部分
                x0=k2*(y_max-y0)+x0
                y0=y_max
                code0=code0&0b0111
            elif code1&0b1000==0b1000:  #剪[x1,y1]在框上边的部分
                x1=k2*(y_max-y1)+x1
                y1=y_max
                code1=code1&0b0111
    elif algorithm == 'Liang-Barsky':
        t0,t1=0.0,1.0
        deltax=x1-x0
        deltay=y1-y0
        q=[-deltax,deltax,-deltay,deltay]   #左，右，下，上
        d=[x0-x_min,x_max-x0,y0-y_min,y_max-y0]
        for i in range(0,4):
            if q[i] < 0:
                r = d[i]/q[i]
                if r > t1:
                    return [[-1,-1],[-1,-1]]
                elif r > t0:
                    t0 = r
            elif q[i] > 0:
                r = d[i]/q[i]
                if r < t0:
                    return [[-1,-1],[-1,-1]]
                elif r < t1:
                    t1 = r
            elif d[i] < 0:
                return [[-1,-1],[-1,-1]]
        x1=x0+t1*deltax
        y1=y0+t1*deltay
        x0=x0+t0*deltax
        y0=y0+t0*deltay
        return [[round(x0),round(y0)],[round(x1),round(y1)]]
