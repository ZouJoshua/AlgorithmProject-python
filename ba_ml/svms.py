#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2017/9/20 9:06
@Software : PyCharm
@File     : svms.py
@Desc     :支持向量机
"""

from numpy import *



###### 简化版SMO算法 ######


### SMO 算法中的辅助函数 ###

def loadDataSet(fileName):
    """
    对数据文件解析，得到数据矩阵和类标签
    :param fileName: 文件名
    :return: 数据矩阵，类标签矩阵
    """
    dataMat =[];labelMat = []
    fr = open(fileName)
    for line in fr.readlines():
        lineArr = line.strip().split('\t')
        dataMat.append([float(lineArr[0]),float(lineArr[1])])
        labelMat.append(float(lineArr[2]))
    return dataMat,labelMat

def selectJrand(i,m):
    """
    用均匀分布随机生成下标值
    :param i:第一个alpha的下标
    :param m:所有alpha的数目
    :return:alpha另一个下标
    """
    j = i
    while (j==i):
        j = int(random.uniform(0,m))
    return j

def clipAlpha(aj,H,L):
    if aj > H:
        aj = H
    if L > aj:
        aj = L
    return  aj

# 算法

def smoSimple(dataMatIn,classLables,C,toler,maxIter):
    """
    伪代码：
    创建一个alpha向量并将其初始化为O向量
    当迭代次数小于最大迭代次数时（外循环）
        对数据集中的每个数据向量（内循环）：
            如果该数据向量可以被优化：
                随机选择另外一个数据向量
                同时优化这两个向量
                如果两个向量都不能被优化，退出内循环
        如果所有向量都没被优化，增加迭代数目，继续下一次循环
    :param dataMatIn: 数据集
    :param classLables: 类别标签
    :param C: 常数C
    :param toler: 容错率
    :param maxIter: 取消前最大循环次数
    :return:
    """
    dataMatrix = mat(dataMatIn)
    labelMat = mat(classLables).transpose()
    b = 0 ; m,n = shape(dataMatrix)
    alphas = mat(np.zeros((m,1)))
    iter = 0
    while (iter < maxIter):
        alphasPairsChanged = 0 # 记录alpha是否已经进行优化
        for i in range(m):
            fXi = float(multiply(alphas,labelMat).T*(dataMatrix*dataMatrix[i,:].T)) + b  # 预测的类别
            Ei = fXi - float(labelMat[i])
            '''
            如果alpha可以优化，则进入优化程序
            '''
            if ((labelMat[i]*Ei < toler) and (alphas[i] < C)) or ((labelMat[i]*Ei > toler) and (alphas[i] > C)):
                '''
                随机选择第二个alpha
                '''
                j = selectJrand(i,m)
                fXj = float(multiply(alphas,labelMat).T*(dataMatrix*dataMatrix[j,:].T)) + b
                Ej = fXj - float(labelMat[j])
                alphaIold = alphas[i].copy()
                alphaJold = alphas[j].copy()
                '''
                保证alpha在 0 和 C 之间
                '''
                if (labelMat[i] != labelMat[j]):
                    L = max(0,alphas[j] - alphas[i])
                    H = min(C,C + alphas[j] -alphas[i])
                else:
                    L = max(0,alphas[j] + alphas[i] - C)
                    H = min(C,alphas[j] + alphas[i])
                if L == H:
                    print("L == H")
                    continue
                eta = 2.0 * dataMatrix[i,:]*dataMatrix[j,:].T - dataMatrix[i,:]*dataMatrix[i,:].T - dataMatrix[j,:]*dataMatrix[j,:].T
                if eta >= 0:
                    print("eta >= 0")
                    continue
                alphas[j] -= labelMat[j] * (Ei - Ej)/eta
                alphas[j] = clipAlpha(alphas[j],H,L)
                if (abs(alphas[j] - alphaJold) < 0.00001):
                    print("j not moving enough")
                    continue
                alphas[i] += labelMat[j]*labelMat[i]*(alphaJold - alphas[j])
                '''
                设置常数项
                '''
                b1 = b - Ei - labelMat[i]*(alphas[i]-alphaIold)*dataMatrix[i,:]*dataMatrix[i,:].T - labelMat[j]*(alphas[j] - alphaJold)*dataMatrix[i,:]*dataMatrix[j,:].T
                b2 = b - Ej - labelMat[i]*(alphas[i]-alphaIold)*dataMatrix[i,:]*dataMatrix[j,:].T - labelMat[j]*(alphas[j] - alphaJold)*dataMatrix[j,:]*dataMatrix[j,:].T
                if (0 < alphas[i]) and (C > alphas[i]):
                    b = b1
                elif(0 <alphas[j]) and (C > alphas[j]):
                    b = b2
                else:
                    b = (b1 + b2)/2.0
                alphasPairsChanged += 1
                print ("iter: %d i: %d,pairs changed %d" %(iter,i,alphasPairsChanged))
        if (alphasPairsChanged == 0):
            iter += 1
        else:
            iter = 0
        print("iteration number: %d" % iter)
    return b,alphas

###### 完整Platt SMO算法加速优化 ######

### 完整 SMO 算法的支持函数 ###

class optStruct:
    def __init__(self,dataMatIn,classLabels,C,toler,kTup):
        self.X = dataMatIn
        self.labelMat = classLabels
        self.C = C
        self.tol = toler
        self.m =shape(dataMatIn)[0]
        self.alphas = mat(zeros((self.m,1)))
        self.b = 0
        self.eCache = mat(zeros((self.m,2))) #误差缓存
        self.k = mat(zeros((self.m,self.m))
        for i in range(self.m):
            self.k[:,i] =  kernelTrans(self.x,self.x[i,:],kTup)

def calcEK(oS,k):
    fXk = float(multiply(oS.alphas,oS.labelMat).T * oS.k[:,k]) + oS.b
    Ek = fXk - float(oS.labelMat[k])
    return Ek

def selectJ(i,oS,Ei):
    #内循环中的启发式方法
    maxK = -1;maxDeltaE = 0;Ej = 0
    oS.eCache[i] = [1,Ei]
    validEcacheList = nonzero(oS.eCache[:,0].A)[0]
    if (len(validEcacheList)) >1:
        for k in validEcacheList:
            if k == i:
                continue
            Ek = calcEK(oS,k)
            deltaE = abs(Ei - Ek)
            if (deltaE > maxDeltaE):
                maxK = k;maxDeltaE = deltaE;Ej = Ek#选择具有最大步长的j
        return maxK,Ej
    else:
        j = selectJrand(i,oS.m)
        Ej = calcEK(oS,j)
    return j,Ej

def updateEK(oS,k):
    Ek = calcEK(oS,k)
    oS.eCache[k] = [1,Ek]

 # 核转换函数
def kernelTrans(x, xi, kTup):
    m, n = shape(x)
    k = mat(zeros([m, 1]))
    if kTup[0] == "lin":
        k = x * xi.T
    elif kTup[0] == "rbf":
        for j in range(m):
            deltaRow = x[j, :] - xi
            k[j] = deltaRow * deltaRow.T
        k = exp(k / (-1 * kTup[1] ** 2))
    else:
        raise NameError("Houston We Have a Problem That Kernel is not recognized")
    return k

#算法

def innerL(i,oS):
    Ei = calcEk(oS, i)
    if ((oS.labelMat[i] * Ei < -oS.tol) and (oS.alphas[i] < oS.C)) or ((oS.labelMat[i]*Ei > oS.tol) and (oS.alphas[i] > 0)):
        j, Ej = selectJ(i, oS, Ei)
        alphaIold = oS.alphas[i].copy()
        alphaJold = oS.alphas[j].copy()
        if (oS.labelMat[i] != oS.labelMat[j]):
            L = max(0, oS.alphas[j] - oS.alphas[i])
            H = min(oS.C, oS.C + oS.alphas[j] - oS.alphas[i])
        else:
            L = max(0, oS.alphas[j] + oS.alphas[i] - oS.C)
            H = min(oS.C, oS.alphas[j] + oS.alphas[i])
        if L == H:
            print("L == H")
            return 0
        eta = 2.0 * oS.k[i,j] - oS.k[i,i] - oS.k[j,j]
        if eta >= 0:
            print("eta >= 0")
            return 0
        oS.alphas[j] -= oS .labelMat[j] * (Ei - Ej)/eta
        oS.alphas[j] = clipAlpha(oS.alphas[j] / H, L)
        updateEk(oS, j)#更新误差缓存
        if (abs(oS.alphas[j] - alphaJold) < 0.00001):
            print("j not moving enough")
            return 0
        oS.alphas[i] += oS.labelMat[j] * oS.labelMat[i] * (alphaJold - oS.alphas[j])
        updateEk(oS, i)#更新误差缓存
        '''
        设置常数项
        '''
        b1 = oS.b - Ei - oS.labelMat[i] * (oS.alphas[i] - alphaIold) * oS.k[i, i] - oS.labelMat[j] * (oS.alphas[j] - alphaJold) * oS.k[i, j]
        b2 = oS.b - Ej - oS.labelMat[i] * (oS.alphas[i] - alphaIold) * oS.k[i, j] - oS.labelMat[j] * (oS.alphas[j] - alphaJold) * oS.k[j, j]
        if (0 < oS.alphas[i]) and (oS.C > oS.alphas[i]):
            oS.b = b1
        elif (0 < oS.alphas[j]) and (oS.C > oS.alphas[j]):
            oS.b = b2
        else:
            oS.b = (b1 + b2) / 2.0
        return 1
    else:
        return 0

def smoP(dataMatIn,classLabels,C,toler,maxIter,kTup=('lin',0)):
    oS = optStruct(mat(dataMatIn),mat(classLabels).transpose(),C,toler)
    iter = 0
    entireSet = True
    alphaPairsChanged = 0
    while (iter < maxIter) and ((alphaPairsChanged > 0) or (entireSet)):
        alphaPairsChanged = 0
        if entireSet:
            for i in range(oS.m):
                alphaPairsChanged += innerL(i,oS)
            print("fullSet,iter:%d i:%d ,pairs changed %d" %(iter,i,alphaPairsChanged))
            iter += 1
        else:
            nonBoundIs = nonzero((oS.alphas.A > 0) * (oS.alphas.A < C))[0]
            for i in nonBoundIs:
                alphaPairsChanged += innerL(i,oS)
            print("non-bound ,iter:%d i:%d,pairs changed %d" %(iter,i,alphaPairsChanged))
        if entireSet:
            entireSet = False
        elif (alphaPairsChanged == 0):
            entireSet = True
            print("iteration number :%d" % iter)
        return oS.b,oS.alphas


