import matplotlib.pyplot as plt
import copy
import random
import pandas as pd
import numpy as np
import math
import re
random.seed(1)
Operations_data=np.array(pd.read_excel('data2.xlsx',sheet_name='Operations')).tolist()
Machine_tools_data=np.array(pd.read_excel('data2.xlsx',sheet_name='Machine tools')).tolist()

def stringquchu(str0,intemlist):
    return0=copy.deepcopy(str0)
    for i in intemlist:
        return0=return0.replace(i, '')
    return return0

def quchong(fitnesspop):#返回元素
    optimal_f2=[]
    for i in fitnesspop:
      if not i in optimal_f2:
        optimal_f2.append(i)
    return optimal_f2

def str2list(str0):#一阶字符串转list
    str1=copy.deepcopy(str0)
    str1=str1[1:-1]
    str1=re.sub(' ','', str1)
    str1=str1.split(',')
    str1=[(int)(str1[i]) for i in range(len(str1))]
    return str1


#案例数据
n_machining_shop= (int)(max([Machine_tools_data[i][0] for i in range(len(Machine_tools_data))]) )#分布式机械加工车间的数量
n_machine_tool=[0 for i in range(n_machining_shop)] #各分布式机械加工车间的机床数量
for i in range(len(Machine_tools_data)):
    n_machine_tool[(int)(Machine_tools_data[i][0]-1)]=max(n_machine_tool[(int)(Machine_tools_data[i][0]-1)],(int)(Machine_tools_data[i][1]))

       



c0ij=[[Machine_tools_data[sum(n_machine_tool[:i])+j][5]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]

c1ij=[[Machine_tools_data[sum(n_machine_tool[:i])+j][6] 
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]

 
#附加载荷损耗功率的系数c0和c1
n_job=max([Operations_data[i][0] for i in range(len(Operations_data))]) #工件种类





n_job_operation_number=[0 
                        for i in range(n_job)] #各工件的工序数量
for i in range(len(Operations_data)):
    n_job_operation_number[Operations_data[i][0]-1]=max(n_job_operation_number[Operations_data[i][0]-1],Operations_data[i][4])



n_batches_number=quchong([str2list(Operations_data[i][7])
               for i in range(len(Operations_data))])#各类工件批次的数量
n_job_number=[len(n_batches_number[i]) for i in range(len(n_batches_number))] #各工件批次的数量


operation_type=[[0 for k in range(n_job_operation_number[i])]  for i in range(n_job)]
#作业的种类，索引分别代表工件、工序，0代表车，1代表铣，2代表钻
for i in range(n_job):
    for k in range(n_job_operation_number[i]):
        assit0=sum(n_job_operation_number[:i])+k
        if Operations_data[assit0][3]=="车":
            operation_type[i][k]=0
        elif Operations_data[assit0][3]=="铣":
            operation_type[i][k]=1
        else:
            operation_type[i][k]=2
        

Parameters_num=[3,4,2]#车铣钻的工艺参数数量


n_job_feasible_shops=[[j for j in range(n_machining_shop)] for i in range(n_job)]#各个工件可选的车间
# n_job_operation_feasible_machines=[[[random.sample(list(range(n_machine_tool[k])),random.randint(2, n_machine_tool[k]))
#                                      for k in range(n_machining_shop)] 
#                                     for j in range(n_job_operation_number[i])] 
#                                    for i in range(n_job)]
#各工件的工序可选机床,四个索引分别对应工件、工序、车间、机床

n_job_operation_feasible_machines=[[[[]
                                     for k in range(n_machining_shop)] 
                                    for j in range(n_job_operation_number[i])] 
                                   for i in range(n_job)]

for i in range(n_job):#工件
    for j in range(n_job_operation_number[i]):#工序
        for k in range(n_machining_shop):#车间
            string0=Operations_data[sum(n_job_operation_number[:i])+j][5]
            b=string0.split(",")
            intlist=[[int( b[l][1])-1 ,int( b[l][2:])-1] for l in range(len(b))]
            n_job_operation_feasible_machines[i][j][k]=[intlist[l][1] for l in range(len(intlist)) if k==intlist[l][0] ]

caozuoshuliang=[[Operations_data[sum(n_job_operation_number[:k])+l][9]
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]#各个操作的数量

CTijkm=[[[[Operations_data[sum(n_job_operation_number[:k])+l][8]
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]#索引分别是车间，机床，工件，工序

kcijk=[[[Machine_tools_data[sum(n_machine_tool[:i])+j][9]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]#切削力系数
zijkm=[[[[0
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]#铣刀齿数
Dijkm=[[[[0
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
      for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]
deltaDijkm=copy.deepcopy(Dijkm)

for i in range(n_job):#工件
    for j in range(n_job_operation_number[i]):#工序
        if operation_type[i][j]==1:#铣削
            # print([i,j])
            millingtool=stringquchu(Operations_data[sum(n_job_operation_number[:i])+j][22],['[',']',' ']).split(',')
            millingtooldia=stringquchu(Operations_data[sum(n_job_operation_number[:i])+j][23],['[',']',' ']).split(',')
            
            feasiblemachinetool=stringquchu(Operations_data[sum(n_job_operation_number[:i])+j][5],['M',' ']).split(',')
            feasiblemachinetool=[[(int)(feasiblemachinetool[k][0])-1,(int)(feasiblemachinetool[k][1])-1] for k in range(len(feasiblemachinetool))]
            for k in range(len(feasiblemachinetool)):
                zijkm[feasiblemachinetool[k][0]][feasiblemachinetool[k][1]][i][j]=(int)(millingtool[k])
                Dijkm[feasiblemachinetool[k][0]][feasiblemachinetool[k][1]][i][j]=(int)(millingtooldia[k])
        elif operation_type[i][j]==2:#钻
            feasiblemachinetool=stringquchu(Operations_data[sum(n_job_operation_number[:i])+j][5],['M',' ']).split(',')
            feasiblemachinetool=[[(int)(feasiblemachinetool[k][0])-1,(int)(feasiblemachinetool[k][1])-1] for k in range(len(feasiblemachinetool))]
                
            for k in range(len(feasiblemachinetool)):    
                millingtool=Operations_data[sum(n_job_operation_number[:i])+j][23]
                # print([i,j,k,feasiblemachinetool[k]])
                Dijkm[feasiblemachinetool[k][0]][feasiblemachinetool[k][1]][i][j]=(int)(Operations_data[sum(n_job_operation_number[:i])+j][23])
                deltaDijkm[feasiblemachinetool[k][0]][feasiblemachinetool[k][1]][i][j]=(int)(Operations_data[sum(n_job_operation_number[:i])+j][23])
# print("hello")
# print([0,3,1,10])
# print(Dijkm[0][3][1][10])
# print(operation_type[1][10])



r1ijkm=[[[[Operations_data[sum(n_job_operation_number[:k])+l][19]
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]

r2ijkm=[[[[Operations_data[sum(n_job_operation_number[:k])+l][20]
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]

r3ijkm=[[[[Operations_data[sum(n_job_operation_number[:k])+l][21]
            for l in range(n_job_operation_number[k])]
        for k in range(n_job)]  
     for j in range(n_machine_tool[i])] 
    for i in range(len(n_machine_tool))]

Lairkm=[[Operations_data[sum(n_job_operation_number[:k])+l][16] 
         for l in range(n_job_operation_number[k])]
        for k in range(n_job)]

deltakm=[[Operations_data[sum(n_job_operation_number[:k])+l][18]  
         for l in range(n_job_operation_number[k])]
        for k in range(n_job)]

Lcutkm=[[Operations_data[sum(n_job_operation_number[:k])+l][17] 
         for l in range(n_job_operation_number[k])]
        for k in range(n_job)]
nkl=copy.deepcopy(n_batches_number)

# [[0 
#          for l in range(n_batches_number[k])]
#         for k in range(n_job)]

# for k in range(len(nkl)):
#     piliangstr=Operations_data[sum(n_job_operation_number[:k])+0][7]
#     piliangstr=stringquchu(piliangstr,['[',']',' ']).split(',')
#     for l in range(n_batches_number[k]):
#         nkl[k][l]=(int)(piliangstr[k][l])

# for i in range(n_job):#工件
#     for j in range(n_job_operation_number[i]):#工序
#         for k in range(n_machining_shop):#车间
#             string0=Operations_data[sum(n_job_operation_number[:i])+j][6]
#             b=string0.split(",")
#             intlist=[[int( b[l][1])-1 ,int( b[l][2:])-1] for l in range(len(b))]
#             n_job_operation_feasible_machines[i][j][k]=[intlist[l][1] for l in range(len(intlist)) if k==intlist[l][0] ]




# n_job_operation_feasible_machines_tools=[[[[]
#                                            for j in range(len(n_machine_tool))] 
#                                           for k in range(n_job_operation_number[i])]
#                                          for i in range(n_job)]
#下次从这里开始
parameter_bound=[[[[[[0 
                      for n in range(2)] 
                     for m in range(Parameters_num[operation_type[k][l]])] 
                    for l in range(n_job_operation_number[k])]
                   for k in range(n_job)] 
                  for j in range(n_machine_tool[i])]
                 for i in range(len(n_machine_tool))]
#工艺参数的上下限，索引分别是车间、机床、工件、工序、参数数量、上下限

for i in range(len(n_machine_tool)):#车间
    for j in range(n_machine_tool[i]):#机床
        for k in range(n_job):#工件
            for l in range(n_job_operation_number[k]):#工序
                for m in range(Parameters_num[operation_type[k][l]]):#参数数量
                    bound=[(Operations_data[sum(n_job_operation_number[:k])+l][10+n]).split("-") for n in range(Parameters_num[operation_type[k][l]])]
                    parameter_bound[i][j][k][l][m]=[(float)(bound[m][0]),(float)(bound[m][1])]
                    
                    
                    # if operation_type[k][l]==0:#车
                    #     bound=[(Operations_data[sum(n_job_operation_number[:k])+l][10+n]).split("-") for n in range(3)]
                    #     parameter_bound[i][j][k][l][m]=[[(float)(bound[n][0]),(float)(bound[n][1])] for n in range(len(bound))]
                    # elif operation_type[k][l]==1:#铣
                    #     bound=[(Operations_data[sum(n_job_operation_number[:k])+l][10+n]).split("-") for n in range(4)]
                    #     parameter_bound[i][j][k][l][m]=[[(float)(bound[n][0]),(float)(bound[n][1])] for n in range(len(bound))]
                    # else:
                    #     bound=[(Operations_data[sum(n_job_operation_number[:k])+l][10+n]).split("-") for n in range(2)]
                    #     parameter_bound[i][j][k][l][m]=[[(float)(bound[n][0]),(float)(bound[n][1])] for n in range(len(bound))]
                    

#工艺参数的最大最小值，索引分别对应车间，机床，工件，工序，工艺参数，种类（1是最大值 0是最小值）
def data_set(input0):
    t_ts=[[[[0
                 for l in range(n_job_operation_number[k])]
            for k in range(len(n_job_operation_number))] 
        for j in range(n_machine_tool[i])] 
      for i in range(len(n_machine_tool))]
    
    for i in range(len(Operations_data)):
        string0=Operations_data[i][input0]
        gongjian0=Operations_data[i][0]-1
        gongxu0=Operations_data[i][4]-1
        machine_string=(stringquchu(Operations_data[i][5],["M"])).split(",")
        data_string=(stringquchu(string0,["[","]"," "])).split(",")
        for j in range(len(machine_string)):
            chejian0=(int)(machine_string[j][0])-1
            jichuang0=(int)(machine_string[j][1:])-1
            t_ts[chejian0][jichuang0][gongjian0][gongxu0]=(int)(data_string[j])

    # for i in range(len(n_job_operation_feasible_machines)):
    #     for j in range(len(n_job_operation_feasible_machines[i])):
    #         index0=sum(n_job_operation_number[:i])+j
    #         toolstring=Operations_data[index0][7]
    #         if ',' not in toolstring:
    #             t_tslist=(Operations_data[index0][input0]).replace("],[", "")
    #             toollist=(Operations_data[index0][7].replace("T", "")).split(',')
    #             toollist=[int(k)-1 for k in toollist]
    #             # machinelist0=((Operations_data[index0][6].strip('[]').replace("M", ""))).split(',')
    #             # machinelist=[[int(machinelist0[k][0])-1,int(machinelist0[k][1:])-1] for k in range(len(machinelist0))]
    #             t_tsstring=(t_tslist.strip('[]')).split(',')
    #             for k in range(len(t_ts[i][j])):
    #                 for l in range(len(t_ts[i][j][k])):
    #                     t_ts[i][j][k][l][0]=int(t_tsstring[0])
    #                     del(t_tsstring[0])
    #         else:

    #             # machinelist0=((Operations_data[index0][6].strip('[]').replace("M", ""))).split(',')
    #             # machinelist=[[int(machinelist0[k][0])-1,int(machinelist0[k][1:])-1] for k in range(len(machinelist0))]
    #             t_tslist=(Operations_data[index0][input0])
    #             t_tsstringlen=len(t_tslist)
    #             t_tsstring=t_tslist[1:t_tsstringlen-1].split('],[')
    #             t_tsstring[0]=t_tsstring[0][1:]
    #             t_tsstring[-1]=t_tsstring[-1][:-1]
    #             for k in range(len(t_tsstring)):
    #                 t_tsstring[k]=t_tsstring[k].split(',')
    #                 t_tsstring[k]=[int(t_tsstring[k][l]) for l in range(len(t_tsstring[k]))]
    #             for k in range(len(t_ts[i][j])):
    #                 t_ts[i][j][k]=t_tsstring[0]
    #                 del(t_tsstring[0])
    return t_ts

for i in range(n_job):
    for k in range(n_job_operation_number[i]):
        index0=sum(n_job_operation_number[:i])+k
        machines=(Operations_data[index0][5].replace("M", "")).split(',')
        # tool0=(Operations_data[index0][7].replace("T", "")).split(',')
        # tool0=[int(tool0[l])-1 for l in range(len(tool0))]
        machine0=[[] for l in range(n_machining_shop)]
        for l in range(len(machines)):
            machine0[int(machines[l][0])-1].append(int(machines[l][1])-1)
        # for j in range(len(machine0)):#每个车间
        #     n_job_operation_feasible_machines_tools[i][k][j]=[tool0  for l in range(len(machine0[j]))]
                                         


#各工件工序在各机床上的安装卸载时间之和,t_lu[i][j][k][m]是工件i的工序j在车间k的机床m的安装和拆卸时间之和
t_set=data_set(24)#各工件工序在各机床上各刀具的对刀时间,t_ts[i][j][k][l][m]是工件i的工序j在车间k的机床l的采用刀具m的对刀时间
t_tc=data_set(25)#各工件工序在各机床上采用各刀具的换刀时间,t_tc[i][j][k][l][m]是工件i的工序j在车间k的机床l的采用刀具m的切削时间

P_st=[[0
        for j in range(n_machine_tool[i])]
      for i in range(len(n_machine_tool))]
for i in range(len(Machine_tools_data)):
        P_st[Machine_tools_data[i][0]-1][Machine_tools_data[i][1]-1]=Machine_tools_data[i][3]

P_nl=data_set(26)#空载功率需要修改

P_au=[[0 
        for j in range(n_machine_tool[i])]
      for i in range(len(n_machine_tool))]
for i in range(len(Machine_tools_data)):
        P_au[Machine_tools_data[i][0]-1][Machine_tools_data[i][1]-1]=Machine_tools_data[i][4]
#各车间机床的辅助设备功率,[i][j]分别对应车间号和机床号




# #各个刀具的寿命，索引分别是工件、工序、车间、机床、刀具




#各车间机床的附加载荷损耗功率,[i][j][k][l][m]分别对应工件、工序、车间、机床、刀具


# #案例数据，需要根据事情情况修改****************************

n_variables_1=sum([n_job_operation_number[i]*n_job_number[i] for i in range(n_job)])#operation number
n_variables=n_variables_1*7
#变量数量，分别是:
#    车间、机床、加工顺序，四种工艺参数
def totalsum(input0):#能耗求和，最大阶级是3
    return0=0
    for i in range(len(input0)):
        for j in range(len(input0[i])):
            for k in range(len(input0[i][j])):
                    return0=return0+input0[i][j][k]
    return return0

def totalsum2(input0):#能耗求和，最大阶级是3
    return0=0
    for i in range(len(input0)):
        for j in range(len(input0[i])):
                    return0=return0+input0[i][j]
    return return0

def getBrightColor():
    # 获得亮色，保证其中两色分别90和ff，第三色为任意值即可
    full_range = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
    combination = ["90"]
    # 将 ff 随机插入 90 前或后
    combination.insert(random.randint(0,1),"ff")
    third_color = "{0}{1}".format(full_range[random.randint(0,15)],full_range[random.randint(0,15)])
    combination.insert(random.randint(0,2),third_color)
    color = "#" + "".join(combination)
    return color

def totalmax(input0):#时间的最大值，最大阶级是3
    return0=0
    for i in range(len(input0)):
        for j in range(len(input0[i])):
            for k in range(len(input0[i][j])):
                if return0<input0[i][j][k]:
                    return0=input0[i][j][k]
    return return0

def totalsum(input0):#时间的最大值，最大阶级是3
    return0=0
    for i in range(len(input0)):
        for j in range(len(input0[i])):
            for k in range(len(input0[i][j])):
                    return0=return0+input0[i][j][k]
    return return0
 
def guiyihua(input0):
    return0=copy.deepcopy(input0)
    while return0>1 or return0<0.1:
        if return0>1:
            return0=return0/10
        elif return0<0.1:
            return0=return0*10
    return0=return0*100
    return return0

def Operationtimeandenergy(gongjian,piliang,gongxu,chejian,jichuang,canshu,operationtype,delta_assit):
    #工件，批量，工序，车间，机床，参数，操作种类（1，2，3），0-1是否需要上下料
    toollife=1
    
    if operationtype==0:#车
        toollife=CTijkm[chejian][jichuang][gongjian][gongxu]/(canshu[0]*canshu[1]*canshu[2])
        toollife=guiyihua(toollife)
        t_co0=caozuoshuliang[gongjian][gongxu]*Lcutkm[gongjian][gongxu]*deltakm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1]*canshu[2])
        t_air0=Lairkm[gongjian][gongxu]*deltakm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1]*canshu[2])
        t_air1=t_air0*t_co0/(toollife*piliang)
        P_mr=canshu[0]*canshu[1]*canshu[2]*kcijk[chejian][jichuang][gongjian]
    elif operationtype==1:#铣削   
        toollife=CTijkm[chejian][jichuang][gongjian][gongxu]/(math.pow(3.14*Dijkm[chejian][jichuang][gongjian][gongxu]*canshu[0], r1ijkm[chejian][jichuang][gongjian][gongxu])*math.pow(canshu[0]*canshu[1]*zijkm[chejian][jichuang][gongjian][gongxu], r2ijkm[chejian][jichuang][gongjian][gongxu])*math.pow(canshu[2], r3ijkm[chejian][jichuang][gongjian][gongxu]))
        toollife=guiyihua(toollife)
        t_co0=caozuoshuliang[gongjian][gongxu]*Lcutkm[gongjian][gongxu]*deltakm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1]*canshu[2]*canshu[3]*zijkm[chejian][jichuang][gongjian][gongxu])

        t_air0=Lairkm[gongjian][gongxu]*deltakm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1]*canshu[2]*zijkm[chejian][jichuang][gongjian][gongxu])
        t_air1=t_air0*t_co0/(toollife*piliang)
        P_mr=canshu[0]*canshu[1]*canshu[2]*canshu[3]*zijkm[chejian][jichuang][gongjian][gongxu]*kcijk[chejian][jichuang][gongjian]
    else:#钻孔
        toollife=CTijkm[chejian][jichuang][gongjian][gongxu]/(math.pow(3.14*Dijkm[chejian][jichuang][gongjian][gongxu]*canshu[0], r1ijkm[chejian][jichuang][gongjian][gongxu])*math.pow(canshu[1],r2ijkm[chejian][jichuang][gongjian][gongxu])*math.pow(deltaDijkm[chejian][jichuang][gongjian][gongxu]/2,r3ijkm[chejian][jichuang][gongjian][gongxu]))
        toollife=guiyihua(toollife)
        t_co0=caozuoshuliang[gongjian][gongxu]*Lcutkm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1])
        t_air0=Lairkm[gongjian][gongxu]*piliang/(canshu[0]*canshu[1])
        t_air1=t_air0*t_co0/(toollife*piliang)
        P_mr=canshu[0]*canshu[1]*3.14*Dijkm[chejian][jichuang][gongjian][gongxu]*Dijkm[chejian][jichuang][gongjian][gongxu]/4
    t_set0=t_set[chejian][jichuang][gongjian][gongxu]*piliang*delta_assit
    t_tc0=t_tc[chejian][jichuang][gongjian][gongxu]*piliang*t_co0/toollife
    
    e_lu0=t_set0*P_st[chejian][jichuang] 
    # print(P_nl[chejian][jichuang][gongjian][gongxu])
    e_ac=t_air0*(P_st[chejian][jichuang]+P_nl[chejian][jichuang][gongjian][gongxu]+P_au[chejian][jichuang]) 
    P_ad=c0ij[chejian][jichuang]*P_mr+c1ij[chejian][jichuang]*P_mr*P_mr
    e_co=t_co0*(P_st[chejian][jichuang]+P_nl[chejian][jichuang][gongjian][gongxu]+P_au[chejian][jichuang]+P_mr+P_ad)
    e_tc=t_tc0*P_st[chejian][jichuang]
    operation_time=t_set0+t_air0+t_air1+t_co0+t_tc0
    operation_time=guiyihua(operation_time/piliang)*piliang
    operation_energy=(e_lu0+e_ac+e_co+e_tc)
    seperate_energy=[e_lu0,e_ac,e_co,e_tc]
    # print([operation_time,operation_energy,operation_energy/operation_time])
    return [operation_time,operation_energy,seperate_energy]
    


def vector12vector2(vector1,distri):#一维向量转二维向量，输入分别是一维向量和分布情况
    assit=0
    return0=[0 for i in range(len(distri))]
    for i in range(len(distri)):
        return0[i]=vector1[assit:assit+distri[i]]
        assit+=distri[i]
    return return0

def vector12vector3(vector1,distri):#一维向量转三维向量，输入分别是一维向量和分布情况
    assit=0
    return0=[[0 for j in range(len(distri[i]))] for i in range(len(distri))]
    for i in range(len(distri)):
        for j in range(len(distri[i])):
            return0[i][j]=vector1[assit:
                                  assit+len(distri[i][j])]
        assit+=len(distri[i][j])
    return return0

def vector12vector4(vector1,distri):#一维向量转四维向量，输入分别是一维向量和分布情况
    assit=0
    return0=[[[0 for k in range(len(distri[i][j]))] for j in range(len(distri[i]))] for i in range(len(distri))]
    for i in range(len(distri)):
        for j in range(len(distri[i])):
            for k in range(len(distri[i][j])):
                return0[i][j][k]=vector1[assit:
                  assit+len(distri[i][j][k])]
        assit+=len(distri[i][j][k])
    return return0 


def fitnesspopfun(pop):
    return [fitness(i)[0:2] for i in pop]

def gantteplot(schedule,num):
    fig, axs = plt.subplots(n_machining_shop)

    picis=[0 for j in range(n_job)]#每个工件分了多少批次
    color_asit=[[]for i in range(n_job)]#颜色辅助变量
    color=[[]for i in range(n_machining_shop)]#颜色区分
    MS=[[]for i in range(n_machining_shop)]#机器编号
    T = [[]for i in range(n_machining_shop)]#操作持续时间
    macStartTime = [[]for i in range(n_machining_shop)]#操作开始时间
    J = [[]for i in range(n_machining_shop)]#工件号
    B=[[]for i in range(n_machining_shop)]#批次号
    oper = [[]for i in range(n_machining_shop)]#工序号

        
    
    for i in range(len(schedule)):#访问各个车间
        for j in schedule[i]:#访问各个机床
            for k in j:#访问各个操作
                MS[i].append(k[7])#机器号
                T[i].append(k[4])#操作持续时间
                macStartTime[i].append(k[3])#操作开始时间
                J[i].append(k[0]+1)#工件号
                B[i].append(k[1]+1)#批次号
                oper[i].append(k[2]+1)#工序号
                picis[k[0]]=max(picis[k[0]],k[1]+1)
    for i in range(len(picis)):#访问各个工件
        color_asit[i]=[getBrightColor() for k in range(picis[i])]
        # 画图
        
    batches=[[] for i in range(n_machining_shop)]
    for i in range(len(schedule)):#访问各个车间
        for j in schedule[i]:#访问各个机床
            for k in j:#访问各个操作
                if [k[0]+1,k[1]+1] not in batches[i]:
                    batches[i].append([k[0]+1,k[1]+1])
        batches[i].sort(key=lambda x: x[0]*100+x[1])

    for i in range(len(schedule)):#访问各个车间
        for j in schedule[i]:#访问各个机床
            for k in j:#访问各个操作
                color[i].append(color_asit[k[0]][k[1]])
    
    for i in range(len(schedule)):#访问各个车间
        gantt(axs[i],MS[i], T[i], macStartTime[i], J[i], B[i],oper[i],color[i])
        # for j in range(len(batches[i])):
        #     x1=int(j/n_machine_tool[i])
        #     y1=j%n_machine_tool[i]
        #     axs[i].barh(y1,400,0.5,left=63000+x1*3000,color=color_asit[batches[i][j][0]-1][batches[i][j][1]-1])
        #     axs[i].text(64000+x1*3000-500, y1-0.4, '%s-%s' %
        #           (batches[i][j][0],batches[i][j][1]), size=8)
            
        # axs[i].set_yticks([])
        # if i<3:
        #     axs[i].set_xticks([])
        # else:
        #     axs[i].set_xticks([0,20000,40000,60000])
        
 
    plt.rcParams.update({'font.size': 4})
    plt.tight_layout()
    plt.savefig("allcmp"+str(num)+".svg",bbox_inches='tight') 
    plt.show()


def gantt(axs0,MS, T, macStartTime, workpiece,B, operation,colors):
    maxtime=max([T[i]+macStartTime[i] for i in range(len(T))])
    for i in range(len(MS)):
        axs0.barh(MS[i],T[i],0.5,left=macStartTime[i],color=colors[i])
        # axs0.text(macStartTime[i] + T[i] / 2-maxtime*0.01, MS[i]-0.10, '%s-%s' %
        #           (workpiece[i],B[i]), size=4)
        # figure0.xticks(fontsize=6) 
    # yticks_assit=['$M_{'+str(i+1)+'}$' for i in range(len(quchong(MS)))]
    # figure0.yticks(range(len(set(MS))), yticks_assit)

def fitness(individual0):#评价个体，给出对应的目标函数
    individual=copy.deepcopy(individual0)# individual0.tolist()#这个可能不需要
    variables1_encode=individual[0:n_variables_1]#车间选择    
    variables2_encode=individual[n_variables_1:2*n_variables_1] #机床选择   
    variables3_encode=individual[2*n_variables_1:3*n_variables_1]#加工顺序    
    variables4_encode=individual[3*n_variables_1:]#工艺参数    

    # print(variables1_encode)
    # print(n_batches_number)
    variables1_assit1=vector12vector2(variables1_encode,n_job_number)
    variables1=[[0 for j in range(len(variables1_assit1[i]))] for i in range(len(variables1_assit1))]
    #第一个变量nb_ij，各工序所选车间，索引分别包括工件，批次
    for i in range(len(variables1)):
        for j in range(len(variables1[i])):
            variables1[i][j]=(int)(variables1_assit1[i][j]*len(n_job_feasible_shops[i]))
            if variables1[i][j]==len(n_job_feasible_shops[i]):
                    variables1[i][j]-=1
    
    distrib1=[[[0
                for k in range(n_job_operation_number[i])]
                for j in range(len(variables1[i]))]
              for i in range(n_job)]
    variables2_assit1=vector12vector3(variables2_encode,distrib1)
    variables2=copy.deepcopy(variables2_assit1)
    #第二个变量，各工序选择机床的情况，三个索引分别代表工件、批次、工序所对应的可选机床索引
    for i in range(len(variables2_assit1)):#工件
        for j in range(len(variables2_assit1[i])):#批次
            for k in range(len(variables2_assit1[i][j])):#工序
                variables2[i][j][k]=(int)(variables2_assit1[i][j][k]*len(n_job_operation_feasible_machines[i][k][variables1[i][j]]))
                if variables2[i][j][k]==len(n_job_operation_feasible_machines[i][k][variables1[i][j]]):
                    variables2[i][j][k]-=1
                #上面的是实际机床编号
    

    
    distrib3=[[[0 
                for k in range(n_job_operation_number[i])] 
                for j in range(len(variables1[i]))]
              for i in range(n_job)]
    variables3_assit1=vector12vector3(variables3_encode,distrib3)    

    operations_assit=[[]
                      for i in range(n_machining_shop)]#各个车间待调度的工序
    sequence_encode=[[]
                      for i in range(n_machining_shop)]#各个车间待调度工序顺序的编码
    
    for i in range(len(variables1)):
        for j in range(len(variables1[i])):#这个地方加了一个len，可能有问题
            for k in range(n_job_operation_number[i]):
                operations_assit[variables1[i][j]].append([i,j,k])
                sequence_encode[variables1[i][j]].append(variables3_assit1[i][j][k])
    sequence_assit=[[j
                      for j in range(len(sequence_encode[i]))]
                    for i in range(n_machining_shop)]#各个车间待调度工序顺序的编码
    operations=[[]
                for i in range(n_machining_shop)]
    for i in range(n_machining_shop):
        sequence_assit[i].sort(key = lambda x: sequence_encode[i][x])
        operations[i]=[operations_assit[i][sequence_assit[i][j]] 
                        for j in range(len(sequence_assit[i]))]

    # operations2=[[0 for j in range(variables1[i])] for i in range(n_job)]#各车间待调度的工序
    variables3=copy.deepcopy(operations)
    #第三个变量：各车间待调度工序的加工顺序，第一个索引是车间，第二个索引是第几个待调度的工序，第三个索引的0 1 2分别是工件、批次、工序
    distrib4=[[[[0 
                     for l in range(Parameters_num[operation_type[i][k]])]
                    for k in range(n_job_operation_number[i])]
                for j in range(len(n_batches_number[i]))]
              for i in range(n_job)]
    variables4_assit=vector12vector4(variables4_encode,distrib4) 
    variables4=[[[[0 
                   for l in range(Parameters_num[operation_type[i][k]])] 
                  for k in range(n_job_operation_number[i])]
                 for j in range(len(n_batches_number[i]))]
                for i in range(n_job)]
    #第四个变量，工艺参数，索引分别对应工件，批次，工序，工艺参数
    for i in range(n_job):
        for j in range(len(n_batches_number[i])):
            for k in range(n_job_operation_number[i]):
                shopnum=variables1[i][j]
                toolnum=variables2[i][j][k]
                operationtype=operation_type[i][k]
                variables4[i][j][k]=[variables4_assit[i][j][k][l]*(parameter_bound[shopnum][toolnum][i][k][l][1]-parameter_bound[shopnum][toolnum][i][k][l][0])+parameter_bound[shopnum][toolnum][i][k][l][0] for l in range(Parameters_num[operationtype])]
    
    schedule=[[[] for j in range(n_machine_tool[i])] for i in range(n_machining_shop)] #reschdule[i][j][k] 调度信息   i是设备序号012...  j是操作号012... k是指代操作信息（0是操作序号，1是开始时间，2是结束时间）
    #调度信息，索引分别对应车间、机床、工序和信息，信息0表示工件号，1表示批次号，2表示工序号，3是开始时间，4是加工时间，5是结束时间,6是工艺参数，7是机床号，8是机床索引号，9是前四类能耗
    schedule_assit=[[[[0 
                        for l in range(9)]
                      for k in range(n_job_operation_number[i])] 
                      for j in range(len(variables1[i]))]
                    for i in range(n_job)]
    #调度辅助信息，索引分别对应工件，批次、工序所选的:车间、机床、开始时间、加工时间、结束时间、工艺参数、机床索引号、机床号、能耗
    #[chejian0,jichuang0,start_time,operationtime,start_time+operationtime,variables2[gongjian0][pici0],jichuang_index,jichuang0,operationenergy]
    #下面进行插入式解码

    for i in range(len(schedule)):#遍历每个车间
        for k in range(len(variables3[i])):#遍历每个工序
            gongjian0=variables3[i][k][0]
            pici0=variables3[i][k][1]
            gongxu0=variables3[i][k][2]
            piliang=nkl[gongjian0][pici0]
            chejian0=i
            jichuang_index=variables2[gongjian0][pici0][gongxu0]#可选机床索引
            jichuang0=n_job_operation_feasible_machines[gongjian0][gongxu0][chejian0][jichuang_index]#机床索引
            canshu0=variables4[gongjian0][pici0][gongxu0]#参数
            caozuozhonglei=operation_type[gongjian0][gongxu0]#操作类型，车铣钻
            
            shangxialiao=1
            if gongxu0>0 and k>0:
                if variables3[i][k-1]==[gongjian0,pici0,gongxu0-1]:
                    shangxialiao=0
            #工件，批量，工序，车间，机床，参数，操作种类（1，2，3），0-1是否需要上下料

            [operationtime,operationenergy,separete_energy]=Operationtimeandenergy(gongjian0,piliang,gongxu0,chejian0,jichuang0,canshu0,caozuozhonglei,shangxialiao)
            start_time=0
            insert_index=0
            if len(schedule[i][jichuang0])==0:#如果是该机器上的第一个工序
                if variables3[i][k][2]==0:#如果是工件的第一个工序
                    start_time=0
                else:#如果不是工件的第一个工序
                    start_time=schedule_assit[gongjian0][pici0][gongxu0-1][4]#该工件批次的上一个工序的结束时间                                           
                    # print()
            else:
                gongxushuliang=len(schedule[chejian0][jichuang0])
                min_starttime=0
                if variables3[i][k][2]>0:
                    min_starttime=schedule_assit[gongjian0][pici0][gongxu0-1][4]#该工件批次的上一个工序的结束时间
                    # print(schedule_assit[gongjian0][pici0][gongxu0-1][5])
                interval=[[max(schedule[chejian0][jichuang0][j-1][5],min_starttime),schedule[chejian0][jichuang0][j][3]] if j>0 else [min_starttime,schedule[chejian0][jichuang0][0][3]]
                          for j in range(gongxushuliang)]

                interval.append([max(schedule[chejian0][jichuang0][gongxushuliang-1][5],min_starttime),float('inf')])
                
                for j in range(len(interval)):
                    if interval[j][1]-interval[j][0]>=operationtime:
                        start_time=interval[j][0]
                        insert_index=j
                        break 
            schedule[i][jichuang0].insert(insert_index, [variables3[i][k][0],variables3[i][k][1],variables3[i][k][2],start_time,operationtime,start_time+operationtime,canshu0,jichuang0,jichuang_index,operationenergy,separete_energy])
            # if len(schedule[i][jichuang0])==0:
                # print(len(schedule[i][jichuang0]))
            schedule_assit[gongjian0][pici0][gongxu0]=[chejian0,jichuang0,start_time,operationtime,start_time+operationtime,canshu0,jichuang_index,jichuang0,operationenergy,separete_energy]            
            # print(schedule_assit[gongjian0][pici0][gongxu0])
    makespan=[[[schedule[i][j][k][5]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))]
    makespan=totalmax(makespan)
    
    energies=[[[schedule[i][j][k][9]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))]

    E_1=totalsum([[[schedule[i][j][k][10][0]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))])
    E_2=totalsum([[[schedule[i][j][k][10][1]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))])
    E_3=totalsum([[[schedule[i][j][k][10][2]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))])
    E_4=totalsum([[[schedule[i][j][k][10][3]
                            for k in range(len(schedule[i][j]))]
                        for j in range(len(schedule[i]))]
                  for i in range(len(schedule))])
    
    E_5=totalsum2([[(makespan-sum([schedule[i][j][k][4]
            for k in range(len(schedule[i][j]))]))*P_st[i][j]  
            for j in range(len(schedule[i]))] 
          for i in range(len(schedule))])
    
    
    
    Energyconsumption=totalsum(energies)+E_5
    return [Energyconsumption/3600000,makespan/3600,schedule,[E_1/3600000,E_2/3600000,E_3/3600000,E_4/3600000,E_5/3600000],[variables1,variables2,variables3,variables4]]


# Elist=[[0,0,0] for i in range(10)]
# for i in range(len(Elist)):
#     [Elist[i][0],Elist[i][1],Elist[i][2]]=fitness([random.randint(1, 10000)/10000 for i in range(n_variables)])
# Elist=sorted(Elist,key=lambda x: x[0])

# for i in range(len(Elist)):
#     gantteplot(Elist[i][2],i)


# test_num=1
# a1= [[random.randint(1, 10000)/10000 for i in range(n_variables)] for i in range(test_num)]
# E1=[0 for i in range(len(a1))]
# T1=[0 for i in range(len(a1))]
# schedule1=[0 for i in range(len(a1))]
# P1=[0 for i in range(len(a1))]
# for i in range(len(a1)):
#     [E1[i],T1[i],schedule1[i]]=fitness(a1[i])
#     P1[i]=E1[i]/T1[i]


# gantteplot(schedule1[0],n_machining_shop)

